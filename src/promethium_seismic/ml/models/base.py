# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Base class for the model architectures."""

from typing import Any

import torch.nn as nn


class PromethiumModel(nn.Module):
    """Base class for all Promethium models.

    Holds the configuration a model was built from and fixes the forward
    interface.

    Two call styles are accepted and they mean the same thing::

        UNet(n_channels=1, n_classes=1)
        UNet({"n_channels": 1, "n_classes": 1})

    The first is what a reader of any other PyTorch library expects and is
    how these models are built by hand. The second is what the registry
    uses, because it loads a configuration out of a checkpoint or a YAML
    file and has a mapping in hand rather than a set of names. Accepting
    only the mapping, which is what this class used to do, made the obvious
    call raise TypeError.
    """

    def __init__(self, config: dict[str, Any] | None = None, **kwargs: Any):
        """Build the model.

        Args:
            config: The configuration as a mapping. Optional when every
                setting is passed as a keyword argument.
            **kwargs: Individual settings. Merged over `config`, so an
                explicit keyword wins over the same key in the mapping.
        """
        super().__init__()
        merged: dict[str, Any] = dict(config or {})
        merged.update(kwargs)
        self.config = merged

    def forward(self, x):
        """Run the model.

        Args:
            x: Input tensor.

        Raises:
            NotImplementedError: always. Subclasses provide the behaviour.
        """
        raise NotImplementedError

    def get_config(self) -> dict[str, Any]:
        """Return the configuration this model was built from."""
        return self.config
