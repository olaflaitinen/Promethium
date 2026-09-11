# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import numpy as np
import torch
from torch.utils.data import Dataset


class SeismicTorchDataset(Dataset):
    """
    PyTorch Dataset for 2D seismic patches.
    """

    def __init__(
        self,
        data: np.ndarray,
        patch_size: tuple[int, int] = (64, 64),
        stride: tuple[int, int] = (32, 32),
        missing_trace_prob: float = 0.0,
    ):
        """
        Args:
            data: 2D numpy array (time x trace or trace x time).
            patch_size: (height, width).
            stride: (y_step, x_step).
            missing_trace_prob: Probability to mask a trace (augmentation).
        """
        self.data = np.nan_to_num(data)
        self.patch_height, self.patch_width = patch_size
        self.stride_y, self.stride_x = stride
        self.missing_trace_prob = missing_trace_prob

        # Create patches
        self.patches = []
        h, w = self.data.shape
        # Simple patching logic (could be optimized with unfold)
        for y in range(0, h - self.patch_height + 1, self.stride_y):
            for x in range(0, w - self.patch_width + 1, self.stride_x):
                self.patches.append(
                    self.data[y : y + self.patch_height, x : x + self.patch_width]
                )

    def __len__(self):
        return len(self.patches)

    def __getitem__(self, idx):
        patch = self.patches[idx]

        # Normalize patch (standardize)
        mean = patch.mean()
        std = patch.std() + 1e-6
        norm_patch = (patch - mean) / std

        # Create mask
        mask = np.ones_like(norm_patch)
        if self.missing_trace_prob > 0:
            # Mask entire columns (traces)
            for col in range(self.patch_width):
                if np.random.random() < self.missing_trace_prob:
                    mask[:, col] = 0
                    norm_patch[:, col] = 0

        # To Tensor (C, H, W)
        img = torch.from_numpy(norm_patch).float().unsqueeze(0)
        msk = torch.from_numpy(mask).float().unsqueeze(0)

        return img, msk
