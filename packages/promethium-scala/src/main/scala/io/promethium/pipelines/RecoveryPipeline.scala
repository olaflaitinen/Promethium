package io.promethium.pipelines

import breeze.linalg._
import io.promethium.core._
import io.promethium.signal.Filters
import io.promethium.recovery.{MatrixCompletion, CompressiveSensing}
import io.promethium.evaluation.Metrics

/**
 * High-level seismic data recovery pipeline.
 *
 * Orchestrates preprocessing, model execution, postprocessing,
 * and evaluation in a configurable workflow.
 *
 * @param name   Pipeline identifier
 * @param config Pipeline configuration
 */
final case class RecoveryPipeline(
  name: String,
  config: PipelineConfig
) {
  
  /**
   * Execute the recovery pipeline on input data.
   *
   * @param dataset Input seismic dataset
   * @param mask    Optional observation mask for completion problems
   * @return Reconstructed seismic dataset
   */
  def run(dataset: SeismicDataset, 
          mask: Option[DenseMatrix[Boolean]] = None): SeismicDataset = {
    
    // Step 1: Preprocessing
    var processed = dataset
    config.preprocessing.foreach {
      case PreprocessingStep.Normalize(method) =>
        val methodStr = method match {
          case NormalizationMethod.Max => "max"
          case NormalizationMethod.Rms => "rms"
          case NormalizationMethod.Standard => "standard"
        }
        processed = processed.normalize(methodStr)
        
      case PreprocessingStep.Bandpass(low, high) =>
        processed = Filters.bandpassFilter(processed, low, high)
        
      case PreprocessingStep.TimeWindow(t0, t1) =>
        processed = processed.timeWindow(t0, t1)
        
      case PreprocessingStep.RemoveDCOffset =>
        processed = Filters.removeDC(processed)
    }
    
    // Step 2: Model execution
    val recovered = config.model.modelType match {
      case ModelType.MatrixCompletion =>
        val actualMask = mask.getOrElse {
          DenseMatrix.fill(processed.nTraces, processed.nSamples)(true)
        }
        val completed = MatrixCompletion.ista(
          processed.traces,
          actualMask,
          config.model.lambda,
          config.model.maxIter,
          config.model.tolerance
        )
        processed.copy(traces = completed)
        
      case ModelType.CompressiveSensing =>
        // Apply FISTA per trace (simplified approach)
        val result = DenseMatrix.zeros[Double](processed.nTraces, processed.nSamples)
        val n = processed.nSamples
        val A = DenseMatrix.eye[Double](n)  // Identity for denoising
        for (i <- 0 until processed.nTraces) {
          val y = processed.traces(i, ::).t
          val x = CompressiveSensing.fista(y, A, config.model.lambda, config.model.maxIter)
          result(i, ::) := x.t
        }
        processed.copy(traces = result)
        
      case ModelType.Wiener =>
        Filters.wienerFilter(processed, None)
        
      case ModelType.UNet | ModelType.Autoencoder | ModelType.PINN =>
        // Deep learning models would require DL4J integration
        throw UnsupportedOperationException(
          s"Deep learning model ${config.model.modelType} requires DL4J dependency")
    }
    
    // Step 3: Postprocessing
    var result = recovered
    config.postprocessing.foreach {
      case PostprocessingStep.Normalize(method) =>
        val methodStr = method match {
          case NormalizationMethod.Max => "max"
          case NormalizationMethod.Rms => "rms"
          case NormalizationMethod.Standard => "standard"
        }
        result = result.normalize(methodStr)
        
      case PostprocessingStep.Clip(minVal, maxVal) =>
        val clipped = result.traces.map { v =>
          math.max(minVal, math.min(maxVal, v))
        }
        result = result.copy(traces = clipped)
        
      case PostprocessingStep.Denoise =>
        result = Filters.wienerFilter(result, None)
    }
    
    result
  }
  
  /**
   * Evaluate reconstruction quality.
   *
   * @param truth      Ground truth dataset
   * @param prediction Reconstructed dataset
   * @return Map of metric names to values
   */
  def evaluate(truth: SeismicDataset, prediction: SeismicDataset): Map[String, Double] = {
    Metrics.evaluate(truth, prediction, config.evaluation.metrics)
  }
}

/**
 * Factory for creating pipelines from presets.
 */
object PipelinePresets {
  
  /** Matrix completion pipeline with nuclear norm regularization. */
  def matrixCompletion(lambda: Double = 0.1, maxIter: Int = 100): RecoveryPipeline = {
    RecoveryPipeline(
      name = "matrix_completion",
      config = PipelineConfig(
        preprocessing = List(PreprocessingStep.Normalize(NormalizationMethod.Rms)),
        model = ModelConfig(
          modelType = ModelType.MatrixCompletion,
          lambda = lambda,
          maxIter = maxIter
        )
      )
    )
  }
  
  /** Wiener filter denoising pipeline. */
  def wiener(): RecoveryPipeline = {
    RecoveryPipeline(
      name = "wiener",
      config = PipelineConfig(
        model = ModelConfig(modelType = ModelType.Wiener)
      )
    )
  }
  
  /** FISTA-based sparse recovery pipeline. */
  def fista(lambda: Double = 0.1, maxIter: Int = 100): RecoveryPipeline = {
    RecoveryPipeline(
      name = "fista",
      config = PipelineConfig(
        model = ModelConfig(
          modelType = ModelType.CompressiveSensing,
          lambda = lambda,
          maxIter = maxIter
        )
      )
    )
  }
  
  /**
   * Get pipeline from preset name.
   *
   * @param name Preset name
   * @return RecoveryPipeline
   */
  def fromPreset(name: String): RecoveryPipeline = {
    name.toLowerCase.replace("_", "") match {
      case "matrixcompletion" => matrixCompletion()
      case "wiener" => wiener()
      case "fista" | "compressivesensing" => fista()
      case _ => throw InvalidConfigException(s"Unknown preset: $name")
    }
  }
}
