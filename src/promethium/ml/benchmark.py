# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import torch
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
import json
import logging

from promethium.core.config import get_settings
from promethium.ml.models.registry import ModelRegistry
from promethium.ml.data.dataset import SeismicDataset
# Using standard torch metrics or custom implementation
# For ssim, we can use torchmetrics or implement a basic version

logger = logging.getLogger(__name__)

def ssim(pred: torch.Tensor, target: torch.Tensor) -> float:
    """
    Structural Similarity Index (Simplified for 1 channel).
    """
    C1 = 0.01 ** 2
    C2 = 0.03 ** 2
    
    mu_x = F.avg_pool2d(pred, 3, 1, 1)
    mu_y = F.avg_pool2d(target, 3, 1, 1)
    
    sigma_x = F.avg_pool2d(pred**2, 3, 1, 1) - mu_x**2
    sigma_y = F.avg_pool2d(target**2, 3, 1, 1) - mu_y**2
    sigma_xy = F.avg_pool2d(pred * target, 3, 1, 1) - mu_x * mu_y
    
    ss_map = ((2 * mu_x * mu_y + C1) * (2 * sigma_xy + C2)) / \
             ((mu_x**2 + mu_y**2 + C1) * (sigma_x + sigma_y + C2))
             
    return ss_map.mean().item()

class BenchmarkEngine:
    """
    Engine for running standardized benchmarks on models.
    Calculates: MSE, MAE, PSNR, SSIM, SNR.
    """
    def __init__(self, model_config: Dict[str, Any], checkpoint_path: str):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load Model
        self.model = ModelRegistry.create(model_config.get("family", "unet"), model_config)
        # In a real scenario, we would load state_dict here:
        # self.model.load_state_dict(torch.load(checkpoint_path))
        self.model.to(self.device)
        self.model.eval()
        
    def evaluate_dataset(self, dataset: SeismicDataset) -> Dict[str, float]:
        """
        Run simple evaluation loop.
        """
        mse_list, mae_list, psnr_list, ssim_list, snr_list = [], [], [], [], []
        
        loader = torch.utils.data.DataLoader(dataset, batch_size=16)
        
        with torch.no_grad():
            for batch in loader:
                x = batch["input"].to(self.device).float().unsqueeze(1)
                y = batch.get("target").to(self.device).float().unsqueeze(1)
                
                # Forward
                y_hat = self.model(x)
                
                # Metrics
                mse = F.mse_loss(y_hat, y).item()
                mae = F.l1_loss(y_hat, y).item()
                
                # SNR
                noise = y - y_hat
                signal_power = torch.mean(y**2)
                noise_power = torch.mean(noise**2)
                snr = 10 * torch.log10(signal_power / (noise_power + 1e-8)).item()
                
                # PSNR
                psnr = 10 * torch.log10(torch.tensor(1.0) / (mse + 1e-8)).item()
                
                # SSIM
                ssim_val = ssim(y_hat, y)
                
                mse_list.append(mse)
                mae_list.append(mae)
                snr_list.append(snr)
                psnr_list.append(psnr)
                ssim_list.append(ssim_val)
                
        metrics = {
            "mse": np.mean(mse_list),
            "mae": np.mean(mae_list),
            "snr": np.mean(snr_list),
            "psnr": np.mean(psnr_list),
            "ssim": np.mean(ssim_list)
        }
        
        logger.info(f"Benchmark Results: {json.dumps(metrics, indent=2)}")
        return metrics

if __name__ == "__main__":
    # Example Usage
    pass
