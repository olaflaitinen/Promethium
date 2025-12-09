"""
Core data types for Promethium.jl

Defines SeismicDataset, VelocityModel, and RecoveryPipeline structs.
"""

"""
    SeismicDataset{T,A}

Container for seismic trace data.

# Fields
- `traces::A`: 2D array of amplitudes (n_traces x n_samples)
- `dt::Float64`: Sampling interval in seconds
- `coords::Matrix{Float64}`: Trace coordinates (n_traces x n_coords)
- `metadata::Dict{String,Any}`: Metadata dictionary

# Example
```julia
traces = randn(100, 500)  # 100 traces, 500 samples
ds = SeismicDataset(traces, 0.004)
println(n_traces(ds), " traces")
```
"""
struct SeismicDataset{T<:AbstractFloat, A<:AbstractMatrix{T}}
    traces::A
    dt::Float64
    coords::Matrix{Float64}
    metadata::Dict{String, Any}
    
    function SeismicDataset(
        traces::A, 
        dt::Float64;
        coords::Matrix{Float64} = zeros(Float64, size(traces, 1), 0),
        metadata::Dict{String, Any} = Dict{String, Any}()
    ) where {T<:AbstractFloat, A<:AbstractMatrix{T}}
        @assert dt > 0 "Sampling interval must be positive"
        @assert size(traces, 1) == size(coords, 1) || size(coords, 1) == 0 "Coordinate rows must match trace count"
        new{T, A}(traces, dt, coords, metadata)
    end
end

# Convenience constructor for Matrix{Float64}
SeismicDataset(traces::Matrix{Float64}, dt::Float64; kwargs...) = 
    SeismicDataset{Float64, Matrix{Float64}}(traces, dt; kwargs...)

# Accessors
Base.size(ds::SeismicDataset) = size(ds.traces)
n_traces(ds::SeismicDataset) = size(ds.traces, 1)
n_samples(ds::SeismicDataset) = size(ds.traces, 2)
duration(ds::SeismicDataset) = ds.n_samples * ds.dt

function Base.show(io::IO, ds::SeismicDataset)
    print(io, "SeismicDataset($(n_traces(ds)) traces, $(n_samples(ds)) samples, dt=$(ds.dt)s)")
end

"""
    normalize(ds::SeismicDataset; method=:rms) -> SeismicDataset

Normalize trace amplitudes.

# Methods
- `:rms`: Divide by RMS amplitude per trace
- `:max`: Divide by global maximum
- `:std`: Standardize per trace (zero mean, unit variance)
"""
function normalize(ds::SeismicDataset; method::Symbol=:rms)
    traces = ds.traces
    if method == :rms
        rms = sqrt.(mean(traces.^2, dims=2))
        normalized = traces ./ (rms .+ 1e-10)
    elseif method == :max
        normalized = traces ./ (maximum(abs, traces) + 1e-10)
    elseif method == :std
        μ = mean(traces, dims=2)
        σ = std(traces, dims=2)
        normalized = (traces .- μ) ./ (σ .+ 1e-10)
    else
        error("Unknown normalization method: $method")
    end
    SeismicDataset(normalized, ds.dt; coords=ds.coords, metadata=copy(ds.metadata))
end


"""
    VelocityModel

2D or 3D velocity model for seismic processing.

# Fields
- `grid::Array{Float64}`: Velocity values in m/s
- `dx::Float64`: Horizontal spacing
- `dz::Float64`: Vertical spacing
- `origin::Tuple{Float64,Float64}`: Grid origin (x0, z0)
- `metadata::Dict{String,Any}`: Metadata
"""
struct VelocityModel
    grid::Array{Float64}
    dx::Float64
    dz::Float64
    origin::Tuple{Float64, Float64}
    metadata::Dict{String, Any}
    
    function VelocityModel(
        grid::Array{Float64},
        dx::Float64,
        dz::Float64;
        origin::Tuple{Float64,Float64} = (0.0, 0.0),
        metadata::Dict{String,Any} = Dict{String,Any}()
    )
        @assert dx > 0 && dz > 0 "Grid spacing must be positive"
        new(grid, dx, dz, origin, metadata)
    end
end

function Base.show(io::IO, vm::VelocityModel)
    sz = size(vm.grid)
    vmin, vmax = extrema(vm.grid)
    print(io, "VelocityModel($(sz), v=$(round(vmin))-$(round(vmax)) m/s)")
end


"""
    RecoveryPipeline

Configuration for seismic data recovery pipeline.

# Fields
- `name::String`: Pipeline identifier
- `config::Dict{String,Any}`: Configuration parameters
"""
struct RecoveryPipeline
    name::String
    config::Dict{String, Any}
end

RecoveryPipeline(name::String) = RecoveryPipeline(name, Dict{String,Any}())

function Base.show(io::IO, p::RecoveryPipeline)
    print(io, "RecoveryPipeline(\"$(p.name)\")")
end
