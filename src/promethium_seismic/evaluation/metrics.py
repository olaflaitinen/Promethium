# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Reconstruction Quality Metrics

Comprehensive evaluation metrics for seismic data reconstruction quality.
All functions accept numpy arrays or PyTorch tensors as input.
"""

import numpy as np
from typing import Any, Dict, Optional, Union
from scipy import signal as scipy_signal
from scipy.fft import fft, fftfreq
from scipy.ndimage import uniform_filter


# A torch.Tensor is accepted wherever an array is, but torch is deliberately
# not imported to say so. Every metric here is numpy arithmetic, and naming
# the type in an annotation would make the whole module depend on a two and a
# half gigabyte package for documentation.
ArrayLike = Union[np.ndarray, Any]


def _to_numpy(arr: ArrayLike) -> np.ndarray:
    """Convert any array like input to a numpy array.

    Args:
        arr: A numpy array, a torch tensor, or anything numpy can take.

    Returns:
        The data as a numpy array, detached from any autograd graph and
        moved off the device if it was on one.

    Torch tensors are recognised by their interface rather than by their
    type, so this works whether or not torch is installed.
    """
    if hasattr(arr, "detach") and hasattr(arr, "cpu"):
        return arr.detach().cpu().numpy()
    return np.asarray(arr)


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
    original = _to_numpy(original).astype(np.float64)
    reconstructed = _to_numpy(reconstructed).astype(np.float64)

    if original.shape != reconstructed.shape:
        raise ValueError(
            f"shape mismatch: original is {original.shape} and "
            f"reconstructed is {reconstructed.shape}"
        )

    # Collapse any leading singleton axes so that a (1, 1, H, W) tensor and an
    # (H, W) array are treated the same way.
    original = np.squeeze(original)
    reconstructed = np.squeeze(reconstructed)

    if data_range is None:
        data_range = float(original.max() - original.min())
    if data_range == 0.0:
        # A constant reference. The images are either identical or not, and
        # the ratio below is undefined, so answer the question directly.
        return 1.0 if np.array_equal(original, reconstructed) else 0.0

    C1 = (0.01 * data_range) ** 2
    C2 = (0.03 * data_range) ** 2

    # The window must fit inside the data and must be odd, so that the
    # invalid border is the same width on both sides.
    kernel_size = int(min(win_size, *original.shape))
    if kernel_size % 2 == 0:
        kernel_size -= 1
    kernel_size = max(kernel_size, 3)

    filter_args = {"size": kernel_size, "mode": "reflect"}

    mu_x = uniform_filter(reconstructed, **filter_args)
    mu_y = uniform_filter(original, **filter_args)

    mu_x_sq = mu_x * mu_x
    mu_y_sq = mu_y * mu_y
    mu_xy = mu_x * mu_y

    # The unbiased sample covariance, which is what the reference
    # implementations use. Without the correction the variance terms are low
    # by a factor of (n - 1) / n and SSIM reads slightly high.
    count = kernel_size ** original.ndim
    bias = count / (count - 1)

    sigma_x_sq = bias * (uniform_filter(reconstructed * reconstructed, **filter_args) - mu_x_sq)
    sigma_y_sq = bias * (uniform_filter(original * original, **filter_args) - mu_y_sq)
    sigma_xy = bias * (uniform_filter(reconstructed * original, **filter_args) - mu_xy)

    ssim_map = ((2 * mu_xy + C1) * (2 * sigma_xy + C2)) / (
        (mu_x_sq + mu_y_sq + C1) * (sigma_x_sq + sigma_y_sq + C2)
    )

    # Crop the border where the window ran off the edge. The previous
    # implementation zero padded instead, which computes the local mean near
    # the edge as though the data continued as silence and biases the score
    # downwards on any gather with live amplitudes at its boundary.
    pad = (kernel_size - 1) // 2
    if pad > 0 and all(dim > 2 * pad for dim in ssim_map.shape):
        interior = tuple(slice(pad, -pad) for _ in ssim_map.shape)
        ssim_map = ssim_map[interior]

    return float(ssim_map.mean())


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
