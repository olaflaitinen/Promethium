import pytorch_lightning as pl
import torch
from torch import nn
from promethium.ml.models import UNet
from typing import Optional

class PromethiumLightningModule(pl.LightningModule):
    """
    PyTorch Lightning wrapper for Distributed Training (Multi-GPU).
    """
    def __init__(self, learning_rate: float = 1e-3, **model_kwargs):
        super().__init__()
        self.save_hyperparameters()
        self.model = UNet(**model_kwargs)
        self.criterion = nn.MSELoss()

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, mask = batch
        # Input to model: Masked data
        masked_input = x * mask
        y_hat = self.model(masked_input)
        
        # Loss calculation (Self-supervised or supervised depending on task)
        # Simply reconsturction loss for now
        loss = self.criterion(y_hat, x)
        self.log('train_loss', loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.hparams.learning_rate)

def train_distributed(
    train_loader, 
    val_loader, 
    accelerator: str = "auto", 
    devices: int = 1, 
    epochs: int = 10
):
    """
    Launch distributed training.
    """
    model = PromethiumLightningModule()
    trainer = pl.Trainer(
        accelerator=accelerator,
        devices=devices,
        max_epochs=epochs,
        strategy="ddp" if devices > 1 else "auto"
    )
    trainer.fit(model, train_loader, val_loader)
