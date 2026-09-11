# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# Promethium Signal Processing Module

"""
Signal processing implementations including filtering, spectral analysis,
transforms, deconvolution, and interpolation methods.
"""

from promethium_seismic.signal.filters import (
    bandpass_filter,
    butter_bandpass,
    notch_filter,
)
from promethium_seismic.signal.transforms import fft, ifft, wavelet_transform


# Convenience aliases for common filter types
def lowpass_filter(data, cutoff, fs, order=5, zero_phase=True):
    """Apply lowpass filter using bandpass with low cutoff near DC."""
    return bandpass_filter(data, 0.1, cutoff, fs, order, zero_phase)


def highpass_filter(data, cutoff, fs, order=5, zero_phase=True):
    """Apply highpass filter using bandpass with high cutoff near Nyquist."""
    nyq = 0.5 * fs
    return bandpass_filter(data, cutoff, nyq * 0.99, fs, order, zero_phase)


__all__ = [
    "bandpass_filter",
    "lowpass_filter",
    "highpass_filter",
    "notch_filter",
    "butter_bandpass",
    "fft",
    "ifft",
    "wavelet_transform",
]
