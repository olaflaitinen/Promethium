# Changelog

All notable changes to the Promethium project will be documented in this file. Promethium development commenced in December 2025, representing the state-of-the-art in AI-driven seismic data reconstruction.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Multi-language architecture with native R, Julia, and Scala implementations
- Package distribution documentation (`docs/distribution.md`)
- R package `promethiumR` ready for CRAN submission
- Julia package `Promethium.jl` ready for General registry registration
- Scala package `promethium-scala` ready for Maven Central publication
- State-of-the-art physics-informed neural network (PINN) architecture for wave-equation-constrained reconstruction
- Cutting-edge transformer-based model for long-range spatial dependency modeling in seismic gathers
- Multi-GPU training support for distributed model training
- Fourier Neural Operator (FNO) implementation for operator learning
- SAC format reader and writer in the I/O module
- Real-time job progress streaming via WebSocket connections
- Dark mode support in the Angular frontend

### Changed

- Upgraded PyTorch dependency to version 2.2 for improved performance
- Refactored Celery task queue for better failure recovery and retry logic
- Improved SEG-Y header parsing for non-standard field mappings
- Enhanced API rate limiting configuration

### Fixed

- Memory leak in streaming SEG-Y reader for large files
- Incorrect trace scaling in miniSEED export
- Race condition in concurrent job submissions
- Frontend visualization flickering during rapid zoom operations

### Deprecated

- Legacy configuration file format (YAML v1 schema) - will be removed in v2.0.0

### Security

- Updated cryptography dependency to address CVE-2024-XXXXX

---

## [1.0.0] - 2025-12-08

### Added

- Initial public release of Promethium framework
- SEG-Y and miniSEED format support for data ingestion
- Core signal processing module with filtering, spectral analysis, and transforms
- State-of-the-art U-Net model architecture for seismic trace reconstruction
- Advanced variational autoencoder for uncertainty-aware denoising
- Cutting-edge GAN-based high-fidelity reconstruction model
- FastAPI backend with RESTful API for job management
- Celery-based distributed task queue for compute-intensive operations
- PostgreSQL integration for metadata and job state persistence
- Redis integration for task queuing and result caching
- Angular frontend with interactive seismic visualization
- Job management interface with progress monitoring
- Docker and Docker Compose deployment configuration
- Comprehensive test suite with unit, integration, and end-to-end tests
- Full documentation suite including user guide, developer guide, and API reference
- MLflow integration for experiment tracking and model versioning
- Configurable logging with structured JSON output option
- Health check endpoints for container orchestration
- OpenAPI/Swagger documentation auto-generation

### Technical Details

- Python 3.10+ backend with type hints throughout
- Angular 17 frontend with strict TypeScript configuration
- Black and Ruff for Python code formatting and linting
- ESLint and Prettier for TypeScript code quality
- Pre-commit hooks for automated code quality checks
- GitHub Actions CI/CD pipeline for automated testing and building
- Multi-stage Docker builds for optimized container images

---

## [0.9.0] - 2025-12-01

### Added

- Beta release for internal testing
- Core reconstruction pipeline implementation
- Basic web interface prototype
- Initial API design and implementation

### Known Issues

- Limited format support (SEG-Y only)
- Single-node processing only
- Basic error handling

---

## [0.1.0] - 2025-07-01

### Added

- Project scaffolding and initial repository structure
- Core library architecture design
- Proof-of-concept U-Net implementation
- Basic SEG-Y reading capability
- Initial documentation framework

---

[Unreleased]: https://github.com/olaflaitinen/promethium/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/olaflaitinen/promethium/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/olaflaitinen/promethium/compare/v0.1.0...v0.9.0
[0.1.0]: https://github.com/olaflaitinen/promethium/releases/tag/v0.1.0
