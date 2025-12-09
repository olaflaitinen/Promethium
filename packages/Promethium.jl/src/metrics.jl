"""
Evaluation metrics for Promethium.jl

Implements SNR, MSE, PSNR, SSIM following the Promethium specification.
"""

"""
    compute_snr(reference, estimate) -> Float64

Compute Signal-to-Noise Ratio in decibels (dB).

# Formula
SNR = 10 * log10(signal_power / noise_power)
"""
function compute_snr(reference::AbstractArray, estimate::AbstractArray)
    signal_power = mean(reference.^2)
    noise_power = mean((reference .- estimate).^2)
    10 * log10(signal_power / (noise_power + 1e-10))
end

"""
    compute_mse(reference, estimate) -> Float64

Compute Mean Squared Error.
"""
compute_mse(reference::AbstractArray, estimate::AbstractArray) = 
    mean((reference .- estimate).^2)

"""
    compute_psnr(reference, estimate) -> Float64

Compute Peak Signal-to-Noise Ratio in decibels (dB).

# Formula
PSNR = 10 * log10(max_val^2 / MSE)
"""
function compute_psnr(reference::AbstractArray, estimate::AbstractArray)
    mse = compute_mse(reference, estimate)
    max_val = maximum(abs, reference)
    10 * log10(max_val^2 / (mse + 1e-10))
end

"""
    compute_ssim(reference, estimate; C1=0.0001, C2=0.0009) -> Float64

Compute Structural Similarity Index.

Simplified implementation for comparison with other languages.
"""
function compute_ssim(reference::AbstractArray, estimate::AbstractArray;
                      C1::Float64=0.0001, C2::Float64=0.0009)
    μ_x = mean(reference)
    μ_y = mean(estimate)
    σ_x = std(vec(reference))
    σ_y = std(vec(estimate))
    σ_xy = cov(vec(reference), vec(estimate))
    
    numerator = (2 * μ_x * μ_y + C1) * (2 * σ_xy + C2)
    denominator = (μ_x^2 + μ_y^2 + C1) * (σ_x^2 + σ_y^2 + C2)
    
    numerator / denominator
end

"""
    evaluate(reference, estimate; metrics=[:snr, :mse, :psnr, :ssim]) -> Dict{Symbol, Float64}

Compute all specified evaluation metrics.

# Example
```julia
metrics = evaluate(ground_truth, reconstructed)
println("SNR: ", metrics[:snr], " dB")
```
"""
function evaluate(reference::AbstractArray, estimate::AbstractArray;
                  metrics::Vector{Symbol}=[:snr, :mse, :psnr, :ssim])
    results = Dict{Symbol, Float64}()
    
    :snr in metrics && (results[:snr] = compute_snr(reference, estimate))
    :mse in metrics && (results[:mse] = compute_mse(reference, estimate))
    :psnr in metrics && (results[:psnr] = compute_psnr(reference, estimate))
    :ssim in metrics && (results[:ssim] = compute_ssim(reference, estimate))
    
    results
end
