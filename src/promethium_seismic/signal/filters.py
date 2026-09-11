# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt, iirnotch
from typing import Optional, Tuple
from promethium_seismic.core.exceptions import ProcessingError
from promethium_seismic.core.logging import logger

def butter_bandpass(
    lowcut: float, 
    highcut: float, 
    fs: float, 
    order: int = 5
) -> np.ndarray:
    """Design a Butterworth bandpass filter using SOS."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    
    if not (0 < low < 1) or not (0 < high < 1):
        raise ProcessingError(f"Filter frequencies {lowcut}, {highcut} are out of bounds for fs={fs}")
        
    sos = butter(order, [low, high], btype='band', output='sos')
    return sos

def bandpass_filter(
    data: np.ndarray, 
    lowcut: float, 
    highcut: float, 
    fs: float, 
    order: int = 5, 
    zero_phase: bool = True
) -> np.ndarray:
    """
    Apply bandpass filter to 1D data.
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
        raise ProcessingError(f"Bandpass filtering failed: {e}")

def notch_filter(
    data: np.ndarray, 
    freq: float, 
    fs: float, 
    quality: float = 30.0
) -> np.ndarray:
    """
    Apply notch filter to remove specific frequency (e.g., 50/60Hz).
    """
    nyq = 0.5 * fs
    freq_norm = freq / nyq
    b, a = iirnotch(freq_norm, quality)
    
    # Using filtfilt for zero phase notch
    from scipy.signal import filtfilt
    return filtfilt(b, a, data)
