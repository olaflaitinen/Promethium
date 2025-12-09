"""
Pipeline module for Promethium.jl

Provides RecoveryPipeline type and execution functions.
"""

"""
    RecoveryPipeline

Configuration for seismic data recovery pipeline execution.

# Fields
- `name::String`: Pipeline identifier / preset name
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

"""
    from_preset(name::String) -> RecoveryPipeline

Create a pipeline from a preset name.

# Available Presets
- `"matrix_completion"`: Nuclear norm minimization via ISTA
- `"wiener"`: Frequency-domain Wiener filter
- `"fista"`: Fast ISTA for sparse recovery
"""
function from_preset(name::String)
    presets = Dict(
        "matrix_completion" => Dict{String,Any}(
            "model_type" => "matrix_completion",
            "lambda" => 0.1,
            "max_iter" => 100,
            "tol" => 1e-5
        ),
        "wiener" => Dict{String,Any}(
            "model_type" => "wiener",
            "noise_var" => nothing
        ),
        "fista" => Dict{String,Any}(
            "model_type" => "fista",
            "lambda" => 0.1,
            "max_iter" => 100,
            "tol" => 1e-5
        )
    )
    
    if !haskey(presets, name)
        available = join(keys(presets), ", ")
        error("Unknown preset: $name. Available: $available")
    end
    
    RecoveryPipeline(name, presets[name])
end

"""
    run_pipeline(pipe::RecoveryPipeline, ds::SeismicDataset; mask=nothing) -> SeismicDataset

Execute a recovery pipeline on seismic data.

# Arguments
- `pipe`: Pipeline configuration
- `ds`: Input seismic dataset
- `mask`: Optional boolean mask for observed entries

# Returns
SeismicDataset with recovered/reconstructed traces
"""
function run_pipeline(pipe::RecoveryPipeline, ds::SeismicDataset; 
                      mask::Union{Nothing, AbstractMatrix{Bool}}=nothing)
    model_type = get(pipe.config, "model_type", pipe.name)
    
    result = if model_type == "matrix_completion"
        λ = get(pipe.config, "lambda", 0.1)
        max_iter = get(pipe.config, "max_iter", 100)
        tol = get(pipe.config, "tol", 1e-5)
        
        actual_mask = isnothing(mask) ? trues(size(ds.traces)) : mask
        completed = matrix_completion_ista(ds.traces, actual_mask; λ=λ, max_iter=max_iter, tol=tol)
        completed
        
    elseif model_type == "wiener"
        # Apply Wiener filter to each trace
        recovered = similar(ds.traces)
        for i in 1:size(ds.traces, 1)
            recovered[i, :] = wiener_filter(ds.traces[i, :])
        end
        recovered
        
    elseif model_type == "fista"
        # For FISTA, need measurement matrix - simplified as identity for denoising
        recovered = similar(ds.traces)
        λ = get(pipe.config, "lambda", 0.1)
        max_iter = get(pipe.config, "max_iter", 100)
        
        for i in 1:size(ds.traces, 1)
            n = size(ds.traces, 2)
            A = Matrix{Float64}(I, n, n)
            recovered[i, :] = compressive_sensing_fista(ds.traces[i, :], A; λ=λ, max_iter=max_iter)
        end
        recovered
        
    else
        error("Unknown model type: $model_type")
    end
    
    SeismicDataset(result, ds.dt; coords=ds.coords, metadata=copy(ds.metadata))
end

# Convenience method
run(pipe::RecoveryPipeline, ds::SeismicDataset; kwargs...) = run_pipeline(pipe, ds; kwargs...)
