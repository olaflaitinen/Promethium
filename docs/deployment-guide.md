# Deployment Guide

This document outlines the procedures for deploying the Promethium framework in a production environment.

## Containerization Strategy

Promethium uses a multi-container architecture orchestrated by Docker Compose.

### Backend Images
*   **Base**: `python:3.10-slim`
*   **Build Context**: Root repository
*   **Dockerfile**: `docker/backend.Dockerfile`
*   **Optimization**: Multi-stage build to reduce image size; only runtime dependencies are included in the final image.

### Frontend Images
*   **Base**: `nginx:alpine`
*   **Build Context**: `frontend/`
*   **Dockerfile**: `docker/frontend.Dockerfile`
*   **Process**:
    1.  Node.js container builds the Angular application (`npm run build`).
    2.  Nginx container serves the static assets from `dist/web/browser`.
    3.  Nginx acts as a reverse proxy for the API if configured, though the default setup exposes API on a separate port.

## Production Configuration

### Environment Variables
Ensure the following variables are set in your deployment environment (e.g., `.env` file or Kubernetes secrets):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL Connection String | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis Connection String | `redis://...` |
| `CELERY_BROKER_URL` | Celery Broker | `redis://...` |
| `DATA_STORAGE_PATH` | Path to persistent volume | `/data` |

### Docker Compose
To launch the production stack:

```bash
docker compose -f docker/docker-compose.yml up --build -d
```

### Kubernetes (Helm)
For cluster deployment, use the provided Helm charts.

```bash
helm install promethium charts/promethium --set ingress.enabled=true
```

## Scaling
*   **API**: Stateless; can be horizontally scaled behind a load balancer.
*   **Workers**: CPU-bound; scale based on job queue depth.
*   **Database**: Vertical scaling recommended; read-replicas for high read load.
