#=
Promethium.jl Examples
Basic Denoising Example

This script demonstrates seismic data denoising using Promethium.jl.
It shows loading data, applying filters, and evaluating reconstruction quality.

Usage:
    julia basic_denoising.jl
=#

using Promethium
using Random
using Statistics
using Printf

println("Promethium.jl - Basic Denoising Example")
println("=" ^ 50)

# -----------------------------------------------------------------------------
# 1. Generate Synthetic Data
# -----------------------------------------------------------------------------

println("\n1. Generating synthetic seismic data...")

# Set random seed for reproducibility
Random.seed!(42)

n_traces = 100
n_samples = 500
sample_rate = 0.004  # 4 ms

# Generate time axis
time_axis = collect(0:sample_rate:(n_samples-1)*sample_rate)

# Create clean synthetic data with reflections
clean_data = zeros(Float64, n_traces, n_samples)

# Ricker wavelet function
function ricker_wavelet(t, f0)
    return (1 - 2 * (π * f0 * t)^2) * exp(-(π * f0 * t)^2)
end

# Add synthetic reflections
reflection_times = [0.2, 0.5, 0.8, 1.2]
f0 = 30.0  # Dominant frequency

for i in 1:n_traces
    for rt in reflection_times
        idx = argmin(abs.(time_axis .- rt))
        amp = 0.5 + 0.5 * rand()
        
        # Add Ricker wavelet
        wavelet_half = 50
        for j in max(1, idx-wavelet_half):min(n_samples, idx+wavelet_half)
            t = (j - idx) * sample_rate
            clean_data[i, j] += amp * ricker_wavelet(t, f0)
        end
    end
end

# Add noise
noise_level = 0.3
noisy_data = clean_data .+ noise_level .* randn(n_traces, n_samples)

@printf("  Traces: %d\n", n_traces)
@printf("  Samples: %d\n", n_samples)
@printf("  Sample rate: %.1f ms\n", sample_rate * 1000)
@printf("  Noise level: %.2f\n", noise_level)

# -----------------------------------------------------------------------------
# 2. Create SeismicDataset
# -----------------------------------------------------------------------------

println("\n2. Creating SeismicDataset objects...")

# Create dataset from noisy data
noisy_dataset = SeismicDataset(
    noisy_data,
    sample_rate=sample_rate,
    metadata=Dict(
        "source" => "synthetic",
        "description" => "Noisy synthetic shot gather"
    )
)

println(noisy_dataset)

# -----------------------------------------------------------------------------
# 3. Apply Wiener Filter
# -----------------------------------------------------------------------------

println("\n3. Applying Wiener filter denoising...")

# Apply Wiener filter
wiener_result = wiener_filter(noisy_dataset, noise_power=noise_level^2)

println("   Wiener filter applied successfully.")

# -----------------------------------------------------------------------------
# 4. Apply Matrix Completion (if traces are missing)
# -----------------------------------------------------------------------------

println("\n4. Demonstrating matrix completion for missing traces...")

# Create data with missing traces
missing_ratio = 0.3
n_missing = round(Int, n_traces * missing_ratio)
missing_indices = sort(randperm(n_traces)[1:n_missing])

missing_data = copy(noisy_data)
missing_data[missing_indices, :] .= 0.0

# Create mask
mask = ones(Bool, n_traces, n_samples)
mask[missing_indices, :] .= false

# Apply matrix completion
@printf("   Removing %d traces (%.0f%% missing)...\n", n_missing, missing_ratio * 100)

# Note: matrix_completion_ista is from the Promethium package
recovered_data = matrix_completion_ista(
    missing_data,
    mask,
    lambda=0.1,
    max_iter=100
)

println("   Matrix completion applied successfully.")

# -----------------------------------------------------------------------------
# 5. Compute Quality Metrics
# -----------------------------------------------------------------------------

println("\n" * "-" ^ 50)
println("Quality Metrics")
println("-" ^ 50)

# SNR function
function compute_snr(reference, estimate)
    signal_power = sum(reference.^2)
    noise_power = sum((reference .- estimate).^2)
    return 10 * log10(signal_power / noise_power)
end

# MSE function
function compute_mse(reference, estimate)
    return mean((reference .- estimate).^2)
end

# Compute metrics for Wiener filter
wiener_data = wiener_result.traces
snr_noisy = compute_snr(clean_data, noisy_data)
snr_wiener = compute_snr(clean_data, wiener_data)

@printf("Original noisy SNR:    %.2f dB\n", snr_noisy)
@printf("After Wiener filter:   %.2f dB\n", snr_wiener)
@printf("  Improvement:         %.2f dB\n", snr_wiener - snr_noisy)

# Compute metrics for matrix completion (only on recovered traces)
if !isempty(missing_indices)
    snr_missing = compute_snr(clean_data[missing_indices, :], recovered_data[missing_indices, :])
    @printf("\nRecovered traces SNR:  %.2f dB\n", snr_missing)
end

# MSE
mse_noisy = compute_mse(clean_data, noisy_data)
mse_wiener = compute_mse(clean_data, wiener_data)

@printf("\nMSE (noisy):          %.4e\n", mse_noisy)
@printf("MSE (Wiener):         %.4e\n", mse_wiener)

# -----------------------------------------------------------------------------
# 6. Save Results (optional)
# -----------------------------------------------------------------------------

println("\n" * "-" ^ 50)
println("Saving results...")

# Create output directory
output_dir = "results"
mkpath(output_dir)

# Save results as NPY (if NPZ.jl available) or JLD2
try
    using JLD2
    
    results_file = joinpath(output_dir, "denoising_results.jld2")
    @save results_file clean_data noisy_data wiener_data recovered_data
    println("Results saved to: $results_file")
catch e
    # Fallback: save as delimited text
    results_file = joinpath(output_dir, "denoising_results.csv")
    # Just save a summary
    println("JLD2 not available. Skipping file save.")
end

println("\nExample completed successfully.")
