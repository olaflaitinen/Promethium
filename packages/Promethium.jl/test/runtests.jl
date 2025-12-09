using Test
using Promethium

@testset "Promethium.jl Tests" begin
    
    @testset "SeismicDataset" begin
        traces = randn(10, 100)
        ds = SeismicDataset(traces, 0.004)
        
        @test n_traces(ds) == 10
        @test n_samples(ds) == 100
        @test ds.dt == 0.004
        
        # Test normalization
        ds_norm = normalize(ds; method=:rms)
        rms = sqrt.(mean(ds_norm.traces.^2, dims=2))
        @test all(abs.(rms .- 1.0) .< 0.01)
    end
    
    @testset "Metrics" begin
        reference = randn(10, 10)
        estimate = copy(reference)
        
        # Perfect reconstruction
        @test compute_snr(reference, estimate) > 100
        @test compute_mse(reference, estimate) < 1e-20
        @test compute_psnr(reference, estimate) > 100
        
        # With noise
        estimate_noisy = reference .+ 0.1 .* randn(10, 10)
        @test compute_snr(reference, estimate_noisy) > 5
        @test compute_snr(reference, estimate_noisy) < 30
        @test compute_mse(reference, estimate_noisy) > 0
    end
    
    @testset "Matrix Completion (ISTA)" begin
        # Create low-rank matrix
        n = 20
        r = 3
        U = randn(n, r)
        V = randn(n, r)
        true_matrix = U * V'
        
        # Create mask (50% observed)
        mask = rand(n, n) .> 0.5
        
        # Observed matrix
        M = copy(true_matrix)
        M[.!mask] .= 0.0
        
        # Complete
        completed = matrix_completion_ista(M, mask; λ=0.1, max_iter=50)
        
        # Check relative error
        rel_error = norm(completed - true_matrix) / norm(true_matrix)
        @test rel_error < 0.5
    end
    
    @testset "Wiener Filter" begin
        # Clean signal
        n = 100
        clean = sin.(range(0, 4π, length=n))
        
        # Add noise
        noisy = clean .+ 0.3 .* randn(n)
        
        # Apply filter
        denoised = wiener_filter(noisy)
        
        # Should reduce error
        error_before = mean((noisy .- clean).^2)
        error_after = mean((denoised .- clean).^2)
        @test error_after < error_before
    end
    
    @testset "Compressive Sensing (FISTA)" begin
        # Sparse signal
        n = 50
        x_true = zeros(n)
        x_true[5] = 2.0
        x_true[15] = -1.5
        x_true[30] = 1.0
        
        # Measurement
        m = 30
        A = randn(m, n)
        y = A * x_true .+ 0.01 .* randn(m)
        
        # Recover
        x_recovered = compressive_sensing_fista(y, A; λ=0.1, max_iter=100)
        
        # Check sparsity
        @test sum(abs.(x_recovered) .> 0.1) <= 10
    end
    
    @testset "Synthetic Data Generation" begin
        ds = synthetic_data(n_traces=50, n_samples=200, seed=42)
        
        @test n_traces(ds) == 50
        @test n_samples(ds) == 200
        @test ds.metadata["synthetic"] == true
    end
end

println("All tests passed!")
