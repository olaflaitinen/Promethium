"""
    Promethium.jl

Advanced Seismic Data Recovery and Reconstruction Framework for Julia.

Native Julia implementation conforming to the Promethium multi-language specification.
"""
module Promethium

using LinearAlgebra
using Statistics
using FFTW

# Version aligned with global Promethium spec
const VERSION = v"1.0.4"

# Core types
export SeismicDataset, VelocityModel, RecoveryPipeline
export n_traces, n_samples, normalize

# I/O
export load_segy, write_segy, synthetic_data

# Pipeline
export from_preset, run_pipeline, run

# Algorithms
export wiener_filter, matrix_completion_ista, compressive_sensing_fista

# Evaluation
export compute_snr, compute_mse, compute_psnr, compute_ssim, evaluate

# Include submodules
include("types.jl")
include("io.jl")
include("metrics.jl")
include("recovery.jl")
include("signal.jl")
include("pipeline.jl")

end # module

