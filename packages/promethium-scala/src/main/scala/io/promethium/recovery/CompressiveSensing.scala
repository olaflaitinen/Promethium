package io.promethium.recovery

import breeze.linalg._
import breeze.numerics._

/**
 * Compressive sensing algorithms for sparse signal recovery.
 *
 * Implements L1-regularized minimization using Fast Iterative
 * Shrinkage-Thresholding Algorithm (FISTA) with Nesterov acceleration.
 */
object CompressiveSensing {
  
  /**
   * Soft thresholding operator.
   */
  private def softThreshold(x: Double, tau: Double): Double = {
    if (x > tau) x - tau
    else if (x < -tau) x + tau
    else 0.0
  }
  
  private def softThreshold(x: DenseVector[Double], tau: Double): DenseVector[Double] = {
    x.map(v => softThreshold(v, tau))
  }
  
  /**
   * Sparse recovery via FISTA (Fast ISTA) with L1 regularization.
   *
   * Solves: min_x (1/2)||Ax - y||_2^2 + lambda * ||x||_1
   *
   * FISTA achieves O(1/k^2) convergence rate vs O(1/k) for ISTA.
   *
   * @param y        Observation vector
   * @param A        Measurement/sensing matrix
   * @param lambda   Regularization parameter
   * @param maxIter  Maximum iterations
   * @param tolerance Convergence tolerance
   * @param verbose  Print iteration progress
   * @return Recovered sparse vector
   */
  def fista(
    y: DenseVector[Double],
    A: DenseMatrix[Double],
    lambda: Double = 0.1,
    maxIter: Int = 100,
    tolerance: Double = 1e-5,
    verbose: Boolean = false
  ): DenseVector[Double] = {
    val m = A.rows
    val n = A.cols
    require(y.length == m, "Observation vector length must match number of rows in A")
    
    var x = DenseVector.zeros[Double](n)
    var z = x.copy
    var t = 1.0
    
    // Lipschitz constant: L = ||A^T A||_2 (spectral norm)
    // Approximate with power iteration or use safe overestimate
    val AtA = A.t * A
    val L = max(abs(diag(AtA))) * n.toDouble  // Conservative estimate
    
    var converged = false
    var iter = 0
    
    while (!converged && iter < maxIter) {
      // Gradient step
      val grad = A.t * (A * z - y)
      val u = z - (1.0 / L) * grad
      
      // Proximal step (soft thresholding)
      val xNew = softThreshold(u, lambda / L)
      
      // FISTA momentum update
      val tNew = (1.0 + math.sqrt(1.0 + 4.0 * t * t)) / 2.0
      z = xNew + ((t - 1.0) / tNew) * (xNew - x)
      
      // Check convergence
      val relChange = norm(xNew - x) / (norm(x) + 1e-10)
      if (relChange < tolerance) {
        converged = true
        if (verbose) println(s"FISTA converged at iteration $iter")
      }
      
      x = xNew
      t = tNew
      iter += 1
    }
    
    if (verbose && !converged) {
      println(s"FISTA did not converge within $maxIter iterations")
    }
    
    x
  }
  
  /**
   * ISTA (standard Iterative Shrinkage-Thresholding Algorithm).
   *
   * Simpler than FISTA but with slower O(1/k) convergence.
   *
   * @param y       Observation vector
   * @param A       Measurement matrix
   * @param lambda  Regularization parameter
   * @param maxIter Maximum iterations
   * @return Recovered sparse vector
   */
  def ista(
    y: DenseVector[Double],
    A: DenseMatrix[Double],
    lambda: Double = 0.1,
    maxIter: Int = 100
  ): DenseVector[Double] = {
    val n = A.cols
    var x = DenseVector.zeros[Double](n)
    
    val AtA = A.t * A
    val L = max(abs(diag(AtA))) * n.toDouble
    
    for (_ <- 0 until maxIter) {
      val grad = A.t * (A * x - y)
      val u = x - (1.0 / L) * grad
      x = softThreshold(u, lambda / L)
    }
    
    x
  }
  
  /**
   * Configuration for compressive sensing.
   */
  final case class Config(
    lambda: Double = 0.1,
    maxIter: Int = 100,
    tolerance: Double = 1e-5,
    useFista: Boolean = true
  )
}
