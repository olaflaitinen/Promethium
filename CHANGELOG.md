# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-07

### Production Release
- **Feature Complete**: All roadmap phases (Foundation, Advanced Recovery, Scale) implemented.
- **Advanced Recovery**: Standardized PINNs and Compressive Sensing modules.
- **Scale**: Cloud I/O and Distributed Training fully integrated.
- **Verification**: Validated against synthetic benchmarks.
- **Advanced Recovery**: Implemented Physics-Informed Neural Networks (`PINNs`) and optimized Matrix Completion.
- **Scale**: Cloud I/O adapters (S3/Azure) and Distributed Training support (PyTorch Lightning).
- **Visualization**: Interactive Plotly-based seismic viewer in Frontend.
- **Deployment**: Helm charts for Kubernetes support.
- **Core**: Robust `SeismicDataset` model with xarray backend.
- **I/O**: Memory-mapped SEG-Y reader with rigorous header validation.
- **Signal**: Butterworth filters (bandpass, lowpass, highpass) and predictive deconvolution.
- **ML**: U-Net architecture for seismic interpolation.
- **API**: FastAPI backend with `/datasets` and `/jobs` endpoints.
- **UI**: React-based dashboard for dataset and job management.

## [0.1.0] - 2025-12-07

### Initial Release
- Project scaffolding and architecture definition.
