# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import pytorch_lightning as pl
import torch
import torch.nn.functional as F
from typing import Dict, Any, Optional

from promethium_seismic.ml.models.registry import ModelRegistry
from promethium_seismic.core.logging import get_logger

logger = get_logger(__name__)

class PromethiumModule(pl.LightningModule):
    """
    Standard PyTorch Lightning Module for Promethium.
    Handles training loop, logging, and optimization.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.save_hyperparameters()
        self.config = config
        
        # Instantiate Model
        model_name = config.get("model", {}).get("family", "unet")
        model_config = config.get("model", {})
        self.model = ModelRegistry.create(model_name, model_config)
        
        # Loss Configuration
        self.loss_type = config.get("training", {}).get("loss", "mse")

    def forward(self, x):
        return self.model(x)

    def configure_optimizers(self):
        lr = self.config.get("training", {}).get("lr", 1e-3)
        optimizer = torch.optim.AdamW(self.parameters(), lr=lr)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": scheduler,
            "monitor": "val_loss"
        }

    def _compute_loss(self, batch, batch_idx):
        x = batch["input"]
        y = batch.get("target", x) # Autoencoder target is input
        
        y_hat = self(x)
        
        if self.loss_type == "mse":
            loss = F.mse_loss(y_hat, y)
        elif self.loss_type == "l1":
            loss = F.l1_loss(y_hat, y)
        else:
            loss = F.mse_loss(y_hat, y)
            
        return loss

    def training_step(self, batch, batch_idx):
        loss = self._compute_loss(batch, batch_idx)
        self.log("train_loss", loss, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        loss = self._compute_loss(batch, batch_idx)
        self.log("val_loss", loss, prog_bar=True)
        return loss

    def test_step(self, batch, batch_idx):
        loss = self._compute_loss(batch, batch_idx)
        self.log("test_loss", loss)
        return loss


class PromethiumTrainer(pl.Trainer):
    """
    Wrapper around PyTorch Lightning Trainer with Promethium defaults.
    """
    def __init__(self, **kwargs):
        # Set default callbacks or configuration if needed
        super().__init__(**kwargs)

