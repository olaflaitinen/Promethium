# Data Engineering

This document covers data management, storage architecture, and pipeline design in Promethium. The data engineering architecture follows state-of-the-art practices for scalable, reproducible ML pipelines developed in December 2025.

## Data Formats

### Supported Formats

| Format | Read | Write | Use Case |
|--------|------|-------|----------|
| SEG-Y | Yes | Yes | Industry standard |
| SEG-2 | Yes | No | Near-surface |
| miniSEED | Yes | Yes | Seismology |
| SAC | Yes | Yes | Single traces |

### Data Model

```python
class SeismicData:
    traces: np.ndarray      # (n_traces, n_samples)
    sample_rate: float      # Hz
    headers: dict           # Trace headers
    metadata: dict          # File metadata
```

---

## Storage Architecture

### Object Storage Layout

```
promethium-data/
├── datasets/{id}/
│   ├── raw/              # Original files
│   ├── processed/        # Preprocessed data
│   └── metadata.json
├── models/{id}/
│   ├── weights.pt
│   └── config.yaml
└── results/{job_id}/
    ├── output/
    └── metadata.json
```

### Database Schema

| Table | Purpose |
|-------|---------|
| datasets | Dataset metadata |
| jobs | Job records |
| models | Model registry |
| results | Job results |

---

## Data Pipeline

### Ingestion Pipeline

```mermaid
flowchart LR
    UP[Upload] --> VAL[Validate]
    VAL --> PARSE[Parse]
    PARSE --> STORE[Store]
    STORE --> IDX[Index]
```

1. Receive file upload
2. Validate format and integrity
3. Parse headers and data
4. Store in object storage
5. Index metadata in database

### Processing Pipeline

```mermaid
flowchart LR
    LD[Load] --> PRE[Preprocess]
    PRE --> PROC[Process]
    PROC --> VALID[Validate]
    VALID --> ST[Store]
```

Configuration:

```yaml
pipeline:
  preprocessing:
    - normalize: {method: trace_max}
    - filter: {low: 5, high: 80}
  processing:
    - reconstruct: {model: unet-v2}
  postprocessing:
    - denormalize
```

---

## Data Quality

### Quality Checks

| Check | Description |
|-------|-------------|
| Null Traces | Detect zero/null traces |
| Amplitude | Check amplitude range |
| Timing | Verify sample rate |
| Headers | Validate header fields |

### Lineage Tracking

All operations are logged:

```json
{
  "dataset_id": "uuid",
  "operations": [
    {"op": "upload", "timestamp": "..."},
    {"op": "preprocess", "params": {...}},
    {"op": "reconstruct", "model": "..."}
  ]
}
```

---

## Scalability

### Streaming I/O

Memory-efficient processing of large files:

```python
for chunk in stream_segy(path, chunk_size=1000):
    process(chunk)
```

### Distributed Processing

Celery task queue enables horizontal scaling:

```python
@celery_app.task
def process_chunk(dataset_id, start, end):
    data = load_chunk(dataset_id, start, end)
    result = process(data)
    store_chunk(result)
```

---

## Related Documents

| Document | Description |
|----------|-------------|
| [ML Pipelines](ml-pipelines.md) | ML documentation |
| [Architecture](architecture.md) | System architecture |
