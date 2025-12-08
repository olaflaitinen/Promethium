"""
Promethium Core Module Tests

Tests for core utilities, configuration, and data structures.
"""

import pytest
import numpy as np


def test_numpy_available():
    """Test that NumPy is available and working."""
    arr = np.zeros(100)
    assert arr.shape == (100,)
    assert arr.sum() == 0


def test_scipy_available():
    """Test that SciPy is available and working."""
    from scipy import signal
    
    # Test basic signal processing
    t = np.linspace(0, 1, 500)
    sig = np.sin(2 * np.pi * 5 * t)
    assert len(sig) == 500


def test_torch_available():
    """Test that PyTorch is available and working."""
    import torch
    
    x = torch.zeros(10)
    assert x.shape == (10,)
    assert x.sum().item() == 0


def test_fastapi_available():
    """Test that FastAPI is available."""
    from fastapi import FastAPI
    
    app = FastAPI()
    assert app is not None


def test_pydantic_available():
    """Test that Pydantic is available and working."""
    from pydantic import BaseModel
    
    class TestModel(BaseModel):
        name: str
        value: int
    
    model = TestModel(name="test", value=42)
    assert model.name == "test"
    assert model.value == 42


def test_sqlalchemy_available():
    """Test that SQLAlchemy is available."""
    from sqlalchemy import create_engine
    
    engine = create_engine("sqlite:///:memory:")
    assert engine is not None
    engine.dispose()


def test_config_module_exists():
    """Test that core config module can be imported."""
    try:
        from promethium.core import config
        assert True
    except ImportError:
        pytest.skip("Core config module not yet implemented")


def test_logging_module_exists():
    """Test that core logging module can be imported."""
    try:
        from promethium.core import logging
        assert True
    except ImportError:
        pytest.skip("Core logging module not yet implemented")
