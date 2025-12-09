"""
Core data structures for Promethium.jl.
"""

# ============== SeismicDataset ==============

"""
    SeismicDataset{T<:AbstractFloat}

Container for seismic trace data with metadata.

# Fields
- `traces::Matrix{T}`: 2D array (ntraces x nsamples)
- `dt::Float64`: Sampling interval in seconds
- `coords::Union{Matrix{Float64}, Nothing}`: Optional coordinates (ntraces x 2)
- `metadata::Dict{String, Any}`: Key-value metadata

# Examples
```julia
traces = randn(100, 500)
ds = SeismicDataset(traces, 0.004)
println("Duration: \$(duration(ds)) seconds")
```
"""
struct SeismicDataset{T<:AbstractFloat}
    traces::Matrix{T}
    dt::Float64
    coords::Union{Matrix{Float64}, Nothing}
    metadata::Dict{String, Any}
    
    function SeismicDataset(
        traces::Matrix{T},
        dt::Float64;
        coords::Union{Matrix{Float64}, Nothing} = nothing,
        metadata::Dict{String, Any} = Dict{String, Any}()
    ) where {T<:AbstractFloat}
        @assert dt > 0 "Sampling interval dt must be positive"
        @assert size(traces, 1) > 0 "Must have at least one trace"
        @assert size(traces, 2) > 0 "Traces must have at least one sample"
        new{T}(traces, dt, coords, metadata)
    end
end

# Convenience constructor from Any matrix
function SeismicDataset(traces::AbstractMatrix, dt::Real; kwargs...)
    SeismicDataset(Float64.(traces), Float64(dt); kwargs...)
end

"""
    n_traces(ds::SeismicDataset) -> Int

Return number of traces in dataset.
"""
n_traces(ds::SeismicDataset) = size(ds.traces, 1)

"""
    n_samples(ds::SeismicDataset) -> Int

Return number of samples per trace.
"""
n_samples(ds::SeismicDataset) = size(ds.traces, 2)

"""
    duration(ds::SeismicDataset) -> Float64

Return total recording duration in seconds.
"""
duration(ds::SeismicDataset) = (n_samples(ds) - 1) * ds.dt

"""
    time_axis(ds::SeismicDataset) -> StepRangeLen

Return time axis vector.
"""
time_axis(ds::SeismicDataset) = range(0.0, step=ds.dt, length=n_samples(ds))

"""
    normalize(ds::SeismicDataset, method::Symbol=:rms) -> SeismicDataset

Normalize traces using specified method.

# Methods
- `:max`: Divide by maximum absolute value
- `:rms`: Divide by RMS amplitude
- `:standard`: Z-score normalization
"""
function normalize(ds::SeismicDataset{T}, method::Symbol=:rms) where {T}
    normalized = similar(ds.traces)
    
    for i in 1:n_traces(ds)
        row = ds.traces[i, :]
        
        if method == :max
            maxval = maximum(abs.(row))
            normalized[i, :] = maxval > 1e-10 ? row ./ maxval : row
            
        elseif method == :rms
            rms = sqrt(mean(row .^ 2))
            normalized[i, :] = rms > 1e-10 ? row ./ rms : row
            
        elseif method == :standard
            m = mean(row)
            s = std(row)
            normalized[i, :] = s > 1e-10 ? (row .- m) ./ s : row .- m
            
        else
            error("Unknown normalization method: $method")
        end
    end
    
    SeismicDataset(normalized, ds.dt; coords=ds.coords, metadata=ds.metadata)
end

"""
    subset_traces(ds::SeismicDataset, indices) -> SeismicDataset

Extract subset of traces by indices.
"""
function subset_traces(ds::SeismicDataset{T}, indices) where {T}
    new_traces = ds.traces[indices, :]
    new_coords = isnothing(ds.coords) ? nothing : ds.coords[indices, :]
    SeismicDataset(new_traces, ds.dt; coords=new_coords, metadata=ds.metadata)
end

"""
    time_window(ds::SeismicDataset, t0::Real, t1::Real) -> SeismicDataset

Extract time window from all traces.
"""
function time_window(ds::SeismicDataset{T}, t0::Real, t1::Real) where {T}
    @assert t0 >= 0 && t0 < t1 "Invalid time window"
    i0 = max(1, round(Int, t0 / ds.dt) + 1)
    i1 = min(n_samples(ds), round(Int, t1 / ds.dt) + 1)
    new_traces = ds.traces[:, i0:i1]
    SeismicDataset(new_traces, ds.dt; coords=ds.coords, metadata=ds.metadata)
end

"""
    statistics(ds::SeismicDataset) -> Dict{String, Float64}

Compute basic statistics for the dataset.
"""
function statistics(ds::SeismicDataset)
    all_values = vec(ds.traces)
    Dict{String, Float64}(
        "min" => minimum(all_values),
        "max" => maximum(all_values),
        "mean" => mean(all_values),
        "std" => std(all_values),
        "rms" => sqrt(mean(all_values .^ 2))
    )
end

Base.show(io::IO, ds::SeismicDataset) = 
    print(io, "SeismicDataset($(n_traces(ds)) traces, $(n_samples(ds)) samples, dt=$(ds.dt))")


# ============== VelocityModel ==============

