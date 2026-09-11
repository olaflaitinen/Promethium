# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Reproducibility utilities for deterministic behavior.
"""

import random

import numpy as np
import torch


def set_seed(seed: int = 42) -> None:
    """
    Set random seeds for reproducibility across all libraries.

    Args:
        seed: Random seed value. Default is 42.

    Example:
        >>> from promethium_seismic.utils import set_seed
        >>> set_seed(42)
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def get_device(prefer_gpu: bool = True) -> str:
    """
    Determine the best available device for computation.

    Args:
        prefer_gpu: If True, prefer CUDA if available. Default is True.

    Returns:
        Device string: 'cuda' if GPU available and preferred, else 'cpu'.

    Example:
        >>> from promethium_seismic.utils import get_device
        >>> device = get_device()
        >>> print(f"Using device: {device}")
    """
    if prefer_gpu and torch.cuda.is_available():
        return "cuda"
    return "cpu"
