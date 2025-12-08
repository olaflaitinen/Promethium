# Developer Guide

This document provides comprehensive guidance for developers contributing to or extending the Promethium framework.

## Table of Contents

- [Development Environment](#development-environment)
- [Backend Development](#backend-development)
- [Frontend Development](#frontend-development)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Debugging](#debugging)
- [Performance Profiling](#performance-profiling)
- [Documentation](#documentation)

---

## Development Environment

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Backend runtime |
| Node.js | 20+ | Frontend tooling |
| Docker | 24+ | Containerization |
| Docker Compose | 2.20+ | Local orchestration |
| Git | 2.40+ | Version control |
| VS Code (recommended) | Latest | IDE |

### Repository Setup

```bash
# Clone repository
git clone https://github.com/olaflaitinen/promethium.git
cd promethium

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### IDE Configuration

#### VS Code

Recommended extensions:

- Python (Microsoft)
- Pylance
- Angular Language Service
- ESLint
- Prettier
- Docker
- GitLens

Workspace settings (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": null,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## Backend Development

### Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Locally

```bash
# Start dependencies
docker compose -f docker/docker-compose.yml up -d postgres redis

# Apply migrations
alembic upgrade head

# Start API server
uvicorn src.promethium.api.main:app --reload --port 8000

# Start worker (separate terminal)
celery -A src.promethium.workflows.tasks worker --loglevel=info
```

### Project Structure

```
src/promethium/
├── __init__.py          # Package initialization
├── core/                # Core utilities
│   ├── config.py        # Configuration management
│   ├── exceptions.py    # Custom exceptions
│   └── logging.py       # Logging setup
├── io/                  # Data I/O
├── signal/              # Signal processing
├── ml/                  # Machine learning
├── api/                 # FastAPI application
└── workflows/           # Task definitions
```

### Adding a New API Endpoint

1. **Create router** (if new domain):

```python
# src/promethium/api/routers/new_feature.py
from fastapi import APIRouter, Depends
from ..dependencies import get_current_user

router = APIRouter(prefix="/new-feature", tags=["New Feature"])

@router.get("/")
async def list_items(user = Depends(get_current_user)):
    """List all items."""
    return {"items": []}
```

2. **Register router**:

```python
# src/promethium/api/main.py
from .routers import new_feature

app.include_router(new_feature.router, prefix="/api/v1")
```

3. **Add request/response models**:

```python
# src/promethium/api/models/requests.py
from pydantic import BaseModel

class NewItemRequest(BaseModel):
    name: str
    description: str | None = None
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Adding a New Model Architecture

1. **Define model class**:

```python
# src/promethium/ml/models/new_model.py
import torch.nn as nn
from .base import ReconstructionModel

class NewModel(ReconstructionModel):
    def __init__(self, config):
        super().__init__()
        # Define layers
        
    def forward(self, x, mask):
        # Forward pass
        return output
```

2. **Register in model registry**:

```python
# src/promethium/ml/models/__init__.py
from .new_model import NewModel

MODEL_REGISTRY = {
    "unet": UNet,
    "new_model": NewModel,
}
```

---

## Frontend Development

### Environment Setup

```bash
cd frontend
npm install
```

### Running Locally

```bash
# Development server with hot reload
npm start

# Build for production
npm run build

# Run linter
npm run lint

# Run tests
npm test
```

### Project Structure

```
frontend/src/
├── app/
│   ├── core/              # Core services, guards
│   ├── shared/            # Shared components
│   ├── features/          # Feature modules
│   ├── store/             # NgRx state
│   ├── app.component.ts
│   ├── app.config.ts
│   └── app.routes.ts
├── assets/                # Static assets
├── environments/          # Environment configs
└── styles/                # Global styles
```

### Creating a New Feature

1. **Generate module**:

```bash
ng generate component features/new-feature
```

2. **Add routing**:

```typescript
// app.routes.ts
export const routes: Routes = [
  {
    path: 'new-feature',
    loadComponent: () => import('./features/new-feature/new-feature.component')
      .then(m => m.NewFeatureComponent)
  }
];
```

3. **Create service**:

```typescript
// features/new-feature/new-feature.service.ts
@Injectable({ providedIn: 'root' })
export class NewFeatureService {
  constructor(private http: HttpClient) {}
  
  getItems(): Observable<Item[]> {
    return this.http.get<Item[]>('/api/v1/new-feature');
  }
}
```

### State Management

NgRx pattern:

```typescript
// store/new-feature/new-feature.actions.ts
export const loadItems = createAction('[New Feature] Load Items');
export const loadItemsSuccess = createAction(
  '[New Feature] Load Items Success',
  props<{ items: Item[] }>()
);

// store/new-feature/new-feature.reducer.ts
export const newFeatureReducer = createReducer(
  initialState,
  on(loadItemsSuccess, (state, { items }) => ({ ...state, items }))
);

// store/new-feature/new-feature.effects.ts
loadItems$ = createEffect(() => this.actions$.pipe(
  ofType(loadItems),
  switchMap(() => this.service.getItems()),
  map(items => loadItemsSuccess({ items }))
));
```

---

## Testing

### Backend Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/promethium --cov-report=html

# Run specific test file
pytest tests/unit/test_filtering.py -v

# Run marked tests
pytest tests/ -m "slow" -v
```

#### Test Structure

```
tests/
├── unit/                # Unit tests
│   ├── test_io.py
│   ├── test_signal.py
│   └── test_ml.py
├── integration/         # Integration tests
│   ├── test_api.py
│   └── test_pipeline.py
├── e2e/                 # End-to-end tests
│   └── test_workflow.py
├── fixtures/            # Test fixtures
│   └── sample_data/
└── conftest.py          # Shared fixtures
```

#### Writing Tests

```python
import pytest
from promethium.signal import bandpass_filter

class TestBandpassFilter:
    def test_basic_filtering(self, sample_trace):
        """Test basic bandpass filter application."""
        result = bandpass_filter(sample_trace, low=5.0, high=80.0)
        assert result.shape == sample_trace.shape
        
    def test_invalid_frequencies(self, sample_trace):
        """Test error handling for invalid frequencies."""
        with pytest.raises(ValueError):
            bandpass_filter(sample_trace, low=80.0, high=5.0)
```

### Frontend Testing

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- --include=**/new-feature.component.spec.ts
```

#### Writing Component Tests

```typescript
describe('NewFeatureComponent', () => {
  let component: NewFeatureComponent;
  let fixture: ComponentFixture<NewFeatureComponent>;
  
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewFeatureComponent],
      providers: [{ provide: NewFeatureService, useValue: mockService }]
    }).compileComponents();
    
    fixture = TestBed.createComponent(NewFeatureComponent);
    component = fixture.componentInstance;
  });
  
  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
```

---

## Code Quality

### Python Code Style

```bash
# Format with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type check with mypy
mypy src/promethium
```

Configuration in `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py310']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.10"
strict = true
```

### TypeScript Code Style

```bash
cd frontend

# Lint
npm run lint

# Format with Prettier
npm run format
```

### Pre-commit Hooks

Configured hooks (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.0
    hooks:
      - id: ruff
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
```

---

## Debugging

### Backend Debugging

#### VS Code Launch Configuration

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.promethium.api.main:app", "--reload"],
      "jinja": true
    },
    {
      "name": "Celery Worker",
      "type": "python",
      "request": "launch",
      "module": "celery",
      "args": ["-A", "src.promethium.workflows.tasks", "worker", "-l", "INFO"]
    }
  ]
}
```

#### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed information for debugging")
logger.info("General operational information")
logger.warning("Warning about potential issues")
logger.error("Error that should be investigated")
```

### Frontend Debugging

- Use browser DevTools (F12)
- Angular DevTools extension for component inspection
- Redux DevTools for NgRx state debugging
- `debugger` statements for breakpoints

---

## Performance Profiling

### Backend Profiling

```python
# Using cProfile
python -m cProfile -o profile.stats script.py

# Analyze results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumtime').print_stats(20)"
```

#### Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Function code
    pass
```

### GPU Profiling

```python
import torch.profiler

with torch.profiler.profile(
    activities=[
        torch.profiler.ProfilerActivity.CPU,
        torch.profiler.ProfilerActivity.CUDA,
    ]
) as prof:
    model(input_data)

print(prof.key_averages().table(sort_by="cuda_time_total"))
```

---

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def process_traces(
    data: np.ndarray,
    sample_rate: float,
    filter_params: dict | None = None,
) -> np.ndarray:
    """Process seismic traces with optional filtering.
    
    Applies preprocessing steps to seismic trace data including
    normalization and optional bandpass filtering.
    
    Args:
        data: Input trace data with shape (n_traces, n_samples).
        sample_rate: Sampling rate in Hz.
        filter_params: Optional dictionary with 'low' and 'high' keys
            specifying filter corner frequencies in Hz.
    
    Returns:
        Processed trace data with the same shape as input.
    
    Raises:
        ValueError: If data dimensions are invalid.
        TypeError: If filter_params contains invalid types.
    
    Example:
        >>> data = np.random.randn(100, 1000)
        >>> result = process_traces(data, 250.0, {'low': 5, 'high': 80})
    """
```

### Building Documentation

```bash
# If using MkDocs
pip install mkdocs mkdocs-material
mkdocs serve  # Local preview
mkdocs build  # Build static site
```

---

## Related Documents

| Document | Description |
|----------|-------------|
| [Contributing](../CONTRIBUTING.md) | Contribution guidelines |
| [Architecture](architecture.md) | System architecture |
| [API Reference](api-reference.md) | API documentation |
| [Configuration](configuration.md) | Configuration options |
