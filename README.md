# Promethium – Advanced Seismic Data Recovery and Reconstruction Framework

![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![Status](https://img.shields.io/badge/status-active%20development-orange.svg)

Promethium is a production-grade, state-of-the-art framework designed for the systematic recovery, reconstruction, and enhancement of multi-channel seismic data. It unifies classical geophysical signal processing with modern deep learning architectures to address challenges in seismic data quality, including missing traces, noise contamination, and irregular sampling.

## Key Features

- **Seismic Data Ingestion**: High-performance I/O for industry-standard formats including SEG-Y, SEG-2, miniSEED, and SAC.
- **Signal Conditioning**: Industrial-grade modules for bandpass filtering, notch filtering, spectral gating, and predictive deconvolution.
- **Advanced Recovery Algorithms**: Implementation of Matrix Completion (SoftImpute, Nuclear Norm Minimization) and Compressive Sensing/L1 minimization strategies.
- **Deep Learning Integration**: PyTorch-based U-Net architectures, Denoising Autoencoders, and Physics-Informed Neural Networks (PINNs) specific to wavefield reconstruction.
- **Job Orchestration**: Asynchronous task management using Celery and Redis for handling terabyte-scale datasets.
- **Interactive Visualization**: React-based dashboard for real-time job monitoring, dataset inspection, and quality control.
- **Scalable Deployment**: Fully dockerized architecture supporting microservices and cloud-native deployment.

## Architecture Summary

Promethium follows a modular, layered architecture:

- **Core Library (`src/promethium/core`)**: Fundamental data models (`SeismicTrace`, `SeismicDataset`), configuration, and logging.
- **I/O Layer (`src/promethium/io`)**: Robust readers and writers with memory-mapping capabilities.
- **Signal Processing (`src/promethium/signal`)**: Classical filtering and deconvolution routines.
- **Machine Learning (`src/promethium/ml`)**: Neural network models, training pipelines, and inference logic.
- **Backend API (`src/promethium/api`)**: FASTAPI-based REST interface.
- **Workflows (`src/promethium/workflows`)**: Distributed task definitions.

For a detailed breakdown, please refer to the [Architecture Documentation](docs/architecture.md).

## Quick Start

### Prerequisites

- Docker Engine (v20.10+)
- Docker Compose (v2.0+)

### Running the Full Stack

To simplify evaluation, Promethium provides a Docker Compose configuration that orchestrates the API, Worker, Database (PostgreSQL), and Message Broker (Redis).

1. **Clone the Repository**
   ```bash
   git clone https://github.com/olaflaitinen/Promethium.git
   cd Promethium
   ```

2. **Launch Services**
   ```bash
   docker compose up --build -d
   ```

3. **Access Interfaces**
   - **Web Dashboard**: http://localhost:8000 (Hosted via API static mount or separate frontend service)
   - **API Documentation**: http://localhost:8000/docs

### Local Development (Python)

For algorithm development without Docker:

```bash
# Create environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -e .[dev]

# Run tests
pytest tests/
```

## Use Cases

- **Exploration Geophysics**: Enhancing legacy datasets with sparse acquisition geometries.
- **Reservoir Characterization**: Removing coherent noise to improve attribute analysis.
- **Earthquake Monitoring**: Reconstructing gaps in continuous waveform streams.

## Advanced Capabilities

### Physics-Informed Neural Networks (PINNs)
Promethium includes a `PhysicsInformedNN` module (`src/promethium/ml/pinns.py`) that incorporates the acoustic wave equation into the loss function, ensuring that reconstructed wavefields are physically consistent.

### High-Performance Recovery
The `SoftImpute` algorithm (`src/promethium/recovery/matrix_completion.py`) is optimized with truncated SVD for efficient handling of large-scale matrices.

### Cloud-Native I/O & Scale
- **Cloud Storage**: Built-in adapters (`src/promethium/io/cloud.py`) for S3 and Azure Blob Storage.
- **Distributed Training**: Helpers for multi-GPU training via PyTorch Lightning (`src/promethium/ml/training_distributed.py`).
- **Kubernetes**: Production-ready Helm charts (`charts/promethium`) for cluster deployment.


## Documentation

- [Overview](docs/overview.md)
- [Architecture](docs/architecture.md)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)
- [API Reference](docs/api-reference.md)
- [ML Pipelines](docs/ml-pipelines.md)
- [Benchmarking](docs/benchmarking.md)
- [Deployment Guide](docs/deployment-guide.md)

## Status

Promethium is currently in an **active development phase**. While core modules for ingestion and deep learning are functional, ongoing work focuses on extending the library of physics-based constraints. See the Future Roadmap section above for details. 

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license. See [LICENSE.md](LICENSE.md) for details.

## Citation

If you use Promethium in academic research, please cite:

```bibtex
@software{promethium2025,
  author = {Promethium Team},
  title = {Promethium: Advanced Seismic Data Recovery Framework},
  year = {2025},
  url = {https://github.com/olaflaitinen/Promethium}
}
```
