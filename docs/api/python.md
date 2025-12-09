# Python API Reference

[![PyPI](https://img.shields.io/pypi/v/promethium-seismic.svg)](https://pypi.org/project/promethium-seismic/)
[![Python](https://img.shields.io/pypi/pyversions/promethium-seismic.svg)](https://pypi.org/project/promethium-seismic/)

Promethium provides a state-of-the-art (SoTA) Python implementation for seismic data recovery and reconstruction.

**PyPI Package:** [https://pypi.org/project/promethium-seismic/](https://pypi.org/project/promethium-seismic/)

## Installation

```bash
pip install promethium-seismic==1.0.4
```

### Optional Dependencies

```bash
# Visualization support
pip install promethium-seismic[viz]

# Server components (FastAPI, Celery, Redis)
pip install promethium-seismic[server]

# All optional dependencies
pip install promethium-seismic[all]
```

### Development Installation

```bash
git clone https://github.com/olaflaitinen/promethium.git
cd promethium
pip install -e ".[dev]"
```

## Quick Start

```python
import promethium as pm
from promethium import read_segy, SeismicRecoveryPipeline

# Load seismic data
data = read_segy("survey.sgy")

# Create recovery pipeline
pipeline = SeismicRecoveryPipeline.from_preset("unet_denoise_v1")

# Run reconstruction
result = pipeline.run(data)

# Evaluate
metrics = pm.evaluate_reconstruction(data.values, result)
print(metrics)
```

---

## Core Types

### SeismicDataset

```python
from promethium import SeismicDataset

# Create from NumPy array
ds = SeismicDataset(traces, dt=0.004)

# Properties
ds.n_traces      # Number of traces
ds.n_samples     # Samples per trace
ds.time_axis     # Time vector

# Methods
ds.normalize(method="max")  # "max", "rms", "standard"
ds.subset_traces(start, end)
ds.time_window(t_start, t_end)
```

### VelocityModel

```python
from promethium import VelocityModel

# Constant velocity
vm = VelocityModel.constant(nx=100, nz=50, velocity=2000)

# Linear gradient
vm = VelocityModel.linear(nx=100, nz=50, v_top=1500, v_bottom=4000)

# Interpolation
v = vm.interpolate_at(x=500, z=250)
```

---

## I/O Functions

```python
from promethium.io import read_segy, write_segy, read_miniseed

# SEG-Y
data = read_segy("survey.sgy")
write_segy(data, "output.sgy")

# MiniSEED
data = read_miniseed("recording.mseed")

# Synthetic data
data = pm.synthetic(n_traces=100, n_samples=500, dt=0.004)
```

---

## Signal Processing

```python
from promethium.signal import bandpass_filter, wiener_filter, remove_dc

# Bandpass filter
filtered = bandpass_filter(data, low_freq=5, high_freq=80)

# Wiener filter
denoised = wiener_filter(data)

# Remove DC offset
centered = remove_dc(data)
```

---

## Recovery Algorithms

### Matrix Completion (ISTA)

```python
from promethium.ml import matrix_completion_ista

completed = matrix_completion_ista(
    observed=traces,
    mask=mask,
    lambda_=0.1,
    max_iter=100
)
```

### Compressive Sensing (FISTA)

```python
from promethium.ml import compressive_sensing_fista

recovered = compressive_sensing_fista(
    y=measurements,
    A=sensing_matrix,
    lambda_=0.1,
    max_iter=100
)
```

### Deep Learning Models

```python
from promethium.ml import load_model, reconstruct

# Load pre-trained model
model = load_model("unet-v2-reconstruction")

# Reconstruct
result = reconstruct(model, data, missing_traces=[10, 15, 23])
```

---

## Pipelines

```python
from promethium import SeismicRecoveryPipeline

# From preset
pipeline = SeismicRecoveryPipeline.from_preset("matrix_completion")
pipeline = SeismicRecoveryPipeline.from_preset("unet_denoise_v1")

# Custom configuration
pipeline = SeismicRecoveryPipeline(
    preprocessing=["remove_dc", "bandpass"],
    model="unet-v2",
    postprocessing=["normalize"]
)

# Run
result = pipeline.run(data)
```

---

## Evaluation Metrics

```python
from promethium import evaluate_reconstruction
from promethium.metrics import compute_snr, compute_mse, compute_psnr, compute_ssim

# Individual metrics
snr = compute_snr(original, recovered)
mse = compute_mse(original, recovered)
psnr = compute_psnr(original, recovered)
ssim = compute_ssim(original, recovered)

# All metrics
metrics = evaluate_reconstruction(original, recovered)
```

---

## Cross-Language Consistency

All implementations produce numerically consistent results:

| Metric | Tolerance |
|--------|-----------|
| SNR | 0.1 dB |
| MSE | 1e-6 |
| PSNR | 0.1 dB |
| SSIM | 1e-4 |

---

## Version

```python
import promethium
print(promethium.__version__)
# 1.0.4
```
