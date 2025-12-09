#' Evaluation Metrics for Seismic Reconstruction Quality
#'
#' All metrics follow the Promethium specification for cross-language
#' consistency with Python, Julia, and Scala implementations.

EPSILON <- 1e-10

#' Compute Signal-to-Noise Ratio
#'
#' SNR = 10 * log10(P_signal / P_noise)
#'
#' @param reference Reference SeismicDataset (ground truth)
#' @param estimate Estimated/reconstructed SeismicDataset
#' @return SNR in decibels
#'
#' @examples
#' ref <- SeismicDataset(matrix(rnorm(100), 10, 10), dt = 0.004)
#' est <- SeismicDataset(ref$traces + 0.1 * rnorm(100), dt = 0.004)
#' snr <- compute_snr(ref, est)
#'
#' @export
compute_snr <- function(reference, estimate) {
  if (!inherits(reference, "SeismicDataset") || 
      !inherits(estimate, "SeismicDataset")) {
    stop("Both arguments must be SeismicDataset objects")
  }
  
  ref <- as.vector(reference$traces)
  est <- as.vector(estimate$traces)
  
  if (length(ref) != length(est)) {
    stop("Dimension mismatch between reference and estimate")
  }
  
  signal_power <- mean(ref^2)
  noise <- ref - est
  noise_power <- mean(noise^2)
  
  10 * log10(signal_power / (noise_power + EPSILON))
}

#' Compute Mean Squared Error
#'
#' MSE = mean((reference - estimate)^2)
#'
#' @param reference Reference SeismicDataset
#' @param estimate Estimated SeismicDataset
#' @return MSE value
#'
#' @export
compute_mse <- function(reference, estimate) {
  if (!inherits(reference, "SeismicDataset") || 
      !inherits(estimate, "SeismicDataset")) {
    stop("Both arguments must be SeismicDataset objects")
  }
  
  ref <- reference$traces
  est <- estimate$traces
  
  if (!all(dim(ref) == dim(est))) {
    stop("Dimension mismatch between reference and estimate")
  }
  
  mean((ref - est)^2)
}

#' Compute Peak Signal-to-Noise Ratio
#'
#' PSNR = 10 * log10(max_val^2 / MSE)
#'
#' @param reference Reference SeismicDataset
#' @param estimate Estimated SeismicDataset
#' @return PSNR in decibels
#'
#' @export
compute_psnr <- function(reference, estimate) {
  max_val <- max(abs(reference$traces))
  mse <- compute_mse(reference, estimate)
  10 * log10(max_val^2 / (mse + EPSILON))
}

#' Compute Structural Similarity Index
#'
#' Simplified SSIM based on luminance and contrast components.
#'
#' @param reference Reference SeismicDataset
#' @param estimate Estimated SeismicDataset
#' @return SSIM value in [-1, 1]
#'
#' @export
compute_ssim <- function(reference, estimate) {
  if (!inherits(reference, "SeismicDataset") || 
      !inherits(estimate, "SeismicDataset")) {
    stop("Both arguments must be SeismicDataset objects")
  }
  
  x <- as.vector(reference$traces)
  y <- as.vector(estimate$traces)
  
  if (length(x) != length(y)) {
    stop("Dimension mismatch")
  }
  
  mu_x <- mean(x)
  mu_y <- mean(y)
  sigma_x <- sd(x)
  sigma_y <- sd(y)
  sigma_xy <- mean((x - mu_x) * (y - mu_y))
  
  # Stability constants
  C1 <- 0.01^2
  C2 <- 0.03^2
  
  numerator <- (2 * mu_x * mu_y + C1) * (2 * sigma_xy + C2)
  denominator <- (mu_x^2 + mu_y^2 + C1) * (sigma_x^2 + sigma_y^2 + C2)
  
  numerator / denominator
}

#' Compute Relative Error
#'
#' RelError = ||estimate - reference||_F / ||reference||_F
#'
#' @param reference Reference SeismicDataset
#' @param estimate Estimated SeismicDataset
#' @return Relative Frobenius norm error
#'
#' @export
compute_relative_error <- function(reference, estimate) {
  diff <- estimate$traces - reference$traces
  sqrt(sum(diff^2)) / (sqrt(sum(reference$traces^2)) + EPSILON)
}

#' Evaluate All Metrics
#'
#' Compute specified evaluation metrics between reference and estimate.
#'
#' @param reference Reference SeismicDataset
#' @param estimate Estimated SeismicDataset
#' @param metrics Character vector of metric names (default: all)
#' @return Named list of metric values
#'
#' @examples
#' ref <- SeismicDataset(matrix(rnorm(100), 10, 10), dt = 0.004)
#' est <- SeismicDataset(ref$traces + 0.1 * rnorm(100), dt = 0.004)
#' metrics <- promethium_evaluate(ref, est)
#'
#' @export
promethium_evaluate <- function(reference, estimate, 
                                metrics = c("snr", "mse", "psnr", "ssim")) {
  result <- list()
  
  for (metric in metrics) {
    value <- switch(tolower(metric),
      "snr" = compute_snr(reference, estimate),
      "mse" = compute_mse(reference, estimate),
      "psnr" = compute_psnr(reference, estimate),
      "ssim" = compute_ssim(reference, estimate),
      "relative_error" = compute_relative_error(reference, estimate),
      stop("Unknown metric: ", metric)
    )
    result[[metric]] <- value
  }
  
  result
}
