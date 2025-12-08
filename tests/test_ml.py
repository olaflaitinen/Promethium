"""
Promethium ML Module Tests

Tests for machine learning models and training utilities.
"""

import pytest
import torch
import numpy as np


def test_unet_import():
    """Test that UNet model can be imported."""
    from promethium.ml.models import UNet
    assert UNet is not None


def test_unet_forward_pass():
    """Test UNet forward pass with sample input."""
    from promethium.ml.models import UNet
    
    model = UNet(n_channels=1, n_classes=1)
    model.eval()
    
    # Create sample input (batch, channels, height, width)
    x = torch.randn(1, 1, 64, 64)
    
    with torch.no_grad():
        y = model(x)
    
    assert y.shape == (1, 1, 64, 64), f"Expected shape (1, 1, 64, 64), got {y.shape}"


def test_unet_trainable():
    """Test that UNet has trainable parameters."""
    from promethium.ml.models import UNet
    
    model = UNet(n_channels=1, n_classes=1)
    
    params = list(model.parameters())
    assert len(params) > 0, "Model should have parameters"
    
    total_params = sum(p.numel() for p in params)
    assert total_params > 0, "Model should have trainable parameters"


def test_numpy_to_tensor_conversion():
    """Test conversion between numpy arrays and PyTorch tensors."""
    data = np.random.randn(100, 100).astype(np.float32)
    
    tensor = torch.from_numpy(data)
    assert tensor.shape == (100, 100)
    assert tensor.dtype == torch.float32
    
    back_to_numpy = tensor.numpy()
    np.testing.assert_array_almost_equal(data, back_to_numpy)
