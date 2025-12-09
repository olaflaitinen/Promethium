package io.promethium

import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers
import breeze.linalg._
import breeze.numerics._

import io.promethium.core._
import io.promethium.evaluation._
import io.promethium.recovery._

class PromethiumSpec extends AnyFunSuite with Matchers {
  
  test("SeismicDataset creation and basic operations") {
    val traces = DenseMatrix.rand(10, 100)
    val ds = SeismicDataset(traces, 0.004)
    
    ds.nTraces shouldBe 10
    ds.nSamples shouldBe 100
    ds.dt shouldBe 0.004
  }
  
  test("SeismicDataset normalization") {
    val traces = DenseMatrix.rand(10, 100)
    val ds = SeismicDataset(traces, 0.004)
    val dsNorm = ds.normalize("max")
    
    max(abs(dsNorm.traces)) should be <= 1.0 + 1e-6
  }
  
  test("Metrics - SNR for identical signals") {
    val reference = DenseMatrix.rand(10, 10)
    val estimate = reference.copy
    
    val snr = Metrics.computeSNR(reference, estimate)
    snr should be > 100.0
  }
  
  test("Metrics - MSE is non-negative") {
    val reference = DenseMatrix.rand(10, 10)
    val estimate = reference + DenseMatrix.rand(10, 10) * 0.1
    
    val mse = Metrics.computeMSE(reference, estimate)
    mse should be >= 0.0
  }
  
  test("Metrics - evaluate returns all requested metrics") {
    val reference = DenseMatrix.rand(10, 10)
    val estimate = reference + DenseMatrix.rand(10, 10) * 0.1
    
    val results = Metrics.evaluate(reference, estimate)
    
    results should contain key "snr"
    results should contain key "mse"
    results should contain key "psnr"
    results should contain key "ssim"
  }
  
  test("Matrix completion recovers low-rank matrix") {
    // Create low-rank matrix
    val n = 20
    val r = 3
    val U = DenseMatrix.rand(n, r)
    val V = DenseMatrix.rand(n, r)
    val trueMatrix = U * V.t
    
    // Create mask (50% observed)
    val mask = DenseMatrix.fill(n, n)(scala.util.Random.nextDouble() > 0.5)
    
    // Observed matrix
    val M = trueMatrix.copy
    for (i <- 0 until n; j <- 0 until n if !mask(i, j)) {
      M(i, j) = 0.0
    }
    
    // Complete
    val completed = MatrixCompletion.ista(M, mask, lambda = 0.1, maxIter = 50)
    
    // Check relative error
    val relError = norm(completed - trueMatrix) / norm(trueMatrix)
    relError should be < 0.5
  }
  
  test("Compressive sensing recovers sparse signal") {
    val n = 50
    val m = 30
    
    // Sparse signal
    val xTrue = DenseVector.zeros[Double](n)
    xTrue(5) = 2.0
    xTrue(15) = -1.5
    xTrue(30) = 1.0
    
    // Measurement
    val A = DenseMatrix.rand(m, n)
    val y = A * xTrue + DenseVector.rand(m) * 0.01
    
    // Recover
    val xRec = CompressiveSensing.fista(y, A, lambda = 0.1, maxIter = 100)
    
    // Check sparsity
    val numLarge = (0 until n).count(i => abs(xRec(i)) > 0.1)
    numLarge should be <= 10
  }
  
  test("RecoveryPipeline from preset") {
    val pipe = RecoveryPipeline.fromPreset("matrix_completion")
    
    pipe.name shouldBe "matrix_completion"
    pipe.config should contain key "lambda"
  }
}
