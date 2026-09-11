# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# Promethium - Advanced Seismic Data Recovery and Reconstruction Framework
# Main package initialization

"""
Promethium is a state-of-the-art, AI-driven framework for seismic signal
reconstruction, denoising, and geophysical data enhancement.

Distribution Name: promethium-seismic
Import Namespace: promethium_seismic
Version: 1.0.4

Installation:
    pip install promethium-seismic==1.0.4

Quick Start:
    >>> import promethium_seismic
    >>> from promethium_seismic import load_segy, SeismicRecoveryPipeline
    >>>
    >>> # Load seismic data
    >>> data = load_segy("survey.sgy")
    >>>
    >>> # Create and run reconstruction pipeline
    >>> pipeline = SeismicRecoveryPipeline.from_preset("unet_denoise_v1")
    >>> result = pipeline.run(data)
    >>>
    >>> # Evaluate reconstruction quality
    >>> metrics = promethium_seismic.evaluate_reconstruction(data, result)
    >>> print(metrics)

Copyright (c) 2025 Olaf Yunus Laitinen Imanov
Licensed under MPL-2.0
"""

__version__ = "1.0.4"
__author__ = "Olaf Yunus Laitinen Imanov"
__license__ = "MPL-2.0"

# -----------------------------------------------------------------------------
# Eager imports: the light core
#
# Only what depends on nothing heavier than the standard library is imported
# at module load. Everything else is deferred below, so that
# `import promethium_seismic` costs a few milliseconds and works in an environment
# that has numpy and scipy and nothing else.
# -----------------------------------------------------------------------------
from promethium_seismic.core.config import get_settings, settings
from promethium_seismic.core.logging import get_logger

# -----------------------------------------------------------------------------
# Lazy imports
#
# Each public name is mapped to the submodule that defines it and to the
# optional dependency group that submodule needs. Resolution happens on first
# attribute access, through the module __getattr__ that PEP 562 defines.
#
# The point of the extra name in this table is the error message. Without it a
# user who calls read_segy without the io extra gets ModuleNotFoundError for
# segyio, which tells them nothing about what to do. With it they get told
# which extra to install.
# -----------------------------------------------------------------------------
_LAZY: dict[str, tuple[str, str | None]] = {
    # name: (submodule, extra required, or None when the core is enough)
    "read_segy": ("promethium_seismic.io", "io"),
    "write_segy": ("promethium_seismic.io", "io"),
    "load_segy": ("promethium_seismic.io", "io"),
    "bandpass_filter": ("promethium_seismic.signal", None),
    "lowpass_filter": ("promethium_seismic.signal", None),
    "highpass_filter": ("promethium_seismic.signal", None),
    "notch_filter": ("promethium_seismic.signal", None),
    "InferenceEngine": ("promethium_seismic.ml", "ml"),
    "load_model": ("promethium_seismic.ml", "ml"),
    "reconstruct": ("promethium_seismic.ml", "ml"),
    "compute_snr": ("promethium_seismic.ml", "ml"),
    "compute_ssim": ("promethium_seismic.ml", "ml"),
    "SeismicRecoveryPipeline": ("promethium_seismic.pipelines", "ml"),
    "signal_to_noise_ratio": ("promethium_seismic.evaluation", None),
    "mean_squared_error": ("promethium_seismic.evaluation", None),
    "peak_signal_to_noise_ratio": ("promethium_seismic.evaluation", None),
    "structural_similarity_index": ("promethium_seismic.evaluation", None),
    "frequency_domain_correlation": ("promethium_seismic.evaluation", None),
    "phase_coherence": ("promethium_seismic.evaluation", None),
    "set_seed": ("promethium_seismic.utils.reproducibility", "ml"),
    "get_device": ("promethium_seismic.utils.reproducibility", "ml"),
    "generate_synthetic_traces": ("promethium_seismic.utils.synthetic", None),
    "add_noise": ("promethium_seismic.utils.synthetic", None),
    "plot_traces": ("promethium_seismic.utils.visualization", "viz"),
    "plot_comparison": ("promethium_seismic.utils.visualization", "viz"),
}


class MissingDependencyError(ImportError):
    """Raised when a feature is used without the extra that provides it."""


def _missing(name: str, extra: str, cause: BaseException) -> MissingDependencyError:
    """Build the error a user can act on.

    Args:
        name: The attribute that was requested.
        extra: The optional dependency group that provides it.
        cause: The original import failure.

    Returns:
        An error naming the install command.
    """
    return MissingDependencyError(
        f"promethium_seismic.{name} needs the '{extra}' extra, which is not "
        f"installed. Install it with:\n\n"
        f"    pip install 'promethium-seismic[{extra}]'\n\n"
        f"The underlying import failed with: {cause}"
    )


def __getattr__(name: str):
    """Resolve a public name on first use.

    Args:
        name: The attribute being looked up.

    Returns:
        The object from the submodule that defines it.

    Raises:
        MissingDependencyError: when the submodule needs an extra that is not
            installed.
        AttributeError: when the name is not part of the public surface.
    """
    entry = _LAZY.get(name)
    if entry is None:
        raise AttributeError(f"module 'promethium_seismic' has no attribute '{name}'")

    module_name, extra = entry
    import importlib

    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        if extra is None:
            raise
        raise _missing(name, extra, exc) from exc

    value = getattr(module, name)
    globals()[name] = value  # cache, so this runs once per name
    return value


def __dir__() -> list[str]:
    """List the public surface, including names not yet imported."""
    return sorted(set(globals()) | set(_LAZY))


def load_miniseed(path: str, **kwargs):
    """
    Load seismic data from miniSEED format.

    Args:
        path: Path to miniSEED file.
        **kwargs: Additional arguments passed to obspy.read.

    Returns:
        xarray.DataArray with seismic data.
    """
    import numpy as np
    import xarray as xr
    from obspy import read as obspy_read

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
    import numpy as np
    import xarray as xr
    from obspy import read as obspy_read

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


def get_model(name: str, *, device: str | None = None):
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
        >>> model = promethium_seismic.get_model('unet_denoise_v1', device='cuda')
    """
    from promethium_seismic.ml.models.registry import ModelRegistry
    from promethium_seismic.utils.reproducibility import get_device as _get_device

    if device is None:
        device = _get_device()

    model = ModelRegistry.create(name, {"n_channels": 1, "n_classes": 1})
    model.to(device)
    model.eval()

    return model


def run_recovery(data, pipeline=None, preset: str | None = None, **kwargs):
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
        >>> result = promethium_seismic.run_recovery(
        ...     noisy_data, preset='unet_denoise_v1'
        ... )
    """
    if pipeline is None:
        if preset is None:
            preset = "unet_denoise_v1"
        # Imported here rather than at module scope: the pipelines package
        # pulls torch, and this function is the only thing in the module that
        # needs it.
        from promethium_seismic.pipelines import SeismicRecoveryPipeline

        pipeline = SeismicRecoveryPipeline.from_preset(preset)

    return pipeline.run(data, **kwargs)


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
