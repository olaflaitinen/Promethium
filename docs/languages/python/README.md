# Python Guide for Promethium

## Installation

```bash
pip install promethium-seismic
```

Or from source:
```bash
git clone https://github.com/olaflaitinen/Promethium.git
cd Promethium
pip install -e ".[all]"
```

## Quick Start

```python
import promethium as pm

# Load data
dataset = pm.SeismicDataset(traces, dt=0.004)

# Create pipeline
pipeline = pm.SeismicRecoveryPipeline.from_preset("matrix_completion")

# Run recovery
result = pipeline.run(dataset)

# Evaluate
metrics = pm.evaluate_reconstruction(dataset.traces, result.traces)
print(f"SNR: {metrics['snr']:.2f} dB")
```

## Core Classes

### SeismicDataset

```python
from promethium import SeismicDataset

ds = SeismicDataset(
    traces=numpy_array,      # (n_traces, n_samples)
    dt=0.004,                # Sampling interval (s)
    coordinates=coord_array, # Optional
    metadata={"key": "val"}  # Optional
)

# Operations
ds_subset = ds.subset(trace_slice=slice(0, 50))
ds_norm = ds.normalize(method="rms")
```

### SeismicRecoveryPipeline

```python
from promethium import SeismicRecoveryPipeline

# From preset
pipe = SeismicRecoveryPipeline.from_preset("wiener")

# Custom config
pipe = SeismicRecoveryPipeline(
    name="custom",
    config={
        "model": {"type": "matrix_completion", "lambda": 0.1},
        "preprocessing": {"normalize": True}
    }
)

result = pipe.run(dataset)
```

## CLI Usage

```bash
# Run pipeline
promethium run input.segy output.segy --pipeline matrix_completion

# Evaluate reconstruction
promethium evaluate reference.segy reconstructed.segy

# List available models
promethium models list
```

## Advanced: Custom Models

```python
from promethium.ml.models import UNet

model = UNet(in_channels=1, out_channels=1, depth=4)
# Train with PyTorch...
```

See API reference for full documentation.
