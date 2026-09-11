# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Model architectures for seismic reconstruction.

This package had no __init__.py, so `from promethium_seismic.ml.models
import UNet` failed with "cannot import name 'UNet' ... (unknown location)",
which is what three of the six failing tests were reporting.

The modules themselves were still reaching the wheel: building with and
without this file gives nine and seven packaged modules, a difference of
exactly the two __init__ files added here. The defect was the import path,
not the packaging.
"""

from promethium_seismic.ml.models.autoencoder import Autoencoder
from promethium_seismic.ml.models.base import PromethiumModel
from promethium_seismic.ml.models.registry import ModelRegistry
from promethium_seismic.ml.models.unet import ConvBlock, UNet, UpSample

__all__ = [
    "Autoencoder",
    "ConvBlock",
    "ModelRegistry",
    "PromethiumModel",
    "UNet",
    "UpSample",
]
