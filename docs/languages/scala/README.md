# Scala Guide for promethium-scala

## Installation

Add to `build.sbt`:

```scala
libraryDependencies += "io.github.olaflaitinen" %% "promethium-scala" % "1.0.4"
```

Or build from source:

```bash
cd packages/promethium-scala
sbt publishLocal
```

## Quick Start

```scala
import io.promethium.core._
import io.promethium.evaluation._
import io.promethium.recovery._
import breeze.linalg._

// Create dataset
val traces = DenseMatrix.rand(100, 500)
val ds = SeismicDataset(traces, dt = 0.004)

// Create and run pipeline
val pipe = RecoveryPipeline.fromPreset("matrix_completion")
val result = pipe.run(ds)

// Evaluate
val metrics = Metrics.evaluate(ds.traces, result.traces)
println(s"SNR: ${metrics("snr")} dB")
```

## Core Classes

### SeismicDataset

```scala
import io.promethium.core.SeismicDataset
import breeze.linalg.DenseMatrix

val ds = SeismicDataset(
  traces = DenseMatrix.rand(100, 500),
  dt = 0.004,
  coords = Some(DenseMatrix.zeros(100, 2)),
  metadata = Map("survey" -> "Test")
)

// Properties
ds.nTraces    // 100
ds.nSamples   // 500
ds.duration   // 2.0

// Normalize
val dsNorm = ds.normalize("rms")

// Subset
val dsSub = ds.subset(0 until 50, 0 until 250)
```

### RecoveryPipeline

```scala
import io.promethium.core.RecoveryPipeline

// From preset
val pipe = RecoveryPipeline.fromPreset("wiener")

// Custom configuration
val customPipe = RecoveryPipeline(
  name = "custom",
  config = Map(
    "modelType" -> "matrix_completion",
    "lambda" -> 0.1,
    "maxIter" -> 100
  )
)

val result = pipe.run(dataset)
```

## Recovery Algorithms

### Matrix Completion

```scala
import io.promethium.recovery.MatrixCompletion

val mask = DenseMatrix.fill(n, n)(scala.util.Random.nextBoolean())
val completed = MatrixCompletion.ista(
  M = observed,
  mask = mask,
  lambda = 0.1,
  maxIter = 100
)
```

### Compressive Sensing

```scala
import io.promethium.recovery.CompressiveSensing

val xRecovered = CompressiveSensing.fista(
  y = observations,
  A = measurementMatrix,
  lambda = 0.1,
  maxIter = 100
)
```

### Signal Filters

```scala
import io.promethium.signal.Filters

val denoised = Filters.wienerFilter(noisySignal)
val filtered = Filters.bandpassFilter(signal, dt=0.004, lowFreq=5.0, highFreq=80.0)
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
val results = Metrics.evaluate(reference, estimate, 
  Seq("snr", "mse", "psnr", "ssim"))
```

## Testing

```bash
cd packages/promethium-scala
sbt test
```

## Spark Integration

For large-scale processing with Apache Spark:

```scala
import org.apache.spark.sql.SparkSession
import io.promethium.core._

val spark = SparkSession.builder.appName("PromethiumJob").getOrCreate()

// Parallelize trace processing
val tracesRDD = spark.sparkContext.parallelize(traceList)
val denoisedRDD = tracesRDD.map(t => Filters.wienerFilter(t))
```
