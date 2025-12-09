# R Guide for promethiumR

## Installation

```r
# From GitHub (development)
devtools::install_github("olaflaitinen/Promethium/packages/promethiumR")

# Or from local source
devtools::install("packages/promethiumR")
```

## Quick Start

```r
library(promethiumR)

# Create dataset
traces <- matrix(rnorm(1000), nrow = 10, ncol = 100)
ds <- SeismicDataset(traces, dt = 0.004)

# Create pipeline
pipe <- promethium_pipeline("matrix_completion")

# Run recovery
result <- promethium_run(pipe, ds)

# Evaluate
metrics <- promethium_evaluate(ds$traces, result$traces)
print(sprintf("SNR: %.2f dB", metrics$snr))
```

## Core Classes

### SeismicDataset (S3 class)

```r
# Constructor
ds <- SeismicDataset(
  traces = matrix_data,
  dt = 0.004,
  coords = data.frame(x = 1:10, y = 1:10),
  metadata = list(survey = "Test")
)

# Print
print(ds)

# Normalize
ds_norm <- normalize.SeismicDataset(ds, method = "rms")

# Subset
ds_sub <- subset.SeismicDataset(ds, trace_idx = 1:5)
```

### VelocityModel

```r
grid <- matrix(2000 + runif(100) * 1000, 10, 10)
vm <- VelocityModel(grid, dx = 10, dz = 5)
```

## Recovery Algorithms

### Matrix Completion

```r
# Create mask (TRUE = observed)
mask <- matrix(runif(nrow(M) * ncol(M)) > 0.3, nrow(M), ncol(M))

# Complete
completed <- matrix_completion_ista(M, mask, lambda = 0.1)
```

### Wiener Filter

```r
denoised <- wiener_filter(noisy_signal, noise_var = 0.1)
```

### Compressive Sensing

```r
x_recovered <- compressive_sensing_fista(y, A, lambda = 0.1)
```

## Evaluation Metrics

```r
# Individual metrics
snr <- compute_snr(reference, estimate)
mse <- compute_mse(reference, estimate)
psnr <- compute_psnr(reference, estimate)
ssim <- compute_ssim(reference, estimate)

# All at once
metrics <- promethium_evaluate(reference, estimate)
```

## I/O Functions

```r
# Load/save SEG-Y (stub - requires rsegy)
ds <- promethium_load_segy("data.segy")
promethium_write_segy(ds, "output.segy")

# HDF5 (requires hdf5r)
ds <- promethium_load_hdf5("data.h5")
promethium_save_hdf5(ds, "output.h5")

# Generate synthetic data
ds <- promethium_synthetic(n_traces = 100, n_samples = 500, seed = 42)
```

## Testing

```r
# Run all tests
devtools::test()

# Run specific test file
testthat::test_file("tests/testthat/test-metrics.R")
```