"""
    VelocityModel{T<:AbstractFloat}

2D velocity model for seismic wave propagation.

# Fields
- `velocities::Matrix{T}`: (nz x nx) grid of velocity values (m/s)
- `dx::Float64`: Horizontal grid spacing (m)
- `dz::Float64`: Vertical grid spacing (m)
- `origin::Tuple{Float64,Float64}`: Grid origin (x0, z0)
- `metadata::Dict{String, Any}`: Key-value metadata
"""
struct VelocityModel{T<:AbstractFloat}
    velocities::Matrix{T}
    dx::Float64
    dz::Float64
    origin::Tuple{Float64, Float64}
    metadata::Dict{String, Any}
    
    function VelocityModel(
        velocities::Matrix{T},
        dx::Float64,
        dz::Float64;
        origin::Tuple{Float64, Float64} = (0.0, 0.0),
        metadata::Dict{String, Any} = Dict{String, Any}()
    ) where {T<:AbstractFloat}
        @assert dx > 0 && dz > 0 "Grid spacing must be positive"
        new{T}(velocities, dx, dz, origin, metadata)
    end
end

"""Number of horizontal grid points."""
nx(vm::VelocityModel) = size(vm.velocities, 2)

"""Number of vertical grid points."""
nz(vm::VelocityModel) = size(vm.velocities, 1)

"""Horizontal extent in meters."""
extent_x(vm::VelocityModel) = (nx(vm) - 1) * vm.dx

"""Vertical extent in meters."""
extent_z(vm::VelocityModel) = (nz(vm) - 1) * vm.dz

"""
    interpolate_at(vm::VelocityModel, x::Real, z::Real) -> Float64

Bilinear interpolation of velocity at position (x, z).
"""
function interpolate_at(vm::VelocityModel, x::Real, z::Real)
    x0, z0 = vm.origin
    
    # Continuous grid indices
    ix = (x - x0) / vm.dx
    iz = (z - z0) / vm.dz
    
    # Integer indices (1-based)
    i0 = max(1, min(nz(vm) - 1, floor(Int, iz) + 1))
    j0 = max(1, min(nx(vm) - 1, floor(Int, ix) + 1))
    i1 = i0 + 1
    j1 = j0 + 1
    
    # Fractional parts
    fx = ix - (j0 - 1)
    fz = iz - (i0 - 1)
    
    # Bilinear interpolation
    v00 = vm.velocities[i0, j0]
    v01 = vm.velocities[i0, j1]
    v10 = vm.velocities[i1, j0]
    v11 = vm.velocities[i1, j1]
    
    (1 - fx) * (1 - fz) * v00 +
    fx * (1 - fz) * v01 +
    (1 - fx) * fz * v10 +
    fx * fz * v11
end

"""
    constant_velocity(v, nx, nz, dx, dz) -> VelocityModel

Create constant velocity model.
"""
function constant_velocity(v::Real, nx::Int, nz::Int, dx::Real, dz::Real)
    VelocityModel(fill(Float64(v), nz, nx), Float64(dx), Float64(dz))
end

"""
    linear_velocity(v0, gradient, nx, nz, dx, dz) -> VelocityModel

Create linearly increasing velocity model (v = v0 + gradient * z).
"""
function linear_velocity(v0::Real, gradient::Real, nx::Int, nz::Int, dx::Real, dz::Real)
    grid = Matrix{Float64}(undef, nz, nx)
    for i in 1:nz, j in 1:nx
        grid[i, j] = v0 + gradient * (i - 1) * dz
    end
    VelocityModel(grid, Float64(dx), Float64(dz))
end

Base.show(io::IO, vm::VelocityModel) = 
    print(io, "VelocityModel($(nz(vm))x$(nx(vm)), v=$(round(minimum(vm.velocities)))-$(round(maximum(vm.velocities))) m/s)")


# ============== Pipeline Configuration ==============

"""Abstract type for preprocessing steps."""
abstract type PreprocessingStep end

"""Normalize traces."""
struct NormalizeStep <: PreprocessingStep
    method::Symbol
end

"""Apply bandpass filter."""
struct BandpassStep <: PreprocessingStep
    low_freq::Float64
    high_freq::Float64
end

"""Apply time window."""
struct TimeWindowStep <: PreprocessingStep
    t0::Float64
    t1::Float64
end

"""Remove DC offset."""
struct RemoveDCStep <: PreprocessingStep end

"""Abstract type for postprocessing steps."""
abstract type PostprocessingStep end

"""Normalize after reconstruction."""
struct PostNormalizeStep <: PostprocessingStep
    method::Symbol
end

"""Clip values."""
struct ClipStep <: PostprocessingStep
    min_val::Float64
    max_val::Float64
end

"""Model types for recovery."""
@enum ModelType begin
    MATRIX_COMPLETION
    COMPRESSIVE_SENSING
    WIENER
    UNET
    AUTOENCODER
    PINN
end

"""
    ModelConfig

Configuration for recovery model.
"""
struct ModelConfig
    model_type::ModelType
    lambda::Float64
    max_iter::Int
    tolerance::Float64
    extra_params::Dict{String, Any}
end

function ModelConfig(model_type::ModelType; 
                     lambda=0.1, max_iter=100, tolerance=1e-5,
                     extra_params=Dict{String, Any}())
    ModelConfig(model_type, lambda, max_iter, tolerance, extra_params)
end

"""
    PipelineConfig

Complete pipeline configuration.
"""
struct PipelineConfig
    preprocessing::Vector{PreprocessingStep}
    model::ModelConfig
    postprocessing::Vector{PostprocessingStep}
    eval_metrics::Vector{Symbol}
end
