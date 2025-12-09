#' Recovery Algorithms for Seismic Data Reconstruction
#'
#' Implements matrix completion (ISTA) and compressive sensing (FISTA).

#' Soft Thresholding Operator
#' @param x Numeric value or vector
#' @param tau Threshold value
#' @return Soft-thresholded result
soft_threshold <- function(x, tau) {
  sign(x) * pmax(abs(x) - tau, 0)
}

#' Matrix Completion via ISTA
#'
#' Solves: min_X (1/2)||P_Omega(X - M)||_F^2 + lambda ||X||_*
#' where ||X||_* is the nuclear norm.
#'
#' @param observed Numeric matrix (missing entries can be any value)
#' @param mask Logical matrix (TRUE = observed, FALSE = missing)
#' @param lambda Regularization parameter for nuclear norm
#' @param max_iter Maximum number of iterations
#' @param tolerance Convergence tolerance
#' @param verbose Logical, print progress
#' @return Completed numeric matrix
#'
#' @examples
#' # Create low-rank matrix
#' U <- matrix(rnorm(20 * 3), 20, 3)
#' V <- matrix(rnorm(20 * 3), 20, 3)
#' M <- U %*% t(V)
#'
#' # Create mask (60% observed)
#' mask <- matrix(runif(400) < 0.6, 20, 20)
#' observed <- M * mask
#'
#' # Complete matrix
#' completed <- matrix_completion_ista(observed, mask, lambda = 0.1)
#'
#' @export
matrix_completion_ista <- function(observed, mask, lambda = 0.1, 
                                   max_iter = 100L, tolerance = 1e-5, 
                                   verbose = FALSE) {
  # Input validation
  if (!is.matrix(observed) || !is.numeric(observed)) {
    stop("`observed` must be a numeric matrix")
  }
  if (!is.matrix(mask) || !is.logical(mask)) {
    stop("`mask` must be a logical matrix")
  }
  if (!all(dim(observed) == dim(mask))) {
    stop("Dimensions of `observed` and `mask` must match")
  }
  
  m <- nrow(observed)
  n <- ncol(observed)
  
  # Initialize with observed values, zeros elsewhere
  X <- observed * mask
  
  L <- 1.0  # Lipschitz constant
  
  for (iter in seq_len(max_iter)) {
    # Gradient step
    grad <- (X - observed) * mask
    Z <- X - (1.0 / L) * grad
    
    # Proximal step: singular value soft thresholding
    svd_result <- svd(Z)
    s_thresh <- soft_threshold(svd_result$d, lambda / L)
    
    # Reconstruct with thresholded singular values
    X_new <- svd_result$u %*% diag(s_thresh, nrow = length(s_thresh)) %*% t(svd_result$v)
    
    # Check convergence
    change <- norm(X_new - X, "F")
    rel_change <- change / (norm(X, "F") + EPSILON)
    
    if (verbose && iter %% 10 == 0) {
      message(sprintf("Iter %d: relative change = %.6f", iter, rel_change))
    }
    
    if (rel_change < tolerance) {
      if (verbose) message(sprintf("Converged at iteration %d", iter))
      break
    }
    
    X <- X_new
  }
  
  X
}

#' Compressive Sensing via FISTA
#'
#' Solves: min_x (1/2)||Ax - y||_2^2 + lambda ||x||_1
#' FISTA achieves O(1/k^2) convergence rate.
#'
#' @param y Observation vector
#' @param A Measurement matrix
#' @param lambda L1 regularization parameter
#' @param max_iter Maximum iterations
#' @param tolerance Convergence tolerance
#' @param verbose Print progress
#' @return Recovered sparse vector
#'
#' @examples
#' # Sparse signal
#' n <- 50
#' x_true <- rep(0, n)
#' x_true[c(5, 15, 30)] <- c(2, -1.5, 1)
#'
#' # Measurement
#' m <- 30
#' A <- matrix(rnorm(m * n), m, n)
#' y <- A %*% x_true + rnorm(m) * 0.01
#'
#' # Recover
#' x_rec <- compressive_sensing_fista(y, A, lambda = 0.1)
#'
#' @export
compressive_sensing_fista <- function(y, A, lambda = 0.1, max_iter = 100L,
                                      tolerance = 1e-5, verbose = FALSE) {
  # Input validation
  if (!is.numeric(y)) stop("`y` must be numeric")
  if (!is.matrix(A)) stop("`A` must be a matrix")
  
  m <- nrow(A)
  n <- ncol(A)
  
  if (length(y) != m) {
    stop("Length of `y` must match number of rows in `A`")
  }
  
  x <- rep(0, n)
  z <- x
  t <- 1
  
  # Lipschitz constant estimate
  AtA <- t(A) %*% A
  L <- max(abs(diag(AtA))) * n
  
  for (iter in seq_len(max_iter)) {
    # Gradient step
    grad <- as.vector(t(A) %*% (A %*% z - y))
    u <- z - (1.0 / L) * grad
    
    # Proximal step (soft thresholding for L1)
    x_new <- soft_threshold(u, lambda / L)
    
    # FISTA momentum
    t_new <- (1 + sqrt(1 + 4 * t^2)) / 2
    z <- x_new + ((t - 1) / t_new) * (x_new - x)
    
    # Check convergence
    rel_change <- sqrt(sum((x_new - x)^2)) / (sqrt(sum(x^2)) + EPSILON)
    
    if (verbose && iter %% 10 == 0) {
      message(sprintf("Iter %d: relative change = %.6f", iter, rel_change))
    }
    
    if (rel_change < tolerance) {
      if (verbose) message(sprintf("FISTA converged at iteration %d", iter))
      break
    }
    
    x <- x_new
    t <- t_new
  }
  
  x
}

#' Standard ISTA (simpler but slower O(1/k) convergence)
#' @param y Observation vector
#' @param A Measurement matrix
#' @param lambda L1 regularization parameter
#' @param max_iter Maximum iterations
#' @return Recovered sparse vector
#' @export
compressive_sensing_ista <- function(y, A, lambda = 0.1, max_iter = 100L) {
  n <- ncol(A)
  x <- rep(0, n)
  
  AtA <- t(A) %*% A
  L <- max(abs(diag(AtA))) * n
  
  for (iter in seq_len(max_iter)) {
    grad <- as.vector(t(A) %*% (A %*% x - y))
    u <- x - (1.0 / L) * grad
    x <- soft_threshold(u, lambda / L)
  }
  
  x
}
