# How to Log Experiments

This guide explains how to use the Promethium experiment tracking system to log pipeline runs, parameters, and results.

---

## Overview

The experiment logging system provides:
- Lightweight JSON-lines format storage
- No external service dependencies
- CLI inspection and export tools
- Python API for integration

---

## Quick Start

### Python API

```python
from tools.experiment_logger import ExperimentLogger

# Create logger
logger = ExperimentLogger("my_experiment")

# Start a run
run_id = logger.start_run(
    pipeline="unet_denoising",
    dataset="synthetic_noisy"
)

# Log parameters
logger.log_params({
    "learning_rate": 0.001,
    "epochs": 100,
    "batch_size": 16
})

# Log metrics
logger.log_metrics({
    "snr": 18.5,
    "mse": 0.0023,
    "ssim": 0.92
})

# End run
logger.end_run()
```

### CLI Integration

Experiment logging is automatically enabled when using CLI commands:

```bash
promethium batch-run configs/pipelines/ --experiment-id my_benchmark
```

---

## Experiment Logger API

### Creating a Logger

```python
from tools.experiment_logger import ExperimentLogger

logger = ExperimentLogger(
    experiment_id="my_experiment",
    logs_dir=Path("experiments/logs"),  # Optional: custom directory
)
```

### Starting a Run

```python
run_id = logger.start_run(
    pipeline="matrix_completion",    # Pipeline name
    dataset="synthetic_missing",      # Dataset identifier
    config_path="configs/my.yaml",    # Config file path
    tags={"version": "v1.0"}          # Optional tags
)
```

### Logging Parameters

```python
# Log multiple parameters
logger.log_params({
    "lambda": 0.1,
    "max_iter": 200,
    "tolerance": 1e-6
})

# Log single parameter
logger.log_param("device", "cuda:0")
```

### Logging Metrics

```python
# Final metrics
logger.log_metrics({
    "snr": 18.5,
    "mse": 0.0023
})

# Time-series metrics (e.g., during training)
for epoch in range(100):
    loss = train_epoch()
    logger.log_metrics({"loss": loss}, step=epoch)
```

### Logging Artifacts

```python
logger.log_artifact("results/model.pt", artifact_type="model")
logger.log_artifact("results/plot.png", artifact_type="plot")
```

### Ending a Run

```python
# Successful completion
logger.end_run(status="completed")

# Failed run
logger.end_run(status="failed", error="Out of memory")
```

---

## Context Manager Usage

Use the context manager for automatic run management:

```python
from tools.experiment_logger import ExperimentLogger, ExperimentRun

logger = ExperimentLogger("my_experiment")

with ExperimentRun(logger, pipeline="unet", dataset="synthetic") as run:
    # Your pipeline code
    result = run_pipeline()
    logger.log_metrics({"snr": result.snr})
    # Run automatically ends on exit
```

If an exception occurs, the run is marked as failed automatically.

---

## Log File Format

Experiments are stored as JSON-lines files in `experiments/logs/`:

```
experiments/logs/my_experiment.jsonl
```

Each line is a complete run record:

```json
{
  "run_id": "abc12345",
  "experiment_id": "my_experiment",
  "pipeline": "unet_denoising",
  "dataset": "synthetic_noisy",
  "parameters": {
    "learning_rate": 0.001,
    "epochs": 100
  },
  "metrics": {
    "snr": 18.5,
    "mse": 0.0023
  },
  "start_time": "2025-12-10T12:00:00",
  "end_time": "2025-12-10T12:15:30",
  "duration_seconds": 930,
  "status": "completed"
}
```

---

## CLI Inspection

### List Experiments

```bash
promethium experiments list
```

Output:
```
         Recorded Experiments
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Experiment ID     ┃ Runs  ┃ Last Modified   ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ my_experiment     │ 25    │ 2025-12-10 14:30│
│ unet_benchmark    │ 10    │ 2025-12-09 16:45│
└───────────────────┴───────┴─────────────────┘
```

### Show Experiment Details

```bash
promethium experiments show my_experiment --last 5
```

### Export to CSV

```bash
promethium experiments export my_experiment --format csv --output results.csv
```

---

## Querying Results

### Get All Runs

```python
logger = ExperimentLogger("my_experiment")
runs = logger.get_runs()

for run in runs:
    print(f"Run {run['run_id']}: SNR={run['metrics'].get('snr', 'N/A')}")
```

### Get Best Run

```python
# Best by SNR (higher is better)
best_run = logger.get_best_run("snr", maximize=True)
print(f"Best SNR: {best_run['metrics']['snr']}")

# Best by MSE (lower is better)
best_run = logger.get_best_run("mse", maximize=False)
```

### Get Summary Statistics

```python
summary = logger.get_summary()
print(f"Total runs: {summary['total_runs']}")
print(f"Completed: {summary['completed']}")
print(f"Mean SNR: {summary['metric_summary']['snr']['mean']:.2f}")
```

---

## Integration with Pipelines

The experiment logger integrates with the pipeline runner:

```python
from tools.pipeline_runner import run_pipeline_from_config

# Logging is automatic when experiment_id is provided
result, metrics = run_pipeline_from_config(
    "configs/pipelines/unet.yaml",
    experiment_id="my_experiment"
)
```

---

## Best Practices

### Experiment Naming

- Use descriptive, consistent names
- Include version or date if relevant
- Example: `unet_denoising_v2_20251210`

### Parameter Logging

- Log all hyperparameters
- Include environment info (GPU, versions)
- Log config file paths for reproducibility

### Metric Naming

- Use standardized metric names
- Include units where appropriate
- Be consistent across experiments

### Organization

```
experiments/
  logs/
    unet_experiments.jsonl
    classical_benchmarks.jsonl
    ablation_studies.jsonl
```

---

## See Also

- [Experiment Logger Source](../../tools/experiment_logger.py)
- [CLI Reference](./howto_run_cli.md)
- [Benchmarking Guide](./howto_compare_algorithms.md)
