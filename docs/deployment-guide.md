# Deployment Guide

This document covers deployment scenarios and procedures for Promethium.

## Deployment Options

| Option | Use Case | Complexity |
|--------|----------|------------|
| Docker Compose | Development, small deployments | Low |
| Kubernetes | Production, scaling | High |
| Manual | Custom environments | Medium |

---

## Docker Compose Deployment

### Prerequisites

- Docker 24+
- Docker Compose 2.20+
- 16 GB RAM minimum

### Quick Start

```bash
# Clone repository
git clone https://github.com/olaflaitinen/promethium.git
cd promethium

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
docker compose -f docker/docker-compose.yml up -d

# Check status
docker compose ps
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 4200 | Angular UI |
| backend | 8000 | FastAPI API |
| worker | - | Celery worker |
| postgres | 5432 | Database |
| redis | 6379 | Message broker |

---

## Production Deployment

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 8 cores | 32 cores |
| RAM | 32 GB | 128 GB |
| Storage | 500 GB SSD | 2 TB NVMe |
| GPU | GTX 1080 | A100 |

### Environment Variables

```bash
# Database
PROMETHIUM_DATABASE_URL=postgresql://user:pass@host:5432/promethium

# Redis
PROMETHIUM_REDIS_URL=redis://host:6379/0

# Security
PROMETHIUM_SECRET_KEY=<secure-random-key>

# Storage
PROMETHIUM_DATA_DIR=/data/promethium
PROMETHIUM_MODEL_DIR=/models
```

### TLS Configuration

```yaml
# nginx.conf
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/promethium.crt;
    ssl_certificate_key /etc/ssl/promethium.key;
    
    location / {
        proxy_pass http://frontend:4200;
    }
    
    location /api {
        proxy_pass http://backend:8000;
    }
}
```

---

## Kubernetes Deployment

### Helm Chart

```bash
helm repo add promethium https://charts.promethium.io
helm install promethium promethium/promethium \
  --set postgresql.enabled=true \
  --set redis.enabled=true
```

### Resource Requests

```yaml
resources:
  backend:
    requests:
      cpu: "1"
      memory: "2Gi"
    limits:
      cpu: "4"
      memory: "8Gi"
  
  worker:
    requests:
      cpu: "2"
      memory: "8Gi"
      nvidia.com/gpu: "1"
```

---

## Scaling

### Horizontal Scaling

```bash
# Scale workers
docker compose up -d --scale worker=4
```

### GPU Workers

```yaml
# docker-compose.yml
worker-gpu:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

---

## Related Documents

| Document | Description |
|----------|-------------|
| [Configuration](configuration.md) | Configuration reference |
| [Ops and Monitoring](ops-and-monitoring.md) | Monitoring setup |
