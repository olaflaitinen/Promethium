# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Frequency filters for seismic traces.

Butterworth band, low and high pass, plus a notch for mains hum. All of them
are second order sections rather than transfer function coefficients: a high
order filter expressed as `b, a` loses precision badly enough to go unstable,
and seismic work reaches for high orders routinely.

Zero phase filtering is the default. A causal filter shifts events in time,
and an arrival time that moved because of the processing is worse than one
that is slightly less sharply filtered.
"""

import numpy as np
from scipy.signal import butter, iirnotch, sosfilt, sosfiltfilt

from promethium_seismic.core.exceptions import ProcessingError
from promethium_seismic.core.logging import logger


def butter_bandpass(
    lowcut: float, highcut: float, fs: float, order: int = 5
) -> np.ndarray:
    """Design a Butterworth bandpass filter as second order sections.

    Args:
        lowcut: Lower corner frequency, in Hz.
        highcut: Upper corner frequency, in Hz.
        fs: Sampling frequency, in Hz.
        order: Filter order. Higher is sharper and less stable.

    Returns:
        The filter as second order sections, ready for `sosfilt`.

    Raises:
        ProcessingError: if either corner is outside the open interval
            between zero and the Nyquist frequency, which is where a
            Butterworth design is meaningless rather than merely poor.
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    if not (0 < low < 1) or not (0 < high < 1):
        raise ProcessingError(
            f"Filter frequencies {lowcut}, {highcut} are out of bounds for fs={fs}"
        )

    sos = butter(order, [low, high], btype="band", output="sos")
    return sos


def bandpass_filter(
    data: np.ndarray,
    lowcut: float,
    highcut: float,
    fs: float,
    order: int = 5,
    zero_phase: bool = True,
) -> np.ndarray:
    """Band pass a trace.

    Args:
        data: The trace, or an array whose last axis is time.
        lowcut: Lower corner frequency, in Hz.
        highcut: Upper corner frequency, in Hz.
        fs: Sampling frequency, in Hz.
        order: Filter order.
        zero_phase: Filter forwards and backwards, so that no event is
            shifted in time. The effective order doubles. Turn it off only
            when causality matters more than timing.

    Returns:
        The filtered data, the same shape as the input.

    Raises:
        ProcessingError: if the filter cannot be designed or applied.

    Samples that are not a number are replaced with zero and a warning is
    logged. A filter has no meaning across a gap, and silently propagating
    the gap through the convolution would corrupt every sample within one
    filter length of it.
    """
    if np.any(np.isnan(data)):
        # Handle NaNs: basic strategy is interpolate or zero, but for filtering
        # usually we assume contiguous data. Raise warning or error.
        logger.warning("NaNs detected in data before filtering. Replacing with zero.")
        data = np.nan_to_num(data)

    try:
        sos = butter_bandpass(lowcut, highcut, fs, order=order)
        if zero_phase:
            return sosfiltfilt(sos, data)
        else:
            return sosfilt(sos, data)
    except Exception as e:
        raise ProcessingError(f"Bandpass filtering failed: {e}") from e


def notch_filter(
    data: np.ndarray, freq: float, fs: float, quality: float = 30.0
) -> np.ndarray:
    """Notch out one frequency, usually mains hum.

    Args:
        data: The trace, or an array whose last axis is time.
        freq: The frequency to remove, in Hz. Typically 50 or 60.
        fs: Sampling frequency, in Hz.
        quality: Quality factor. Higher is a narrower notch, which removes
            less of the surrounding signal and rings for longer.

    Returns:
        The filtered data, the same shape as the input.

    Applied forwards and backwards, so the notch shifts nothing in time.
    """
    nyq = 0.5 * fs
    freq_norm = freq / nyq
    b, a = iirnotch(freq_norm, quality)

    # Using filtfilt for zero phase notch
    from scipy.signal import filtfilt

    return filtfilt(b, a, data)
