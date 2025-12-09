package io.promethium.recovery

import breeze.linalg._
import breeze.numerics._

/**
 * Matrix completion algorithms for missing trace recovery.
 *
 * Implements nuclear norm minimization via iterative singular
 * value thresholding for low-rank matrix reconstruction.
 */
object MatrixCompletion {
  
  /**
   * Soft thresholding operator for scalars.
   */
  private def softThreshold(x: Double, tau: Double): Double = {
    if (x > tau) x - tau
    else if (x < -tau) x + tau
    else 0.0
  }
  
  /**
   * Soft thresholding for vectors.
   */
  private def softThreshold(x: DenseVector[Double], tau: Double): DenseVector[Double] = {
    x.map(v => softThreshold(v, tau))
  }
  
  /**
   * Matrix completion via Iterative Shrinkage-Thresholding Algorithm (ISTA).
   *
   * Solves: min_X (1/2)||P_Omega(X - M)||_F^2 + lambda ||X||_*
   *
   * where ||X||_* is the nuclear norm (sum of singular values).
   *
   * @param observed  Observed matrix (missing entries can be any value)
   * @param mask      Boolean mask (true = observed, false = missing)
   * @param lambda    Regularization parameter for nuclear norm
   * @param maxIter   Maximum number of iterations
   * @param tolerance Convergence tolerance
   * @param verbose   Print iteration progress
   * @return Completed matrix
   */
  def ista(
    observed: DenseMatrix[Double],
    mask: DenseMatrix[Boolean],
    lambda: Double = 0.1,
    maxIter: Int = 100,
    tolerance: Double = 1e-5,
    verbose: Boolean = false
  ): DenseMatrix[Double] = {
    require(observed.rows == mask.rows && observed.cols == mask.cols,
      "Observed matrix and mask must have same dimensions")
    
    val m = observed.rows
    val n = observed.cols
    
    // Initialize with observed values, zeros elsewhere
    var X = DenseMatrix.zeros[Double](m, n)
    for (i <- 0 until m; j <- 0 until n) {
      if (mask(i, j)) X(i, j) = observed(i, j)
    }
    
    // Lipschitz constant (1.0 for projection operator)
    val L = 1.0
    
    var converged = false
    var iter = 0
    
    while (!converged && iter < maxIter) {
      // Gradient step: gradient of data fidelity term
      val grad = DenseMatrix.zeros[Double](m, n)
      for (i <- 0 until m; j <- 0 until n) {
        if (mask(i, j)) {
          grad(i, j) = X(i, j) - observed(i, j)
        }
      }
      
      val Z = X - (1.0 / L) * grad
      
      // Proximal step: singular value soft thresholding
      val svd.SVD(u, s, vt) = svd(Z)
      val sThresh = softThreshold(s, lambda / L)
      
      // Reconstruct with thresholded singular values
      // SVD returns U (m x m), S (k), Vt (n x n)
      // We need to slice U and Vt to k components for reconstruction
      val k = sThresh.length
      val XNew = u(::, 0 until k) * diag(sThresh) * vt(0 until k, ::)
      
      // Check convergence
      val relChange = norm((XNew - X).toDenseVector) / (norm(X.toDenseVector) + 1e-10)
      if (relChange < tolerance) {
        converged = true
        if (verbose) println(s"Converged at iteration $iter")
      }
      
      X = XNew
      iter += 1
    }
    
    if (verbose && !converged) {
      println(s"Did not converge within $maxIter iterations")
    }
    
    X
  }
  
  /**
   * Configuration for matrix completion.
   */
  final case class Config(
    lambda: Double = 0.1,
    maxIter: Int = 100,
    tolerance: Double = 1e-5
  )
}
