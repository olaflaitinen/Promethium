package io.promethium.core

import breeze.linalg._
import breeze.numerics._
import breeze.stats._

/**
 * Represents a seismic dataset containing multiple traces.
 *
 * This is the primary data structure for seismic data in Promethium.
 * Each trace represents a time series recorded at a specific receiver location.
 *
 * @param traces    2D matrix where rows are traces and columns are time samples
 * @param dt        Sampling interval in seconds
 * @param coords    Optional coordinate array (x, y) for each trace
 * @param metadata  Key-value metadata pairs
 */
final case class SeismicDataset(
  traces: DenseMatrix[Double],
  dt: Double,
  coords: Option[DenseMatrix[Double]] = None,
  metadata: Map[String, String] = Map.empty
) {
  require(dt > 0, "Sampling interval dt must be positive")
  require(traces.rows > 0, "Dataset must contain at least one trace")
  require(traces.cols > 0, "Traces must contain at least one sample")
  
  /** Number of traces in the dataset. */
  def nTraces: Int = traces.rows
  
  /** Number of samples per trace. */
  def nSamples: Int = traces.cols
  
  /** Total recording duration in seconds. */
  def duration: Double = (nSamples - 1) * dt
  
  /** Time axis values. */
  def timeAxis: DenseVector[Double] = 
    DenseVector.tabulate(nSamples)(i => i * dt)
  
  /**
   * Extract a subset of traces by indices.
   *
   * @param indices Trace indices to extract
   * @return New SeismicDataset with selected traces
   */
  def subsetTraces(indices: Seq[Int]): SeismicDataset = {
    require(indices.forall(i => i >= 0 && i < nTraces), "Invalid trace indices")
    val newTraces = DenseMatrix.zeros[Double](indices.length, nSamples)
    indices.zipWithIndex.foreach { case (srcIdx, dstIdx) =>
      newTraces(dstIdx, ::) := traces(srcIdx, ::)
    }
    val newCoords = coords.map { c =>
      val nc = DenseMatrix.zeros[Double](indices.length, c.cols)
      indices.zipWithIndex.foreach { case (srcIdx, dstIdx) =>
        nc(dstIdx, ::) := c(srcIdx, ::)
      }
      nc
    }
    copy(traces = newTraces, coords = newCoords)
  }
  
  /**
   * Extract a time window from all traces.
   *
   * @param t0 Start time in seconds
   * @param t1 End time in seconds
   * @return New SeismicDataset with windowed traces
   */
  def timeWindow(t0: Double, t1: Double): SeismicDataset = {
    require(t0 >= 0 && t0 < t1, "Invalid time window")
    val i0 = math.max(0, (t0 / dt).toInt)
    val i1 = math.min(nSamples - 1, (t1 / dt).toInt)
    val newTraces = traces(::, i0 to i1)
    copy(traces = newTraces)
  }
  
  /**
   * Normalize traces using specified method.
   *
   * @param method Normalization method: "max", "rms", or "standard"
   * @return Normalized SeismicDataset
   */
  def normalize(method: String = "rms"): SeismicDataset = {
    val normalized = DenseMatrix.zeros[Double](nTraces, nSamples)
    
    method.toLowerCase match {
      case "max" =>
        for (i <- 0 until nTraces) {
          val row = traces(i, ::).t
          val maxVal = max(abs(row))
          if (maxVal > 1e-10) {
            normalized(i, ::) := (row / maxVal).t
          }
        }
        
      case "rms" =>
        for (i <- 0 until nTraces) {
          val row = traces(i, ::).t
          val rms = sqrt(mean(row *:* row))
          if (rms > 1e-10) {
            normalized(i, ::) := (row / rms).t
          }
        }
        
      case "standard" =>
        for (i <- 0 until nTraces) {
          val row = traces(i, ::).t
          val m = mean(row)
          val s = stddev(row)
          if (s > 1e-10) {
            normalized(i, ::) := ((row - m) / s).t
          }
        }
        
      case _ =>
        throw new IllegalArgumentException(s"Unknown normalization method: $method")
    }
    
    copy(traces = normalized)
  }
  
  /**
   * Compute basic statistics for the dataset.
   *
   * @return Map of statistic names to values
   */
  def statistics: Map[String, Double] = {
    val allValues = traces.toDenseVector
    Map(
      "min" -> min(allValues),
      "max" -> max(allValues),
      "mean" -> mean(allValues),
      "std" -> stddev(allValues),
      "rms" -> sqrt(mean(allValues *:* allValues))
    )
  }
  
  override def toString: String = 
    s"SeismicDataset(nTraces=$nTraces, nSamples=$nSamples, dt=$dt, duration=${duration}s)"
}

object SeismicDataset {
  
  /**
   * Create SeismicDataset from raw 2D array.
   *
   * @param data 2D array where each row is a trace
   * @param dt   Sampling interval
   * @return SeismicDataset
   */
  def fromArray(data: Array[Array[Double]], dt: Double): SeismicDataset = {
    require(data.nonEmpty, "Data array must not be empty")
    val nTraces = data.length
    val nSamples = data.head.length
    val matrix = DenseMatrix.zeros[Double](nTraces, nSamples)
    for (i <- data.indices) {
      matrix(i, ::) := DenseVector(data(i)).t
    }
    SeismicDataset(matrix, dt)
  }
  
  /**
   * Generate synthetic seismic dataset for testing.
   *
   * @param nTraces    Number of traces
   * @param nSamples   Samples per trace
   * @param dt         Sampling interval
   * @param noiseLevel Noise level relative to signal
   * @param seed       Random seed for reproducibility
   * @return Synthetic SeismicDataset
   */
  def synthetic(
    nTraces: Int = 100,
    nSamples: Int = 500,
    dt: Double = 0.004,
    noiseLevel: Double = 0.1,
    seed: Option[Long] = None
  ): SeismicDataset = {
    import scala.util.Random
    val random = seed.map(new Random(_)).getOrElse(new Random())
    
    val traces = DenseMatrix.zeros[Double](nTraces, nSamples)
    val t = DenseVector.tabulate(nSamples)(i => i * dt)
    
    for (i <- 0 until nTraces) {
      val nEvents = 3 + random.nextInt(5)
      for (_ <- 0 until nEvents) {
        val eventTime = random.nextDouble() * (t(-1) - 0.2) + 0.1
        val eventAmp = (random.nextDouble() * 1.0 + 0.5) * (if (random.nextBoolean()) 1 else -1)
        val f0 = 30.0
        
        for (j <- 0 until nSamples) {
          val tau = t(j) - eventTime
          val wavelet = (1.0 - 2.0 * math.pow(math.Pi * f0 * tau, 2)) *
                        math.exp(-math.pow(math.Pi * f0 * tau, 2))
          traces(i, j) += eventAmp * wavelet
        }
      }
    }
    
    // Add noise
    if (noiseLevel > 0) {
      val signalRms = sqrt(mean(traces.toDenseVector *:* traces.toDenseVector))
      for (i <- 0 until nTraces; j <- 0 until nSamples) {
        traces(i, j) += noiseLevel * signalRms * random.nextGaussian()
      }
    }
    
    SeismicDataset(
      traces = traces,
      dt = dt,
      metadata = Map(
        "synthetic" -> "true",
        "nTraces" -> nTraces.toString,
        "nSamples" -> nSamples.toString,
        "noiseLevel" -> noiseLevel.toString
      )
    )
  }
}
