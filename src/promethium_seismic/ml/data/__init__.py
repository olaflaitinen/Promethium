# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Dataset plumbing for training.

Like the models package beside it, this directory had no __init__.py, so it
was an implicit namespace package and importable only by the full path of a
module inside it.
"""

from promethium_seismic.ml.data.dataset import SeismicDataset

__all__ = ["SeismicDataset"]
