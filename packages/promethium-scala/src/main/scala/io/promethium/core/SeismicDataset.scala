package io.promethium.core

import breeze.linalg._

/**
 * Container for seismic trace data.
 *
 * Represents a collection of seismic traces with associated sampling
 * information and metadata. This is the primary data structure for
 * seismic processing in Promethium.
 *
 * @param traces     2D matrix of amplitudes (n_traces x n_samples)
 * @param dt         Sampling interval in seconds
 * @param coords     Optional trace coordinates
 * @param metadata   Key-value metadata map
 */
final case class SeismicDataset(
  traces: DenseMatrix[Double],
  dt: Double,
  coords: Option[DenseMatrix[Double]] = None,
  metadata: Map[String, String] = Map.empty
) {
  require(dt > 0, "Sampling interval must be positive")
  
  /** Number of traces in the dataset */
  def nTraces: Int = traces.rows
  
  /** Number of samples per trace */
  def nSamples: Int = traces.cols
  
  /** Total duration in seconds */
  def duration: Double = nSamples * dt
  
  /**
   * Normalize trace amplitudes.
   *
   * @param method Normalization method: "rms", "max", or "std"
   * @return New SeismicDataset with normalized traces
   */
  def normalize(method: String = "rms"): SeismicDataset = {
    val normalized = method match {
      case "rms" =>
        val rms = sqrt(sum(traces *:* traces, Axis._1) / nSamples.toDouble)
        traces(*, ::).map { row =>
          val rmsVal = sqrt(sum(row *:* row) / row.length.toDouble) + 1e-10
          row / rmsVal
        }
      case "max" =>
        val maxVal = max(abs(traces)) + 1e-10
        traces / maxVal
      case _ =>
        throw new IllegalArgumentException(s"Unknown normalization method: $method")
    }
    copy(traces = normalized)
  }
  
  /**
   * Extract subset of traces.
   *
   * @param traceRange Range of trace indices
   * @param sampleRange Range of sample indices
   * @return New SeismicDataset with subset
   */
  def subset(traceRange: Range = 0 until nTraces, 
             sampleRange: Range = 0 until nSamples): SeismicDataset = {
    val subTraces = traces(traceRange, sampleRange).toDenseMatrix
    val subCoords = coords.map(c => c(traceRange, ::).toDenseMatrix)
    copy(traces = subTraces, coords = subCoords)
  }
  
  override def toString: String = 
    s"SeismicDataset($nTraces traces, $nSamples samples, dt=${dt}s)"
}

/**
 * Companion object with factory methods.
 */
object SeismicDataset {
  /**
   * Create from 2D array.
   */
  def fromArray(data: Array[Array[Double]], dt: Double): SeismicDataset = {
    val matrix = DenseMatrix(data: _*)
    SeismicDataset(matrix, dt)
  }
}
