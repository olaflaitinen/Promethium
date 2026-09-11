# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import torch.nn as nn
from typing import Dict, Any

class PromethiumModel(nn.Module):
    """
    Base class for all Promethium models.
    Enforces a standard forward interface and config storage.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config

    def forward(self, x):
        raise NotImplementedError

    def get_config(self) -> Dict[str, Any]:
        return self.config
