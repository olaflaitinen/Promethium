"""
I/O functions for Promethium.jl

Provides SEG-Y reading/writing stubs and reference data loading.
"""

"""
    load_segy(path::String; dt=nothing) -> SeismicDataset

Load seismic data from SEG-Y format.

Note: This is a stub implementation. For full SEG-Y support,
use the SEGY.jl package or implement custom reader.
"""
function load_segy(path::String; dt::Union{Nothing,Float64}=nothing)
    if !isfile(path)
        error("File not found: $path")
    end
    
    @warn "SEG-Y reading is a stub. Install SEGY.jl for full support."
    
    # Stub: return synthetic data
    n_traces = 100
    n_samples = 500
    dt_val = isnothing(dt) ? 0.004 : dt
    
    traces = randn(n_traces, n_samples)
    SeismicDataset(traces, dt_val; 
                   metadata=Dict{String,Any}("source" => path, "format" => "segy"))
end

"""
    write_segy(dataset::SeismicDataset, path::String)

Write seismic data to SEG-Y format.
"""
function write_segy(dataset::SeismicDataset, path::String)
    @warn "SEG-Y writing is a stub. Install SEGY.jl for full support."
    
    # Stub: save as JLD2 instead
    @info "Data not saved (stub implementation)"
    nothing
end

"""
    load_hdf5(path::String; dataset_name="traces") -> SeismicDataset

Load reference test data from HDF5 format.
"""
function load_hdf5(path::String; dataset_name::String="traces")
    # Note: Requires HDF5.jl package
    try
        using HDF5: h5open, read
    catch
        error("HDF5.jl required. Install with: ] add HDF5")
    end
    
    h5open(path, "r") do file
        traces = read(file, dataset_name)
        dt = haskey(file, "dt") ? read(file, "dt") : 0.004
        SeismicDataset(traces, Float64(dt);
                       metadata=Dict{String,Any}("source" => path, "format" => "hdf5"))
    end
end

"""
    synthetic_data(; n_traces=100, n_samples=500, dt=0.004, noise_level=0.1, seed=nothing) -> SeismicDataset

Generate synthetic seismic data for testing.

# Arguments
- `n_traces`: Number of traces
- `n_samples`: Samples per trace  
- `dt`: Sampling interval in seconds
- `noise_level`: Relative noise level (0-1)
- `seed`: Random seed for reproducibility

# Returns
SeismicDataset with synthetic traces
"""
function synthetic_data(; 
    n_traces::Int=100, 
    n_samples::Int=500, 
    dt::Float64=0.004, 
    noise_level::Float64=0.1,
    seed::Union{Nothing,Int}=nothing
)
    if !isnothing(seed)
        import Random
        Random.seed!(seed)
    end
    
    t = collect(0:n_samples-1) .* dt
    traces = zeros(n_traces, n_samples)
    
    for i in 1:n_traces
        # Random number of events
        n_events = rand(3:8)
        event_times = sort(rand(n_events) .* (maximum(t) - 0.2) .+ 0.1)
        event_amps = (rand(n_events) .* 1.0 .+ 0.5) .* rand([-1, 1], n_events)
        
        for (te, ae) in zip(event_times, event_amps)
            # Ricker wavelet
            f0 = 30.0  # Dominant frequency
            tau = t .- te
            wavelet = (1.0 .- 2.0 .* (pi .* f0 .* tau).^2) .* exp.(-(pi .* f0 .* tau).^2)
            traces[i, :] .+= ae .* wavelet
        end
    end
    
    # Add noise
    if noise_level > 0
        signal_rms = sqrt(mean(traces.^2))
        noise = randn(n_traces, n_samples)
        traces .+= noise_level .* signal_rms .* noise
    end
    
    SeismicDataset(traces, dt;
                   metadata=Dict{String,Any}(
                       "synthetic" => true,
                       "n_traces" => n_traces,
                       "n_samples" => n_samples,
                       "noise_level" => noise_level
                   ))
end
