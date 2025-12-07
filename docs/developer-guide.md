# Developer Guide

This guide provides instructions for setting up the development environment for Promethium.

## Prerequisites

*   **Python**: v3.10 or higher.
*   **Node.js**: v18 LTS or higher.
*   **Docker**: Optional, but recommended for dependency management (Postgres/Redis).

## Backend Development (Python)

The backend is located in `src/promethium`.

### Setup
1.  Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
2.  Activate the environment:
    *   Windows: `.venv\Scripts\activate`
    *   Linux/Mac: `source .venv/bin/activate`
3.  Install dependencies in editable mode:
    ```bash
    pip install -e .[dev]
    ```

### Running the API
```bash
uvicorn promethium.api.main:app --reload --host 0.0.0.0 --port 8000
```
The API documentation will be available at `http://localhost:8000/docs`.

### Running Tests
Promethium uses `pytest` for unit and integration testing.
```bash
pytest tests/
```

## Frontend Development (Angular)

The frontend is located in the `frontend/` directory.

### Setup
1.  Navigate to the directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Install Angular CLI globally (optional but recommended):
    ```bash
    npm install -g @angular/cli
    ```

### Running the Dev Server
```bash
ng serve
# Or via npm
npm start
```
The application will run at `http://localhost:4200`. A proxy is configured to forward `/api` requests to `http://localhost:8000`.

### Building for Production
```bash
ng build --configuration production
```
Artifacts will be output to `frontend/dist/web/browser`.

## Code Style

*   **Python**: Follow PEP 8. Format code using `black` or `ruff`.
*   **TypeScript**: Follow the official Angular Style Guide.
*   **Git**: Use semantic commit messages (e.g., `feat: add robust seg-y reader`). 
*   **Tone**: Keep all documentation and comments professional. Do not use emojis.
