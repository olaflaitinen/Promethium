# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-12-07

### Added
- **Angular Frontend**: Complete rewrite of the user interface using Angular v17+.
- **Docker Architecture**: Centralized container configuration in `docker/`.
- **Documentation**: Comprehensive guide suite in `docs/` covering Architecture, Deployment, and User workflows.
- **Deep Learning**: Integrated `PromethiumLightningModule` for distributed training.

### Changed
- **Refactor**: Repository structure optimized for modularity (`src/promethium/core`, `io`, `signal`, `ml`).
- **Build System**: Removed Vite; standardized on Angular CLI for frontend builds.
- **License**: Adopted CC BY-NC 4.0.

### Fixed
- **Docker Sync**: Improved container startup order and health checks.
- **Documentation**: Standardized tone and removed non-professional elements.
