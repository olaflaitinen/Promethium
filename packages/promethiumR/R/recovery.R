#' Matrix Completion via ISTA
#'
#' Iterative Shrinkage-Thresholding Algorithm for nuclear norm regularized
#' matrix completion.
#'
#' @param M Observed matrix (use NA for missing entries)
#' @param mask Logical matrix (TRUE = observed)
#' @param lambda Regularization parameter
#' @param max_iter Maximum iterations
#' @param tol Convergence tolerance
#' @return Completed matrix
#' @export
matrix_completion_ista <- function(M, mask, lambda = 0.1,
                                    max_iter = 100, tol = 1e-5) {
  # Initialize
  X <- M
  X[!mask] <- 0
  L <- 1.0
  
  for (k in seq_len(max_iter)) {
    # Gradient step
    grad <- mask * (X - M)
    grad[is.na(grad)] <- 0
    Z <- X - (1/L) * grad
    
    # SVD soft-thresholding (proximal operator for nuclear norm)
    svd_result <- svd(Z)
    S_thresh <- pmax(svd_result$d - lambda/L, 0)
    
    # Reconstruct
    X_new <- svd_result$u %*% diag(S_thresh, nrow = length(S_thresh)) %*% t(svd_result$v)
    
    # Check convergence
    rel_change <- norm(X_new - X, "F") / (norm(X, "F") + 1e-10)
    if (rel_change < tol) {
      message(sprintf("Converged at iteration %d", k))
      break
    }
    X <- X_new
  }
  
  X
}

#' Compressive Sensing via FISTA
#'
#' Fast Iterative Shrinkage-Thresholding Algorithm for L1-regularized
#' sparse recovery.
#'
#' @param y Observation vector
#' @param A Measurement matrix
#' @param lambda Regularization parameter
#' @param max_iter Maximum iterations
#' @param tol Convergence tolerance
#' @return Recovered sparse vector
#' @export
compressive_sensing_fista <- function(y, A, lambda = 0.1,
                                       max_iter = 100, tol = 1e-5) {
  n <- ncol(A)
  x <- rep(0, n)
  z <- x
  t_k <- 1
  
 # Estimate Lipschitz constant
  L <- max(svd(A)$d)^2
  
  soft_threshold <- function(u, tau) {
    sign(u) * pmax(abs(u) - tau, 0)
  }
  
  for (k in seq_len(max_iter)) {
    # Gradient step
    grad <- t(A) %*% (A %*% z - y)
    u <- z - (1/L) * grad
    
    # Proximal step (soft thresholding)
    x_new <- soft_threshold(u, lambda/L)
    
    # FISTA momentum
    t_new <- (1 + sqrt(1 + 4 * t_k^2)) / 2
    z <- x_new + ((t_k - 1) / t_new) * (x_new - x)
    
    # Check convergence
    if (sqrt(sum((x_new - x)^2)) / (sqrt(sum(x^2)) + 1e-10) < tol) {
      message(sprintf("Converged at iteration %d", k))
      break
    }
    
    x <- x_new
    t_k <- t_new
  }
  
  x
}

#' Wiener Filter for Denoising
#'
#' Apply frequency-domain Wiener filter for signal denoising.
#'
#' @param y Noisy signal vector
#' @param noise_var Estimated noise variance
#' @return Denoised signal
#' @export
wiener_filter <- function(y, noise_var = NULL) {
  N <- length(y)
  
  # FFT
  Y <- fft(y)
  P_y <- Mod(Y)^2 / N
  
  # Estimate noise PSD
  if (is.null(noise_var)) {
    # Estimate from high-frequency components
    noise_var <- median(P_y[floor(N/2):N])
  }
  P_n <- rep(noise_var, N)
  
  # Wiener filter
  P_s <- pmax(P_y - P_n, 0)
  H <- P_s / (P_s + P_n + 1e-10)
  
  # Apply and inverse transform
  S_hat <- H * Y
  s_hat <- Re(fft(S_hat, inverse = TRUE)) / N
  
  s_hat
}
