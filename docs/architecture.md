# Architecture Overview

This document describes the high-level architecture of Promethium as a multi-language seismic data recovery framework.

## Design Philosophy

Promethium is implemented as **four independent native libraries** that share a common mathematical specification but have **no runtime inter-language dependencies**. Each implementation is a first-class citizen in its respective ecosystem.

## Core Principles

1. **Specification First**: All implementations derive from a shared mathematical and algorithmic specification.

2. **Native Implementations**: Each language uses idiomatic constructs and native libraries, with no FFI or bridges to other languages.

3. **Cross-Language Consistency**: Given identical inputs and parameters, all implementations produce numerically consistent results within defined tolerances.

4. **Ecosystem Integration**: Each implementation integrates naturally with its ecosystem (PyPI, CRAN, Julia Registry, Maven Central).

## System Architecture

```
+------------------------------------------------------------------+
|                    Promethium Specification                       |
|  (Mathematical Models, Algorithms, Data Structures, Metrics)      |
+------------------------------------------------------------------+
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
+---------------+    +---------------+    +---------------+
|    Python     |    |      R        |    |    Julia      |
| promethium-   |    | promethiumR   |    | Promethium.jl |
|   seismic     |    |               |    |               |
+---------------+    +---------------+    +---------------+
| NumPy, SciPy  |    | Matrix, Rcpp  |    | FFTW, Linear  |
| PyTorch, JAX  |    | torch, keras  |    |  Algebra,Flux |
+---------------+    +---------------+    +---------------+
        |                     |                     |
        v                     v                     v
+---------------+    +---------------+    +---------------+
|  PyPI / pip   |    | CRAN / GitHub |    | Pkg Registry  |
+---------------+    +---------------+    +---------------+

                              +
                              |
                              v
                    +---------------+
                    |    Scala      |
                    | promethium-   |
                    |    scala      |
                    +---------------+
                    | Breeze, ND4J  |
                    | DL4J          |
                    +---------------+
                              |
                              v
                    +---------------+
                    | Maven Central |
                    +---------------+
```

## Package Structure

### Python (`src/promethium/`)

```
promethium/
  __init__.py           # Public API exports
  core/                 # Configuration, logging, exceptions
  io/                   # SEG-Y, MiniSEED, HDF5, cloud storage
  signal/               # Filters, transforms, deconvolution
  ml/                   # U-Net, autoencoder, GAN, PINN
  pipelines/            # SeismicRecoveryPipeline
  evaluation/           # Metrics (SNR, MSE, PSNR, SSIM)
  cli/                  # Command-line interface
  api/                  # FastAPI backend (optional)
```

### R (`packages/promethiumR/`)

```
promethiumR/
  DESCRIPTION           # Package metadata
  NAMESPACE             # Exports
  R/
    dataset.R           # SeismicDataset S3 class
    metrics.R           # Evaluation functions
    recovery.R          # ISTA, FISTA, Wiener
    pipeline.R          # Pipeline orchestration
    io.R                # Data I/O
  tests/testthat/       # Unit tests
```

### Julia (`packages/Promethium.jl/`)

```
Promethium.jl/
  Project.toml          # Package manifest
  src/
    Promethium.jl       # Main module
    types.jl            # SeismicDataset, VelocityModel
    metrics.jl          # Evaluation metrics
    recovery.jl         # Matrix completion, FISTA
    signal.jl           # Wiener filter, transforms
    pipeline.jl         # RecoveryPipeline
  test/runtests.jl      # Test suite
```

### Scala (`packages/promethium-scala/`)

```
promethium-scala/
  build.sbt             # SBT build definition
  src/main/scala/io/promethium/
    core/               # SeismicDataset, VelocityModel, Pipeline
    evaluation/         # Metrics
    recovery/           # MatrixCompletion, CompressiveSensing
    signal/             # Filters
  src/test/scala/       # ScalaTest suite
```

## Data Flow

```
Input Data (SEG-Y, HDF5, NumPy)
        |
        v
+-------------------+
| SeismicDataset    |
| - traces          |
| - dt              |
| - coordinates     |
| - metadata        |
+-------------------+
        |
        v
+-------------------+
| RecoveryPipeline  |
| - preprocessing   |
| - model config    |
| - postprocessing  |
+-------------------+
        |
        v
+-------------------+
| Recovery Model    |
| - Matrix Compl.   |
| - Comp. Sensing   |
| - U-Net / PINN    |
+-------------------+
        |
        v
+-------------------+
| Evaluation        |
| - SNR, MSE, PSNR  |
| - SSIM            |
+-------------------+
        |
        v
Output Data + Metrics
```

## Algorithm Categories

### Classical Signal Processing
- Wiener filtering
- Adaptive filters (LMS, Kalman)
- Deconvolution
- Time-frequency transforms (STFT, wavelet)

### Optimization-Based Recovery
- Matrix completion via nuclear norm minimization (ISTA)
- Compressive sensing via L1 minimization (FISTA)
- Sparse representation

### Deep Learning
- U-Net for interpolation and denoising
- Convolutional autoencoders
- GANs for high-fidelity reconstruction
- Physics-informed neural networks (PINN)

## Cross-Language Validation

All implementations are validated against shared test vectors stored in `testdata/` and `tests/cross_language/`. Numerical tolerances:

| Type | Tolerance |
|------|-----------|
| Metric values | 1e-6 absolute, 1e-4 relative |
| Signal arrays | 1e-8 absolute, 1e-6 relative |

## Versioning

All language implementations share synchronized major.minor versions:
- Current: **1.0.4**
- Python: `promethium-seismic==1.0.4`
- R: `promethiumR` version 1.0.4
- Julia: `Promethium` v1.0.4
- Scala: `io.promethium:promethium-scala:1.0.4`
