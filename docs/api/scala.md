# Scala API Reference

Promethium for Scala provides a native JVM implementation of the seismic data recovery framework.

## Installation

Add to your `build.sbt`:

```scala
libraryDependencies += "io.promethium" %% "promethium-scala" % "1.0.4"
```

## Quick Start

```scala
import io.promethium.core._
import io.promethium.pipelines._
import io.promethium.evaluation._

// Create or load dataset
val dataset = SeismicDataset.synthetic(nTraces = 100, nSamples = 500, dt = 0.004)

// Create pipeline from preset
val pipeline = PipelinePresets.matrixCompletion(lambda = 0.1)

// Run recovery
val result = pipeline.run(dataset)

// Evaluate
val metrics = Metrics.evaluate(dataset, result)
println(s"SNR: ${metrics("snr")} dB")
```

## Core Types

### SeismicDataset

```scala
final case class SeismicDataset(
  traces: DenseMatrix[Double],  // (nTraces x nSamples)
  dt: Double,                   // Sampling interval (seconds)
  coords: Option[DenseMatrix[Double]] = None,
  metadata: Map[String, String] = Map.empty
)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `nTraces` | Number of traces |
| `nSamples` | Samples per trace |
| `duration` | Total recording time |
| `normalize(method)` | Normalize traces ("max", "rms", "standard") |
| `subsetTraces(indices)` | Extract subset of traces |
| `timeWindow(t0, t1)` | Extract time window |

**Factory Methods:**

```scala
// From raw array
SeismicDataset.fromArray(data: Array[Array[Double]], dt: Double)

// Generate synthetic data
SeismicDataset.synthetic(
  nTraces = 100,
  nSamples = 500,
  dt = 0.004,
  noiseLevel = 0.1,
  seed = Some(42)
)
```

### VelocityModel

```scala
final case class VelocityModel(
  velocities: DenseMatrix[Double],  // (nz x nx) grid
  dx: Double,                       // Horizontal spacing
  dz: Double,                       // Vertical spacing
  origin: (Double, Double) = (0.0, 0.0),
  metadata: Map[String, String] = Map.empty
)
```

**Factory Methods:**

```scala
VelocityModel.constant(velocity, nx, nz, dx, dz)
VelocityModel.linear(v0, gradient, nx, nz, dx, dz)
```

## Recovery Algorithms

### Matrix Completion

```scala
import io.promethium.recovery.MatrixCompletion

val completed = MatrixCompletion.ista(
  observed = observedMatrix,
  mask = maskMatrix,        // true = observed
  lambda = 0.1,
  maxIter = 100,
  tolerance = 1e-5
)
```

### Compressive Sensing

```scala
import io.promethium.recovery.CompressiveSensing

val recovered = CompressiveSensing.fista(
  y = observations,
  A = measurementMatrix,
  lambda = 0.1,
  maxIter = 100
)
```

## Signal Processing

### Filters

```scala
import io.promethium.signal.Filters

// Wiener filter
val denoised = Filters.wienerFilter(dataset, noiseVar = None)

// Bandpass filter
val filtered = Filters.bandpassFilter(dataset, lowFreq = 5.0, highFreq = 80.0)

// Remove DC offset
val zeroed = Filters.removeDC(dataset)
```

## Pipelines

### Using Presets

```scala
import io.promethium.pipelines.PipelinePresets

val pipe1 = PipelinePresets.matrixCompletion(lambda = 0.1)
val pipe2 = PipelinePresets.wiener()
val pipe3 = PipelinePresets.fista(lambda = 0.1)
```

### Custom Pipeline

```scala
import io.promethium.core._
import io.promethium.pipelines._

val config = PipelineConfig(
  preprocessing = List(
    PreprocessingStep.Normalize(NormalizationMethod.Rms),
    PreprocessingStep.Bandpass(5.0, 80.0)
  ),
  model = ModelConfig(
    modelType = ModelType.MatrixCompletion,
    lambda = 0.1,
    maxIter = 100
  ),
  postprocessing = List(
    PostprocessingStep.Normalize(NormalizationMethod.Max)
  )
)

val pipeline = RecoveryPipeline("custom", config)
val result = pipeline.run(dataset, mask = Some(observationMask))
```

## Evaluation Metrics

```scala
import io.promethium.evaluation.Metrics

// Individual metrics
val snr = Metrics.computeSNR(reference, estimate)
val mse = Metrics.computeMSE(reference, estimate)
val psnr = Metrics.computePSNR(reference, estimate)
val ssim = Metrics.computeSSIM(reference, estimate)

// All at once
val metrics = Metrics.evaluate(reference, estimate, 
  Seq("snr", "mse", "psnr", "ssim"))
```

## I/O

### SEG-Y Format

```scala
import io.promethium.io.SegyIO

// Read
val dataset = SegyIO.read("data.sgy")

// Write
SegyIO.write("output.sgy", dataset)
```

## Error Handling

```scala
import io.promethium.core._

try {
  val ds = SegyIO.read("missing.sgy")
} catch {
  case e: IoException => 
    println(s"I/O error: ${e.getMessage}")
  case e: InvalidConfigException => 
    println(s"Config error: ${e.getMessage}")
  case e: AlgorithmConvergenceException =>
    println(s"Convergence error: ${e.getMessage}")
}
```

## Building from Source

```bash
cd packages/promethium-scala
sbt compile
sbt test
sbt package
```

## Cross-Language Consistency

This Scala implementation produces numerically identical results to Python, R, and Julia within specified tolerances (1e-6 absolute, 1e-4 relative for metrics).
