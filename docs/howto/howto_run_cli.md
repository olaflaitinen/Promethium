# How to Run the Promethium CLI

This guide covers the installation and usage of the Promethium command-line interface for seismic data processing.

---

## Prerequisites

- Python 3.10 or higher
- pip package manager

## Installation

### Install from PyPI

```bash
pip install promethium-seismic[cli]
```

### Install from Source

```bash
git clone https://github.com/olaflaitinen/Promethium.git
cd Promethium
pip install -e ".[cli]"
```

---

## CLI Overview

The Promethium CLI provides commands for:

| Command | Description |
|---------|-------------|
| `promethium run` | Execute recovery pipelines |
| `promethium evaluate` | Compute quality metrics |
| `promethium ingest` | Convert raw seismic files |
| `promethium batch-run` | Run multiple configs in batch |
| `promethium datasets` | List available datasets |
| `promethium models` | List pipeline presets |
| `promethium experiments` | Manage experiment logs |
| `promethium version` | Show version information |

---

## Basic Usage

### Run a Recovery Pipeline

```bash
promethium run input.sgy output.sgy --pipeline matrix_completion --max-iter 200
```

Options:
- `--pipeline, -p`: Pipeline preset (matrix_completion, wiener, fista, unet)
- `--config, -c`: Path to YAML configuration file
- `--lambda`: Regularization parameter (default: 0.1)
- `--max-iter`: Maximum iterations (default: 100)
- `--verbose, -v`: Enable verbose output

### Evaluate Reconstruction Quality

```bash
promethium evaluate reference.npy reconstructed.npy --metrics snr,mse,ssim --output metrics.json
```

Options:
- `--metrics, -m`: Comma-separated list of metrics
- `--output, -o`: Save results to JSON file

Available metrics: snr, mse, psnr, ssim

### Ingest Raw Data

```bash
promethium ingest raw_data/ processed_data/ --format hdf5 --normalize
```

Options:
- `--format, -f`: Output format (hdf5, npy, zarr)
- `--normalize, -n`: Normalize traces
- `--verbose, -v`: Verbose output

### Batch Processing

```bash
promethium batch-run configs/pipelines/ --output results/ --experiment-id my_benchmark
```

Options:
- `--output, -o`: Output directory
- `--experiment-id`: Experiment ID for logging
- `--parallel, -j`: Number of parallel runs

---

## Configuration Files

### Pipeline Configuration

Create a YAML file to define your pipeline:

```yaml
# configs/pipelines/my_pipeline.yaml
pipeline:
  name: "matrix_completion"
  type: "classical"

input:
  path: "data/input.npy"
  format: "npy"

model:
  algorithm: "ista"
  lambda: 0.1
  max_iter: 200

output:
  path: "results/output"
  save_metrics: true
```

Run with:

```bash
promethium run input.npy output.npy --config configs/pipelines/my_pipeline.yaml
```

---

## Experiment Tracking

### List Experiments

```bash
promethium experiments list --dir experiments/logs/
```

### Show Experiment Details

```bash
promethium experiments show my_experiment --last 10
```

### Export to CSV

```bash
promethium experiments export my_experiment --format csv --output results.csv
```

---

## Examples

### Complete Workflow

```bash
# 1. Download a dataset
promethium datasets list

# 2. Ingest raw data
promethium ingest data/raw/ data/processed/ --format npy

# 3. Run reconstruction
promethium run data/processed/noisy.npy results/denoised.npy \
    --pipeline wiener --verbose

# 4. Evaluate results
promethium evaluate data/processed/clean.npy results/denoised.npy \
    --metrics snr,mse,ssim --output results/metrics.json

# 5. Check logs
promethium experiments list
```

---

## Troubleshooting

### CLI Not Found

Ensure the package is installed with CLI dependencies:

```bash
pip install promethium-seismic[cli]
```

### Missing Dependencies

If you see import errors, install required components:

```bash
pip install typer rich pyyaml
```

### GPU Support

For deep learning pipelines, ensure PyTorch CUDA is available:

```python
import torch
print(torch.cuda.is_available())
```

---

## See Also

- [Configuration Guide](../configuration.md)
- [API Reference](../api-reference.md)
- [Benchmarking Guide](../benchmarking.md)
