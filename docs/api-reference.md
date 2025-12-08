# API Reference

This document provides comprehensive documentation for the Promethium REST API.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Common Patterns](#common-patterns)
- [Endpoints](#endpoints)
  - [Authentication](#authentication-endpoints)
  - [Datasets](#datasets)
  - [Jobs](#jobs)
  - [Models](#models)
  - [Results](#results)
  - [Health](#health)
- [Error Handling](#error-handling)
- [WebSocket API](#websocket-api)

---

## Overview

### Base URL

```
Production: https://your-domain.com/api/v1
Development: http://localhost:8000/api/v1
```

### Content Types

All requests and responses use JSON:

```
Content-Type: application/json
Accept: application/json
```

File uploads use multipart form data:

```
Content-Type: multipart/form-data
```

### Interactive Documentation

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

---

## Authentication

### JWT Authentication

Promethium uses JWT (JSON Web Token) bearer authentication.

#### Obtaining a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "your-password"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Using the Token

Include the token in the Authorization header:

```http
GET /api/v1/datasets
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Token Refresh

```http
POST /api/v1/auth/refresh
Authorization: Bearer <current-token>
```

---

## Common Patterns

### Pagination

List endpoints support pagination:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number (1-indexed) |
| per_page | integer | 20 | Items per page (max 100) |

**Request:**

```http
GET /api/v1/datasets?page=2&per_page=50
```

**Response:**

```json
{
  "items": [...],
  "total": 150,
  "page": 2,
  "per_page": 50,
  "pages": 3
}
```

### Filtering

Filter using query parameters:

```http
GET /api/v1/jobs?status=completed&created_after=2025-01-01
```

### Sorting

Sort using the `sort` parameter:

```http
GET /api/v1/datasets?sort=-created_at
```

Prefix with `-` for descending order.

---

## Endpoints

### Authentication Endpoints

#### POST /auth/login

Authenticate and obtain access token.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Email address |
| password | string | Yes | Password |

**Response:** `200 OK`

```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /auth/refresh

Refresh access token.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`

```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /auth/logout

Invalidate current token.

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

---

### Datasets

#### GET /datasets

List all datasets accessible to the user.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | Page number |
| per_page | integer | Items per page |
| format | string | Filter by format (segy, miniseed) |
| search | string | Search in name and description |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "survey_2025.sgy",
      "format": "segy",
      "traces": 1000,
      "samples": 2000,
      "sample_rate": 250.0,
      "size_bytes": 16000000,
      "status": "ready",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:35:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20,
  "pages": 3
}
```

#### POST /datasets

Upload a new dataset.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | file | Yes | Seismic data file |
| description | string | No | Dataset description |
| tags | array | No | Tags for organization |

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "name": "survey_2025.sgy",
  "status": "processing",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### GET /datasets/{id}

Get dataset details.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | uuid | Dataset ID |

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "name": "survey_2025.sgy",
  "description": "Field survey data",
  "format": "segy",
  "traces": 1000,
  "samples": 2000,
  "sample_rate": 250.0,
  "size_bytes": 16000000,
  "status": "ready",
  "statistics": {
    "min": -32000,
    "max": 32000,
    "mean": 0.5,
    "rms": 5000
  },
  "headers": {
    "text_header": "...",
    "binary_header": {...}
  },
  "tags": ["exploration", "2025"],
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z"
}
```

#### DELETE /datasets/{id}

Delete a dataset.

**Response:** `204 No Content`

#### GET /datasets/{id}/preview

Get dataset preview image.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| width | integer | 800 | Image width |
| height | integer | 600 | Image height |
| colormap | string | gray | Color palette |

**Response:** `200 OK` (image/png)

---

### Jobs

#### GET /jobs

List all jobs.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status |
| type | string | Filter by job type |
| created_after | datetime | Filter by creation date |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "uuid",
      "type": "reconstruction",
      "status": "completed",
      "progress": 100,
      "dataset_id": "uuid",
      "model_id": "uuid",
      "created_at": "2025-01-15T10:30:00Z",
      "started_at": "2025-01-15T10:31:00Z",
      "completed_at": "2025-01-15T10:45:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 20,
  "pages": 2
}
```

#### POST /jobs

Create a new job.

**Request Body:**

```json
{
  "type": "reconstruction",
  "dataset_id": "uuid",
  "model_id": "uuid",
  "parameters": {
    "missing_traces": [10, 15, 23],
    "patch_size": 256,
    "overlap": 0.5,
    "batch_size": 8
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Job type (reconstruction, denoising) |
| dataset_id | uuid | Yes | Input dataset ID |
| model_id | uuid | Yes | Model to use |
| parameters | object | No | Job-specific parameters |

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "type": "reconstruction",
  "status": "pending",
  "progress": 0,
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### GET /jobs/{id}

Get job details.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "type": "reconstruction",
  "status": "running",
  "progress": 45,
  "dataset_id": "uuid",
  "model_id": "uuid",
  "parameters": {...},
  "logs": [
    {"timestamp": "2025-01-15T10:31:00Z", "level": "info", "message": "Starting job"},
    {"timestamp": "2025-01-15T10:32:00Z", "level": "info", "message": "Processing batch 1/10"}
  ],
  "created_at": "2025-01-15T10:30:00Z",
  "started_at": "2025-01-15T10:31:00Z"
}
```

#### POST /jobs/{id}/cancel

Cancel a running job.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "status": "cancelled"
}
```

#### GET /jobs/{id}/logs

Stream job logs.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| since | datetime | Logs after this timestamp |
| level | string | Minimum log level |

**Response:** `200 OK`

```json
{
  "logs": [
    {"timestamp": "2025-01-15T10:31:00Z", "level": "info", "message": "..."}
  ]
}
```

---

### Models

#### GET /models

List available models.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| type | string | Filter by model type |
| architecture | string | Filter by architecture |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "unet-v2-reconstruction",
      "version": "2.0.0",
      "architecture": "unet",
      "type": "reconstruction",
      "description": "General-purpose U-Net for trace reconstruction",
      "metrics": {
        "snr_improvement": 12.5,
        "ssim": 0.95
      },
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 10
}
```

#### GET /models/{id}

Get model details.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "name": "unet-v2-reconstruction",
  "version": "2.0.0",
  "architecture": "unet",
  "type": "reconstruction",
  "description": "...",
  "parameters": {
    "input_channels": 1,
    "output_channels": 1,
    "features": [64, 128, 256, 512]
  },
  "training_data": "Description of training dataset",
  "metrics": {...},
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

### Results

#### GET /jobs/{job_id}/results

Get job results.

**Response:** `200 OK`

```json
{
  "job_id": "uuid",
  "status": "completed",
  "output_dataset_id": "uuid",
  "metrics": {
    "snr_improvement_db": 10.5,
    "ssim": 0.93,
    "mse": 0.0012
  },
  "artifacts": [
    {"name": "comparison.png", "url": "/api/v1/results/uuid/artifacts/comparison.png"},
    {"name": "metrics.json", "url": "/api/v1/results/uuid/artifacts/metrics.json"}
  ]
}
```

#### GET /jobs/{job_id}/results/download

Download result data.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| format | string | Output format (segy, miniseed, npy) |

**Response:** `200 OK` (application/octet-stream)

---

### Health

#### GET /health

Basic health check.

**Response:** `200 OK`

```json
{
  "status": "healthy"
}
```

#### GET /health/ready

Readiness check (for orchestration).

**Response:** `200 OK`

```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "storage": "ok"
  }
}
```

#### GET /health/live

Liveness check.

**Response:** `200 OK`

```json
{
  "status": "alive"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {"field": "dataset_id", "message": "Dataset not found"}
    ]
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |

### Error Codes

| Code | Description |
|------|-------------|
| VALIDATION_ERROR | Request validation failed |
| AUTHENTICATION_ERROR | Authentication required or failed |
| AUTHORIZATION_ERROR | Insufficient permissions |
| NOT_FOUND | Resource not found |
| CONFLICT | Resource conflict |
| RATE_LIMITED | Too many requests |
| INTERNAL_ERROR | Server error |

---

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('wss://your-domain.com/api/v1/ws');
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
  }));
};
```

### Subscribing to Job Updates

```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'job',
  job_id: 'uuid'
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle job update
};
```

### Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| auth | Client | Authenticate connection |
| subscribe | Client | Subscribe to channel |
| unsubscribe | Client | Unsubscribe from channel |
| job_update | Server | Job status update |
| job_log | Server | Job log message |
| error | Server | Error message |

---

## Related Documents

| Document | Description |
|----------|-------------|
| [User Guide](user-guide.md) | User-facing documentation |
| [Developer Guide](developer-guide.md) | Development instructions |
| [Configuration](configuration.md) | Configuration options |
