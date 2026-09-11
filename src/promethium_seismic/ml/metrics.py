# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import numpy as np
import torch
import torch.nn.functional as F


def compute_snr(
    target: np.ndarray | torch.Tensor, prediction: np.ndarray | torch.Tensor
) -> float:
    """
    Compute Signal-to-Noise Ratio (SNR) in dB.
    """
    if isinstance(target, np.ndarray):
        target = torch.from_numpy(target)
    if isinstance(prediction, np.ndarray):
        prediction = torch.from_numpy(prediction)

    noise = target - prediction
    signal_power = torch.mean(target**2)
    noise_power = torch.mean(noise**2)

    snr = 10 * torch.log10(signal_power / (noise_power + 1e-8))
    return snr.item()


def compute_ssim(
    target: np.ndarray | torch.Tensor, prediction: np.ndarray | torch.Tensor
) -> float:
    """
    Compute Structural Similarity Index (SSIM).
    Assumes single channel seismic data (height, width).
    """
    if isinstance(target, np.ndarray):
        target = torch.from_numpy(target)
    if isinstance(prediction, np.ndarray):
        prediction = torch.from_numpy(prediction)

    # Ensure 4D (B, C, H, W) for pooling
    if target.ndim == 2:
        target = target.unsqueeze(0).unsqueeze(0)
    if prediction.ndim == 2:
        prediction = prediction.unsqueeze(0).unsqueeze(0)

    C1 = 0.01**2
    C2 = 0.03**2

    mu_x = F.avg_pool2d(prediction, 3, 1, 1)
    mu_y = F.avg_pool2d(target, 3, 1, 1)

    sigma_x = F.avg_pool2d(prediction**2, 3, 1, 1) - mu_x**2
    sigma_y = F.avg_pool2d(target**2, 3, 1, 1) - mu_y**2
    sigma_xy = F.avg_pool2d(prediction * target, 3, 1, 1) - mu_x * mu_y

    ss_map = ((2 * mu_x * mu_y + C1) * (2 * sigma_xy + C2)) / (
        (mu_x**2 + mu_y**2 + C1) * (sigma_x + sigma_y + C2)
    )

    return ss_map.mean().item()
