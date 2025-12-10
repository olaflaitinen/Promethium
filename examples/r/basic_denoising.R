# Promethium R Examples
# 
# Basic Denoising Example
#
# This script demonstrates seismic data denoising using promethiumR.
# It shows how to load data, apply denoising algorithms, and evaluate results.

# Load the promethiumR package
library(promethiumR)

# -----------------------------------------------------------------------------
# 1. Load Seismic Data
# -----------------------------------------------------------------------------

cat("Promethium R - Basic Denoising Example\n")
cat("=" , rep("=", 50), "\n", sep = "")

# Create synthetic noisy data for demonstration
set.seed(42)
n_traces <- 100
n_samples <- 500
sample_rate <- 0.004  # 4 ms

# Generate clean synthetic reflections
time_axis <- seq(0, (n_samples - 1) * sample_rate, by = sample_rate)
clean_data <- matrix(0, nrow = n_traces, ncol = n_samples)

for (i in 1:n_traces) {
  # Add some synthetic reflections
  reflection_times <- c(0.2, 0.5, 0.8, 1.2)
  for (t in reflection_times) {
    idx <- which.min(abs(time_axis - t))
    if (idx > 0 && idx <= n_samples) {
      # Ricker wavelet
      f0 <- 30  # dominant frequency
      amp <- runif(1, 0.5, 1.0)
      wavelet_samples <- seq(-0.1, 0.1, by = sample_rate)
      wavelet <- amp * (1 - 2 * (pi * f0 * wavelet_samples)^2) * 
                 exp(-(pi * f0 * wavelet_samples)^2)
      
      start_idx <- max(1, idx - length(wavelet) %/% 2)
      end_idx <- min(n_samples, start_idx + length(wavelet) - 1)
      wave_length <- end_idx - start_idx + 1
      clean_data[i, start_idx:end_idx] <- clean_data[i, start_idx:end_idx] + 
                                          wavelet[1:wave_length]
    }
  }
}

# Add Gaussian noise
noise_level <- 0.3
noisy_data <- clean_data + rnorm(n_traces * n_samples, mean = 0, sd = noise_level)

cat("Generated synthetic data:\n")
cat("  Traces:", n_traces, "\n")
cat("  Samples:", n_samples, "\n")
cat("  Sample rate:", sample_rate * 1000, "ms\n")
cat("  Noise level:", noise_level, "\n\n")

# -----------------------------------------------------------------------------
# 2. Create SeismicDataset Objects
# -----------------------------------------------------------------------------

# Create SeismicDataset from noisy data
noisy_dataset <- SeismicDataset(
  traces = noisy_data,
  sample_rate = sample_rate,
  metadata = list(
    source = "synthetic",
    description = "Noisy synthetic shot gather"
  )
)

# Print dataset info
print(noisy_dataset)

# -----------------------------------------------------------------------------
# 3. Apply Wiener Filter Denoising
# -----------------------------------------------------------------------------

cat("\nApplying Wiener filter denoising...\n")

# Apply Wiener filter
# Note: This uses the wiener_filter function from promethiumR
denoised_data <- wiener_filter(noisy_dataset, noise_power = noise_level^2)

cat("Wiener filter applied successfully.\n")

# -----------------------------------------------------------------------------
# 4. Apply Bandpass Filter
# -----------------------------------------------------------------------------

cat("\nApplying bandpass filter...\n")

# Apply bandpass filter to remove noise outside frequency band
bandpass_result <- bandpass_filter(
  noisy_dataset,
  low_freq = 5,
  high_freq = 60,
  sample_rate = 1 / sample_rate
)

cat("Bandpass filter applied successfully.\n")

# -----------------------------------------------------------------------------
# 5. Evaluate Results
# -----------------------------------------------------------------------------

cat("\n", rep("-", 50), "\n", sep = "")
cat("Quality Metrics\n")
cat(rep("-", 50), "\n", sep = "")

# Compute SNR for original noisy data
snr_noisy <- compute_snr(
  reference = clean_data,
  estimate = noisy_data
)
cat("Original noisy data SNR:", round(snr_noisy, 2), "dB\n")

# Compute SNR after Wiener filter
if (!is.null(denoised_data)) {
  denoised_traces <- if (is.list(denoised_data)) denoised_data$traces else denoised_data
  snr_wiener <- compute_snr(
    reference = clean_data,
    estimate = denoised_traces
  )
  cat("After Wiener filter SNR:", round(snr_wiener, 2), "dB\n")
  cat("  Improvement:", round(snr_wiener - snr_noisy, 2), "dB\n")
}

# Compute MSE
mse_noisy <- compute_mse(clean_data, noisy_data)
cat("\nMSE (noisy):", format(mse_noisy, scientific = TRUE, digits = 3), "\n")

# -----------------------------------------------------------------------------
# 6. Visualization (if available)
# -----------------------------------------------------------------------------

if (interactive()) {
  cat("\nGenerating plots...\n")
  
  # Setup plot layout
  par(mfrow = c(2, 2), mar = c(4, 4, 3, 1))
  
  # Plot clean data
  image(t(clean_data), 
        main = "Clean Data",
        xlab = "Time (samples)", 
        ylab = "Trace",
        col = gray.colors(256))
  
  # Plot noisy data
  image(t(noisy_data), 
        main = "Noisy Data",
        xlab = "Time (samples)", 
        ylab = "Trace",
        col = gray.colors(256))
  
  # Plot denoised data
  if (!is.null(denoised_data)) {
    denoised_traces <- if (is.list(denoised_data)) denoised_data$traces else denoised_data
    image(t(denoised_traces), 
          main = "Denoised (Wiener)",
          xlab = "Time (samples)", 
          ylab = "Trace",
          col = gray.colors(256))
  }
  
  # Plot difference
  if (!is.null(denoised_data)) {
    denoised_traces <- if (is.list(denoised_data)) denoised_data$traces else denoised_data
    diff_data <- noisy_data - denoised_traces
    image(t(diff_data), 
          main = "Removed Noise",
          xlab = "Time (samples)", 
          ylab = "Trace",
          col = gray.colors(256))
  }
  
  par(mfrow = c(1, 1))
}

cat("\nExample completed successfully.\n")
