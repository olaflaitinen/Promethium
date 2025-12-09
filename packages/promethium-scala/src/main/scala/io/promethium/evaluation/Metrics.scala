package io.promethium.evaluation

import breeze.linalg._
import breeze.numerics._

/**
 * Evaluation metrics for seismic reconstruction quality assessment.
 *
 * Implements SNR, MSE, PSNR, SSIM following the Promethium specification
 * for cross-language numerical consistency.
 */
object Metrics {
  
  private val EPSILON = 1e-10
  
  /**
   * Compute Signal-to-Noise Ratio in decibels.
   *
   * SNR = 10 * log10(signal_power / noise_power)
   *
   * @param reference Ground truth signal
   * @param estimate  Reconstructed signal
   * @return SNR value in dB
   */
  def computeSNR(reference: DenseMatrix[Double], 
                 estimate: DenseMatrix[Double]): Double = {
    require(reference.rows == estimate.rows && reference.cols == estimate.cols,
            "Matrices must have same dimensions")
    
    val signalPower = sum(reference *:* reference) / reference.size.toDouble
    val noise = reference - estimate
    val noisePower = sum(noise *:* noise) / noise.size.toDouble
    
    10 * log10(signalPower / (noisePower + EPSILON))
  }
  
  /**
   * Compute Mean Squared Error.
   *
   * @param reference Ground truth signal
   * @param estimate  Reconstructed signal
   * @return MSE value
   */
  def computeMSE(reference: DenseMatrix[Double], 
                 estimate: DenseMatrix[Double]): Double = {
    val diff = reference - estimate
    sum(diff *:* diff) / diff.size.toDouble
  }
  
  /**
   * Compute Peak Signal-to-Noise Ratio in decibels.
   *
   * PSNR = 10 * log10(max_val^2 / MSE)
   *
   * @param reference Ground truth signal
   * @param estimate  Reconstructed signal
   * @return PSNR value in dB
   */
  def computePSNR(reference: DenseMatrix[Double], 
                  estimate: DenseMatrix[Double]): Double = {
    val mse = computeMSE(reference, estimate)
    val maxVal = max(abs(reference))
    10 * log10(maxVal * maxVal / (mse + EPSILON))
  }
  
  /**
   * Compute Structural Similarity Index.
   *
   * Simplified global SSIM for cross-language comparison.
   *
   * @param reference Ground truth signal
   * @param estimate  Reconstructed signal
   * @param C1        Stability constant (default 0.0001)
   * @param C2        Stability constant (default 0.0009)
   * @return SSIM value in [0, 1]
   */
  def computeSSIM(reference: DenseMatrix[Double],
                  estimate: DenseMatrix[Double],
                  C1: Double = 0.0001,
                  C2: Double = 0.0009): Double = {
    val refVec = reference.toDenseVector
    val estVec = estimate.toDenseVector
    
    val muX = mean(refVec)
    val muY = mean(estVec)
    
    val sigmaX = sqrt(variance(refVec))
    val sigmaY = sqrt(variance(estVec))
    
    // Covariance
    val sigmaXY = {
      val centeredX = refVec - muX
      val centeredY = estVec - muY
      sum(centeredX *:* centeredY) / (refVec.length - 1).toDouble
    }
    
    val numerator = (2 * muX * muY + C1) * (2 * sigmaXY + C2)
    val denominator = (muX * muX + muY * muY + C1) * (sigmaX * sigmaX + sigmaY * sigmaY + C2)
    
    numerator / denominator
  }
  
  /**
   * Compute multiple evaluation metrics.
   *
   * @param reference Ground truth signal
   * @param estimate  Reconstructed signal
   * @param metrics   Sequence of metric names to compute
   * @return Map of metric name to value
   */
  def evaluate(reference: DenseMatrix[Double],
               estimate: DenseMatrix[Double],
               metrics: Seq[String] = Seq("snr", "mse", "psnr", "ssim")): Map[String, Double] = {
    metrics.map {
      case "snr" => "snr" -> computeSNR(reference, estimate)
      case "mse" => "mse" -> computeMSE(reference, estimate)
      case "psnr" => "psnr" -> computePSNR(reference, estimate)
      case "ssim" => "ssim" -> computeSSIM(reference, estimate)
      case other => throw new IllegalArgumentException(s"Unknown metric: $other")
    }.toMap
  }
  
  // Helper for variance calculation
  private def variance(v: DenseVector[Double]): Double = {
    val mu = mean(v)
    val centered = v - mu
    sum(centered *:* centered) / (v.length - 1).toDouble
  }
}
