package io.promethium.recovery

import breeze.linalg._
import breeze.numerics._

/**
 * Compressive sensing algorithms for sparse signal recovery.
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
   * Solves: min_x (1/2)||Ax - y||_2^2 + λ||x||_1
   *
   * @param y        Observation vector
   * @param A        Measurement matrix
   * @param lambda   Regularization parameter
   * @param maxIter  Maximum iterations
   * @param tol      Convergence tolerance
   * @return Recovered sparse vector
   */
  def fista(y: DenseVector[Double],
            A: DenseMatrix[Double],
            lambda: Double = 0.1,
            maxIter: Int = 100,
            tol: Double = 1e-5): DenseVector[Double] = {
    
    val n = A.cols
    var x = DenseVector.zeros[Double](n)
    var z = x.copy
    var t = 1.0
    
    // Lipschitz constant (max eigenvalue of A'A)
    val svdResult = svd(A)
    val L = max(svdResult.singularValues) * max(svdResult.singularValues)
    
    var converged = false
    var iter = 0
    
    while (!converged && iter < maxIter) {
      // Gradient step
      val grad = A.t * (A * z - y)
      val u = z - (1.0 / L) * grad
      
      // Proximal step
      val xNew = softThreshold(u, lambda / L)
      
      // FISTA momentum
      val tNew = (1.0 + sqrt(1.0 + 4.0 * t * t)) / 2.0
      z = xNew + ((t - 1.0) / tNew) * (xNew - x)
      
      // Check convergence
      val relChange = norm(xNew - x) / (norm(x) + 1e-10)
      if (relChange < tol) {
        converged = true
        println(s"FISTA converged at iteration $iter")
      }
      
      x = xNew
      t = tNew
      iter += 1
    }
    
    if (!converged) {
      println(s"FISTA did not converge within $maxIter iterations")
    }
    
    x
  }
}
