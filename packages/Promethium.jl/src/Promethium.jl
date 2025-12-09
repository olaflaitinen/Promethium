"""
    Promethium.jl

Advanced Seismic Data Recovery and Reconstruction Framework for Julia.

Native Julia implementation conforming to the Promethium multi-language specification.
Provides algorithms for seismic data denoising, interpolation, and reconstruction
using classical signal processing, optimization-based methods, and deep learning.

# Installation

```julia
using Pkg
Pkg.add("Promethium")
```

# Quick Start

```julia
using Promethium

# Generate synthetic data
ds = synthetic_data(ntraces=100, nsamples=500, dt=0.004)

# Create recovery pipeline
pipe = from_preset("matrix_completion")

# Run reconstruction
result = run(pipe, ds)

# Evaluate
metrics = evaluate(ds, result)
println("SNR: \$(metrics[:snr]) dB")
```

# Modules

- `Data`: Core data structures (SeismicDataset, VelocityModel)
- `IO`: File format readers/writers (SEG-Y, HDF5)
- `Signal`: Classical signal processing (filters, deconvolution)
- `Recovery`: Optimization algorithms (ISTA, FISTA, SVT)
- `Evaluation`: Quality metrics (SNR, MSE, PSNR, SSIM)
- `Pipelines`: End-to-end workflow orchestration
"""
module Promethium

using LinearAlgebra
using Statistics
using FFTW
using Random

# Version aligned with global Promethium spec
const VERSION = v"1.0.4"

# ============== Core Types ==============
# ============== Core Types ==============
export SeismicDataset, VelocityModel, RecoveryPipeline
export n_traces, n_samples, normalize, time_axis, duration
export subset_traces, time_window
export constant_velocity, linear_velocity, nx, nz, interpolate_at

# ============== I/O ==============
export load_segy, write_segy, synthetic_data, load_hdf5, save_hdf5

# ============== Pipeline ==============
export from_preset, run_pipeline, run

# ============== Algorithms ==============
export wiener_filter, bandpass_filter, remove_dc
export matrix_completion_ista, compressive_sensing_fista

# ============== Evaluation ==============
export compute_snr, compute_mse, compute_psnr, compute_ssim, evaluate

# Include submodules
include("types.jl")
include("io.jl")
include("metrics.jl")
include("recovery.jl")
include("signal.jl")
include("pipeline.jl")

end # module
