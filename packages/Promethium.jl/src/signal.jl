"""
Signal processing functions for Promethium.jl
"""

"""
    wiener_filter(y; noise_var=nothing) -> Vector

Apply frequency-domain Wiener filter for denoising.

# Arguments
- `y`: Noisy signal vector
- `noise_var`: Estimated noise variance (auto-estimated if nothing)

# Returns
Denoised signal
"""
function wiener_filter(y::AbstractVector; noise_var::Union{Nothing,Float64}=nothing)
    N = length(y)
    
    # FFT
    Y = fft(y)
    P_y = abs.(Y).^2 ./ N
    
    # Estimate noise PSD from high-frequency components
    if isnothing(noise_var)
        noise_var = median(P_y[div(N,2):end])
    end
    P_n = fill(noise_var, N)
    
    # Wiener filter transfer function
    P_s = max.(P_y .- P_n, 0.0)
    H = P_s ./ (P_s .+ P_n .+ 1e-10)
    
    # Apply filter and inverse transform
    S_hat = H .* Y
    s_hat = real.(ifft(S_hat))
    
    return s_hat
end

"""
    bandpass_filter(x, dt, low_freq, high_freq) -> Vector

Apply bandpass filter in frequency domain.
"""
function bandpass_filter(x::AbstractVector, dt::Float64, low_freq::Float64, high_freq::Float64)
    N = length(x)
    X = fft(x)
    
    # Frequency axis
    freqs = fftfreq(N, 1/dt)
    
    # Create bandpass mask
    mask = (abs.(freqs) .>= low_freq) .& (abs.(freqs) .<= high_freq)
    
    # Apply and inverse
    X_filtered = X .* mask
    return real.(ifft(X_filtered))
end

# Helper: generate frequency axis for FFT
function fftfreq(n::Int, d::Float64=1.0)
    val = 1.0 / (n * d)
    N = div(n - 1, 2) + 1
    p1 = collect(0:N-1)
    p2 = collect(-div(n, 2):-1)
    return vcat(p1, p2) .* val
end
