# Benchmarking

This document covers performance benchmarking methodology and metrics for Promethium.

## Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| SEG-Y Ingestion | 500 MB/s | SSD storage |
| Trace Filtering | 10,000 traces/s | Single CPU |
| U-Net Inference | 100 gathers/s | A100 GPU |
| Full Reconstruction | < 5 min/10 GB | GPU-enabled |

---

## Benchmark Suite

### Running Benchmarks

```bash
# Full suite
python -m promethium.benchmarks.run_all

# Specific benchmarks
python -m promethium.benchmarks.io_throughput
python -m promethium.benchmarks.ml_inference
python -m promethium.benchmarks.signal_processing
```

### Benchmark Categories

| Category | Measures |
|----------|----------|
| I/O | Read/write throughput |
| Signal | Processing speed |
| ML | Inference latency |
| API | Request throughput |

---

## Metrics

### I/O Benchmarks

- Read throughput (MB/s)
- Write throughput (MB/s)
- Trace read rate (traces/s)

### ML Benchmarks

- Inference latency (ms/batch)
- GPU utilization (%)
- Memory usage (GB)

### Quality Metrics

- SNR improvement (dB)
- SSIM score
- MSE

---

## Benchmark Configuration

```yaml
benchmarks:
  io:
    file_sizes: [100MB, 1GB, 10GB]
    iterations: 5
  
  ml:
    models: [unet-v1, unet-v2]
    batch_sizes: [4, 8, 16]
    warm_up: 10
    iterations: 100
  
  signal:
    trace_counts: [1000, 10000, 100000]
```

---

## Hardware Requirements

### Minimum

| Component | Specification |
|-----------|--------------|
| CPU | 4 cores |
| RAM | 16 GB |
| Storage | SSD 100 GB |
| GPU | GTX 1080 (optional) |

### Recommended

| Component | Specification |
|-----------|--------------|
| CPU | 16 cores |
| RAM | 64 GB |
| Storage | NVMe 1 TB |
| GPU | RTX 3090 / A100 |

---

## Interpreting Results

### Performance Report

```
=== I/O Benchmark ===
SEG-Y Read: 523 MB/s
SEG-Y Write: 412 MB/s

=== ML Benchmark ===
UNet-v2 Inference: 8.3 ms/batch (batch=8)
GPU Utilization: 87%

=== Quality ===
SNR Improvement: 12.5 dB
SSIM: 0.95
```

---

## Related Documents

| Document | Description |
|----------|-------------|
| [ML Pipelines](ml-pipelines.md) | Model documentation |
| [Configuration](configuration.md) | Configuration reference |
