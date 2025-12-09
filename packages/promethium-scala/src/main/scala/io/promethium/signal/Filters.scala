package io.promethium.signal

import breeze.linalg._
import breeze.numerics._
import breeze.signal._
import io.promethium.core.SeismicDataset

/**
 * Signal processing filters for seismic data.
 *
 * Provides frequency-domain filtering operations including
 * bandpass, lowpass, highpass, and Wiener filters.
 */
object Filters {
  
  private val EPSILON = 1e-10
  
  /**
   * Apply Wiener filter for noise attenuation.
   *
   * The Wiener filter minimizes mean squared error between estimated and true signal:
   * H(f) = Pxx(f) / (Pxx(f) + Pnn(f))
   *
   * @param signal   Input signal
   * @param noiseVar Noise variance estimate (None for auto-estimate)
   * @return Filtered signal
   */
  def wienerFilter(signal: DenseVector[Double], 
                   noiseVar: Option[Double] = None): DenseVector[Double] = {
    val n = signal.length
    
    // FFT
    val Y = fourierTr(signal)
    val Py = Y.map(c => c.real * c.real + c.imag * c.imag) / n.toDouble
    
    // Estimate noise PSD
    val Pn: DenseVector[Double] = noiseVar match {
      case Some(v) => DenseVector.fill(n)(v)
      case None =>
        // Estimate from high-frequency tail
        val tailStart = n / 2
        val tailMean = sum(Py(tailStart until n)) / (n - tailStart).toDouble
        DenseVector.fill(n)(tailMean)
    }
    
    // Wiener filter
    val Ps = Py.map(v => math.max(v, 0.0)) - Pn.map(v => math.max(v, 0.0))
    val H = (Ps + EPSILON) /:/ (Ps + Pn + EPSILON)
    
    // Apply filter
    val SHat = Y *:* H.map(h => breeze.math.Complex(h, 0.0))
    
    // Inverse FFT
    iFourierTr(SHat).map(_.real)
  }
  
  /**
   * Apply Wiener filter to entire dataset.
   *
   * @param dataset  Input seismic dataset
   * @param noiseVar Optional noise variance estimate
   * @return Filtered dataset
   */
  def wienerFilter(dataset: SeismicDataset, 
                   noiseVar: Option[Double]): SeismicDataset = {
    val result = DenseMatrix.zeros[Double](dataset.nTraces, dataset.nSamples)
    for (i <- 0 until dataset.nTraces) {
      val row = dataset.traces(i, ::).t
      result(i, ::) := wienerFilter(row, noiseVar).t
    }
    dataset.copy(traces = result)
  }
  
  /**
   * Apply bandpass filter in frequency domain.
   *
   * @param signal   Input signal
   * @param dt       Sampling interval
   * @param lowFreq  Low cutoff frequency (Hz)
   * @param highFreq High cutoff frequency (Hz)
   * @param taperWidth Taper width in Hz for smooth rolloff
   * @return Filtered signal
   */
  def bandpassFilter(signal: DenseVector[Double], dt: Double,
                     lowFreq: Double, highFreq: Double,
                     taperWidth: Double = 5.0): DenseVector[Double] = {
    val n = signal.length
    val X = fourierTr(signal)
    
    // Frequency axis
    val df = 1.0 / (n * dt)
    
    // Create bandpass mask with cosine taper
    val mask = DenseVector.zeros[Double](n)
    for (i <- 0 until n) {
      val freq = if (i <= n / 2) i * df else (i - n) * df
      val absFreq = math.abs(freq)
      
      if (absFreq >= lowFreq && absFreq <= highFreq) {
        mask(i) = 1.0
      } else if (absFreq >= lowFreq - taperWidth && absFreq < lowFreq) {
        mask(i) = 0.5 * (1 + math.cos(math.Pi * (lowFreq - absFreq) / taperWidth))
      } else if (absFreq > highFreq && absFreq <= highFreq + taperWidth) {
        mask(i) = 0.5 * (1 + math.cos(math.Pi * (absFreq - highFreq) / taperWidth))
      }
    }
    
    // Apply mask
    val XFiltered = X *:* mask.map(m => breeze.math.Complex(m, 0.0))
    
    // Inverse FFT
    iFourierTr(XFiltered).map(_.real)
  }
  
  /**
   * Apply bandpass filter to entire dataset.
   *
   * @param dataset  Input dataset
   * @param lowFreq  Low cutoff frequency (Hz)
   * @param highFreq High cutoff frequency (Hz)
   * @return Filtered dataset
   */
  def bandpassFilter(dataset: SeismicDataset, 
                     lowFreq: Double, highFreq: Double): SeismicDataset = {
    val result = DenseMatrix.zeros[Double](dataset.nTraces, dataset.nSamples)
    for (i <- 0 until dataset.nTraces) {
      val row = dataset.traces(i, ::).t
      result(i, ::) := bandpassFilter(row, dataset.dt, lowFreq, highFreq).t
    }
    dataset.copy(traces = result)
  }
  
  /**
   * Remove DC offset (mean) from signal.
   *
   * @param signal Input signal
   * @return Signal with zero mean
   */
  def removeDC(signal: DenseVector[Double]): DenseVector[Double] = {
    signal - mean(signal)
  }
  
  /**
   * Remove DC offset from entire dataset.
   *
   * @param dataset Input dataset
   * @return Dataset with zero-mean traces
   */
  def removeDC(dataset: SeismicDataset): SeismicDataset = {
    val result = DenseMatrix.zeros[Double](dataset.nTraces, dataset.nSamples)
    for (i <- 0 until dataset.nTraces) {
      val row = dataset.traces(i, ::).t
      result(i, ::) := removeDC(row).t
    }
    dataset.copy(traces = result)
  }
}
