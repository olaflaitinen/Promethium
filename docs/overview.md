# Promethium Overview

Promethium is a research-grade framework designed to bridge the gap between classical geophysical processing and modern deep learning for seismic data reconstruction.

## Problem Statement

Seismic data acquisition is often constrained by logistical, financial, and environmental factors, leading to:
*   **Irregular Sampling**: Gaps in spatial coverage.
*   **Missing Traces**: Dead channels or rejected shots.
*   **Aliasing**: Insufficient sampling of high-frequency signal components.

These deficiencies compromise downstream processing tasks such as migration, inversion, and attribute analysis.

## Solution

Promethium provides a unified environment to apply and compare:
1.  **classical interpolation methods** (MWNI, POCS).
2.  **optimization-based recovery** (Matrix Completion, Compressive Sensing).
3.  **data-driven deep learning** (U-Nets, GANs).
4.  **physics-informed deep learning** (PINNs).

## Technology Stack

### Frontend
*   **Angular v17+**: Provides a robust, type-safe environment for building complex dashboards.
*   **Plotly.js**: High-performance rendering of seismic traces and heatmaps.
*   **RxJS**: Handles real-time data streams and state management.

### Backend
*   **Python 3.10+**: The lingua franca of scientific computing and AI.
*   **FastAPI**: High-performance, async-first web framework.
*   **PyTorch**: The backend for all deep learning modules.
*   **Celery/Redis**: Distributed task queue for managing long-running reconstruction jobs.

## Design Philosophy

*   **Modularity**: Algorithms are decoupled from I/O and visualization.
*   **Reproducibility**: All experiments are configuration-driven and versioned.
*   **Scalability**: Docker-first design ensures deployment consistency from laptop to cluster.
