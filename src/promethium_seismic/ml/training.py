# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import torch
import torch.nn as nn
import numpy as np
from typing import Dict
from promethium_seismic.core.logging import logger
import os

def calculate_psnr(mse: float, max_val: float = 1.0) -> float:
    if mse == 0:
        return 100.0
    return 20 * np.log10(max_val / np.sqrt(mse))

def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0
    for inputs, masks in loader:
        inputs, masks = inputs.to(device), masks.to(device)
        
        # Target is the input (self-supervised for reconstruction)
        # Input to model is masked input
        masked_inputs = inputs * masks
        
        optimizer.zero_grad()
        outputs = model(masked_inputs)
        
        # Loss computed on known (masked=1) data? 
        # Or if we have ground truth, loss on unknown (masked=0)?
        # For self-supervised without external ground truth:
        # Actually usually: Input = corrupted, Target = Clean (simulated)
        # Here we simulated corruption in Dataset.__getitem__.
        # So inputs (raw from patch) is 'Clean', masked_inputs is 'Corrupted'.
        
        # Loss should be between Output and Clean.
        # But should we penalize missing regions? Yes, that's the point.
        loss = criterion(outputs, inputs)
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    return total_loss / len(loader)

def train_model(
    model: nn.Module, 
    train_loader: torch.utils.data.DataLoader, 
    val_loader: torch.utils.data.DataLoader,
    epochs: int = 10,
    lr: float = 1e-3,
    device: str = 'cpu',
    save_path: str = "model.pth"
) -> Dict[str, list]:
    
    device = torch.device(device if torch.cuda.is_available() else 'cpu')
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    
    history = {"train_loss": [], "val_loss": [], "val_psnr": []}
    
    logger.info(f"Starting training on {device} for {epochs} epochs")
    
    for epoch in range(epochs):
        train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_mse_accum = 0.0
        with torch.no_grad():
            for inputs, masks in val_loader:
                inputs, masks = inputs.to(device), masks.to(device)
                masked_inputs = inputs * masks
                outputs = model(masked_inputs)
                loss = criterion(outputs, inputs)
                val_loss += loss.item()
                val_mse_accum += loss.item() # Simplified per batch
                
        avg_val_loss = val_loss / len(val_loader)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(avg_val_loss)
        
        # Approx PSNR
        psnr = calculate_psnr(avg_val_loss) # Assuming standardized data ~ [-3,3] -> max_val?
        history["val_psnr"].append(psnr)
        
        logger.info(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss:.6f} | Val Loss: {avg_val_loss:.6f}")
        
    torch.save(model.state_dict(), save_path)
    logger.info(f"Model saved to {save_path}")
    return history
