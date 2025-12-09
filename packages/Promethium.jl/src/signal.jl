"""
Signal processing functions for seismic data.

Provides Wiener filter, bandpass filter, and DC offset removal.
"""

# ============== Wiener Filter ==============

"""
    wiener_filter(signal::AbstractVector; noise_var=nothing) -> Vector

Apply frequency-domain Wiener filter to signal.

# Arguments
- `signal`: Input 1D signal
- `noise_var`: Noise variance estimate (auto-estimated if nothing)

# Returns
- Filtered signal
"""
function wiener_filter(signal::AbstractVector{T}; noise_var=nothing) where {T<:Real}
    n = length(signal)
    
    # FFT
    Y = fft(signal)
    Py = abs2.(Y) ./ n
    
    # Estimate noise PSD
    Pn = if isnothing(noise_var)
        tail_start = div(n, 2)
        fill(mean(Py[tail_start:end]), n)
    else
        fill(noise_var, n)
    end
    
    # Wiener filter
    Ps = max.(Py .- Pn, 0.0)
    H = (Ps .+ EPSILON) ./ (Ps .+ Pn .+ EPSILON)
    
    # Apply filter
    Y_filtered = Y .* H
    
    # Inverse FFT
    real.(ifft(Y_filtered))
end

"""
    wiener_filter(ds::SeismicDataset; noise_var=nothing) -> SeismicDataset

Apply Wiener filter to all traces in dataset.
"""
function wiener_filter(ds::SeismicDataset; noise_var=nothing)
    result = similar(ds.traces)
    
    for i in 1:n_traces(ds)
        result[i, :] = wiener_filter(ds.traces[i, :]; noise_var=noise_var)
    end
    
    SeismicDataset(result, ds.dt; coords=ds.coords, metadata=ds.metadata)
end


# ============== Bandpass Filter ==============

"""
    bandpass_filter(signal::AbstractVector, dt, low_freq, high_freq; taper_width=5.0)

Apply frequency-domain bandpass filter.

# Arguments
- `signal`: Input signal
- `dt`: Sampling interval
- `low_freq`: Low cutoff frequency (Hz)
- `high_freq`: High cutoff frequency (Hz)
- `taper_width`: Cosine taper width in Hz

# Returns
- Filtered signal
"""
function bandpass_filter(
    signal::AbstractVector{T},
    dt::Real,
    low_freq::Real,
    high_freq::Real;
    taper_width::Real = 5.0
) where {T<:Real}
    
    n = length(signal)
    X = fft(signal)
    df = 1.0 / (n * dt)
    
    # Create bandpass mask with cosine taper
    mask = zeros(Float64, n)
    
    for i in 1:n
        freq = i <= div(n, 2) + 1 ? (i - 1) * df : (i - 1 - n) * df
        abs_freq = abs(freq)
        
        if low_freq <= abs_freq <= high_freq
            mask[i] = 1.0
        elseif low_freq - taper_width < abs_freq < low_freq
            mask[i] = 0.5 * (1 + cos(pi * (low_freq - abs_freq) / taper_width))
        elseif high_freq < abs_freq < high_freq + taper_width
            mask[i] = 0.5 * (1 + cos(pi * (abs_freq - high_freq) / taper_width))
        end
    end
    
    X_filtered = X .* mask
    real.(ifft(X_filtered))
end

"""
    bandpass_filter(ds::SeismicDataset, low_freq, high_freq) -> SeismicDataset

Apply bandpass filter to all traces.
"""
function bandpass_filter(ds::SeismicDataset, low_freq::Real, high_freq::Real)
    result = similar(ds.traces)
    
    for i in 1:n_traces(ds)
        result[i, :] = bandpass_filter(ds.traces[i, :], ds.dt, low_freq, high_freq)
    end
    
    SeismicDataset(result, ds.dt; coords=ds.coords, metadata=ds.metadata)
end


# ============== Remove DC Offset ==============

"""
    remove_dc(signal::AbstractVector) -> Vector

Remove DC offset (mean) from signal.
"""
remove_dc(signal::AbstractVector) = signal .- mean(signal)

"""
    remove_dc(ds::SeismicDataset) -> SeismicDataset

Remove DC offset from all traces.
"""
function remove_dc(ds::SeismicDataset)
    result = similar(ds.traces)
    
    for i in 1:n_traces(ds)
        result[i, :] = remove_dc(ds.traces[i, :])
    end
    
    SeismicDataset(result, ds.dt; coords=ds.coords, metadata=ds.metadata)
end
