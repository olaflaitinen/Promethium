# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class RecoveryAlgorithm(ABC):
    """
    Abstract base class for all recovery/reconstruction algorithms.
    """

    def __init__(self, params: dict[str, Any] | None = None):
        self.params = params or {}

    @abstractmethod
    def fit(
        self, data: np.ndarray, mask: np.ndarray | None = None
    ) -> "RecoveryAlgorithm":
        """
        Fit the model to the data (observed).

        Args:
            data: Input data array (e.g., Gather).
            mask: Binary mask (1=observed, 0=missing).
        """
        pass

    @abstractmethod
    def transform(self, data: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """
        Reconstruct the missing data.

        Returns:
            Reconstructed full data.
        """
        pass

    def fit_transform(
        self, data: np.ndarray, mask: np.ndarray | None = None
    ) -> np.ndarray:
        return self.fit(data, mask).transform(data, mask)
