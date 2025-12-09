package io.promethium.signal

import breeze.linalg._
import breeze.numerics._
import breeze.signal._

/**
 * Signal processing functions for seismic data.
 */
object Filters {
  
  private val EPSILON = 1e-10
  
  /**
   * Apply Wiener filter for denoising.
   *
   * @param y        Noisy signal
   * @param noiseVar Noise variance estimate (null for auto-estimate)
   * @return Denoised signal
   */
  def wienerFilter(y: DenseVector[Double], noiseVar: Option[Double] = None): DenseVector[Double] = {
    val n = y.length
    
    // FFT
    val Y = fourierTr(y)
    val Py = Y.map(c => c.real * c.real + c.imag * c.imag) / n.toDouble
    
    // Estimate noise PSD
    val Pn = noiseVar match {
      case Some(v) => DenseVector.fill(n)(v)
      case None =>
        // Estimate from high-frequency tail
        val tailStart = n / 2
        val tailMean = sum(Py(tailStart until n)) / (n - tailStart).toDouble
        DenseVector.fill(n)(tailMean)
    }
    
    // Wiener filter
    val Ps = Py.map(v => max(v, 0.0)) - Pn.map(v => max(v, 0.0))
    val H = (Ps + EPSILON) /:/ (Ps + Pn + EPSILON)
    
    // Apply filter
    val SHat = Y *:* H.map(h => breeze.math.Complex(h, 0.0))
    
    // Inverse FFT
    iFourierTr(SHat).map(_.real)
  }
  
  /**
   * Apply bandpass filter in frequency domain.
   *
   * @param x        Input signal
   * @param dt       Sampling interval
   * @param lowFreq  Low cutoff frequency (Hz)
   * @param highFreq High cutoff frequency (Hz)
   * @return Filtered signal
   */
  def bandpassFilter(x: DenseVector[Double], dt: Double, 
                     lowFreq: Double, highFreq: Double): DenseVector[Double] = {
    val n = x.length
    val X = fourierTr(x)
    
    // Frequency axis
    val df = 1.0 / (n * dt)
    
    // Create bandpass mask
    val mask = DenseVector.zeros[Double](n)
    for (i <- 0 until n) {
      val freq = if (i <= n/2) i * df else (i - n) * df
      if (abs(freq) >= lowFreq && abs(freq) <= highFreq) {
        mask(i) = 1.0
      }
    }
    
    // Apply mask
    val XFiltered = X *:* mask.map(m => breeze.math.Complex(m, 0.0))
    
    // Inverse FFT
    iFourierTr(XFiltered).map(_.real)
  }
}
