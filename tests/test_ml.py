# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Tests for the model architectures and training utilities.

Everything here needs the ml extra. When it is absent the whole module skips
rather than failing collection, so a contributor working on the core install
still gets a green run and a clear reason for what did not execute.
"""

import numpy as np
import pytest

torch = pytest.importorskip(
    "torch",
    reason="these tests need the ml extra: pip install 'promethium-seismic[ml]'",
)


def test_unet_import():
    """Test that UNet model can be imported."""
    from promethium_seismic.ml.models import UNet

    assert UNet is not None


def test_unet_forward_pass():
    """Test UNet forward pass with sample input."""
    from promethium_seismic.ml.models import UNet

    model = UNet(n_channels=1, n_classes=1)
    model.eval()

    # Create sample input (batch, channels, height, width)
    x = torch.randn(1, 1, 64, 64)

    with torch.no_grad():
        y = model(x)

    assert y.shape == (1, 1, 64, 64), f"Expected shape (1, 1, 64, 64), got {y.shape}"


def test_unet_trainable():
    """Test that UNet has trainable parameters."""
    from promethium_seismic.ml.models import UNet

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
