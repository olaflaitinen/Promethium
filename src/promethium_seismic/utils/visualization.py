# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Visualization utilities for seismic data.
"""

import numpy as np

# Lazy import matplotlib to avoid import errors if not installed
_plt = None
_mpl = None


def _get_plt():
    """Lazy load matplotlib."""
    global _plt
    if _plt is None:
        import matplotlib.pyplot as plt

        _plt = plt
    return _plt


def plot_traces(
    data: np.ndarray,
    sample_rate: float = 250.0,
    traces_to_plot: list[int] | None = None,
    title: str = "Seismic Traces",
    figsize: tuple[int, int] = (12, 6),
    normalize: bool = True,
) -> None:
    """
    Plot seismic traces in wiggle or overlay format.

    Args:
        data: Input data array of shape (n_traces, n_samples).
        sample_rate: Sampling rate in Hz.
        traces_to_plot: List of trace indices to plot. Default plots first 10.
        title: Plot title.
        figsize: Figure size as (width, height).
        normalize: If True, normalize each trace individually.

    Example:
        >>> from promethium_seismic.utils import generate_synthetic_traces, plot_traces
        >>> traces, meta = generate_synthetic_traces()
        >>> plot_traces(traces, sample_rate=meta['sample_rate'])
    """
    plt = _get_plt()

    if traces_to_plot is None:
        traces_to_plot = list(range(min(10, data.shape[0])))

    n_samples = data.shape[1]
    dt = 1.0 / sample_rate
    t = np.arange(n_samples) * dt

    fig, ax = plt.subplots(figsize=figsize)

    for i, trace_idx in enumerate(traces_to_plot):
        trace = data[trace_idx].copy()

        if normalize:
            max_val = np.max(np.abs(trace))
            if max_val > 0:
                trace = trace / max_val

        # Offset for visibility
        offset = i * 1.5
        ax.plot(t, trace + offset, "k-", linewidth=0.5)
        ax.fill_betweenx([offset - 0.5, offset + 0.5], t[0], t[-1], alpha=0.1)

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Trace Index")
    ax.set_title(title)
    ax.set_yticks([i * 1.5 for i in range(len(traces_to_plot))])
    ax.set_yticklabels([str(idx) for idx in traces_to_plot])

    plt.tight_layout()
    plt.show()


def plot_comparison(
    original: np.ndarray,
    reconstructed: np.ndarray,
    sample_rate: float = 250.0,
    trace_idx: int = 0,
    title: str = "Original vs Reconstructed",
    figsize: tuple[int, int] = (14, 8),
) -> None:
    """
    Plot comparison between original and reconstructed traces.

    Creates a multi-panel figure showing:
    - Original trace
    - Reconstructed trace
    - Difference (residual)
    - Overlay comparison

    Args:
        original: Original data array.
        reconstructed: Reconstructed data array.
        sample_rate: Sampling rate in Hz.
        trace_idx: Index of trace to compare.
        title: Plot title.
        figsize: Figure size.

    Example:
        >>> from promethium_seismic.utils import plot_comparison
        >>> plot_comparison(clean_data, recovered_data, trace_idx=5)
    """
    plt = _get_plt()

    n_samples = original.shape[1] if original.ndim > 1 else len(original)
    dt = 1.0 / sample_rate
    t = np.arange(n_samples) * dt

    if original.ndim > 1:
        orig_trace = original[trace_idx]
        recon_trace = reconstructed[trace_idx]
    else:
        orig_trace = original
        recon_trace = reconstructed

    diff = orig_trace - recon_trace

    fig, axes = plt.subplots(4, 1, figsize=figsize, sharex=True)

    # Original
    axes[0].plot(t, orig_trace, "b-", linewidth=0.8)
    axes[0].set_ylabel("Amplitude")
    axes[0].set_title("Original")
    axes[0].grid(True, alpha=0.3)

    # Reconstructed
    axes[1].plot(t, recon_trace, "g-", linewidth=0.8)
    axes[1].set_ylabel("Amplitude")
    axes[1].set_title("Reconstructed")
    axes[1].grid(True, alpha=0.3)

    # Difference
    axes[2].plot(t, diff, "r-", linewidth=0.8)
    axes[2].set_ylabel("Amplitude")
    axes[2].set_title(f"Difference (RMSE: {np.sqrt(np.mean(diff**2)):.4f})")
    axes[2].grid(True, alpha=0.3)

    # Overlay
    axes[3].plot(t, orig_trace, "b-", linewidth=0.8, label="Original", alpha=0.7)
    axes[3].plot(t, recon_trace, "g--", linewidth=0.8, label="Reconstructed", alpha=0.7)
    axes[3].set_xlabel("Time (s)")
    axes[3].set_ylabel("Amplitude")
    axes[3].set_title("Overlay Comparison")
    axes[3].legend()
    axes[3].grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_gather(
    data: np.ndarray,
    sample_rate: float = 250.0,
    title: str = "Seismic Gather",
    cmap: str = "seismic",
    figsize: tuple[int, int] = (10, 8),
    clip_percentile: float = 99.0,
) -> None:
    """
    Plot seismic data as a 2D image (gather view).

    Args:
        data: Input data array of shape (n_traces, n_samples).
        sample_rate: Sampling rate in Hz.
        title: Plot title.
        cmap: Colormap name.
        figsize: Figure size.
        clip_percentile: Percentile for amplitude clipping.

    Example:
        >>> from promethium_seismic.utils import generate_synthetic_traces
        >>> from promethium_seismic.utils.visualization import plot_gather
        >>> traces, meta = generate_synthetic_traces()
        >>> plot_gather(traces, sample_rate=meta['sample_rate'])
    """
    plt = _get_plt()

    n_traces, n_samples = data.shape
    dt = 1.0 / sample_rate

    clip_val = np.percentile(np.abs(data), clip_percentile)

    fig, ax = plt.subplots(figsize=figsize)

    extent = [0, n_traces, n_samples * dt, 0]
    im = ax.imshow(
        data.T,
        aspect="auto",
        cmap=cmap,
        vmin=-clip_val,
        vmax=clip_val,
        extent=extent,
    )

    ax.set_xlabel("Trace Number")
    ax.set_ylabel("Time (s)")
    ax.set_title(title)

    plt.colorbar(im, ax=ax, label="Amplitude")

    plt.tight_layout()
    plt.show()
