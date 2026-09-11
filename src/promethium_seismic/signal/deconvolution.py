# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import numpy as np
from scipy.linalg import solve, toeplitz

from promethium_seismic.core.logging import logger


def predictive_deconvolution(
    data: np.ndarray,
    operator_length: int,
    prediction_distance: int,
    white_noise: float = 0.1,
) -> np.ndarray:
    """
    Predictive deconvolution (spiking or gap) using Wiener-Levinson.

    Args:
        data: Input trace.
        operator_length: Length of operator (samples).
        prediction_distance: Gap (alpha).
        white_noise: Pre-whitening percentage (e.g. 0.1%).
    """
    n = len(data)
    if n < operator_length + prediction_distance:
        logger.warning("Trace too short for deconvolution parameters.")
        return data

    # Autocorrelation
    corr_len = operator_length + prediction_distance
    full_corr = np.correlate(data, data, mode="full")
    mid = len(full_corr) // 2
    r = full_corr[mid : mid + corr_len + 1]

    # Levinson-Durbin or Toeplitz solve
    # R * a = g
    R = toeplitz(r[:operator_length])

    # Pre-whitening
    R[np.diag_indices_from(R)] *= 1.0 + white_noise / 100.0

    # RHS: Cross-correlation between x(t) and x(t+alpha) -> r[alpha:]
    g = r[prediction_distance : prediction_distance + operator_length]

    try:
        # Solve for filter coefficients 'a'
        a = solve(R, g, assume_a="pos")
    except np.linalg.LinAlgError:
        logger.warning("unstable deconvolution matrix. returning original.")
        return data

    # Prediction error filter
    # f = [1, 0, ..., 0] - [0, ..., a]
    # Actually, for predictive decon, output is prediction error.
    # PEF = [1, 0...0, -a0, -a1...]
    pef = np.zeros(prediction_distance + len(a))
    pef[0] = 1.0
    pef[prediction_distance:] = -a

    return np.convolve(data, pef, mode="same")
