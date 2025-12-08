# Operations and Monitoring

This document covers logging, metrics, monitoring, and operational practices for Promethium.

## Logging

### Log Configuration

```yaml
logging:
  level: INFO
  format: json
  output:
    - console
    - file: /var/log/promethium/app.log
```

### Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed debugging information |
| INFO | General operational information |
| WARNING | Potential issues |
| ERROR | Errors requiring attention |
| CRITICAL | System failures |

### Structured Logging

```python
import structlog
logger = structlog.get_logger()

logger.info("job_started", job_id=job_id, dataset_id=dataset_id)
```

---

## Metrics

### Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| promethium_jobs_total | Counter | Total jobs by status |
| promethium_job_duration_seconds | Histogram | Job execution time |
| promethium_api_requests_total | Counter | API requests |
| promethium_api_latency_seconds | Histogram | API response time |
| promethium_worker_tasks_active | Gauge | Active worker tasks |

### Prometheus Endpoint

```
GET /metrics
```

### Grafana Dashboards

Pre-built dashboards available:

- System Overview
- Job Processing
- API Performance
- Worker Health

---

## Health Checks

### Endpoints

| Endpoint | Purpose |
|----------|---------|
| /health | Basic health |
| /health/ready | Readiness probe |
| /health/live | Liveness probe |

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## Alerting

### Alert Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighErrorRate | Error rate > 5% | Warning |
| JobQueueBacklog | Queue > 100 | Warning |
| WorkerDown | Worker unavailable | Critical |
| DatabaseConnectionLost | DB unreachable | Critical |

### Notification Channels

- Email
- Slack
- PagerDuty

---

## Operational Runbooks

### High Job Queue

1. Check worker health
2. Scale workers if needed
3. Check for stuck jobs
4. Review error logs

### Database Issues

1. Check connection pool
2. Verify database health
3. Review slow queries
4. Check disk space

---

## Related Documents

| Document | Description |
|----------|-------------|
| [Deployment Guide](deployment-guide.md) | Deployment instructions |
| [Configuration](configuration.md) | Configuration reference |
