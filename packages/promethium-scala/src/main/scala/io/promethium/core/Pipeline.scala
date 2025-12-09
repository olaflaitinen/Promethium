package io.promethium.core

import breeze.linalg._

/**
 * Recovery pipeline configuration and execution.
 */
final case class RecoveryPipeline(
  name: String,
  config: Map[String, Any] = Map.empty
) {
  
  /**
   * Run the pipeline on a dataset.
   *
   * @param dataset Input seismic dataset
   * @param mask    Optional observation mask
   * @return Recovered dataset
   */
  def run(dataset: SeismicDataset, mask: Option[DenseMatrix[Boolean]] = None): SeismicDataset = {
    import io.promethium.recovery._
    
    val modelType = config.getOrElse("modelType", "matrix_completion").toString
    
    val result = modelType match {
      case "matrix_completion" =>
        val lambda = config.getOrElse("lambda", 0.1).asInstanceOf[Double]
        val maxIter = config.getOrElse("maxIter", 100).asInstanceOf[Int]
        val actualMask = mask.getOrElse {
          DenseMatrix.fill(dataset.nTraces, dataset.nSamples)(true)
        }
        MatrixCompletion.ista(dataset.traces, actualMask, lambda, maxIter)
        
      case "wiener" =>
        import io.promethium.signal.Filters
        val recovered = DenseMatrix.zeros[Double](dataset.nTraces, dataset.nSamples)
        for (i <- 0 until dataset.nTraces) {
          val row = dataset.traces(i, ::).t
          recovered(i, ::) := Filters.wienerFilter(row).t
        }
        recovered
        
      case _ =>
        throw new IllegalArgumentException(s"Unknown model type: $modelType")
    }
    
    dataset.copy(traces = result)
  }
}

object RecoveryPipeline {
  
  /**
   * Create pipeline from preset name.
   */
  def fromPreset(name: String): RecoveryPipeline = {
    val presets: Map[String, Map[String, Any]] = Map(
      "matrix_completion" -> Map("modelType" -> "matrix_completion", "lambda" -> 0.1, "maxIter" -> 100),
      "wiener" -> Map("modelType" -> "wiener"),
      "fista" -> Map("modelType" -> "fista", "lambda" -> 0.1, "maxIter" -> 100)
    )
    
    presets.get(name) match {
      case Some(config) => RecoveryPipeline(name, config)
      case None => throw new IllegalArgumentException(
        s"Unknown preset: $name. Available: ${presets.keys.mkString(", ")}"
      )
    }
  }
}
