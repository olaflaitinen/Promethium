# Configuration

This document covers configuration options for Promethium.

## Configuration Hierarchy

Configuration is resolved in order of precedence (highest first):

1. Environment variables
2. Command-line arguments
3. Environment-specific files (`config/{env}.yaml`)
4. Default configuration (`config/default.yaml`)

---

## Environment Variables

### Database

| Variable | Description | Default |
|----------|-------------|---------|
| PROMETHIUM_DATABASE_URL | PostgreSQL connection URL | - |
| PROMETHIUM_DATABASE_POOL_SIZE | Connection pool size | 5 |

### Redis

| Variable | Description | Default |
|----------|-------------|---------|
| PROMETHIUM_REDIS_URL | Redis connection URL | - |
| PROMETHIUM_REDIS_MAX_CONNECTIONS | Max connections | 10 |

### Security

| Variable | Description | Default |
|----------|-------------|---------|
| PROMETHIUM_SECRET_KEY | JWT signing key | - |
| PROMETHIUM_JWT_ALGORITHM | JWT algorithm | HS256 |
| PROMETHIUM_JWT_EXPIRATION | Token expiration (minutes) | 60 |

### Storage

| Variable | Description | Default |
|----------|-------------|---------|
| PROMETHIUM_DATA_DIR | Data storage path | /data |
| PROMETHIUM_MODEL_DIR | Model storage path | /models |
| PROMETHIUM_TEMP_DIR | Temporary files | /tmp |

### API

| Variable | Description | Default |
|----------|-------------|---------|
| PROMETHIUM_API_HOST | API host | 0.0.0.0 |
| PROMETHIUM_API_PORT | API port | 8000 |
| PROMETHIUM_CORS_ORIGINS | Allowed origins | * |

---

## Configuration Files

### Default Configuration

```yaml
# config/default.yaml
database:
  pool_size: 5
  pool_timeout: 30

redis:
  max_connections: 10
  socket_timeout: 5

api:
  host: 0.0.0.0
  port: 8000
  workers: 4

ml:
  default_model: unet-v2
  batch_size: 8
  device: auto

logging:
  level: INFO
  format: json
```

### Production Configuration

```yaml
# config/production.yaml
database:
  pool_size: 20

api:
  workers: 8

logging:
  level: WARNING
```

---

## Model Configuration

```yaml
# Model-specific configuration
models:
  unet-v2:
    architecture: unet
    features: [64, 128, 256, 512]
    dropout: 0.1
    
  inference:
    batch_size: 8
    patch_size: 256
    overlap: 0.5
```

---

## Pipeline Configuration

```yaml
# Processing pipeline configuration
pipelines:
  reconstruction:
    preprocessing:
      - normalize: {method: trace_max}
      - filter: {low: 5, high: 80}
    
    processing:
      - reconstruct: {model: unet-v2}
    
    postprocessing:
      - denormalize
```

---

## Related Documents

| Document | Description |
|----------|-------------|
| [Deployment Guide](deployment-guide.md) | Deployment instructions |
| [Developer Guide](developer-guide.md) | Development setup |
