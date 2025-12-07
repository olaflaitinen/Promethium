import torch
import numpy as np
from typing import Optional, Tuple
from pathlib import Path
from .models import UNet
from .pinns import PhysicsInformedNN

class InferencePipeline:
    """
    Standardized inference pipeline for Promethium ML models.
    Handles model loading, patch-based inference, and reconstruction.
    """
    def __init__(self, model_path: str, model_type: str = "unet", device: str = "auto"):
        self.model_path = model_path
        self.model_type = model_type.lower()
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() and device == "auto" else "cpu"
        )
        self.model = self._load_model()
        self.model.eval()
        self.model.to(self.device)

    def _load_model(self) -> torch.nn.Module:
        if self.model_type == "unet":
            model = UNet(in_channels=1, out_channels=1)
        elif self.model_type == "pinn":
            model = PhysicsInformedNN()
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Load weights
        if Path(self.model_path).exists():
           checkpoint = torch.load(self.model_path, map_location=self.device)
           
           # Handle both full checkpoint dicts and direct state_dicts
           if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
               model.load_state_dict(checkpoint["state_dict"])
           else:
               model.load_state_dict(checkpoint)
        else:
            # For testing/demo purposes, we allow initialization without weights 
            # if the file doesn't exist, but warn heavily.
            print(f"WARNING: Model weights not found at {self.model_path}. Using random initialization.")
            
        return model

    def predict(self, data: np.ndarray, patch_size: Tuple[int, int] = (64, 64), stride: Tuple[int, int] = (32, 32)) -> np.ndarray:
        """
        Run inference on a full 2D seismic section using tiling/patching.
        """
        # Ensure input is float32 and normalized
        original_shape = data.shape
        data_norm = (data - np.mean(data)) / (np.std(data) + 1e-9)
        inputs = torch.from_numpy(data_norm).float()
        
        # Add channel and batch dims: (1, 1, H, W)
        inputs = inputs.unsqueeze(0).unsqueeze(0)
        
        # TODO: Implement proper tiling logic using torch.nn.functional.unfold/fold 
        # or manual loop for large datasets to avoid OOM.
        # For 'v1.0.0', implementing a naive full-image pass if size permits, 
        # or center-crop strategy.
        
        # Assuming data fits in memory for this implementation step
        with torch.no_grad():
            inputs = inputs.to(self.device)
            outputs = self.model(inputs)
            outputs = outputs.cpu().numpy().squeeze()
            
        # Denormalize (simplified)
        result = outputs * (np.std(data) + 1e-9) + np.mean(data)
        
        return result
