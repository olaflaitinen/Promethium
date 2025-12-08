"""
Promethium Test Configuration

Pytest configuration and fixtures for the Promethium test suite.
"""

import os
import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root: Path) -> Path:
    """Return the test data directory."""
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture(scope="session")
def sample_segy_path(test_data_dir: Path) -> Path:
    """Return path to sample SEG-Y file."""
    return test_data_dir / "sample.sgy"


@pytest.fixture
def sample_traces():
    """Generate sample seismic trace data."""
    import numpy as np
    
    n_traces = 100
    n_samples = 1000
    sample_rate = 250.0  # Hz
    
    # Generate synthetic seismic data
    t = np.linspace(0, n_samples / sample_rate, n_samples)
    traces = np.zeros((n_traces, n_samples))
    
    for i in range(n_traces):
        # Add synthetic reflections
        traces[i] = (
            np.sin(2 * np.pi * 30 * t) * np.exp(-0.5 * t) +
            0.1 * np.random.randn(n_samples)
        )
    
    return {
        "traces": traces,
        "n_traces": n_traces,
        "n_samples": n_samples,
        "sample_rate": sample_rate,
    }


@pytest.fixture
def mock_model():
    """Create a mock reconstruction model for testing."""
    class MockModel:
        def __call__(self, x):
            return x  # Identity for testing
        
        def eval(self):
            return self
        
        def to(self, device):
            return self
    
    return MockModel()


# ============================================================================
# Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "gpu: marks tests requiring GPU"
    )
    config.addinivalue_line(
        "markers", "integration: marks integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--run-gpu",
        action="store_true",
        default=False,
        help="run GPU tests"
    )
