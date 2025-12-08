# Promethium - Advanced Seismic Data Recovery and Reconstruction Framework
# Main package initialization

"""
Promethium is a state-of-the-art, AI-driven framework for seismic signal 
reconstruction, denoising, and geophysical data enhancement.

Developed in December 2025 with cutting-edge deep learning architectures
and production-grade engineering practices.

Copyright (c) 2025 Olaf Yunus Laitinen Imanov
Licensed under CC BY-NC 4.0
"""

__version__ = "1.0.0"
__author__ = "Olaf Yunus Laitinen Imanov"
__license__ = "CC BY-NC 4.0"

from promethium.core.config import settings
from promethium.core.logging import get_logger

__all__ = [
    "__version__",
    "__author__",
    "settings",
    "get_logger",
]
