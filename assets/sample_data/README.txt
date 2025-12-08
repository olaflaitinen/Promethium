# Promethium Sample Data

This directory contains sample seismic data files for testing and demonstration.

## Available Samples

- `sample_2d.sgy` - Small 2D seismic line (100 traces, 1000 samples)
- `sample_gather.sgy` - Common midpoint gather (50 traces)
- `sample_noise.sgy` - Noisy data for denoising tests

## Usage

```python
from promethium.io import read_segy

data = read_segy("assets/sample_data/sample_2d.sgy")
print(f"Traces: {data.n_traces}, Samples: {data.n_samples}")
```

## Note

These are synthetic data files generated for testing purposes only.
They do not represent real seismic surveys.

Copyright (c) 2025 Olaf Yunus Laitinen Imanov
