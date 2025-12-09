using Test
using Promethium
using LinearAlgebra
using Statistics

@testset "Promethium.jl" begin
    
    # ============== Core Types Tests ==============
    @testset "SeismicDataset" begin
        traces = randn(10, 100)
        ds = SeismicDataset(traces, 0.004)
        
        @test n_traces(ds) == 10
        @test n_samples(ds) == 100
        @test ds.dt == 0.004
        @test duration(ds) ≈ 0.396 atol=0.001
        
        # Time axis
        t = time_axis(ds)
        @test length(t) == 100
        @test t[1] == 0.0
        @test t[2] ≈ 0.004
    end
    
    @testset "SeismicDataset normalization" begin
        traces = randn(10, 100) .* 10
        ds = SeismicDataset(traces, 0.004)
        
        ds_norm = normalize(ds, :rms)
        for i in 1:n_traces(ds_norm)
            rms = sqrt(mean(ds_norm.traces[i, :] .^ 2))
            @test rms ≈ 1.0 atol=0.01
        end
    end
    
    @testset "SeismicDataset subsetting" begin
        ds = synthetic_data(ntraces=50, nsamples=200, seed=42)
        
        subset = subset_traces(ds, [1, 5, 10])
        @test n_traces(subset) == 3
        
        windowed = time_window(ds, 0.1, 0.3)
        @test n_samples(windowed) < n_samples(ds)
    end
    
    @testset "VelocityModel" begin
        vm = constant_velocity(1500.0, 100, 50, 10.0, 5.0)
        
        @test nx(vm) == 100
        @test nz(vm) == 50
        @test minimum(vm.velocities) == 1500.0
        @test maximum(vm.velocities) == 1500.0
        
        # Interpolation
        v = interpolate_at(vm, 50.0, 25.0)
        @test v ≈ 1500.0
    end
    
    @testset "VelocityModel linear gradient" begin
        vm = linear_velocity(1500.0, 0.5, 100, 50, 10.0, 5.0)
        
        @test vm.velocities[1, 1] ≈ 1500.0
        @test vm.velocities[end, 1] > vm.velocities[1, 1]
    end
    
    # ============== Metrics Tests ==============
    @testset "Metrics - SNR" begin
        ref = SeismicDataset(randn(10, 10), 0.004)
        est = SeismicDataset(copy(ref.traces), 0.004)
        
        snr = compute_snr(ref, est)
        @test snr > 100.0  # Should be very high for identical signals
    end
    
    @testset "Metrics - MSE" begin
        ref = SeismicDataset(randn(10, 10), 0.004)
        noise = randn(10, 10) * 0.1
        est = SeismicDataset(ref.traces + noise, 0.004)
        
        mse = compute_mse(ref, est)
        @test mse >= 0.0
    end
    
    @testset "Metrics - SSIM" begin
        ref = SeismicDataset(randn(10, 10), 0.004)
        noise = randn(10, 10) * 0.1
        est = SeismicDataset(ref.traces + noise, 0.004)
        
        ssim = compute_ssim(ref, est)
        @test -1.0 <= ssim <= 1.0
    end
    
    @testset "Metrics - evaluate" begin
        ref = SeismicDataset(randn(10, 10), 0.004)
        noise = randn(10, 10) * 0.1
        est = SeismicDataset(ref.traces + noise, 0.004)
        
        results = evaluate(ref, est)
        
        @test haskey(results, :snr)
        @test haskey(results, :mse)
        @test haskey(results, :psnr)
        @test haskey(results, :ssim)
    end
    
    # ============== Recovery Tests ==============
    @testset "Matrix completion ISTA" begin
        # Create low-rank matrix
        n = 20
        r = 3
        U = randn(n, r)
        V = randn(n, r)
        true_matrix = U * V'
        
        # Create mask (60% observed)
        mask = rand(n, n) .< 0.6
        observed = true_matrix .* mask
        
        completed = matrix_completion_ista(observed, mask; 
            lambda=0.1, max_iter=50)
        
        # Check relative error
        rel_error = norm(completed - true_matrix) / norm(true_matrix)
        @test rel_error < 0.5
    end
    
    @testset "Compressive sensing FISTA" begin
        n = 50
        m = 30
        
        # Sparse signal
        x_true = zeros(n)
        x_true[5] = 2.0
        x_true[15] = -1.5
        x_true[30] = 1.0
        
        A = randn(m, n)
        y = A * x_true + randn(m) * 0.01
        
        x_rec = compressive_sensing_fista(y, A; lambda=0.1, max_iter=100)
        
        # Check sparsity
        num_large = count(abs.(x_rec) .> 0.1)
        @test num_large <= 10
    end
    
    # ============== Signal Processing Tests ==============
    @testset "Wiener filter" begin
        n = 100
        clean = [sin(2π * i / 20) for i in 1:n]
        noisy = clean + randn(n) * 0.3
        
        denoised = wiener_filter(noisy)
        
        error_before = sum((noisy - clean).^2)
        error_after = sum((denoised - clean).^2)
        
        @test error_after < error_before
    end
    
    # ============== Pipeline Tests ==============
    @testset "Pipeline from preset" begin
        ds = synthetic_data(ntraces=20, nsamples=100, 
                           noise_level=0.1, seed=42)
        pipe = from_preset("wiener")
        
        result = run(pipe, ds)
        
        @test n_traces(result) == n_traces(ds)
        @test n_samples(result) == n_samples(ds)
    end
    
    @testset "Pipeline evaluation" begin
        truth = synthetic_data(ntraces=10, nsamples=50, 
                              noise_level=0.0, seed=42)
        noisy = SeismicDataset(
            truth.traces + randn(10, 50) * 0.1,
            0.004
        )
        
        pipe = from_preset("wiener")
        result = run(pipe, noisy)
        metrics = evaluate(truth, result)
        
        @test haskey(metrics, :snr)
        @test metrics[:snr] > 0.0
    end
    
    # ============== I/O Tests ==============
    @testset "Synthetic data generation" begin
        ds = synthetic_data(ntraces=50, nsamples=200, 
                           dt=0.002, seed=123)
        
        @test n_traces(ds) == 50
        @test n_samples(ds) == 200
        @test ds.dt == 0.002
        @test get(ds.metadata, "synthetic", false) == true
    end
    
end
