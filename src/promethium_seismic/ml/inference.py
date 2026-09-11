# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import torch
import numpy as np
import xarray as xr
from pathlib import Path
from tqdm import tqdm
from typing import Dict, Any, Tuple

from promethium_seismic.core.logging import get_logger
from promethium_seismic.core.config import get_settings
from promethium_seismic.ml.models.registry import ModelRegistry
from promethium_seismic.io.zarr_wrapper import load_zarr

logger = get_logger(__name__)
settings = get_settings()

class InferenceEngine:
    """
    Batched, Patch-based Inference Engine.
    Handles:
    - Loading large volumes
    - Sliding window extraction
    - Batched GPU inference
    - Window blending (Cosine weighted)
    - Reassembly
    """
    def __init__(self, model_path: str, device: str = None):
        self.device = device or settings.DEFAULT_DEVICE
        
        # Load Checkpoint & Config
        # In real scenario: load from .pt file
        # Mocking for implementation structure
        self.config = {"n_channels": 1, "n_classes": 1} # Mock
        model_name = "unet" # Mock
        
        self.model = ModelRegistry.create(model_name, self.config)
        self.model.to(self.device)
        self.model.eval()
        
    @torch.no_grad()
    def run(
        self, 
        input_path: str, 
        output_path: str,
        patch_size: int = 128,
        overlap: float = 0.25,
        batch_size: int = 8
    ):
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        logger.info(f"Starting inference on {input_path}")
        
        # Load Data
        if input_path.suffix == ".zarr":
            data = load_zarr(input_path)
        else:
            # Fallback or error
            raise ValueError(f"Unsupported format {input_path.suffix}. Convert to Zarr first.")
            
        n_traces, n_time = data.shape
        stride = int(patch_size * (1 - overlap))
        
        # Output Buffer
        output = np.zeros_like(data.values)
        weights = np.zeros_like(data.values)
        
        # Cosine Window for blending
        # 1D window
        w = np.sin(np.pi * np.arange(0.5, patch_size + 0.5) / patch_size)
        # 2D window
        window = np.outer(w, w)
        
        # generate patches
        patches = []
        coords = []
        
        for t in range(0, n_traces - patch_size + 1, stride):
            for s in range(0, n_time - patch_size + 1, stride):
                patch = data[t:t+patch_size, s:s+patch_size].values
                patches.append(patch)
                coords.append((t, s))
                
                if len(patches) == batch_size:
                    self._process_batch(patches, coords, output, weights, window)
                    patches = []
                    coords = []
                    
        # Process remaining
        if patches:
             self._process_batch(patches, coords, output, weights, window)
             
        # Normalize by weights
        output /= (weights + 1e-8)
        
        # Save
        # Reuse Zarr wrapper logic or save as specific reconstruction format
        # For now, just logging done
        logger.info("Inference complete. Saving results...")
        
    def _process_batch(self, patches, coords, output, weights, window):
        # Prepare Batch
        batch = np.array(patches) # B, H, W
        batch = torch.from_numpy(batch).unsqueeze(1).float().to(self.device) # B, 1, H, W
        
        # Infer
        pred = self.model(batch)
        pred = pred.cpu().numpy()[:, 0, :, :]
        
        # Accumulate
        for i, (t, s) in enumerate(coords):
            h, w = pred[i].shape
            output[t:t+h, s:s+w] += pred[i] * window
            weights[t:t+h, s:s+w] += window

# Notebook Helper Functions
def load_model(name: str) -> torch.nn.Module:
    """
    Mock loader for notebook usage.
    """
    config = {"n_channels": 1, "n_classes": 1} 
    model = ModelRegistry.create("unet", config)
    model.eval()
    return model

def reconstruct(model: torch.nn.Module, data: np.ndarray, missing_traces: list = None) -> np.ndarray:
    """
    Simple reconstruction wrapper for notebook demo.
    """
    # Simply run inference using the engine logic (or simplified forward pass)
    # For demo purposes, let's wrap logic around the model directly for single efficient pass
    # or handle data shape adjustment
    
    device = next(model.parameters()).device
    
    # Ensure correct shape (1, 1, H, W)
    inp = torch.from_numpy(data).float().unsqueeze(0).unsqueeze(0).to(device)
    
    with torch.no_grad():
        out = model(inp)
        
    return out.cpu().numpy()[0, 0]


def load_model(path: str, device: str = None) -> 'PromethiumModule':
    """
    Load a pre-trained model from a checkpoint.
    
    Args:
        path: Path to the .ckpt file or model directory.
        device: Device to load model on (e.g., 'cuda', 'cpu').
        
    Returns:
        Loaded PromethiumModule in eval mode.
    """
    from promethium_seismic.ml.train import PromethiumModule
    
    if device is None:
        device = settings.DEFAULT_DEVICE
    
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
    try:
        # Assuming path is a checkpoint file
        model = PromethiumModule.load_from_checkpoint(path, map_location=device)
        model.to(device)
        model.eval()
        model.freeze()
        return model
    except Exception as e:
        logger.error(f"Failed to load model from {path}: {e}")
        raise


def reconstruct(
    data: np.ndarray, 
    model: 'PromethiumModule', 
    device: str = None,
    patch_size: Tuple[int, int] = (128, 128),
    overlap: float = 0.25
) -> np.ndarray:
    """
    High-level convenience function for reconstruction.
    
    Args:
        data: Input seismic data (2D array).
        model: Loaded PromethiumModule.
        device: Computation advice.
        patch_size: Size of sliding window.
        overlap: Overlap fraction.
        
    Returns:
        Reconstructed numpy array.
    """
    engine = InferenceEngine(model, device=device, patch_size=patch_size, overlap=overlap)
    return engine.run(data)
