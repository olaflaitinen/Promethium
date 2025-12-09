# Promethium - Advanced Seismic Data Recovery and Reconstruction Framework
# Main package initialization

"""
Promethium is a state-of-the-art, AI-driven framework for seismic signal 
reconstruction, denoising, and geophysical data enhancement.

Distribution Name: promethium-seismic
Import Namespace: promethium
Version: 1.0.0

Installation:
    pip install promethium-seismic==1.0.2

Quick Start:
    >>> import promethium
    >>> from promethium import load_segy, SeismicRecoveryPipeline
    >>> 
    >>> # Load seismic data
    >>> data = load_segy("survey.sgy")
    >>> 
    >>> # Create and run reconstruction pipeline
    >>> pipeline = SeismicRecoveryPipeline.from_preset("unet_denoise_v1")
    >>> result = pipeline.run(data)
    >>> 
    >>> # Evaluate reconstruction quality
    >>> metrics = promethium.evaluate_reconstruction(data, result)
    >>> print(metrics)

Copyright (c) 2025 Olaf Yunus Laitinen Imanov
Licensed under CC BY-NC 4.0
"""

__version__ = "1.0.2"
__author__ = "Olaf Yunus Laitinen Imanov"
__license__ = "CC BY-NC 4.0"

# -----------------------------------------------------------------------------
# Core utilities
# -----------------------------------------------------------------------------
from promethium.core.config import settings, get_settings
from promethium.core.logging import get_logger

# -----------------------------------------------------------------------------
# I/O functions - reading and writing seismic data formats
# -----------------------------------------------------------------------------
from promethium.io import read_segy, write_segy

# Aliases for consistency with common naming conventions
load_segy = read_segy


def load_miniseed(path: str, **kwargs):
    """
    Load seismic data from miniSEED format.
    
    Args:
        path: Path to miniSEED file.
        **kwargs: Additional arguments passed to obspy.read.
        
    Returns:
        xarray.DataArray with seismic data.
    """
    from obspy import read as obspy_read
    import numpy as np
    import xarray as xr
    
    stream = obspy_read(path, **kwargs)
    
    # Convert to numpy array
    traces = []
    for tr in stream:
        traces.append(tr.data)
    
    data = np.array(traces, dtype=np.float32)
    
    # Get timing info from first trace
    sample_rate = stream[0].stats.sampling_rate
    n_samples = data.shape[1] if data.ndim > 1 else len(data)
    times = np.arange(n_samples) / sample_rate
    
    return xr.DataArray(
        data,
        dims=("trace", "time"),
        coords={"trace": np.arange(len(traces)), "time": times},
        attrs={"sample_rate": sample_rate, "format": "miniseed"},
    )


def load_sac(path: str, **kwargs):
    """
    Load seismic data from SAC format.
    
    Args:
        path: Path to SAC file.
        **kwargs: Additional arguments passed to obspy.read.
        
    Returns:
        xarray.DataArray with seismic data.
    """
    from obspy import read as obspy_read
    import numpy as np
    import xarray as xr
    
    stream = obspy_read(path, format="SAC", **kwargs)
    
    traces = []
    for tr in stream:
        traces.append(tr.data)
    
    data = np.array(traces, dtype=np.float32)
    
    sample_rate = stream[0].stats.sampling_rate
    n_samples = data.shape[1] if data.ndim > 1 else len(data)
    times = np.arange(n_samples) / sample_rate
    
    return xr.DataArray(
        data,
        dims=("trace", "time"),
        coords={"trace": np.arange(len(traces)), "time": times},
        attrs={"sample_rate": sample_rate, "format": "sac"},
    )


# -----------------------------------------------------------------------------
# Signal processing utilities
# -----------------------------------------------------------------------------
from promethium.signal import (
    bandpass_filter,
    lowpass_filter,
    highpass_filter,
    notch_filter,
)

# -----------------------------------------------------------------------------
# ML components
# -----------------------------------------------------------------------------
from promethium.ml import (
    InferenceEngine,
    load_model,
    reconstruct,
    compute_snr,
    compute_ssim,
)


def get_model(name: str, *, device: str = None):
    """
    Get a pre-defined seismic reconstruction model by name.
    
    Args:
        name: Model name (e.g., 'unet_denoise_v1', 'autoencoder_v1').
        device: Device to load model on ('cuda', 'cpu', or None for auto).
        
    Returns:
        Loaded model ready for inference.
        
    Available models:
        - 'unet_denoise_v1': U-Net for denoising
        - 'unet_reconstruction_v1': U-Net for trace reconstruction
        - 'autoencoder_v1': Autoencoder for compression/denoising
        
    Example:
        >>> model = promethium.get_model('unet_denoise_v1', device='cuda')
    """
    from promethium.ml.models.registry import ModelRegistry
    from promethium.utils.reproducibility import get_device as _get_device
    
    if device is None:
        device = _get_device()
        
    model = ModelRegistry.create(name, {"n_channels": 1, "n_classes": 1})
    model.to(device)
    model.eval()
    
    return model


# -----------------------------------------------------------------------------
# High-level pipelines
# -----------------------------------------------------------------------------
from promethium.pipelines import SeismicRecoveryPipeline


def run_recovery(data, pipeline=None, preset: str = None, **kwargs):
    """
    Run seismic data recovery using a pipeline.
    
    Convenience function that creates a pipeline if needed and runs recovery.
    
    Args:
        data: Input seismic data (numpy array or xarray.DataArray).
        pipeline: SeismicRecoveryPipeline instance. If None, creates from preset.
        preset: Preset name if pipeline is None. Default 'unet_denoise_v1'.
        **kwargs: Additional arguments passed to pipeline.run().
        
    Returns:
        Reconstructed data array.
        
    Example:
        >>> result = promethium.run_recovery(noisy_data, preset='unet_denoise_v1')
    """
    if pipeline is None:
        if preset is None:
            preset = "unet_denoise_v1"
        pipeline = SeismicRecoveryPipeline.from_preset(preset)
        
    return pipeline.run(data, **kwargs)


# -----------------------------------------------------------------------------
# Evaluation metrics
# -----------------------------------------------------------------------------
from promethium.evaluation import (
    signal_to_noise_ratio,
    mean_squared_error,
    peak_signal_to_noise_ratio,
    structural_similarity_index,
    frequency_domain_correlation,
    phase_coherence,
    evaluate_reconstruction,
)

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------
from promethium.utils import (
    set_seed,
    get_device,
    generate_synthetic_traces,
    add_noise,
    plot_traces,
    plot_comparison,
)

# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Core
    "settings",
    "get_settings",
    "get_logger",
    # I/O
    "read_segy",
    "write_segy",
    "load_segy",
    "load_miniseed",
    "load_sac",
    # Signal processing
    "bandpass_filter",
    "lowpass_filter",
    "highpass_filter",
    "notch_filter",
    # ML
    "InferenceEngine",
    "load_model",
    "reconstruct",
    "compute_snr",
    "compute_ssim",
    "get_model",
    # Pipelines
    "SeismicRecoveryPipeline",
    "run_recovery",
    # Evaluation
    "signal_to_noise_ratio",
    "mean_squared_error",
    "peak_signal_to_noise_ratio",
    "structural_similarity_index",
    "frequency_domain_correlation",
    "phase_coherence",
    "evaluate_reconstruction",
    # Utils
    "set_seed",
    "get_device",
    "generate_synthetic_traces",
    "add_noise",
    "plot_traces",
    "plot_comparison",
]


