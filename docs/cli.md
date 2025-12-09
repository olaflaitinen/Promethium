# Command-Line Interface

Promethium provides a command-line interface for running seismic data recovery pipelines directly from the terminal.

## Installation

```bash
pip install promethium-seismic[cli]
```

## Commands

### Run Pipeline

Execute a recovery pipeline on seismic data:

```bash
promethium run input.sgy output.sgy --pipeline matrix_completion
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--pipeline`, `-p` | Pipeline preset name | `matrix_completion` |
| `--config`, `-c` | Path to YAML configuration | None |
| `--lambda` | Regularization parameter | 0.1 |
| `--max-iter` | Maximum iterations | 100 |
| `--verbose`, `-v` | Verbose output | False |

**Examples:**

```bash
# Matrix completion with custom parameters
promethium run noisy.sgy recovered.sgy -p matrix_completion --lambda 0.05

# Wiener denoising
promethium run noisy.sgy denoised.sgy -p wiener -v

# Using configuration file
promethium run input.h5 output.h5 -c pipeline_config.yaml
```

### Evaluate Reconstruction

Compare reconstructed data against ground truth:

```bash
promethium evaluate reference.npy estimate.npy
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--metrics`, `-m` | Comma-separated metrics | `snr,mse,psnr,ssim` |
| `--output`, `-o` | Save results to JSON | None |

**Examples:**

```bash
# Standard evaluation
promethium evaluate truth.npy recon.npy

# Specific metrics with JSON output
promethium evaluate truth.npy recon.npy -m snr,psnr -o metrics.json
```

### List Datasets

Show available example datasets:

```bash
promethium datasets
```

### List Models

Show available pipeline presets:

```bash
promethium models
```

### Version

Display version information:

```bash
promethium version
```

## Pipeline Presets

| Name | Type | Description |
|------|------|-------------|
| `matrix_completion` | Classical | Nuclear norm minimization via ISTA |
| `wiener` | Classical | Frequency-domain Wiener filter |
| `fista` | Classical | Fast ISTA for sparse recovery |
| `unet_v1` | Deep Learning | 4-level U-Net for interpolation |
| `autoencoder` | Deep Learning | Convolutional autoencoder denoising |
| `pinn` | Physics-Informed | Wave equation constrained NN |

## Configuration Files

YAML configuration format:

```yaml
pipeline:
  name: matrix_completion
  preprocessing:
    normalize: true
    normalize_method: rms
  model:
    type: matrix_completion
    lambda: 0.1
    max_iter: 100
    tol: 1e-5
  postprocessing:
    denoise: false
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (file not found, invalid parameters, etc.) |
