/**
 * Promethium Scala Examples
 * Basic Denoising Example
 *
 * This example demonstrates seismic data denoising using promethium-scala.
 * It shows how to load data, apply denoising algorithms, and evaluate results.
 *
 * To run:
 *   sbt "runMain examples.BasicDenoising"
 */
package examples

import io.github.olaflaitinen.promethium._
import io.github.olaflaitinen.promethium.core.{SeismicDataset, VelocityModel}
import io.github.olaflaitinen.promethium.signal.{WienerFilter, BandpassFilter}
import io.github.olaflaitinen.promethium.metrics.{SNR, MSE, SSIM}
import io.github.olaflaitinen.promethium.pipelines.SeismicRecoveryPipeline

import scala.util.Random
import breeze.linalg._
import breeze.numerics._

object BasicDenoising {

  def main(args: Array[String]): Unit = {
    println("Promethium Scala - Basic Denoising Example")
    println("=" * 50)

    // -------------------------------------------------------------------------
    // 1. Generate Synthetic Data
    // -------------------------------------------------------------------------
    println("\n1. Generating synthetic seismic data...")

    val nTraces = 100
    val nSamples = 500
    val sampleRate = 0.004  // 4 ms
    val random = new Random(42)

    // Generate clean synthetic data
    val cleanData = DenseMatrix.zeros[Double](nTraces, nSamples)
    val reflectionTimes = Seq(0.2, 0.5, 0.8, 1.2)
    val f0 = 30.0  // Dominant frequency

    def rickerWavelet(t: Double, freq: Double): Double = {
      val piF = math.Pi * freq * t
      (1 - 2 * piF * piF) * math.exp(-piF * piF)
    }

    for (i <- 0 until nTraces) {
      for (rt <- reflectionTimes) {
        val idx = (rt / sampleRate).toInt
        val amp = 0.5 + 0.5 * random.nextDouble()

        for (j <- math.max(0, idx - 50) until math.min(nSamples, idx + 50)) {
          val t = (j - idx) * sampleRate
          cleanData(i, j) += amp * rickerWavelet(t, f0)
        }
      }
    }

    // Add noise
    val noiseLevel = 0.3
    val noisyData = cleanData + DenseMatrix.rand[Double](nTraces, nSamples) * noiseLevel

    println(s"  Traces: $nTraces")
    println(s"  Samples: $nSamples")
    println(s"  Sample rate: ${sampleRate * 1000} ms")
    println(s"  Noise level: $noiseLevel")

    // -------------------------------------------------------------------------
    // 2. Create SeismicDataset
    // -------------------------------------------------------------------------
    println("\n2. Creating SeismicDataset...")

    val noisyDataset = SeismicDataset(
      traces = noisyData,
      sampleRate = sampleRate,
      metadata = Map(
        "source" -> "synthetic",
        "description" -> "Noisy synthetic shot gather"
      )
    )

    println(noisyDataset)

    // -------------------------------------------------------------------------
    // 3. Apply Wiener Filter
    // -------------------------------------------------------------------------
    println("\n3. Applying Wiener filter denoising...")

    val wienerFilter = WienerFilter(noisePower = noiseLevel * noiseLevel)
    val denoisedDataset = wienerFilter.apply(noisyDataset)

    println("   Wiener filter applied successfully.")

    // -------------------------------------------------------------------------
    // 4. Apply Bandpass Filter
    // -------------------------------------------------------------------------
    println("\n4. Applying bandpass filter...")

    val bandpassFilter = BandpassFilter(
      lowFreq = 5.0,
      highFreq = 60.0,
      sampleRate = 1.0 / sampleRate
    )
    val bandpassResult = bandpassFilter.apply(noisyDataset)

    println("   Bandpass filter applied successfully.")

    // -------------------------------------------------------------------------
    // 5. Compute Quality Metrics
    // -------------------------------------------------------------------------
    println("\n" + "-" * 50)
    println("Quality Metrics")
    println("-" * 50)

    // SNR calculation
    def computeSNR(reference: DenseMatrix[Double], estimate: DenseMatrix[Double]): Double = {
      val signalPower = sum(reference *:* reference)
      val diff = reference - estimate
      val noisePower = sum(diff *:* diff)
      10 * math.log10(signalPower / noisePower)
    }

    // MSE calculation
    def computeMSE(reference: DenseMatrix[Double], estimate: DenseMatrix[Double]): Double = {
      val diff = reference - estimate
      sum(diff *:* diff) / (reference.rows * reference.cols)
    }

    val snrNoisy = computeSNR(cleanData, noisyData)
    val snrDenoised = computeSNR(cleanData, denoisedDataset.traces)

    println(f"Original noisy SNR:   $snrNoisy%.2f dB")
    println(f"After Wiener filter:  $snrDenoised%.2f dB")
    println(f"  Improvement:        ${snrDenoised - snrNoisy}%.2f dB")

    val mseNoisy = computeMSE(cleanData, noisyData)
    val mseDenoised = computeMSE(cleanData, denoisedDataset.traces)

    println(f"\nMSE (noisy):         $mseNoisy%.4e")
    println(f"MSE (denoised):      $mseDenoised%.4e")

    // -------------------------------------------------------------------------
    // 6. Run Pipeline
    // -------------------------------------------------------------------------
    println("\n" + "-" * 50)
    println("Running recovery pipeline...")

    val pipeline = SeismicRecoveryPipeline.fromPreset("wiener")
    val pipelineResult = pipeline.run(noisyDataset)

    println("Pipeline completed successfully.")

    // -------------------------------------------------------------------------
    // 7. Summary
    // -------------------------------------------------------------------------
    println("\n" + "=" * 50)
    println("Example completed successfully.")
    println(s"SNR improvement: ${snrDenoised - snrNoisy}%.2f dB")
  }
}
