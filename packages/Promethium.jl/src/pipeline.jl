"""
Pipeline orchestration for end-to-end seismic recovery workflows.
"""

# ============== RecoveryPipeline ==============

import Base: run

"""
    RecoveryPipeline

High-level recovery pipeline orchestrating preprocessing, model, and postprocessing.

# Fields
- `name::String`: Pipeline identifier
- `config::PipelineConfig`: Configuration

# Example
```julia
pipe = from_preset("matrix_completion")
result = run(pipe, dataset)
metrics = evaluate(truth, result)
```
"""
struct RecoveryPipeline
    name::String
    config::PipelineConfig
end

"""
    run(pipeline::RecoveryPipeline, dataset::SeismicDataset; mask=nothing)

Execute recovery pipeline on input data.

# Arguments
- `pipeline`: RecoveryPipeline configuration
- `dataset`: Input seismic dataset
- `mask`: Optional observation mask for completion problems

# Returns
- `SeismicDataset`: Reconstructed data
"""
function run(pipeline::RecoveryPipeline, dataset::SeismicDataset; 
             mask::Union{Matrix{Bool}, Nothing} = nothing)
    
    processed = dataset
    
    # Step 1: Preprocessing
    for step in pipeline.config.preprocessing
        processed = apply_preprocessing(processed, step)
    end
    
    # Step 2: Model execution
    recovered = apply_model(processed, pipeline.config.model, mask)
    
    # Step 3: Postprocessing
    for step in pipeline.config.postprocessing
        recovered = apply_postprocessing(recovered, step)
    end
    
    recovered
end

# Alias for convenience
run_pipeline = run

"""Apply a preprocessing step."""
function apply_preprocessing(ds::SeismicDataset, step::NormalizeStep)
    normalize(ds, step.method)
end

function apply_preprocessing(ds::SeismicDataset, step::BandpassStep)
    bandpass_filter(ds, step.low_freq, step.high_freq)
end

function apply_preprocessing(ds::SeismicDataset, step::TimeWindowStep)
    time_window(ds, step.t0, step.t1)
end

function apply_preprocessing(ds::SeismicDataset, step::RemoveDCStep)
    remove_dc(ds)
end

"""Apply recovery model."""
function apply_model(ds::SeismicDataset, config::ModelConfig, 
                     mask::Union{Matrix{Bool}, Nothing})
    
    if config.model_type == MATRIX_COMPLETION
        actual_mask = isnothing(mask) ? trues(size(ds.traces)) : mask
        completed = matrix_completion_ista(
            ds.traces, actual_mask;
            lambda = config.lambda,
            max_iter = config.max_iter,
            tolerance = config.tolerance
        )
        SeismicDataset(completed, ds.dt; coords=ds.coords, metadata=ds.metadata)
        
    elseif config.model_type == COMPRESSIVE_SENSING
        # Apply FISTA per trace (simplified)
        result = similar(ds.traces)
        nsamples = n_samples(ds)
        A = Matrix{Float64}(I, nsamples, nsamples)  # Identity for denoising
        
        for i in 1:n_traces(ds)
            y = ds.traces[i, :]
            result[i, :] = compressive_sensing_fista(
                y, A;
                lambda = config.lambda,
                max_iter = config.max_iter
            )
        end
        SeismicDataset(result, ds.dt; coords=ds.coords, metadata=ds.metadata)
        
    elseif config.model_type == WIENER
        wiener_filter(ds)
        
    else
        error("Model type $(config.model_type) not implemented")
    end
end

"""Apply a postprocessing step."""
function apply_postprocessing(ds::SeismicDataset, step::PostNormalizeStep)
    normalize(ds, step.method)
end

function apply_postprocessing(ds::SeismicDataset, step::ClipStep)
    clipped = clamp.(ds.traces, step.min_val, step.max_val)
    SeismicDataset(clipped, ds.dt; coords=ds.coords, metadata=ds.metadata)
end


# ============== Pipeline Presets ==============

"""
    from_preset(name::AbstractString) -> RecoveryPipeline

Create pipeline from preset name.

# Available Presets
- `"matrix_completion"`: Nuclear norm minimization via ISTA
- `"wiener"`: Wiener filter denoising
- `"fista"`: FISTA sparse recovery
"""
function from_preset(name::AbstractString)
    name_lower = lowercase(replace(name, "_" => ""))
    
    if name_lower == "matrixcompletion"
        RecoveryPipeline(
            "matrix_completion",
            PipelineConfig(
                [NormalizeStep(:rms)],
                ModelConfig(MATRIX_COMPLETION; lambda=0.1, max_iter=100),
                PostprocessingStep[],
                [:snr, :mse, :psnr, :ssim]
            )
        )
        
    elseif name_lower == "wiener"
        RecoveryPipeline(
            "wiener",
            PipelineConfig(
                PreprocessingStep[],
                ModelConfig(WIENER),
                PostprocessingStep[],
                [:snr, :mse, :psnr, :ssim]
            )
        )
        
    elseif name_lower in ["fista", "compressivesensing"]
        RecoveryPipeline(
            "fista",
            PipelineConfig(
                PreprocessingStep[],
                ModelConfig(COMPRESSIVE_SENSING; lambda=0.1, max_iter=100),
                PostprocessingStep[],
                [:snr, :mse, :psnr, :ssim]
            )
        )
        
    else
        error("Unknown preset: $name")
    end
end

"""
    matrix_completion_preset(; lambda=0.1, max_iter=100) -> RecoveryPipeline

Create matrix completion pipeline with custom parameters.
"""
function matrix_completion_preset(; lambda::Float64=0.1, max_iter::Int=100)
    RecoveryPipeline(
        "matrix_completion_custom",
        PipelineConfig(
            [NormalizeStep(:rms)],
            ModelConfig(MATRIX_COMPLETION; lambda=lambda, max_iter=max_iter),
            PostprocessingStep[],
            [:snr, :mse, :psnr, :ssim]
        )
    )
end

"""
    wiener_preset() -> RecoveryPipeline

Create Wiener filter pipeline.
"""
function wiener_preset()
    from_preset("wiener")
end
