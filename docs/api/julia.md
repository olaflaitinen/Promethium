# Julia API Reference

# Julia API Reference

[![Julia](https://img.shields.io/badge/Julia-1.9+-9558B2?logo=julia)](https://julialang.org/)
[![Registry](https://img.shields.io/badge/Registry-General-green)](https://github.com/JuliaRegistries/General)

Promethium.jl provides a state-of-the-art (SoTA) native Julia implementation of the seismic data recovery framework.

**Julia Package:** [https://juliahub.com/ui/Packages/Promethium](https://juliahub.com/ui/Packages/Promethium)

## Installation

```julia
using Pkg
Pkg.add("Promethium")
using Promethium
```

## Quick Start

```julia
using Promethium

# Generate synthetic data
ds = synthetic_data(ntraces=100, nsamples=500, dt=0.004, noise_level=0.1)

# Create recovery pipeline
pipe = from_preset("matrix_completion")

# Run reconstruction
result = run(pipe, ds)

# Evaluate
metrics = evaluate(ds, result)
println("SNR: $(metrics[:snr]) dB")
```

## Core Types

### SeismicDataset

```julia
struct SeismicDataset{T<:AbstractFloat}
    traces::Matrix{T}           # (ntraces x nsamples)
    dt::Float64                 # Sampling interval (seconds)
    coords::Union{Matrix,Nothing}
    metadata::Dict{String,Any}
end
```

**Methods:**

| Function | Description |
|----------|-------------|
| `n_traces(ds)` | Number of traces |
| `n_samples(ds)` | Samples per trace |
| `duration(ds)` | Recording duration |
| `time_axis(ds)` | Time vector |
| `normalize(ds, :rms)` | Normalize traces |
| `subset_traces(ds, indices)` | Extract subset |
| `time_window(ds, t0, t1)` | Extract time window |

**Factory Functions:**

```julia
# Generate synthetic data
ds = synthetic_data(ntraces=100, nsamples=500, dt=0.004, seed=42)
```

### VelocityModel

```julia
struct VelocityModel{T<:AbstractFloat}
    velocities::Matrix{T}   # (nz x nx)
    dx::Float64
    dz::Float64
    origin::Tuple{Float64,Float64}
    metadata::Dict{String,Any}
end
```

**Factory Functions:**

```julia
vm = constant_velocity(1500.0, 100, 50, 10.0, 5.0)
vm = linear_velocity(1500.0, 0.5, 100, 50, 10.0, 5.0)
```

## Recovery Algorithms

### Matrix Completion

```julia
completed = matrix_completion_ista(
    observed, mask;
    lambda = 0.1,
    max_iter = 100,
    tolerance = 1e-5
)
```

### Compressive Sensing

```julia
recovered = compressive_sensing_fista(
    y, A;
    lambda = 0.1,
    max_iter = 100
)
```

## Signal Processing

### Filters

```julia
# Wiener filter
denoised = wiener_filter(ds)

# Bandpass filter
filtered = bandpass_filter(ds, 5.0, 80.0)

# Remove DC offset
dc_removed = remove_dc(ds)
```

## Pipelines

### Using Presets

```julia
pipe = from_preset("matrix_completion")
pipe = from_preset("wiener")
pipe = from_preset("fista")
```

### Running Pipeline

```julia
result = run(pipe, dataset)
result = run(pipe, dataset; mask=observation_mask)
```

## Evaluation Metrics

```julia
# Individual metrics
snr = compute_snr(reference, estimate)
mse = compute_mse(reference, estimate)
psnr = compute_psnr(reference, estimate)
ssim = compute_ssim(reference, estimate)

# All at once
metrics = evaluate(reference, estimate; 
    metrics=[:snr, :mse, :psnr, :ssim])
```

## I/O

### SEG-Y Format

```julia
# Read
ds = load_segy("data.sgy")

# Write
write_segy("output.sgy", ds)
```

## Cross-Language Consistency

This Julia implementation produces numerically identical results to Python, R, and Scala within specified tolerances (1e-6 absolute, 1e-4 relative for metrics).
