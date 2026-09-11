# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Reconstruction Quality Metrics

Comprehensive evaluation metrics for seismic data reconstruction quality.
All functions accept numpy arrays or PyTorch tensors as input.
"""

import numpy as np
import torch
import torch.nn.functional as F
from typing import Union, Dict, Any, Optional
from scipy import signal as scipy_signal
from scipy.fft import fft, fftfreq


ArrayLike = Union[np.ndarray, torch.Tensor]


def _to_numpy(arr: ArrayLike) -> np.ndarray:
    """Convert input to numpy array."""
    if isinstance(arr, torch.Tensor):
        return arr.detach().cpu().numpy()
    return np.asarray(arr)


def _to_tensor(arr: ArrayLike) -> torch.Tensor:
    """Convert input to PyTorch tensor."""
    if isinstance(arr, np.ndarray):
        return torch.from_numpy(arr).float()
    return arr.float()


def signal_to_noise_ratio(
    original: ArrayLike,
    reconstructed: ArrayLike,
) -> float:
    """
    Compute Signal-to-Noise Ratio (SNR) in decibels.
    
    SNR = 10 * log10(signal_power / noise_power)
    
    where noise = original - reconstructed
    
    Args:
        original: Original (reference) signal.
        reconstructed: Reconstructed signal.
        
    Returns:
        SNR value in dB. Higher values indicate better reconstruction.
        
    Example:
        >>> snr = signal_to_noise_ratio(clean_data, reconstructed_data)
        >>> print(f"SNR: {snr:.2f} dB")
    """
    original = _to_numpy(original).astype(np.float64)
    reconstructed = _to_numpy(reconstructed).astype(np.float64)
    
    noise = original - reconstructed
    signal_power = np.mean(original ** 2)
    noise_power = np.mean(noise ** 2)
    
    if noise_power < 1e-10:
        return float('inf')
        
    snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
    return float(snr)


def mean_squared_error(
    original: ArrayLike,
    reconstructed: ArrayLike,
) -> float:
    """
    Compute Mean Squared Error (MSE).
    
    MSE = mean((original - reconstructed)^2)
    
    Args:
        original: Original (reference) signal.
        reconstructed: Reconstructed signal.
        
    Returns:
        MSE value. Lower values indicate better reconstruction.
        
    Example:
        >>> mse = mean_squared_error(clean_data, reconstructed_data)
        >>> print(f"MSE: {mse:.6f}")
    """
    original = _to_numpy(original).astype(np.float64)
    reconstructed = _to_numpy(reconstructed).astype(np.float64)
    
    mse = np.mean((original - reconstructed) ** 2)
    return float(mse)


def peak_signal_to_noise_ratio(
    original: ArrayLike,
    reconstructed: ArrayLike,
    data_range: Optional[float] = None,
) -> float:
    """
    Compute Peak Signal-to-Noise Ratio (PSNR) in decibels.
    
    PSNR = 10 * log10(max_value^2 / MSE)
    
    Args:
        original: Original (reference) signal.
        reconstructed: Reconstructed signal.
        data_range: Dynamic range of the data. If None, computed from original.
        
    Returns:
        PSNR value in dB. Higher values indicate better reconstruction.
        
    Example:
        >>> psnr = peak_signal_to_noise_ratio(clean_data, reconstructed_data)
        >>> print(f"PSNR: {psnr:.2f} dB")
    """
    original = _to_numpy(original).astype(np.float64)
    reconstructed = _to_numpy(reconstructed).astype(np.float64)
    
    mse = np.mean((original - reconstructed) ** 2)
    
    if mse < 1e-10:
        return float('inf')
        
    if data_range is None:
        data_range = np.max(original) - np.min(original)
        
    psnr = 10 * np.log10((data_range ** 2) / (mse + 1e-10))
    return float(psnr)


def structural_similarity_index(
    original: ArrayLike,
    reconstructed: ArrayLike,
    win_size: int = 7,
    data_range: Optional[float] = None,
) -> float:
    """
    Compute Structural Similarity Index (SSIM).
    
    SSIM measures perceptual similarity between two signals based on
    luminance, contrast, and structure comparisons.
    
    Args:
        original: Original (reference) signal. Should be 2D.
        reconstructed: Reconstructed signal. Should be 2D.
        win_size: Size of the sliding window for local SSIM computation.
        data_range: Dynamic range of the data. If None, computed from original.
        
    Returns:
        SSIM value in range [-1, 1]. Higher values indicate better similarity.
        
    Example:
        >>> ssim = structural_similarity_index(clean_data, reconstructed_data)
        >>> print(f"SSIM: {ssim:.4f}")
    """
    original = _to_tensor(original)
    reconstructed = _to_tensor(reconstructed)
    
    # Ensure 4D tensor (B, C, H, W)
    while original.ndim < 4:
        original = original.unsqueeze(0)
    while reconstructed.ndim < 4:
        reconstructed = reconstructed.unsqueeze(0)
        
    if data_range is None:
        data_range = float(torch.max(original) - torch.min(original))
        
    # SSIM constants
    C1 = (0.01 * data_range) ** 2
    C2 = (0.03 * data_range) ** 2
    
    # Use average pooling to compute local means
    kernel_size = min(win_size, original.shape[-1], original.shape[-2])
    if kernel_size < 3:
        kernel_size = 3
        
    padding = kernel_size // 2
    
    mu_x = F.avg_pool2d(reconstructed, kernel_size, stride=1, padding=padding)
    mu_y = F.avg_pool2d(original, kernel_size, stride=1, padding=padding)
    
    mu_x_sq = mu_x ** 2
    mu_y_sq = mu_y ** 2
    mu_xy = mu_x * mu_y
    
    sigma_x_sq = F.avg_pool2d(reconstructed ** 2, kernel_size, stride=1, padding=padding) - mu_x_sq
    sigma_y_sq = F.avg_pool2d(original ** 2, kernel_size, stride=1, padding=padding) - mu_y_sq
    sigma_xy = F.avg_pool2d(reconstructed * original, kernel_size, stride=1, padding=padding) - mu_xy
    
    ssim_map = ((2 * mu_xy + C1) * (2 * sigma_xy + C2)) / (
        (mu_x_sq + mu_y_sq + C1) * (sigma_x_sq + sigma_y_sq + C2)
    )
    
    return float(ssim_map.mean().item())


def frequency_domain_correlation(
    original: ArrayLike,
    reconstructed: ArrayLike,
    sample_rate: float = 1.0,
) -> float:
    """
    Compute correlation in the frequency domain.
    
    Measures how well the frequency content of the reconstructed signal
    matches the original.
    
    Args:
        original: Original (reference) signal.
        reconstructed: Reconstructed signal.
        sample_rate: Sampling rate of the signals (Hz).
        
    Returns:
        Correlation coefficient in range [-1, 1]. Higher values indicate
        better frequency content match.
        
    Example:
        >>> freq_corr = frequency_domain_correlation(clean_data, reconstructed_data, sample_rate=250.0)
        >>> print(f"Frequency Correlation: {freq_corr:.4f}")
    """
    original = _to_numpy(original).flatten().astype(np.float64)
    reconstructed = _to_numpy(reconstructed).flatten().astype(np.float64)
    
    # Compute amplitude spectra
    orig_fft = np.abs(fft(original))
    recon_fft = np.abs(fft(reconstructed))
    
    # Use only positive frequencies
    n = len(orig_fft) // 2
    orig_spectrum = orig_fft[:n]
    recon_spectrum = recon_fft[:n]
    
    # Compute correlation
    correlation = np.corrcoef(orig_spectrum, recon_spectrum)[0, 1]
    
    if np.isnan(correlation):
        return 0.0
        
    return float(correlation)


def phase_coherence(
    original: ArrayLike,
    reconstructed: ArrayLike,
) -> float:
    """
    Compute phase coherence between original and reconstructed signals.
    
    Measures how well the phase information is preserved in the reconstruction.
    
    Args:
        original: Original (reference) signal.
        reconstructed: Reconstructed signal.
        
    Returns:
        Phase coherence value in range [0, 1]. Higher values indicate
        better phase preservation.
        
    Example:
        >>> coherence = phase_coherence(clean_data, reconstructed_data)
        >>> print(f"Phase Coherence: {coherence:.4f}")
    """
    original = _to_numpy(original).flatten().astype(np.float64)
    reconstructed = _to_numpy(reconstructed).flatten().astype(np.float64)
    
    # Compute phase angles
    orig_fft = fft(original)
    recon_fft = fft(reconstructed)
    
    orig_phase = np.angle(orig_fft)
    recon_phase = np.angle(recon_fft)
    
    # Compute phase difference
    phase_diff = orig_phase - recon_phase
    
    # Wrap to [-pi, pi]
    phase_diff = np.angle(np.exp(1j * phase_diff))
    
    # Coherence as mean cosine of phase difference
    coherence = np.mean(np.cos(phase_diff))
    
    # Normalize to [0, 1]
    coherence = (coherence + 1) / 2
    
    return float(coherence)


def evaluate_reconstruction(
    original: ArrayLike,
    reconstructed: ArrayLike,
    sample_rate: float = 1.0,
    data_range: Optional[float] = None,
) -> Dict[str, float]:
    """
    Compute all reconstruction quality metrics at once.
    
    Convenience function that returns a dictionary with all available metrics.
    
    Args:
        original: Original (reference) signal.
        reconstructed: Reconstructed signal.
        sample_rate: Sampling rate of the signals (Hz).
        data_range: Dynamic range of the data. If None, computed from original.
        
    Returns:
        Dictionary containing all metrics:
            - snr: Signal-to-Noise Ratio (dB)
            - mse: Mean Squared Error
            - psnr: Peak Signal-to-Noise Ratio (dB)
            - ssim: Structural Similarity Index
            - freq_correlation: Frequency Domain Correlation
            - phase_coherence: Phase Coherence
            
    Example:
        >>> metrics = evaluate_reconstruction(clean_data, reconstructed_data)
        >>> for name, value in metrics.items():
        ...     print(f"{name}: {value:.4f}")
    """
    metrics = {
        "snr": signal_to_noise_ratio(original, reconstructed),
        "mse": mean_squared_error(original, reconstructed),
        "psnr": peak_signal_to_noise_ratio(original, reconstructed, data_range),
        "ssim": structural_similarity_index(original, reconstructed, data_range=data_range),
        "freq_correlation": frequency_domain_correlation(original, reconstructed, sample_rate),
        "phase_coherence": phase_coherence(original, reconstructed),
    }
    
    return metrics
