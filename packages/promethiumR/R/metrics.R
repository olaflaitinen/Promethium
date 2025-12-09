#' Compute Signal-to-Noise Ratio
#'
#' @param reference Reference (ground truth) signal matrix
#' @param estimate Estimated/reconstructed signal matrix
#' @return SNR value in decibels (dB)
#' @export
compute_snr <- function(reference, estimate) {
  signal_power <- mean(reference^2)
  noise_power <- mean((reference - estimate)^2)
  10 * log10(signal_power / (noise_power + 1e-10))
}

#' Compute Mean Squared Error
#'
#' @param reference Reference signal
#' @param estimate Estimated signal
#' @return MSE value
#' @export
compute_mse <- function(reference, estimate) {
  mean((reference - estimate)^2)
}

#' Compute Peak Signal-to-Noise Ratio
#'
#' @param reference Reference signal
#' @param estimate Estimated signal
#' @return PSNR value in decibels (dB)
#' @export
compute_psnr <- function(reference, estimate) {
  mse <- compute_mse(reference, estimate)
  max_val <- max(abs(reference))
  10 * log10(max_val^2 / (mse + 1e-10))
}

#' Compute Structural Similarity Index (SSIM)
#'
#' Simplified SSIM for 1D/2D signals.
#'
#' @param reference Reference signal
#' @param estimate Estimated signal
#' @param C1 Stability constant (default 0.01^2)
#' @param C2 Stability constant (default 0.03^2)
#' @return SSIM value in [0, 1]
#' @export
compute_ssim <- function(reference, estimate, C1 = 0.0001, C2 = 0.0009) {
  mu_x <- mean(reference)
  mu_y <- mean(estimate)
  sigma_x <- sd(as.vector(reference))
  sigma_y <- sd(as.vector(estimate))
  sigma_xy <- cov(as.vector(reference), as.vector(estimate))
  
  numerator <- (2 * mu_x * mu_y + C1) * (2 * sigma_xy + C2)
  denominator <- (mu_x^2 + mu_y^2 + C1) * (sigma_x^2 + sigma_y^2 + C2)
  
  numerator / denominator
}

#' Evaluate Reconstruction Quality
#'
#' Compute multiple evaluation metrics for reconstruction quality assessment.
#'
#' @param reference Reference (ground truth) data
#' @param estimate Reconstructed/estimated data
#' @param metrics Character vector of metrics to compute
#' @return Named list of metric values
#' @export
#' @examples
#' ref <- matrix(rnorm(100), 10, 10)
#' est <- ref + rnorm(100, sd = 0.1)
#' promethium_evaluate(ref, est)
promethium_evaluate <- function(reference, estimate,
                                 metrics = c("snr", "mse", "psnr", "ssim")) {
  results <- list()
  
  if ("snr" %in% metrics) {
    results$snr <- compute_snr(reference, estimate)
  }
  if ("mse" %in% metrics) {
    results$mse <- compute_mse(reference, estimate)
  }
  if ("psnr" %in% metrics) {
    results$psnr <- compute_psnr(reference, estimate)
  }
  if ("ssim" %in% metrics) {
    results$ssim <- compute_ssim(reference, estimate)
  }
  
  results
}
