# Contributing to Promethium

Thank you for your interest in contributing to the Promethium project. This document provides guidelines and procedures for contributing to ensure a smooth collaboration process.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Licensing](#licensing)

---

## Code of Conduct

All contributors are expected to adhere to the project's [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold a respectful, inclusive, and professional environment.

---

## Getting Started

### Prerequisites

Before contributing, ensure you have the following installed:

- Python 3.10 or higher
- Node.js 20 or higher
- Docker and Docker Compose
- Git

### Fork and Clone

1. Fork the repository on GitHub.
2. Clone your fork locally:

```bash
git clone https://github.com/<your-username>/promethium.git
cd promethium
```

3. Add the upstream repository as a remote:

```bash
git remote add upstream https://github.com/olaflaitinen/promethium.git
```

---

## Development Environment

### Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Running Services Locally

For full-stack development, use Docker Compose:

```bash
docker compose -f docker/docker-compose.yml up -d postgres redis
```

Then run the backend and frontend development servers:

```bash
# Terminal 1: Backend
uvicorn src.promethium.api.main:app --reload

# Terminal 2: Frontend
cd frontend && npm start
```

---

## Contribution Workflow

### Branch Naming Convention

Use descriptive branch names with the following prefixes:

| Prefix | Purpose |
|--------|---------|
| `feature/` | New features |
| `bugfix/` | Bug fixes |
| `docs/` | Documentation changes |
| `refactor/` | Code refactoring |
| `test/` | Test additions or modifications |
| `chore/` | Maintenance tasks |

Example: `feature/add-sac-format-support`

### Workflow Steps

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes**: Implement your changes following the coding standards.

4. **Test your changes**: Ensure all tests pass.

5. **Commit changes**: Use meaningful commit messages.

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**: Submit a PR against the `main` branch.

---

## Coding Standards

### Python Code Style

- **Formatter**: Black (line length 88)
- **Linter**: Ruff
- **Type Hints**: Required for all public functions and methods
- **Docstrings**: Google-style docstrings for modules, classes, and functions

```python
def compute_snr(signal: np.ndarray, noise: np.ndarray) -> float:
    """Compute the signal-to-noise ratio.

    Args:
        signal: The signal array.
        noise: The noise array.

    Returns:
        The computed SNR in decibels.

    Raises:
        ValueError: If arrays have different shapes.
    """
    ...
```

### TypeScript Code Style

- **Formatter**: Prettier
- **Linter**: ESLint with Angular configuration
- **Strict Mode**: TypeScript strict mode enabled

### General Guidelines

- Keep functions focused and single-purpose.
- Prefer composition over inheritance.
- Write self-documenting code with clear variable names.
- Avoid magic numbers; use named constants.
- Handle errors explicitly.

---

## Testing Requirements

### Backend Tests

All contributions must include appropriate tests:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/promethium --cov-report=html

# Run specific test file
pytest tests/unit/test_filtering.py -v
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage
```

### Test Coverage Requirements

- New features: Minimum 80% line coverage
- Bug fixes: Include regression tests
- Critical paths: 100% coverage expected

---

## Documentation

### Documentation Requirements

- All public APIs must be documented.
- New features require user-facing documentation updates.
- Complex algorithms should include explanatory comments.
- Update the relevant `docs/*.md` files as needed.

### Building Documentation

```bash
# If using MkDocs
mkdocs serve
```

---

## Pull Request Process

### Before Submitting

1. Ensure all tests pass locally.
2. Run linters and formatters.
3. Update documentation if applicable.
4. Rebase on the latest `main` branch.

### Pull Request Template

When opening a PR, include:

- **Description**: Clear explanation of changes.
- **Related Issue**: Link to related issue(s).
- **Type of Change**: Feature, bugfix, docs, etc.
- **Testing**: How the changes were tested.
- **Checklist**: Confirmation of coding standards adherence.

### Review Process

1. At least one maintainer approval is required.
2. All CI checks must pass.
3. Address reviewer feedback promptly.
4. Squash commits before merging if requested.

### Merge Strategy

- Feature branches are merged via squash merge.
- The PR author is credited in the squash commit message.

---

## Issue Reporting

### Bug Reports

When reporting bugs, include:

- Promethium version
- Operating system and version
- Python/Node.js version
- Minimal reproduction steps
- Expected versus actual behavior
- Relevant logs or error messages

### Feature Requests

When requesting features, include:

- Problem statement
- Proposed solution
- Use case description
- Alternative solutions considered

### Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Confirmed bugs |
| `enhancement` | Feature requests |
| `documentation` | Documentation improvements |
| `good first issue` | Suitable for new contributors |
| `help wanted` | Community help requested |
| `priority: high` | High-priority issues |

---

## Licensing

By contributing to Promethium, you agree that your contributions will be licensed under the same license as the project: **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.

You certify that you have the right to submit the contribution under this license.

---

## Recognition

Contributors are recognized in the following ways:

- Listed in the repository's contributor list
- Mentioned in release notes for significant contributions
- Acknowledged in relevant documentation sections

---

Thank you for contributing to Promethium. Your efforts help advance the field of seismic data science.
