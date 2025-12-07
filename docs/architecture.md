# Architecture Overview

Promethium is architected as a set of loosely coupled modules and services, designed for scalability and maintainability.

## System Diagram

The system consists of three main logical tiers:

1.  **Presentation Tier (Frontend)**: An Angular Single Page Application (SPA).
2.  **Application Tier (Backend)**: FastAPI REST API and Celery Workers.
3.  **Data Tier**: PostgreSQL (Metadata), Redis (Broker/Cache), and File Storage (Seismic Data).

## Directory Structure

The repository is organized as follows:

```text
promethium/
├── docker/                 # Container configurations
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── docker-compose.yml
├── docs/                   # Documentation (Markdown)
├── frontend/               # Angular Application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/ # Standalone Components
│   │   │   ├── services/   # API Clients
│   │   │   └── models/     # TypeScript Interfaces
│   │   └── assets/
│   ├── angular.json
│   └── package.json
├── src/
│   └── promethium/
│       ├── api/            # FastAPI Routes & Main App
│       ├── core/           # Configuration & Logging
│       ├── io/             # SEG-Y / Seismic Readers
│       ├── ml/             # PyTorch Models (U-Net, PINNs)
│       ├── recovery/       # Matrix Completion Algorithms
│       ├── signal/         # DSP Filters
│       └── workflows/      # Celery Tasks
└── tests/                  # Pytest Suites
```

## Component Details

### Frontend (Angular)
The user interface is built with **Angular v17+**.
*   **Build System**: Angular CLI (Webpack).
*   **Architecture**: Standalone Components.
*   **State Management**: Signals and RxJS.
*   **Communication**: `HttpClient` service interacting with the FastAPI backend.

### Backend (Python)
The core logic resides in a Python monorepo structure installed as an editable package.
*   **Framework**: FastAPI.
*   **Concurrency**: Fully asynchronous (async/await).
*   **Validation**: Pydantic v2.

### Asynchronous Processing
Heavy computational tasks (reconstruction, training) are offloaded to Celery workers.
1.  User submits job via API.
2.  API pushes task to Redis.
3.  Celery Worker picks up task.
4.  Worker updates status in PostgreSQL and saves results to disk/blob storage.

## Data Flow

1.  **Ingestion**: User uploads SEG-Y file. API validates headers and registers metadata in PostgreSQL. File is stored in `DATA_STORAGE_PATH`.
2.  **Visualization**: Frontend requests trace data. Backend reads byte ranges using highly optimized `segyio` or memory-mapped numpy arrays and returns JSON/Binary data.
3.  **Processing**: User configures a reconstruction pipeline (e.g., "U-Net Interpolation"). The job is queued.
4.  **Result**: Upon completion, the backend notifies the client (polling or potential WebSocket), and the user can view the reconstructed gather side-by-side with the original.
