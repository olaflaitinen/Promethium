"""
Evaluation metrics for seismic data reconstruction quality.
"""

const EPSILON = 1e-10

"""
    compute_snr(reference::SeismicDataset, estimate::SeismicDataset) -> Float64

Compute Signal-to-Noise Ratio in dB.

SNR = 10 * log10(P_signal / P_noise)
"""
function compute_snr(reference::SeismicDataset, estimate::SeismicDataset)
    @assert size(reference.traces) == size(estimate.traces) "Dimension mismatch"
    
    ref = vec(reference.traces)
    est = vec(estimate.traces)
    
    signal_power = mean(ref .^ 2)
    noise = ref .- est
    noise_power = mean(noise .^ 2)
    
    10.0 * log10(signal_power / (noise_power + EPSILON))
end

"""
    compute_mse(reference::SeismicDataset, estimate::SeismicDataset) -> Float64

Compute Mean Squared Error.
"""
function compute_mse(reference::SeismicDataset, estimate::SeismicDataset)
    @assert size(reference.traces) == size(estimate.traces) "Dimension mismatch"
    
    diff = reference.traces .- estimate.traces
    mean(diff .^ 2)
end

"""
    compute_psnr(reference::SeismicDataset, estimate::SeismicDataset) -> Float64

Compute Peak Signal-to-Noise Ratio in dB.
"""
function compute_psnr(reference::SeismicDataset, estimate::SeismicDataset)
    max_val = maximum(abs.(reference.traces))
    mse = compute_mse(reference, estimate)
    10.0 * log10(max_val^2 / (mse + EPSILON))
end

"""
    compute_ssim(reference::SeismicDataset, estimate::SeismicDataset) -> Float64

Compute Structural Similarity Index.

Simplified SSIM based on luminance and contrast components.
"""
function compute_ssim(reference::SeismicDataset, estimate::SeismicDataset)
    @assert size(reference.traces) == size(estimate.traces) "Dimension mismatch"
    
    x = vec(reference.traces)
    y = vec(estimate.traces)
    
    mu_x = mean(x)
    mu_y = mean(y)
    sigma_x = std(x)
    sigma_y = std(y)
    sigma_xy = mean((x .- mu_x) .* (y .- mu_y))
    
    # Stability constants
    C1 = 0.01^2
    C2 = 0.03^2
    
    numerator = (2 * mu_x * mu_y + C1) * (2 * sigma_xy + C2)
    denominator = (mu_x^2 + mu_y^2 + C1) * (sigma_x^2 + sigma_y^2 + C2)
    
    numerator / denominator
end

"""
    compute_relative_error(reference::SeismicDataset, estimate::SeismicDataset) -> Float64

Compute relative Frobenius norm error.
"""
function compute_relative_error(reference::SeismicDataset, estimate::SeismicDataset)
    diff = estimate.traces .- reference.traces
    norm(diff) / (norm(reference.traces) + EPSILON)
end

"""
    evaluate(reference::SeismicDataset, estimate::SeismicDataset; 
             metrics=[:snr, :mse, :psnr, :ssim]) -> Dict{Symbol, Float64}

Compute all specified evaluation metrics.

# Arguments
- `reference`: Ground truth dataset
- `estimate`: Reconstructed/estimated dataset
- `metrics`: Vector of metric symbols to compute

# Returns
- `Dict{Symbol, Float64}`: Metric names mapped to values
"""
function evaluate(
    reference::SeismicDataset,
    estimate::SeismicDataset;
    metrics::Vector{Symbol} = [:snr, :mse, :psnr, :ssim]
)
    result = Dict{Symbol, Float64}()
    
    for metric in metrics
        value = if metric == :snr
            compute_snr(reference, estimate)
        elseif metric == :mse
            compute_mse(reference, estimate)
        elseif metric == :psnr
            compute_psnr(reference, estimate)
        elseif metric == :ssim
            compute_ssim(reference, estimate)
        elseif metric == :relative_error
            compute_relative_error(reference, estimate)
        else
            error("Unknown metric: $metric")
        end
        result[metric] = value
    end
    
    result
end
