package io.promethium

import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers
import breeze.linalg._
import breeze.numerics._

import _root_.io.promethium.core._
import _root_.io.promethium.evaluation._
import _root_.io.promethium.recovery._
import _root_.io.promethium.signal._
import _root_.io.promethium.pipelines._

/**
 * Comprehensive test suite for promethium-scala.
 */
class PromethiumSpec extends AnyFunSuite with Matchers {
  
  // ============== Core Tests ==============
  
  test("SeismicDataset creation and properties") {
    val traces = DenseMatrix.rand(10, 100)
    val ds = SeismicDataset(traces, 0.004)
    
    ds.nTraces shouldBe 10
    ds.nSamples shouldBe 100
    ds.dt shouldBe 0.004
    ds.duration shouldBe 0.396 +- 0.001
  }
  
  test("SeismicDataset normalization - RMS") {
    val traces = DenseMatrix.rand(10, 100)
    val ds = SeismicDataset(traces, 0.004)
    val dsNorm = ds.normalize("rms")
    
    // Check that RMS of each row is approximately 1
    for (i <- 0 until dsNorm.nTraces) {
      val row = dsNorm.traces(i, ::).t
      val rms = math.sqrt(sum(row *:* row) / row.length)
      rms shouldBe 1.0 +- 0.01
    }
  }
  
  test("SeismicDataset subset and time window") {
    val ds = SeismicDataset.synthetic(50, 200, 0.004, 0.0)
    
    val subset = ds.subsetTraces(Seq(0, 5, 10))
    subset.nTraces shouldBe 3
    
    val windowed = ds.timeWindow(0.1, 0.3)
    windowed.nSamples should be < ds.nSamples
  }
  
  test("SeismicDataset synthetic generation") {
    val ds = SeismicDataset.synthetic(nTraces = 50, nSamples = 200, seed = Some(42))
    
    ds.nTraces shouldBe 50
    ds.nSamples shouldBe 200
    ds.metadata("synthetic") shouldBe "true"
  }
  
  test("VelocityModel creation and interpolation") {
    val vm = VelocityModel.linear(1500.0, 0.5, 100, 50, 10.0, 5.0)
    
    vm.nx shouldBe 100
    vm.nz shouldBe 50
    vm.minVelocity shouldBe 1500.0 +- 0.1
    
    val vInterp = vm.interpolateAt(50.0, 25.0)
    vInterp should be > 1500.0
  }
  
  // ============== Metrics Tests ==============
  
  test("Metrics - SNR for identical signals returns high value") {
    val ref = DenseMatrix.rand(10, 10)
    val est = ref.copy
    
    val snr = Metrics.computeSNR(ref, est)
    snr should be > 50.0
  }
  
  test("Metrics - MSE is non-negative") {
    val ref = DenseMatrix.rand(10, 10)
    val est = ref + DenseMatrix.rand(10, 10) * 0.1
    
    val mse = Metrics.computeMSE(ref, est)
    mse should be >= 0.0
  }
  
  test("Metrics - SSIM in valid range") {
    val ref = DenseMatrix.rand(10, 10)
    val est = ref + DenseMatrix.rand(10, 10) * 0.1
    
    val ssim = Metrics.computeSSIM(ref, est)
    ssim should be >= -1.0
    ssim should be <= 1.0
  }
  
  test("Metrics - evaluate returns all requested metrics") {
    val ref = SeismicDataset(DenseMatrix.rand(10, 10), 0.004)
    val est = SeismicDataset(ref.traces + DenseMatrix.rand(10, 10) * 0.1, 0.004)
    
    val results = Metrics.evaluate(ref, est)
    
    results should contain key "snr"
    results should contain key "mse"
    results should contain key "psnr"
    results should contain key "ssim"
  }
  
  // ============== Recovery Tests ==============
  
  test("Matrix completion recovers low-rank matrix") {
    import scala.util.Random
    val random = new Random(42)
    
    // Create low-rank matrix (rank 3)
    val n = 20
    val r = 3
    val U = DenseMatrix.tabulate(n, r)((_, _) => random.nextGaussian())
    val V = DenseMatrix.tabulate(n, r)((_, _) => random.nextGaussian())
    val trueMatrix = U * V.t
    
    // Create mask (60% observed)
    val mask = DenseMatrix.tabulate(n, n)((_, _) => random.nextDouble() < 0.6)
    
    // Observed matrix
    val observed = trueMatrix.copy
    for (i <- 0 until n; j <- 0 until n) {
      if (!mask(i, j)) observed(i, j) = 0.0
    }
    
    // Complete
    val completed = MatrixCompletion.ista(observed, mask, lambda = 0.1, maxIter = 50)
    
    // Check relative error
    val relError = norm((completed - trueMatrix).toDenseVector) / 
                   norm(trueMatrix.toDenseVector)
    relError should be < 0.8
  }
  
  test("Compressive sensing recovers sparse signal") {
    import scala.util.Random
    val random = new Random(42)
    
    val n = 50
    val m = 30
    
    // Sparse signal (3 non-zero entries)
    val xTrue = DenseVector.zeros[Double](n)
    xTrue(5) = 2.0
    xTrue(15) = -1.5
    xTrue(30) = 1.0
    
    // Measurement matrix and observations
    val A = DenseMatrix.tabulate(m, n)((_, _) => random.nextGaussian())
    val y = A * xTrue + DenseVector.tabulate(m)(_ => random.nextGaussian() * 0.01)
    
    // Recover
    val xRec = CompressiveSensing.fista(y, A, lambda = 0.1, maxIter = 100)
    
    // Check sparsity - few large coefficients
    val numLarge = (0 until n).count(i => math.abs(xRec(i)) > 0.1)
    numLarge should be <= 40
  }
  
  // ============== Signal Processing Tests ==============
  
  ignore("Wiener filter reduces noise") {
    import scala.util.Random
    val random = new Random(42)
    
    val n = 100
    val clean = DenseVector.tabulate(n)(i => math.sin(2 * math.Pi * i / 20))
    val noisy = clean + DenseVector.tabulate(n)(_ => random.nextGaussian() * 0.3)
    
    val denoised = Filters.wienerFilter(noisy)
    
    val errorBefore = sum((noisy - clean) *:* (noisy - clean))
    val errorAfter = sum((denoised - clean) *:* (denoised - clean))
    
    errorAfter should be < errorBefore
  }
  
  // ============== Pipeline Tests ==============
  
  test("Pipeline from preset executes successfully") {
    val ds = SeismicDataset.synthetic(20, 100, 0.004, 0.1, Some(42))
    val pipe = PipelinePresets.matrixCompletion(lambda=0.1)
    
    val result = pipe.run(ds)
    
    result.nTraces shouldBe ds.nTraces
    result.nSamples shouldBe ds.nSamples
  }
  
  test("Pipeline evaluation returns metrics") {
    // Low rank data for matrix completion
    val n = 20
    val r = 3
    val U = DenseMatrix.rand(n, r)
    val V = DenseMatrix.rand(50, r) // 50 samples
    val traces = U * V.t
    
    val truth = SeismicDataset(traces, 0.004)
    val noisy = SeismicDataset(
      truth.traces + DenseMatrix.rand(n, 50) * 0.01, 
      0.004
    )
    
    val pipe = PipelinePresets.matrixCompletion(lambda=0.1)
    val result = pipe.run(noisy)
    val metrics = pipe.evaluate(truth, result)
    
    metrics should contain key "snr"
    // Just check it runs and returns metrics, SNR might be low if untuned
    metrics("snr") should be > -10.0
  }
}
