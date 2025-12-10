"""
Promethium Tools Package

Utility modules for the Promethium seismic data recovery framework.
These tools provide functionality for:
- Dataset management and downloading
- Experiment tracking and logging
- Pipeline configuration and execution
- Benchmarking and comparison

Usage:
    from tools.dataset_downloader import DatasetManager
    from tools.experiment_logger import ExperimentLogger
    from tools.pipeline_runner import run_pipeline_from_config
"""

from pathlib import Path

# Package metadata
__version__ = "1.0.4"
__author__ = "Promethium Team"

# Convenience imports
try:
    from .dataset_downloader import DatasetManager, download_dataset, list_datasets
except ImportError:
    pass

try:
    from .experiment_logger import ExperimentLogger, create_experiment
except ImportError:
    pass

try:
    from .pipeline_runner import run_pipeline_from_config, load_config
except ImportError:
    pass

# Package paths
TOOLS_DIR = Path(__file__).parent
ROOT_DIR = TOOLS_DIR.parent
DATASETS_DIR = ROOT_DIR / "datasets"
CONFIGS_DIR = ROOT_DIR / "configs"
EXPERIMENTS_DIR = ROOT_DIR / "experiments"

__all__ = [
    "DatasetManager",
    "download_dataset", 
    "list_datasets",
    "ExperimentLogger",
    "create_experiment",
    "run_pipeline_from_config",
    "load_config",
    "TOOLS_DIR",
    "ROOT_DIR",
    "DATASETS_DIR",
    "CONFIGS_DIR",
    "EXPERIMENTS_DIR",
]
