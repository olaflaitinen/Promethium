package io.promethium.recovery

import breeze.linalg._
import breeze.numerics._

/**
 * Matrix completion algorithms for seismic data recovery.
 *
 * Implements ISTA (Iterative Shrinkage-Thresholding Algorithm) for
 * nuclear norm regularized matrix completion following the Promethium specification.
 */
object MatrixCompletion {
  
  /**
   * Soft thresholding operator.
   *
   * S_τ(x) = sign(x) * max(|x| - τ, 0)
   */
  private def softThreshold(x: Double, tau: Double): Double = {
    if (x > tau) x - tau
    else if (x < -tau) x + tau
    else 0.0
  }
  
  /**
   * Matrix completion via ISTA with nuclear norm regularization.
   *
   * Solves: min_X (1/2)||P_Ω(X - M)||_F² + λ||X||_*
   *
   * @param M        Observed matrix (use Double.NaN for missing entries)
   * @param mask     Boolean matrix (true = observed)
   * @param lambda   Regularization parameter
   * @param maxIter  Maximum number of iterations
   * @param tol      Convergence tolerance
   * @return Completed matrix
   */
  def ista(M: DenseMatrix[Double],
           mask: DenseMatrix[Boolean],
           lambda: Double = 0.1,
           maxIter: Int = 100,
           tol: Double = 1e-5): DenseMatrix[Double] = {
    
    require(M.rows == mask.rows && M.cols == mask.cols,
            "Matrix and mask must have same dimensions")
    
    // Initialize
    val X = M.copy
    for (i <- 0 until X.rows; j <- 0 until X.cols) {
      if (!mask(i, j) || X(i, j).isNaN) X(i, j) = 0.0
    }
    
    val L = 1.0  // Lipschitz constant
    var converged = false
    var iter = 0
    
    while (!converged && iter < maxIter) {
      // Gradient step
      val grad = DenseMatrix.zeros[Double](M.rows, M.cols)
      for (i <- 0 until M.rows; j <- 0 until M.cols) {
        if (mask(i, j) && !M(i, j).isNaN) {
          grad(i, j) = X(i, j) - M(i, j)
        }
      }
      val Z = X - (1.0 / L) * grad
      
      // SVD soft-thresholding (proximal of nuclear norm)
      val svdResult = svd(Z)
      val sThresh = svdResult.singularValues.map(s => softThreshold(s, lambda / L))
      
      val Xnew = svdResult.U * diag(sThresh) * svdResult.Vt
      
      // Check convergence
      val relChange = norm(Xnew - X) / (norm(X) + 1e-10)
      if (relChange < tol) {
        converged = true
        println(s"ISTA converged at iteration $iter")
      }
      
      X := Xnew
      iter += 1
    }
    
    if (!converged) {
      println(s"ISTA did not converge within $maxIter iterations")
    }
    
    X
  }
}
