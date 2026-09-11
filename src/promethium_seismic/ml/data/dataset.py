# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from torch.utils.data import Dataset


class SeismicDataset(Dataset):
    """
    PyTorch Dataset for Seismic Data.

    Supports:
    - Lazy loading via Zarr/Xarray
    - Patch extraction (Random or Grid)
    - On-the-fly augmentation
    """

    def __init__(
        self,
        data_path: str,
        patch_size: int = 128,
        stride: int = 64,
        mode: str = "train",
        transform: Callable | None = None,
        target_path: str | None = None,
    ):
        """
        Args:
            data_path: Path to Zarr store (Input/Noisy).
            patch_size: Size of square patches (time x trace).
            stride: Stride for patch extraction.
            mode: 'train' (random patches) or 'predict' (sequential grid).
            transform: Augmentation pipeline.
            target_path: Path to Zarr store (Clean/Ground Truth) for paired training.
        """
        self.data_path = Path(data_path)
        self.patch_size = patch_size
        self.stride = stride
        self.mode = mode
        self.transform = transform

        # Lazy Load
        # Imported here so that the ml extra does not require the io
        # extra: these two lines are the only place this module reads a
        # store, and zarr belongs to a different install.
        from promethium_seismic.io.zarr_wrapper import load_zarr

        self.data = load_zarr(self.data_path)
        self.target = load_zarr(target_path) if target_path else None

        # Pre-calculate Grid for 'predict' mode or 'train'?
        # For training on massive 3D volumes, random sampling strategy is often SoTA.
        # But for 'standard' PyTorch usage, we often define an epoch length.

        self.n_traces = self.data.shape[0]  # (trace, time)
        self.n_time = self.data.shape[1]

        # Grid definition
        if self.mode == "predict":
            self.starts = self._generate_grid()
        else:
            # Training: Infinite / Arbitrary length?
            # Define a fixed length for one epoch proxy
            self.length = 1000  # Arbitrary "epoch" size

    def _generate_grid(self):
        starts = []
        for t in range(0, self.n_traces - self.patch_size + 1, self.stride):
            for s in range(0, self.n_time - self.patch_size + 1, self.stride):
                starts.append((t, s))
        return starts

    def __len__(self):
        if self.mode == "predict":
            return len(self.starts)
        return self.length

    def __getitem__(self, idx: int) -> dict[str, Any]:
        if self.mode == "predict":
            t_start, s_start = self.starts[idx]
        else:
            # Random Crop for Training
            t_start = np.random.randint(0, self.n_traces - self.patch_size)
            s_start = np.random.randint(0, self.n_time - self.patch_size)

        # Extraction (Lazy via Zarr)
        # Slicing xarray returns xarray, .values converts to numpy
        inp = self.data[
            t_start : t_start + self.patch_size, s_start : s_start + self.patch_size
        ].values

        sample = {"input": inp, "coords": (t_start, s_start)}

        if self.target is not None:
            tgt = self.target[
                t_start : t_start + self.patch_size, s_start : s_start + self.patch_size
            ].values
            sample["target"] = tgt

        if self.transform:
            sample = self.transform(sample)

        return sample
