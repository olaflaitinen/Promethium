# R API Reference

[![CRAN](https://www.r-pkg.org/badges/version/promethiumR)](https://CRAN.R-project.org/package=promethiumR)
[![Downloads](https://cranlogs.r-pkg.org/badges/promethiumR)](https://CRAN.R-project.org/package=promethiumR)

promethiumR provides a state-of-the-art (SoTA) native R implementation of the Promethium seismic data recovery framework.

**CRAN Package:** [https://CRAN.R-project.org/package=promethiumR](https://CRAN.R-project.org/package=promethiumR)

## Installation

```r
# From CRAN
install.packages("promethiumR")
library(promethiumR)

# From GitHub (development)
devtools::install_github("olaflaitinen/promethium/packages/promethiumR")

# From source
install.packages("promethiumR", repos = NULL, type = "source")
```

## Quick Start

```r
library(promethiumR)

# Generate synthetic data
dataset <- promethium_synthetic(ntraces = 100, nsamples = 500, dt = 0.004)

# Create recovery pipeline
pipeline <- from_preset("matrix_completion")

# Run recovery
recovered <- promethium_run(pipeline, dataset)

# Evaluate results
metrics <- promethium_evaluate(dataset, recovered)
print(metrics)
```

---

## Core Types

### SeismicDataset

S3 class for seismic trace data.

```r
# Create from matrix
traces <- matrix(rnorm(1000), nrow = 10, ncol = 100)
ds <- SeismicDataset(traces, dt = 0.004)

# Access properties
n_traces(ds)      # Number of traces
n_samples(ds)     # Samples per trace
time_axis(ds)     # Time vector

# Normalize
ds_norm <- normalize(ds, method = "max")  # or "rms", "standard"
```

### VelocityModel

S3 class for velocity fields.

```r
# Constant velocity
vm <- constant_velocity(nx = 100, nz = 50, dx = 10, dz = 10, velocity = 2000)

# Linear gradient
vm <- linear_velocity(nx = 100, nz = 50, dx = 10, dz = 10,
                      v_top = 1500, v_bottom = 4000)

# Interpolation
v <- interpolate_at(vm, x = 500, z = 250)
```

---

## I/O Functions

### Synthetic Data

```r
ds <- promethium_synthetic(
  ntraces = 100,
  nsamples = 500,
  dt = 0.004,
  noise_level = 0.1,
  seed = 42
)
```

### SEG-Y Format

```r
# Read
ds <- promethium_load_segy("data/survey.sgy")

# Write
promethium_write_segy(ds, "output/recovered.sgy")
```

### HDF5 Format

```r
# Requires hdf5r package
ds <- promethium_load_hdf5("data/survey.h5", group = "seismic")
promethium_save_hdf5(ds, "output/recovered.h5", group = "seismic")
```

---

## Signal Processing

### Wiener Filter

```r
# Apply to dataset
filtered <- wiener_filter(dataset)

# With noise estimate
filtered <- wiener_filter(dataset, noise_var = 0.01)
```

### Bandpass Filter

```r
filtered <- bandpass_filter(dataset, low_freq = 5, high_freq = 80)
```

### DC Removal

```r
centered <- remove_dc(dataset)
```

---

## Recovery Algorithms

### Matrix Completion (ISTA)

```r
# Create missing data mask
mask <- matrix(runif(nrow * ncol) > 0.3, nrow, ncol)

# Run completion
completed <- matrix_completion_ista(
  observed = traces,
  mask = mask,
  lambda = 0.1,
  max_iter = 100,
  tolerance = 1e-5
)
```

### Compressive Sensing (FISTA)

```r
x_recovered <- compressive_sensing_fista(
  y = measurements,
  A = sensing_matrix,
  lambda = 0.1,
  max_iter = 100
)
```

---

## Pipelines

### Create Pipeline

```r
pipeline <- promethium_pipeline(
  preprocessing = c("remove_dc"),
  model_type = "matrix_completion",
  model_config = list(lambda = 0.1, max_iter = 100),
  postprocessing = c("normalize")
)
```

### Use Presets

```r
pipeline <- from_preset("matrix_completion")
pipeline <- from_preset("fista")
pipeline <- from_preset("wiener")
```

### Run Pipeline

```r
result <- promethium_run(pipeline, dataset, verbose = TRUE)
```

---

## Evaluation Metrics

### Individual Metrics

```r
snr <- compute_snr(original, recovered)
mse <- compute_mse(original, recovered)
psnr <- compute_psnr(original, recovered)
ssim <- compute_ssim(original_matrix, recovered_matrix)
rel_err <- compute_relative_error(original, recovered)
```

### Comprehensive Evaluation

```r
metrics <- promethium_evaluate(original_dataset, recovered_dataset)
# Returns list with: snr, mse, psnr, ssim, relative_error
```

---

## Cross-Language Consistency

All implementations produce numerically consistent results:

| Metric | Tolerance |
|--------|-----------|
| SNR | 0.1 dB |
| MSE | 1e-6 |
| PSNR | 0.1 dB |
| SSIM | 1e-4 |

---

## Version

```r
PROMETHIUM_VERSION
# [1] "1.0.4"
```
