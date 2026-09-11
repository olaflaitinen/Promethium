# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import Any

import torch.nn as nn

from promethium_seismic.ml.models.base import PromethiumModel
from promethium_seismic.ml.models.registry import ModelRegistry


@ModelRegistry.register("autoencoder")
class Autoencoder(PromethiumModel):
    """
    Convolutional Autoencoder for Denoising.
    """

    def __init__(self, config: dict[str, Any] | None = None, **kwargs: Any):
        super().__init__(config, **kwargs)
        config = self.config
        n_channels = config.get("n_channels", 1)
        base_filters = config.get("base_filters", 32)

        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(n_channels, base_filters, 3, stride=2, padding=1),  # /2
            nn.BatchNorm2d(base_filters),
            nn.LeakyReLU(),
            nn.Conv2d(base_filters, base_filters * 2, 3, stride=2, padding=1),  # /4
            nn.BatchNorm2d(base_filters * 2),
            nn.LeakyReLU(),
            nn.Conv2d(base_filters * 2, base_filters * 4, 3, stride=2, padding=1),  # /8
            nn.BatchNorm2d(base_filters * 4),
            nn.LeakyReLU(),
        )

        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(
                base_filters * 4,
                base_filters * 2,
                3,
                stride=2,
                padding=1,
                output_padding=1,
            ),  # *2
            nn.BatchNorm2d(base_filters * 2),
            nn.LeakyReLU(),
            nn.ConvTranspose2d(
                base_filters * 2, base_filters, 3, stride=2, padding=1, output_padding=1
            ),  # *4
            nn.BatchNorm2d(base_filters),
            nn.LeakyReLU(),
            nn.ConvTranspose2d(
                base_filters, n_channels, 3, stride=2, padding=1, output_padding=1
            ),  # *8
            nn.Tanh(),  # Assuming normalized input [-1, 1]
        )

    def forward(self, x):
        z = self.encoder(x)
        out = self.decoder(z)
        return out
