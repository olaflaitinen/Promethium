# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Synthetic data generation utilities for demonstrations and testing.
"""

import numpy as np
from typing import Optional, Tuple


def generate_synthetic_traces(
    n_traces: int = 100,
    n_samples: int = 1000,
    sample_rate: float = 250.0,
    frequencies: Optional[list] = None,
    seed: Optional[int] = None,
) -> Tuple[np.ndarray, dict]:
    """
    Generate synthetic seismic traces with realistic waveform characteristics.
    
    Creates traces containing superimposed sinusoidal signals with exponential
    decay envelopes, simulating simple seismic reflections.
    
    Args:
        n_traces: Number of traces to generate.
        n_samples: Number of samples per trace.
        sample_rate: Sampling rate in Hz.
        frequencies: List of frequencies (Hz) to include. Default [5, 15, 25].
        seed: Random seed for reproducibility.
        
    Returns:
        Tuple of (traces array, metadata dict)
        
    Example:
        >>> from promethium.utils import generate_synthetic_traces
        >>> traces, meta = generate_synthetic_traces(n_traces=50, n_samples=500)
        >>> print(f"Generated {traces.shape[0]} traces with {traces.shape[1]} samples")
    """
    if seed is not None:
        np.random.seed(seed)
        
    if frequencies is None:
        frequencies = [5.0, 15.0, 25.0]
        
    dt = 1.0 / sample_rate
    t = np.arange(n_samples) * dt
    
    traces = np.zeros((n_traces, n_samples), dtype=np.float32)
    
    for i in range(n_traces):
        trace = np.zeros(n_samples)
        
        for freq in frequencies:
            # Random amplitude and phase
            amplitude = np.random.uniform(0.5, 1.5)
            phase = np.random.uniform(0, 2 * np.pi)
            
            # Create wavelet with exponential decay
            decay_rate = np.random.uniform(0.5, 2.0)
            envelope = np.exp(-decay_rate * t)
            
            # Add sinusoidal component
            trace += amplitude * envelope * np.sin(2 * np.pi * freq * t + phase)
            
        # Normalize
        max_val = np.max(np.abs(trace))
        if max_val > 0:
            trace = trace / max_val
            
        traces[i] = trace
        
    metadata = {
        "n_traces": n_traces,
        "n_samples": n_samples,
        "sample_rate": sample_rate,
        "dt": dt,
        "duration": n_samples * dt,
        "frequencies": frequencies,
    }
    
    return traces, metadata


def add_noise(
    data: np.ndarray,
    noise_level: float = 0.1,
    noise_type: str = "gaussian",
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Add noise to seismic data.
    
    Args:
        data: Input data array.
        noise_level: Standard deviation of noise relative to signal amplitude.
        noise_type: Type of noise - 'gaussian', 'uniform', or 'impulse'.
        seed: Random seed for reproducibility.
        
    Returns:
        Noisy data array.
        
    Example:
        >>> from promethium.utils import generate_synthetic_traces, add_noise
        >>> traces, _ = generate_synthetic_traces()
        >>> noisy = add_noise(traces, noise_level=0.2)
    """
    if seed is not None:
        np.random.seed(seed)
        
    signal_std = np.std(data)
    noise_std = noise_level * signal_std
    
    if noise_type == "gaussian":
        noise = np.random.normal(0, noise_std, data.shape)
    elif noise_type == "uniform":
        noise = np.random.uniform(-noise_std * np.sqrt(3), noise_std * np.sqrt(3), data.shape)
    elif noise_type == "impulse":
        noise = np.zeros_like(data)
        mask = np.random.random(data.shape) < 0.01
        noise[mask] = np.random.choice([-1, 1], size=np.sum(mask)) * noise_std * 5
    else:
        raise ValueError(f"Unknown noise type: {noise_type}")
        
    return data + noise.astype(data.dtype)


def create_missing_traces(
    data: np.ndarray,
    missing_ratio: float = 0.3,
    pattern: str = "random",
    seed: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a dataset with missing traces for reconstruction experiments.
    
    Args:
        data: Input data array of shape (n_traces, n_samples).
        missing_ratio: Fraction of traces to remove (0 to 1).
        pattern: Missing pattern - 'random', 'regular', or 'block'.
        seed: Random seed for reproducibility.
        
    Returns:
        Tuple of (corrupted data, mask array where 1=present, 0=missing)
        
    Example:
        >>> from promethium.utils import generate_synthetic_traces, create_missing_traces
        >>> traces, _ = generate_synthetic_traces()
        >>> corrupted, mask = create_missing_traces(traces, missing_ratio=0.3)
    """
    if seed is not None:
        np.random.seed(seed)
        
    n_traces = data.shape[0]
    n_missing = int(n_traces * missing_ratio)
    
    mask = np.ones(n_traces, dtype=np.float32)
    
    if pattern == "random":
        missing_idx = np.random.choice(n_traces, n_missing, replace=False)
        mask[missing_idx] = 0
    elif pattern == "regular":
        step = max(1, n_traces // n_missing)
        missing_idx = np.arange(0, n_traces, step)[:n_missing]
        mask[missing_idx] = 0
    elif pattern == "block":
        start = np.random.randint(0, n_traces - n_missing)
        mask[start:start + n_missing] = 0
    else:
        raise ValueError(f"Unknown pattern: {pattern}")
        
    corrupted = data.copy()
    corrupted[mask == 0] = 0
    
    return corrupted, mask
