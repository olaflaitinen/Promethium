"""
Generate cross-language test data for Promethium validation.

This script creates synthetic seismic data and reference outputs
that all language implementations use for consistency testing.
"""
import numpy as np
import json
import os
from pathlib import Path

# Ensure reproducibility
np.random.seed(42)

def generate_ricker_wavelet(t, f0=30):
    """Generate Ricker wavelet."""
    tau = t
    return (1 - 2 * (np.pi * f0 * tau)**2) * np.exp(-(np.pi * f0 * tau)**2)

def generate_synthetic_traces(n_traces=100, n_samples=500, dt=0.004, noise_level=0.1):
    """Generate synthetic seismic traces."""
    t = np.arange(n_samples) * dt
    traces = np.zeros((n_traces, n_samples))
    
    for i in range(n_traces):
        n_events = np.random.randint(3, 8)
        event_times = np.sort(np.random.uniform(0.1, t[-1] - 0.1, n_events))
        event_amps = np.random.uniform(0.5, 1.5, n_events) * np.random.choice([-1, 1], n_events)
        
        for te, ae in zip(event_times, event_amps):
            wavelet = generate_ricker_wavelet(t - te)
            traces[i] += ae * wavelet
    
    # Add noise
    if noise_level > 0:
        signal_rms = np.sqrt(np.mean(traces**2))
        noise = np.random.randn(n_traces, n_samples)
        traces += noise_level * signal_rms * noise
    
    return traces, t

def compute_snr(reference, estimate):
    """Compute SNR in dB."""
    signal_power = np.mean(reference**2)
    noise_power = np.mean((reference - estimate)**2)
    return 10 * np.log10(signal_power / (noise_power + 1e-10))

def compute_mse(reference, estimate):
    """Compute MSE."""
    return np.mean((reference - estimate)**2)

def main():
    output_dir = Path(__file__).parent.parent / "testdata"
    output_dir.mkdir(exist_ok=True)
    
    print("Generating synthetic test data...")
    
    # Generate clean and noisy data
    clean_traces, t = generate_synthetic_traces(100, 500, 0.004, noise_level=0.0)
    noisy_traces, _ = generate_synthetic_traces(100, 500, 0.004, noise_level=0.2)
    
    # Compute metrics
    snr = compute_snr(clean_traces, noisy_traces)
    mse = compute_mse(clean_traces, noisy_traces)
    
    print(f"  SNR: {snr:.2f} dB")
    print(f"  MSE: {mse:.6f}")
    
    # Save as numpy
    np.save(output_dir / "clean_traces.npy", clean_traces)
    np.save(output_dir / "noisy_traces.npy", noisy_traces)
    np.save(output_dir / "time_axis.npy", t)
    
    # Generate low-rank matrix for completion test
    print("Generating matrix completion test data...")
    n = 50
    r = 5  # Rank
    U = np.random.randn(n, r)
    V = np.random.randn(n, r)
    full_matrix = U @ V.T
    
    # Create mask (60% observed)
    mask = np.random.rand(n, n) < 0.6
    observed = full_matrix.copy()
    observed[~mask] = np.nan
    
    np.save(output_dir / "full_matrix.npy", full_matrix)
    np.save(output_dir / "observed_matrix.npy", observed)
    np.save(output_dir / "mask.npy", mask)
    
    # Update expected values
    expected = {
        "version": "1.0.4",
        "generated": "2025-12-09",
        "clean_noisy_snr_db": float(snr),
        "clean_noisy_mse": float(mse),
        "matrix_rank": int(r),
        "matrix_size": int(n),
        "observation_ratio": float(np.mean(mask))
    }
    
    with open(output_dir / "expected.json", "w") as f:
        json.dump(expected, f, indent=2)
    
    print(f"Test data saved to {output_dir}")
    print("Done!")

if __name__ == "__main__":
    main()
