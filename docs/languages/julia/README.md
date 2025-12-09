# Julia Guide for Promethium.jl

## Installation

```julia
using Pkg

# From GitHub
Pkg.add(url="https://github.com/olaflaitinen/Promethium", subdir="packages/Promethium.jl")

# Or from local path
Pkg.develop(path="packages/Promethium.jl")
```

## Quick Start

```julia
using Promethium

# Create dataset
traces = randn(100, 500)
ds = SeismicDataset(traces, 0.004)

# Run recovery
mask = rand(Bool, 100, 500)
completed = matrix_completion_ista(ds.traces, mask; λ=0.1)

# Evaluate
metrics = evaluate(ds.traces, completed)
println("SNR: $(metrics[:snr]) dB")
```

## Core Types

### SeismicDataset

```julia
# Constructor
ds = SeismicDataset(
    traces,           # AbstractMatrix
    0.004;            # dt
    coords = zeros(100, 2),
    metadata = Dict("survey" => "Test")
)

# Accessors
n_traces(ds)
n_samples(ds)

# Normalize
ds_norm = normalize(ds; method=:rms)
```

### VelocityModel

```julia
grid = 2000.0 .+ 1000.0 .* rand(100, 100)
vm = VelocityModel(grid, 10.0, 5.0)
```

## Recovery Algorithms

### Matrix Completion (ISTA)

```julia
# M: matrix with missing entries
# mask: Bool matrix (true = observed)

completed = matrix_completion_ista(M, mask;
    λ = 0.1,
    max_iter = 100,
    tol = 1e-5
)
```

### Compressive Sensing (FISTA)

```julia
# y: observations
# A: measurement matrix

x_recovered = compressive_sensing_fista(y, A;
    λ = 0.1,
    max_iter = 100,
    tol = 1e-5
)
```

### Wiener Filter

```julia
denoised = wiener_filter(noisy_signal)
```

## Evaluation Metrics

```julia
# Individual
snr = compute_snr(reference, estimate)
mse = compute_mse(reference, estimate)
psnr = compute_psnr(reference, estimate)
ssim = compute_ssim(reference, estimate)

# All at once
metrics = evaluate(reference, estimate; 
    metrics=[:snr, :mse, :psnr, :ssim])
```

## Synthetic Data

```julia
ds = synthetic_data(
    n_traces = 100,
    n_samples = 500,
    dt = 0.004,
    noise_level = 0.1,
    seed = 42
)
```

## Testing

```julia
using Pkg
Pkg.test("Promethium")
```

## Performance Tips

1. **Type stability**: All core functions are type-stable for maximum JIT efficiency
2. **Array backends**: `SeismicDataset` is parameterized, allowing GPU arrays
3. **SIMD**: Critical loops are written for automatic vectorization
