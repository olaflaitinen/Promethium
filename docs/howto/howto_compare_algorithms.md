# How to Compare Algorithms

This guide explains how to use the Promethium benchmarking framework to compare seismic reconstruction algorithms systematically.

---

## Overview

The benchmarking system allows you to:
- Compare multiple algorithms on the same datasets
- Collect standardized quality metrics
- Generate reproducible comparison reports
- Track results over time

---

## Quick Start

### Run a Predefined Benchmark

```bash
python -m benchmarks.run_all configs/batch/classical_vs_ml.yaml
```

This runs the classical vs. ML comparison benchmark and outputs:
- JSON results file
- CSV summary table
- Comparison metrics

---

## Creating a Benchmark Configuration

### Benchmark Configuration Structure

Create a YAML file in `configs/batch/`:

```yaml
# configs/batch/my_comparison.yaml
benchmark:
  name: "my_algorithm_comparison"
  description: "Compare algorithm A vs algorithm B"
  
datasets:
  - id: synthetic_noisy
    path: "data/synthetic_noisy.npy"
    reference: "data/synthetic_clean.npy"

pipelines:
  - name: algorithm_a
    type: classical
    config:
      lambda: 0.1
      max_iter: 100
      
  - name: algorithm_b
    type: deep_learning
    config:
      weights: "models/model_b.pt"

metrics:
  primary:
    - snr
    - mse
    - ssim

output:
  results_dir: "benchmarks/results"
  save_csv: true
  generate_plots: true
```

### Configuration Sections

**benchmark**: Metadata about the benchmark

**datasets**: List of datasets to evaluate on
- `id`: Unique identifier
- `path`: Path to input data
- `reference`: Path to ground truth (for metrics)

**pipelines**: Algorithms to compare
- `name`: Algorithm identifier
- `type`: classical, deep_learning, physics_informed
- `config`: Algorithm-specific parameters

**metrics**: Quality metrics to compute
- `primary`: Main comparison metrics
- `secondary`: Additional metrics

**output**: Result output settings

---

## Running Benchmarks

### Command Line

```bash
# Run benchmark
python -m benchmarks.run_all configs/batch/my_comparison.yaml

# Specify output directory
python -m benchmarks.run_all configs/batch/my_comparison.yaml --output results/
```

### Programmatic

```python
from benchmarks.run_all import run_benchmark

results = run_benchmark(
    "configs/batch/my_comparison.yaml",
    output_dir="results/",
    verbose=True
)

# Access results
print(results["summary"])
for run in results["results"]:
    print(f"{run['pipeline']}: SNR={run['metrics'].get('snr', 'N/A'):.2f}")
```

---

## Analyzing Results

### Result Files

After running, find outputs in the results directory:
- `benchmark_<name>_<timestamp>.json` - Full results
- `benchmark_<name>_<timestamp>.csv` - Tabular summary

### JSON Structure

```json
{
  "benchmark": "classical_vs_ml",
  "timestamp": "20251210_120000",
  "summary": {
    "matrix_completion": {
      "snr": {"mean": 15.2, "std": 0.8, "min": 14.1, "max": 16.3}
    },
    "unet_v1": {
      "snr": {"mean": 18.5, "std": 0.5, "min": 17.9, "max": 19.2}
    }
  },
  "results": [...]
}
```

### Loading Results

```python
import json
import pandas as pd

# Load JSON
with open("benchmarks/results/benchmark_classical_vs_ml_20251210.json") as f:
    results = json.load(f)

# Load CSV
df = pd.read_csv("benchmarks/results/benchmark_classical_vs_ml_20251210.csv")
print(df.groupby("pipeline").mean())
```

---

## Visualization

### Built-in Comparison Table

```python
from benchmarks.run_all import print_comparison_table

with open("benchmarks/results/benchmark.json") as f:
    results = json.load(f)

print_comparison_table(results["summary"])
```

Output:
```
                    Benchmark Results Summary
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Pipeline          ┃ SNR             ┃ SSim            ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ matrix_completion │ 15.20 +/- 0.80  │ 0.85 +/- 0.02   │
│ unet_v1           │ 18.50 +/- 0.50  │ 0.92 +/- 0.01   │
└───────────────────┴─────────────────┴─────────────────┘
```

### Custom Plots

```python
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("benchmarks/results/benchmark.csv")

# Bar chart
pivot = df.pivot_table(values="snr", index="pipeline", aggfunc="mean")
pivot.plot(kind="bar", title="SNR by Algorithm")
plt.ylabel("SNR (dB)")
plt.savefig("benchmarks/results/snr_comparison.png")
```

---

## Best Practices

### Dataset Selection

- Use multiple datasets with varying characteristics
- Include both synthetic (with ground truth) and real data
- Document dataset properties in config

### Metric Selection

For seismic data, recommended metrics:
- **SNR**: Signal-to-noise ratio (primary)
- **SSIM**: Structural similarity
- **Frequency Correlation**: Spectral preservation

### Reproducibility

- Set random seeds in config
- Version control benchmark configs
- Log environment details

### Statistical Significance

- Run multiple repetitions
- Report mean and standard deviation
- Use appropriate statistical tests

---

## Predefined Benchmarks

### classical_vs_ml.yaml

Compares classical methods (Wiener, matrix completion) against deep learning (U-Net, autoencoder).

### fk_vs_unet_comparison.yaml

Focuses on interpolation: F-K domain vs U-Net approaches.

---

## See Also

- [Benchmark Runner Source](../../benchmarks/run_all.py)
- [Pipeline Configuration](./howto_run_cli.md#configuration-files)
- [Experiment Logging](./howto_log_experiments.md)
