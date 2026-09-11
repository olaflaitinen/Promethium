# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import torch
import numpy as np
from typing import Dict, Any, Callable, List

class SeismicTransform:
    """Base class for seismic data augmentations."""
    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class Compose:
    """Composes several transforms together."""
    def __init__(self, transforms: List[Callable]):
        self.transforms = transforms

    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        for t in self.transforms:
            sample = t(sample)
        return sample

class ToTensor(SeismicTransform):
    """Convert numpy arrays to PyTorch tensors."""
    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        for key in ["input", "target"]:
            if key in sample and isinstance(sample[key], np.ndarray):
                # Ensure float32 for training
                sample[key] = torch.from_numpy(sample[key]).float()
        return sample

class Normalize(SeismicTransform):
    """
    Standardize data: (x - mean) / std.
    Can be Global or Per-Sample.
    SoTA approach for seismic: Trace-wise RMS normalization often preferred for amplitude preservation rel to events.
    """
    def __init__(self, mode: str = "std", mean: float = 0.0, std: float = 1.0):
        self.mode = mode
        self.mean = mean
        self.std = std

    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        data = sample["input"]
        
        if self.mode == "std":
            data = (data - self.mean) / (self.std + 1e-8)
        elif self.mode == "minmax":
            dmin, dmax = data.min(), data.max()
            data = (data - dmin) / (dmax - dmin + 1e-8)
        elif self.mode == "rms":
            rms = np.sqrt(np.mean(data**2))
            data = data / (rms + 1e-8)
            
        sample["input"] = data
        return sample

class RandomPolarityFlip(SeismicTransform):
    """Randomly invert the trace polarity."""
    def __init__(self, p: float = 0.5):
        self.p = p

    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        if np.random.rand() < self.p:
            sample["input"] = -sample["input"]
            if "target" in sample:
                sample["target"] = -sample["target"]
        return sample

class RandomGain(SeismicTransform):
    """Random amplitude scaling."""
    def __init__(self, factor_range: tuple = (0.5, 1.5)):
        self.low, self.high = factor_range

    def __call__(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        factor = np.random.uniform(self.low, self.high)
        sample["input"] *= factor
        # Gain usually applied to input only if target is "clean" ground truth
        # But if it's reconstruction, we might want to scale target too? 
        # Usually Gain is specific to Input Augmentation.
        return sample


# -----------------------------------------------------------------------------
# Signal Processing Functions
# -----------------------------------------------------------------------------

def fft(data: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Compute the Fast Fourier Transform of the input data.
    
    Args:
        data: Input array (1D or 2D)
        axis: Axis along which to compute FFT
        
    Returns:
        Complex FFT result
    """
    return np.fft.fft(data, axis=axis)


def ifft(data: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Compute the Inverse Fast Fourier Transform.
    
    Args:
        data: Complex FFT data
        axis: Axis along which to compute IFFT
        
    Returns:
        Real-valued reconstructed signal
    """
    return np.fft.ifft(data, axis=axis).real


def wavelet_transform(
    data: np.ndarray, 
    wavelet: str = 'morl',
    scales: np.ndarray = None,
    fs: float = 1.0
) -> np.ndarray:
    """
    Compute the Continuous Wavelet Transform.
    
    Args:
        data: Input 1D signal
        wavelet: Wavelet type ('morl', 'mexh', 'cmor', etc.)
        scales: Array of scales to use (default: automatic)
        fs: Sampling frequency
        
    Returns:
        2D array of wavelet coefficients (scales x time)
    """
    try:
        import pywt
        if scales is None:
            scales = np.arange(1, min(128, len(data) // 2))
        coeffs, freqs = pywt.cwt(data, scales, wavelet, sampling_period=1/fs)
        return coeffs
    except ImportError:
        # Fallback to simple STFT-like approach if pywt not available
        from scipy.signal import stft
        _, _, Zxx = stft(data, fs=fs, nperseg=min(256, len(data)))
        return np.abs(Zxx)

