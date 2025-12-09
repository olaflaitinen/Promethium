package io.promethium.core

/**
 * Configuration and sealed hierarchies for pipeline construction.
 */

/** Normalization methods for seismic data. */
sealed trait NormalizationMethod
object NormalizationMethod {
  case object Max extends NormalizationMethod
  case object Rms extends NormalizationMethod
  case object Standard extends NormalizationMethod
  
  def fromString(s: String): NormalizationMethod = s.toLowerCase match {
    case "max" => Max
    case "rms" => Rms
    case "standard" | "zscore" => Standard
    case _ => throw InvalidConfigException(s"Unknown normalization method: $s")
  }
}

/** Preprocessing step in a pipeline. */
sealed trait PreprocessingStep
object PreprocessingStep {
  final case class Normalize(method: NormalizationMethod) extends PreprocessingStep
  final case class Bandpass(lowFreq: Double, highFreq: Double) extends PreprocessingStep
  final case class TimeWindow(t0: Double, t1: Double) extends PreprocessingStep
  case object RemoveDCOffset extends PreprocessingStep
}

/** Postprocessing step in a pipeline. */
sealed trait PostprocessingStep
object PostprocessingStep {
  final case class Normalize(method: NormalizationMethod) extends PostprocessingStep
  final case class Clip(minVal: Double, maxVal: Double) extends PostprocessingStep
  case object Denoise extends PostprocessingStep
}

/** Model type for recovery. */
sealed trait ModelType
object ModelType {
  case object MatrixCompletion extends ModelType
  case object CompressiveSensing extends ModelType
  case object Wiener extends ModelType
  case object UNet extends ModelType
  case object Autoencoder extends ModelType
  case object PINN extends ModelType
  
  def fromString(s: String): ModelType = s.toLowerCase.replace("_", "") match {
    case "matrixcompletion" => MatrixCompletion
    case "compressivesensing" | "fista" => CompressiveSensing
    case "wiener" => Wiener
    case "unet" => UNet
    case "autoencoder" => Autoencoder
    case "pinn" | "physicsinformed" => PINN
    case _ => throw InvalidConfigException(s"Unknown model type: $s")
  }
}

/**
 * Configuration for a recovery model.
 *
 * @param modelType     Type of model to use
 * @param lambda        Regularization parameter
 * @param maxIter       Maximum iterations
 * @param tolerance     Convergence tolerance
 * @param extraParams   Additional model-specific parameters
 */
final case class ModelConfig(
  modelType: ModelType,
  lambda: Double = 0.1,
  maxIter: Int = 100,
  tolerance: Double = 1e-5,
  extraParams: Map[String, Any] = Map.empty
)

/**
 * Configuration for evaluation metrics.
 *
 * @param metrics List of metric names to compute
 */
final case class EvaluationConfig(
  metrics: Seq[String] = Seq("snr", "mse", "psnr", "ssim")
)

/**
 * Complete pipeline configuration.
 *
 * @param preprocessing  List of preprocessing steps
 * @param model          Model configuration
 * @param postprocessing List of postprocessing steps
 * @param evaluation     Evaluation configuration
 */
final case class PipelineConfig(
  preprocessing: List[PreprocessingStep] = List.empty,
  model: ModelConfig,
  postprocessing: List[PostprocessingStep] = List.empty,
  evaluation: EvaluationConfig = EvaluationConfig()
)
