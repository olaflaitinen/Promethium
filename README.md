# Promethium - Advanced Seismic Data Recovery and Reconstruction Framework

![License](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Angular](https://img.shields.io/badge/angular-17%2B-red.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)

Promethium is a production-grade framework designed for the systematic recovery, reconstruction, and enhancement of multi-channel seismic data. It unifies classical geophysical signal processing with modern deep learning architectures to address challenges in seismic data quality, including missing traces, noise contamination, and irregular sampling.

## Key Features

*   **Seismic Data Ingestion**: High-performance I/O for industry-standard formats including SEG-Y, SEG-2, miniSEED, and SAC.
*   **Signal Conditioning**: Industrial-grade modules for bandpass filtering, notch filtering, spectral gating, and predictive deconvolution.
*   **Advanced Recovery Algorithms**: Implementation of Matrix Completion (SoftImpute, Nuclear Norm Minimization) and Compressive Sensing/L1 minimization strategies.
*   **Deep Learning Integration**: PyTorch-based U-Net architectures, Denoising Autoencoders, and Physics-Informed Neural Networks (PINNs) specific to wavefield reconstruction.
*   **Job Orchestration**: Asynchronous task management using Celery and Redis for handling terabyte-scale datasets.
*   **Interactive Visualization**: Angular-based dashboard for real-time job monitoring, dataset inspection, and quality control.
*   **Scalable Deployment**: Fully dockerized architecture supporting microservices and cloud-native deployment.

## Architecture Summary

Promethium follows a modular, layered architecture:

*   **Core Library (`src/promethium/core`)**: Fundamental data models, configuration, and logging.
*   **I/O Layer (`src/promethium/io`)**: Robust readers and writers with memory-mapping capabilities.
*   **Signal Processing (`src/promethium/signal`)**: Classical filtering and deconvolution routines.
*   **Machine Learning (`src/promethium/ml`)**: Neural network models, training pipelines, and inference logic.
*   **Backend API (`src/promethium/api`)**: FastAPI-based REST interface.
*   **Workflows (`src/promethium/workflows`)**: Distributed task definitions.
*   **Frontend (`frontend/`)**: Angular v17+ application using Standalone Components and Signals.

For a detailed breakdown, please refer to the [Architecture Documentation](docs/architecture.md).

## Quick Start

### Prerequisites

*   Docker Engine (v20.10+)
*   Docker Compose (v2.0+)

### Quick Start (Docker)

To simplify evaluation, Promethium provides a Docker Compose configuration that orchestrates the API, Worker, Database (PostgreSQL), Message Broker (Redis), and Frontend.

**Command**:
```bash
docker compose -f docker/docker-compose.yml up --build -d
```

**Access Interfaces**:
*   **Web Dashboard**: http://localhost:3000
*   **API Documentation**: http://localhost:8000/docs

### Local Development (Hybrid)

You can run the backend and frontend independently for development.

**1. Backend (Python)**
```bash
# Setup environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[dev]

# Run API
uvicorn promethium.api.main:app --reload --port 8000
```

**2. Frontend (Angular)**
```bash
cd frontend
npm install
npm start  # Runs 'ng serve'
```

The frontend will be available at http://localhost:4200.

## Use Cases

*   **Exploration Geophysics**: Enhancing legacy datasets with sparse acquisition geometries.
*   **Reservoir Characterization**: Removing coherent noise to improve attribute analysis.
*   **Earthquake Monitoring**: Reconstructing gaps in continuous waveform streams.

## Documentation

*   [Overview](docs/overview.md)
*   [Architecture](docs/architecture.md)
*   [User Guide](docs/user-guide.md)
*   [Developer Guide](docs/developer-guide.md)
*   [API Reference](docs/api-reference.md)
*   [ML Pipelines](docs/ml-pipelines.md)
*   [Benchmarking](docs/benchmarking.md)
*   [Deployment Guide](docs/deployment-guide.md)

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license. See [LICENSE.md](LICENSE.md) for details.
