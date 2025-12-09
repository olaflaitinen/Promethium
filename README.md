# Promethium - Advanced Seismic Data Recovery and Reconstruction Framework

**A state-of-the-art, high-performance, AI-driven framework for seismic signal reconstruction, denoising, and geophysical data enhancement. Developed in December 2025 with cutting-edge deep learning architectures and production-grade engineering practices.**

---

[![Build Status](https://img.shields.io/github/actions/workflow/status/olaflaitinen/promethium/ci.yml?branch=main&style=flat-square&logo=github&label=Build)](https://github.com/olaflaitinen/promethium/actions)
[![Test Coverage](https://img.shields.io/codecov/c/github/olaflaitinen/promethium?style=flat-square&logo=codecov&label=Coverage)](https://codecov.io/gh/olaflaitinen/promethium)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Angular](https://img.shields.io/badge/Angular-17+-dd0031?style=flat-square&logo=angular)](https://angular.io/)
[![Node.js](https://img.shields.io/badge/Node.js-20+-339933?style=flat-square&logo=node.js)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/Docker-Available-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![Documentation](https://img.shields.io/badge/Docs-Latest-green?style=flat-square)](docs/)
[![Code Style: Black](https://img.shields.io/badge/Code%20Style-Black-000000?style=flat-square)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/badge/Linting-Ruff-D7FF64?style=flat-square)](https://github.com/astral-sh/ruff)
[![ESLint](https://img.shields.io/badge/ESLint-Configured-4B32C3?style=flat-square&logo=eslint)](https://eslint.org/)
[![Maintenance](https://img.shields.io/badge/Maintained-Yes-green?style=flat-square)](https://github.com/olaflaitinen/promethium/commits/main)
[![Non-Commercial](https://img.shields.io/badge/Use-Non--Commercial-orange?style=flat-square)](#license-and-non-commercial-use)

---

<p align="center">
  <img src="assets/branding/promethium-logo.png" alt="Promethium Logo - A dark, rounded waveform symbolizing signal continuity and reconstruction" width="320"/>
</p>

<p align="center">
  <em>Promethium: Illuminating hidden signals within seismic noise.</em>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architectural Overview](#architectural-overview)
- [Repository Structure](#repository-structure)
- [Technology Stack](#technology-stack)
- [Installation and Setup](#installation-and-setup)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [AI/ML and Data Engineering Highlights](#aiml-and-data-engineering-highlights)
- [Performance and Benchmarking](#performance-and-benchmarking)
- [Configuration](#configuration)
- [Development Guide](#development-guide)
- [Contributing](#contributing)
- [License and Non-Commercial Use](#license-and-non-commercial-use)
- [Citation](#citation)
- [Support and Contact](#support-and-contact)

---

## Overview

Promethium is a comprehensive, enterprise-grade, state-of-the-art framework designed to address the critical challenges of seismic data recovery, reconstruction, and enhancement. Initiated in December 2025, the framework integrates cutting-edge signal processing techniques with advanced artificial intelligence and machine learning models to deliver unprecedented quality in seismic data reconstruction. The system represents the convergence of the latest advances in deep learning (including transformer architectures, physics-informed neural networks, and neural operators) with robust, production-ready data engineering practices.

### Target Domains

Promethium serves professionals and researchers across multiple geophysical and seismological domains:

- **Exploration Geophysics**: Enhancing subsurface imaging for oil, gas, and mineral exploration through improved seismic reflection and refraction data quality.
- **Reservoir Characterization**: Enabling high-fidelity seismic attribute analysis for reservoir property estimation and fluid identification.
- **Earthquake Seismology**: Supporting earthquake monitoring networks with robust signal reconstruction for accurate source characterization.
- **Microseismic Monitoring**: Processing low signal-to-noise ratio microseismic events for hydraulic fracturing monitoring and induced seismicity analysis.
- **Engineering Seismology**: Providing enhanced ground motion records for seismic hazard assessment and structural engineering applications.

### Core Capabilities

The framework addresses fundamental data quality challenges inherent in seismic acquisition:

- **Missing Trace Reconstruction**: Interpolating gaps caused by acquisition geometry constraints, equipment failures, or access limitations.
- **Noise Attenuation**: Suppressing coherent and incoherent noise while preserving signal integrity and phase characteristics.
- **Signal Enhancement**: Improving signal-to-noise ratios through adaptive filtering and AI-driven denoising algorithms.
- **Data Regularization**: Converting irregularly sampled data to regular grids suitable for downstream processing workflows.

---

## Key Features

### Seismic Data Ingestion

- **Multi-Format Support**: Native reading and writing of industry-standard formats including SEG-Y (Rev 0, 1, 2), SEG-2, miniSEED, SAC, and GCF.
- **Metadata Preservation**: Complete header parsing and preservation throughout processing workflows.
- **Streaming Ingestion**: Memory-efficient streaming for large-scale datasets exceeding available RAM.
- **Quality Control**: Automated detection of trace anomalies, timing errors, and format inconsistencies.

### Signal Processing

- **Adaptive Filtering**: Time-varying and spatially-varying filter design incorporating local signal characteristics.
- **Spectral Analysis**: Multi-taper spectral estimation, spectrogram computation, and coherence analysis.
- **Time-Frequency Transforms**: Continuous and discrete wavelet transforms, S-transform, and matching pursuit decomposition.
- **Deconvolution**: Predictive deconvolution, spiking deconvolution, and minimum-phase wavelet estimation.
- **Velocity Analysis**: Semblance analysis, velocity spectrum computation, and NMO correction.

### State-of-the-Art AI/ML Reconstruction

- **U-Net Architectures**: Encoder-decoder networks with skip connections optimized for seismic trace reconstruction, including the latest Attention U-Net and Residual U-Net variants.
- **Variational Autoencoders**: Probabilistic generative models for uncertainty-aware reconstruction with state-of-the-art latent space regularization.
- **Generative Adversarial Networks**: Adversarial training for high-fidelity missing data synthesis using modern GAN architectures adapted for scientific data.
- **Physics-Informed Neural Networks (PINNs)**: Incorporating wave equation constraints into network training for physically consistent reconstructions, representing the cutting edge of scientific machine learning.
- **Transformer Models**: State-of-the-art attention-based architectures including Vision Transformers and Swin Transformers for capturing long-range spatial dependencies in seismic gathers.
- **Neural Operators**: Fourier Neural Operators (FNO) and DeepONet frameworks for learning solution operators of seismic wave propagation, representing 2025's most advanced approaches in operator learning.

### Physics-Informed Components

- **Wave Equation Constraints**: Embedding acoustic and elastic wave equation residuals into loss functions.
- **Velocity Model Integration**: Conditioning reconstruction on prior velocity model information.
- **Travel-Time Consistency**: Enforcing moveout relationships in reconstructed gathers.
- **Amplitude Variation with Offset**: Preserving AVO/AVA characteristics through physics-aware training.

### Data Engineering and Scalability

- **Distributed Processing**: Horizontal scaling across compute clusters using task queues and worker pools.
- **Batch Orchestration**: Pipeline-based processing of large survey datasets with checkpoint and resume capabilities.
- **Data Versioning**: Immutable data storage with complete lineage tracking and reproducibility.
- **Storage Backends**: Support for local filesystems, object storage (S3-compatible), and distributed filesystems.

### Angular Frontend

- **Interactive Visualization**: Real-time rendering of seismic traces, gathers, and sections with customizable color palettes.
- **Job Management**: Comprehensive interface for submitting, monitoring, and managing processing jobs.
- **Configuration UI**: Form-based configuration of processing parameters with validation and presets.
- **Result Comparison**: Side-by-side visualization of input and reconstructed data with difference displays.
- **Export Functionality**: Download of processed data, reports, and visualizations in multiple formats.

### Deployment and Integration

- **Containerized Deployment**: Production-ready Docker images with multi-stage builds for minimal footprint.
- **Orchestration Ready**: Kubernetes manifests and Helm charts for cloud-native deployment.
- **API-First Design**: RESTful API enabling integration with existing geophysical workflows and third-party applications.
- **Extensibility**: Plugin architecture for custom format readers, processing algorithms, and ML models.

---

## Architectural Overview

Promethium implements a state-of-the-art modular, layered architecture designed for maintainability, scalability, and extensibility. The system leverages cutting-edge technologies and best practices from both industry and academia to deliver production-grade seismic data processing capabilities.

```mermaid
flowchart TB
    subgraph Frontend["Angular Frontend"]
        FE[Visualization / Job Management / Configuration / Monitoring]
    end

    subgraph API["FastAPI Backend"]
        BE[Authentication / Request Validation / Job Submission / Results]
    end

    subgraph DataLayer["Data Layer"]
        PG[(PostgreSQL<br/>Metadata, Jobs, Users)]
        RD[(Redis<br/>Task Queue, Caching)]
        OS[(Object Storage<br/>Raw Data, Models, Results)]
    end

    subgraph Workers["Celery Worker Pool"]
        WK[Distributed Task Execution / GPU Workloads]
    end

    subgraph Core["Promethium Core Library"]
        IO[I/O Module<br/>Format R/W]
        SIG[Signal Module<br/>Processing]
        ML[ML Module<br/>Models, Training]
        WF[Workflows<br/>Pipelines]
        VAL[Validation<br/>QC Checks]
        UTL[Utilities<br/>Logging, Config]
    end

    Frontend -->|REST API / HTTPS| API
    API --> PG
    API --> RD
    API --> OS
    RD --> Workers
    Workers --> Core
    Core --> OS

    IO --- SIG
    SIG --- ML
    WF --- VAL
    VAL --- UTL
```

For comprehensive architectural documentation including component interactions, data flows, and deployment topologies, refer to [docs/architecture.md](docs/architecture.md).

---

## Repository Structure

```
promethium/
├── src/
│   └── promethium/
│       ├── __init__.py
│       ├── core/                 # Core utilities, configuration, exceptions
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── exceptions.py
│       │   └── logging.py
│       ├── io/                   # Data ingestion and export
│       │   ├── __init__.py
│       │   ├── segy.py
│       │   ├── miniseed.py
│       │   ├── sac.py
│       │   └── formats.py
│       ├── signal/               # Signal processing algorithms
│       │   ├── __init__.py
│       │   ├── filtering.py
│       │   ├── transforms.py
│       │   ├── deconvolution.py
│       │   └── spectral.py
│       ├── ml/                   # Machine learning models and training
│       │   ├── __init__.py
│       │   ├── models/
│       │   │   ├── unet.py
│       │   │   ├── autoencoder.py
│       │   │   ├── gan.py
│       │   │   └── pinn.py
│       │   ├── training.py
│       │   ├── inference.py
│       │   └── metrics.py
│       ├── api/                  # FastAPI backend application
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── routers/
│       │   ├── models/
│       │   ├── services/
│       │   └── dependencies.py
│       └── workflows/            # Pipeline orchestration
│           ├── __init__.py
│           ├── pipelines.py
│           └── tasks.py
├── frontend/                     # Angular web application
│   ├── src/
│   │   ├── app/
│   │   ├── assets/
│   │   └── environments/
│   ├── angular.json
│   ├── package.json
│   └── tsconfig.json
├── config/                       # Configuration files
│   ├── default.yaml
│   ├── production.yaml
│   └── development.yaml
├── docker/                       # Docker configurations
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── Dockerfile.worker
│   └── docker-compose.yml
├── tests/                        # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                         # Documentation
│   ├── overview.md
│   ├── architecture.md
│   ├── user-guide.md
│   └── ...
├── notebooks/                    # Jupyter notebooks for exploration
│   ├── demo_reconstruction.ipynb
│   └── model_training.ipynb
├── assets/                       # Static assets
│   └── branding/
│       └── promethium-logo.png
├── scripts/                      # Utility scripts
│   ├── setup_db.py
│   └── generate_docs.py
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
├── CITATION.md
├── SUPPORT.md
├── GOVERNANCE.md
├── LICENSE
├── pyproject.toml
└── .gitignore
```

### Directory Descriptions

| Directory | Purpose |
|-----------|---------|
| `src/promethium/core/` | Core utilities including configuration management, custom exception hierarchy, and structured logging. |
| `src/promethium/io/` | Format-specific readers and writers for seismic data formats with metadata handling. |
| `src/promethium/signal/` | Signal processing implementations including filtering, spectral analysis, and transforms. |
| `src/promethium/ml/` | Machine learning model definitions, training loops, inference pipelines, and evaluation metrics. |
| `src/promethium/api/` | FastAPI application with routers, request/response models, and business logic services. |
| `src/promethium/workflows/` | High-level pipeline definitions and Celery task implementations. |
| `frontend/` | Angular single-page application with components, services, and state management. |
| `config/` | YAML configuration files for different deployment environments. |
| `docker/` | Dockerfiles and orchestration configurations for containerized deployment. |
| `tests/` | Comprehensive test suites organized by testing scope. |
| `docs/` | Technical documentation in Markdown format. |
| `notebooks/` | Interactive Jupyter notebooks for experimentation and demonstration. |
| `assets/` | Static assets including branding materials and sample data. |
| `scripts/` | Administrative and utility scripts for development and deployment. |

---

## Technology Stack

### Backend Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Runtime | Python 3.10+ | Core application runtime |
| Web Framework | FastAPI | Asynchronous REST API with automatic OpenAPI documentation |
| Task Queue | Celery | Distributed task execution for compute-intensive operations |
| Message Broker | Redis | Task queue backend and result caching |
| Database | PostgreSQL | Persistent storage for metadata, jobs, and user management |
| ORM | SQLAlchemy | Database abstraction and query building |
| Migrations | Alembic | Database schema version control and migrations |
| Authentication | python-jose, passlib | JWT-based authentication and password hashing |
| Validation | Pydantic | Request/response validation and serialization |

### AI/ML Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Deep Learning | PyTorch | Neural network definition and training |
| Scientific Computing | NumPy, SciPy | Numerical operations and signal processing |
| Seismic Processing | ObsPy | Seismic data handling and format support |
| Data Structures | xarray | Multi-dimensional labeled array operations |
| Data Loading | PyTorch DataLoader | Efficient batched data loading with prefetching |
| Model Serving | TorchServe (optional) | Production model serving infrastructure |
| Experiment Tracking | MLflow | Model versioning, metrics tracking, and artifact storage |

### Frontend Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Angular 17+ | Single-page application framework |
| Language | TypeScript | Type-safe JavaScript development |
| State Management | NgRx | Reactive state management with Redux pattern |
| Reactive Extensions | RxJS | Reactive programming for asynchronous operations |
| UI Components | Angular Material | Material Design component library |
| HTTP Client | Angular HttpClient | API communication with interceptors |
| Visualization | D3.js, Plotly | Interactive seismic data visualization |
| Build System | Angular CLI | Development server, building, and testing |

### Infrastructure Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Containerization | Docker | Application containerization and isolation |
| Orchestration | Docker Compose | Multi-container local orchestration |
| CI/CD | GitHub Actions | Automated testing, building, and deployment |
| Code Quality | Black, Ruff, ESLint, Prettier | Code formatting and linting |
| Testing | pytest, Karma, Jasmine | Unit and integration testing frameworks |
| Documentation | MkDocs (optional) | Documentation site generation |

---

## Installation and Setup

### PyPI Installation (Recommended)

Install Promethium directly from PyPI:

```bash
pip install promethium-seismic==1.0.2
```

**PyPI Package:** [https://pypi.org/project/promethium-seismic/1.0.2/](https://pypi.org/project/promethium-seismic/1.0.2/)

This installs the core library with minimal dependencies, suitable for most use cases including Kaggle and Google Colab notebooks.

#### Optional Dependencies

Install with visualization support:

```bash
pip install promethium-seismic[viz]==1.0.0
```

Install with server components (FastAPI, Celery, Redis) for backend deployment:

```bash
pip install promethium-seismic[server]==1.0.0
```

Install all optional dependencies:

```bash
pip install promethium-seismic[all]==1.0.0
```

Install development dependencies:

```bash
pip install promethium-seismic[dev]==1.0.0
```

### Kaggle and Google Colab Usage

Promethium is designed to work seamlessly in cloud notebook environments:

```python
# Install in a notebook cell
!pip install promethium-seismic==1.0.2

import promethium
from promethium import read_segy, SeismicRecoveryPipeline

# Load seismic data (from Kaggle input or uploaded file)
data = read_segy("/kaggle/input/seismic-dataset/survey.sgy")

# Create and run reconstruction pipeline
pipeline = SeismicRecoveryPipeline.from_preset("unet_denoise_v1")
result = pipeline.run(data)

# Evaluate reconstruction quality
metrics = promethium.evaluate_reconstruction(data.values, result)
print(metrics)
```

Key considerations for notebook environments:
- GPU acceleration is automatically enabled when available
- The core library works on CPU-only environments
- Use `/kaggle/input/...` paths for Kaggle datasets
- Use `/content/...` paths for Colab uploaded files

### Prerequisites (for Development or Server Deployment)

For full development or server deployment, ensure the following software is installed:

- **Python**: Version 3.10 or higher
- **Node.js**: Version 20 or higher (for frontend development)
- **Docker**: Version 24 or higher (for containerized deployment)
- **Docker Compose**: Version 2.20 or higher

### Clone the Repository (for Development)

```bash
git clone https://github.com/olaflaitinen/promethium.git
cd promethium
```

### Option 1: Docker Deployment

The recommended approach for running the full Promethium server stack:

```bash
# Copy environment template and configure
cp .env.example .env
# Edit .env with your configuration

# Build and start all services
docker compose -f docker/docker-compose.yml up --build -d

# Verify services are running
docker compose -f docker/docker-compose.yml ps
```

The following services will be available:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:4200 | Angular web application |
| Backend API | http://localhost:8000 | FastAPI REST API |
| API Documentation | http://localhost:8000/docs | Interactive OpenAPI documentation |

### Option 2: Local Development Setup

For development without Docker:

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev,server]"

# Run tests
pytest tests/ -v

# Start the backend API server
uvicorn src.promethium.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Quick Start

This section provides a minimal end-to-end workflow to verify your Promethium installation.

### 1. Start Services

Using Docker Compose:

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 2. Access the Web Interface

Open your browser and navigate to http://localhost:4200.

### 3. Upload Sample Data

1. Navigate to the **Data** section in the sidebar.
2. Click **Upload** and select a SEG-Y file from the `assets/sample_data/` directory.
3. Wait for the upload and initial validation to complete.

### 4. Create a Reconstruction Job

1. Navigate to the **Jobs** section.
2. Click **New Job** and select **Reconstruction** as the job type.
3. Select your uploaded dataset as the input.
4. Choose a reconstruction model (e.g., `unet-v2-noise-reduction`).
5. Configure parameters or use defaults.
6. Click **Submit**.

### 5. Monitor Job Progress

1. The job will appear in the **Jobs** list with status updates.
2. Click on the job to view detailed progress and logs.

### 6. View Results

1. Once the job completes, navigate to **Results**.
2. Select the completed job to view reconstructed data.
3. Use the comparison view to see input versus output.
4. Export results in your preferred format.

---

## Usage Examples

### Python API

```python
from promethium.io import read_segy
from promethium.signal import bandpass_filter
from promethium.ml import load_model, reconstruct

# Load seismic data
data = read_segy("path/to/survey.sgy")

# Apply preprocessing
filtered = bandpass_filter(data, low_freq=5.0, high_freq=80.0)

# Load reconstruction model
model = load_model("unet-v2-reconstruction")

# Perform reconstruction
reconstructed = reconstruct(model, filtered, missing_traces=[10, 15, 23])

# Save results
reconstructed.to_segy("path/to/reconstructed.sgy")
```

### REST API

#### Submit a Reconstruction Job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "reconstruction",
    "input_dataset_id": "uuid-of-dataset",
    "model_id": "unet-v2-reconstruction",
    "parameters": {
      "missing_trace_strategy": "auto_detect",
      "output_format": "segy"
    }
  }'
```

#### Check Job Status

```bash
curl -X GET "http://localhost:8000/api/v1/jobs/<job-id>" \
  -H "Authorization: Bearer <token>"
```

#### Download Results

```bash
curl -X GET "http://localhost:8000/api/v1/jobs/<job-id>/results" \
  -H "Authorization: Bearer <token>" \
  -o reconstructed_data.sgy
```

### Angular UI Workflow

1. **Data Upload**: Use the drag-and-drop interface to upload SEG-Y or miniSEED files.
2. **Quality Control**: Review automated QC reports highlighting trace anomalies.
3. **Job Configuration**: Use the guided wizard to configure reconstruction parameters.
4. **Visualization**: Interactive trace viewer with zoom, pan, and color scale controls.
5. **Comparison**: Synchronized side-by-side view of original and reconstructed data.
6. **Export**: Download processed data with full header preservation.

---

## Example Notebooks

Promethium includes a comprehensive suite of 15 Jupyter notebooks for learning and experimentation. All notebooks are located in the `notebooks/` directory.

### Quick Start

```bash
pip install promethium-seismic==1.0.2
jupyter notebook notebooks/
```

### Notebook Catalog

| Notebook | Description | Level |
|----------|-------------|-------|
| [01_quickstart_basic_usage](notebooks/01_quickstart_basic_usage.ipynb) | Minimal end-to-end example | Beginner |
| [02_data_ingestion_and_quality_control](notebooks/02_data_ingestion_and_quality_control.ipynb) | Loading SEG-Y, miniSEED, SAC | Beginner |
| [03_signal_processing_basics](notebooks/03_signal_processing_basics.ipynb) | Filters and transforms | Beginner |
| [04_matrix_completion_and_compressive_sensing](notebooks/04_matrix_completion_and_compressive_sensing.ipynb) | Classical recovery | Intermediate |
| [05_deep_learning_unet_reconstruction](notebooks/05_deep_learning_unet_reconstruction.ipynb) | U-Net inference | Intermediate |
| [06_gan_based_high_fidelity_reconstruction](notebooks/06_gan_based_high_fidelity_reconstruction.ipynb) | GAN-based recovery | Advanced |
| [07_evaluation_metrics_and_visualization](notebooks/07_evaluation_metrics_and_visualization.ipynb) | SNR, PSNR, SSIM analysis | Intermediate |
| [08_kaggle_and_colab_integration](notebooks/08_kaggle_and_colab_integration.ipynb) | Cloud environment usage | Beginner |
| [09_backend_api_and_job_system_demo](notebooks/09_backend_api_and_job_system_demo.ipynb) | REST API integration | Advanced |
| [10_end_to_end_case_study_synthetic_data](notebooks/10_end_to_end_case_study_synthetic_data.ipynb) | Complete synthetic workflow | Intermediate |
| [11_end_to_end_case_study_real_world_data](notebooks/11_end_to_end_case_study_real_world_data.ipynb) | Real data processing | Advanced |
| [12_benchmarking_and_ablation_studies](notebooks/12_benchmarking_and_ablation_studies.ipynb) | Method comparison | Advanced |
| [13_data_engineering_pipelines_and_batch_jobs](notebooks/13_data_engineering_pipelines_and_batch_jobs.ipynb) | Batch processing | Advanced |
| [14_advanced_model_customization_and_training](notebooks/14_advanced_model_customization_and_training.ipynb) | Custom training | Advanced |
| [15_troubleshooting_and_best_practices](notebooks/15_troubleshooting_and_best_practices.ipynb) | Common issues | All |

### Recommended Learning Path

1. Start with **01_quickstart_basic_usage** for a minimal working example
2. Continue to **02_data_ingestion** to understand data loading
3. Explore **03_signal_processing** for preprocessing techniques
4. Move to **05_deep_learning_unet** for ML-based reconstruction
5. Use **08_kaggle_and_colab** for cloud deployment

See [docs/notebooks-overview.md](docs/notebooks-overview.md) for detailed documentation.

## AI/ML and Data Engineering Highlights

### Supported Model Architectures

| Model Family | Variants | Use Case |
|--------------|----------|----------|
| U-Net | Standard, Attention U-Net, Residual U-Net | General reconstruction, denoising |
| Autoencoder | VAE, Denoising AE, Sparse AE | Feature extraction, compression |
| GAN | Pix2Pix, SRGAN-adapted | High-fidelity reconstruction |
| PINN | Wave-constrained, Velocity-informed | Physics-consistent reconstruction |
| Transformer | Vision Transformer, Swin Transformer | Long-range dependency modeling |

### Training Workflow

1. **Data Preparation**: Convert seismic data to training-ready format with configurable patch extraction.
2. **Augmentation**: Apply domain-specific augmentations including noise injection, trace masking, and amplitude scaling.
3. **Training**: Distributed training with mixed precision, gradient accumulation, and early stopping.
4. **Validation**: Continuous validation with seismic-specific metrics.
5. **Checkpointing**: Model versioning with MLflow integration.

### Evaluation Metrics

- **Signal-to-Noise Ratio (SNR)**: Improvement in SNR after reconstruction.
- **Structural Similarity Index (SSIM)**: Perceptual quality measure.
- **Mean Squared Error (MSE)**: Pixel-wise reconstruction error.
- **Coherence Preservation**: Cross-correlation of reconstructed versus reference.
- **Spectral Fidelity**: Frequency content preservation analysis.

For detailed ML pipeline documentation, see [docs/ml-pipelines.md](docs/ml-pipelines.md).

For data engineering patterns and best practices, see [docs/data-engineering.md](docs/data-engineering.md).

---

## Performance and Benchmarking

### Performance Targets

| Operation | Target Throughput | Notes |
|-----------|-------------------|-------|
| SEG-Y Ingestion | 500 MB/s | SSD storage, streaming mode |
| Trace Filtering | 10,000 traces/s | Single CPU core |
| U-Net Inference | 100 gathers/s | NVIDIA A100 GPU |
| Reconstruction Job | < 5 min for 10 GB | Full pipeline, GPU-enabled |

### Benchmarking Suite

Promethium includes a comprehensive benchmarking suite for performance evaluation:

```bash
# Run full benchmark suite
python -m promethium.benchmarks.run_all

# Run specific benchmarks
python -m promethium.benchmarks.io_throughput
python -m promethium.benchmarks.ml_inference
```

For detailed benchmarking methodology and result interpretation, see [docs/benchmarking.md](docs/benchmarking.md).

---

## Configuration

Promethium uses a hierarchical configuration system with the following precedence (highest to lowest):

1. Environment variables
2. Command-line arguments
3. Environment-specific configuration files (`config/{environment}.yaml`)
4. Default configuration (`config/default.yaml`)

### Key Configuration Categories

| Category | Description | Configuration File Section |
|----------|-------------|---------------------------|
| Database | PostgreSQL connection parameters | `database.*` |
| Redis | Redis connection and pool settings | `redis.*` |
| Storage | Data storage paths and backends | `storage.*` |
| ML | Model paths, inference settings | `ml.*` |
| API | Server settings, CORS, rate limiting | `api.*` |
| Workers | Celery worker configuration | `workers.*` |

### Environment Variables

Essential environment variables:

```bash
# Database
PROMETHIUM_DATABASE_URL=postgresql://user:password@localhost:5432/promethium

# Redis
PROMETHIUM_REDIS_URL=redis://localhost:6379/0

# Security
PROMETHIUM_SECRET_KEY=your-secret-key-here
PROMETHIUM_JWT_ALGORITHM=HS256

# Storage
PROMETHIUM_DATA_DIR=/data/promethium
PROMETHIUM_MODEL_DIR=/models
```

For comprehensive configuration documentation, see [docs/configuration.md](docs/configuration.md).

---

## Development Guide

### Code Style

Promethium enforces consistent code style through automated tooling:

**Python:**
- Formatter: Black
- Linter: Ruff
- Type Checking: mypy

**TypeScript:**
- Formatter: Prettier
- Linter: ESLint
- Strict mode enabled

### Running Tests

```bash
# Backend tests
pytest tests/ -v --cov=src/promethium

# Frontend tests
cd frontend && npm test

# End-to-end tests
pytest tests/e2e/ -v
```

### Pre-Commit Hooks

Install pre-commit hooks to ensure code quality:

```bash
pip install pre-commit
pre-commit install
```

For detailed development workflows, environment setup, and contribution guidelines, see [docs/developer-guide.md](docs/developer-guide.md).

---

## Contributing

Contributions to Promethium are welcome and appreciated. The project accepts contributions in the following areas:

- Bug reports and feature requests via GitHub Issues
- Code contributions via Pull Requests
- Documentation improvements
- Test coverage enhancements
- Performance optimizations

Before contributing, please review:

- [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards
- [GOVERNANCE.md](GOVERNANCE.md) for project governance

---

## License and Non-Commercial Use

Promethium is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.

This license permits:
- Sharing and adapting the material for non-commercial purposes
- Attribution must be given to the original creators

This license prohibits:
- Commercial use without explicit permission
- Sublicensing

For the complete license text, see [LICENSE](LICENSE).

For commercial licensing inquiries, please contact the maintainers.

---

## Citation

If you use Promethium in academic research, please cite it appropriately. See [CITATION.md](CITATION.md) for recommended citation formats and BibTeX entries.

---

## Support and Contact

For support options, community resources, and contact information, see [SUPPORT.md](SUPPORT.md).

### Quick Links

- **Issue Tracker**: [GitHub Issues](https://github.com/olaflaitinen/promethium/issues)
- **Discussions**: [GitHub Discussions](https://github.com/olaflaitinen/promethium/discussions)
- **Documentation**: [docs/](docs/)

---

<p align="center">
  <strong>Promethium</strong> - Advancing seismic data science through intelligent reconstruction.
</p>
