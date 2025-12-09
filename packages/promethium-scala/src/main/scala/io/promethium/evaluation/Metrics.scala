package io.promethium.evaluation

import breeze.linalg._
import breeze.numerics._
import breeze.stats._
import io.promethium.core.SeismicDataset

/**
 * Evaluation metrics for seismic data reconstruction quality.
 *
 * All metrics follow the Promethium specification for cross-language
 * consistency with Python, R, and Julia implementations.
 */
object Metrics {
  
  private val EPSILON = 1e-10
  
  /**
   * Compute Signal-to-Noise Ratio in dB.
   *
   * SNR = 10 * log10(P_signal / P_noise)
   *
   * @param reference Ground truth signal
   * @param estimate  Estimated/reconstructed signal
   * @return SNR in decibels
   */
  def computeSNR(reference: DenseMatrix[Double], 
                 estimate: DenseMatrix[Double]): Double = {
    require(reference.rows == estimate.rows && reference.cols == estimate.cols,
      "Reference and estimate must have same dimensions")
    
    val refVec = reference.toDenseVector
    val estVec = estimate.toDenseVector
    
    val signalPower = mean(refVec *:* refVec)
    val noise = refVec - estVec
    val noisePower = mean(noise *:* noise)
    
    10.0 * math.log10(signalPower / (noisePower + EPSILON))
  }
  
  /**
   * Compute SNR between SeismicDatasets.
   */
  def computeSNR(reference: SeismicDataset, estimate: SeismicDataset): Double = {
    computeSNR(reference.traces, estimate.traces)
  }
  
  /**
   * Compute Mean Squared Error.
   *
   * MSE = mean((reference - estimate)^2)
   *
   * @param reference Ground truth signal
   * @param estimate  Estimated signal
   * @return MSE value
   */
  def computeMSE(reference: DenseMatrix[Double], 
                 estimate: DenseMatrix[Double]): Double = {
    require(reference.rows == estimate.rows && reference.cols == estimate.cols,
      "Reference and estimate must have same dimensions")
    
    val diff = reference - estimate
    mean(diff.toDenseVector *:* diff.toDenseVector)
  }
  
  def computeMSE(reference: SeismicDataset, estimate: SeismicDataset): Double = {
    computeMSE(reference.traces, estimate.traces)
  }
  
  /**
   * Compute Peak Signal-to-Noise Ratio in dB.
   *
   * PSNR = 10 * log10(max_val^2 / MSE)
   *
   * @param reference Ground truth signal
   * @param estimate  Estimated signal
   * @return PSNR in decibels
   */
  def computePSNR(reference: DenseMatrix[Double], 
                  estimate: DenseMatrix[Double]): Double = {
    val maxVal = max(abs(reference))
    val mse = computeMSE(reference, estimate)
    10.0 * math.log10(maxVal * maxVal / (mse + EPSILON))
  }
  
  def computePSNR(reference: SeismicDataset, estimate: SeismicDataset): Double = {
    computePSNR(reference.traces, estimate.traces)
  }
  
  /**
   * Compute Structural Similarity Index (SSIM).
   *
   * Simplified SSIM based on luminance and contrast components.
   *
   * @param reference Ground truth signal
   * @param estimate  Estimated signal
   * @return SSIM value in [-1, 1]
   */
  def computeSSIM(reference: DenseMatrix[Double], 
                  estimate: DenseMatrix[Double]): Double = {
    require(reference.rows == estimate.rows && reference.cols == estimate.cols,
      "Reference and estimate must have same dimensions")
    
    val refVec = reference.toDenseVector
    val estVec = estimate.toDenseVector
    
    val muX = mean(refVec)
    val muY = mean(estVec)
    val sigmaX = stddev(refVec)
    val sigmaY = stddev(estVec)
    
    // Covariance
    val covXY = mean((refVec - muX) *:* (estVec - muY))
    
    // Stability constants
    val C1 = 0.01 * 0.01
    val C2 = 0.03 * 0.03
    
    // SSIM formula
    val numerator = (2 * muX * muY + C1) * (2 * covXY + C2)
    val denominator = (muX * muX + muY * muY + C1) * (sigmaX * sigmaX + sigmaY * sigmaY + C2)
    
    numerator / denominator
  }
  
  def computeSSIM(reference: SeismicDataset, estimate: SeismicDataset): Double = {
    computeSSIM(reference.traces, estimate.traces)
  }
  
  /**
   * Compute all metrics between reference and estimate.
   *
   * @param reference    Ground truth dataset
   * @param estimate     Estimated dataset
   * @param metricNames  List of metrics to compute
   * @return Map of metric names to values
   */
  def evaluate(
    reference: SeismicDataset,
    estimate: SeismicDataset,
    metricNames: Seq[String] = Seq("snr", "mse", "psnr", "ssim")
  ): Map[String, Double] = {
    metricNames.map { name =>
      val value = name.toLowerCase match {
        case "snr" => computeSNR(reference, estimate)
        case "mse" => computeMSE(reference, estimate)
        case "psnr" => computePSNR(reference, estimate)
        case "ssim" => computeSSIM(reference, estimate)
        case _ => throw new IllegalArgumentException(s"Unknown metric: $name")
      }
      name.toLowerCase -> value
    }.toMap
  }
  
  /**
   * Compute relative reconstruction error.
   *
   * RelError = ||estimate - reference||_F / ||reference||_F
   *
   * @param reference Ground truth
   * @param estimate  Estimated signal
   * @return Relative Frobenius norm error
   */
  def relativeError(reference: DenseMatrix[Double], 
                    estimate: DenseMatrix[Double]): Double = {
    val diff = estimate - reference
    norm(diff.toDenseVector) / (norm(reference.toDenseVector) + EPSILON)
  }
}
