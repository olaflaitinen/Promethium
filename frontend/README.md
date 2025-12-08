# Promethium Frontend

Angular-based web interface for the Promethium Seismic Data Recovery and Reconstruction Platform.

## Overview

This frontend provides a comprehensive interface for:

- **Dashboard**: System overview, health monitoring, and quick access to key workflows
- **Datasets**: Upload, manage, and browse seismic data files (SEG-Y, miniSEED, SAC)
- **Pipelines/Jobs**: Configure and execute reconstruction pipelines with ML models
- **Models**: View available AI/ML models (U-Net, Autoencoder, GAN) and their performance metrics
- **Results**: Visualize and compare original vs. reconstructed seismic data
- **System**: Monitor worker status, queue sizes, and resource utilization
- **Documentation**: Access user guides and API references

## Technology Stack

- **Angular 21** with standalone components
- **TypeScript** with strict mode
- **RxJS** for reactive state management
- **Vanilla CSS** with CSS custom properties for theming

## Prerequisites

- Node.js 18+ and npm
- Backend API running at http://localhost:8000 (see backend setup below)

## Quick Start

```bash
# Install dependencies
npm install

# Start development server with API proxy
npm run start
```

The application will be available at http://localhost:4200

## Development

### Directory Structure

```
src/
  app/
    components/       # Reusable UI components
    pages/            # Route-level page components
      dashboard/      # Main dashboard view
      datasets/       # Dataset management
      job-submission/ # Pipeline and job management
      models/         # ML model registry
      results/        # Results analysis
      system/         # System monitoring
      docs/           # Documentation links
      settings/       # Application settings
      visualization/  # Interactive data visualization
    services/         # API and utility services
    shared/           # Shared utilities and icons
  environments/       # Environment configurations
  styles.css          # Global design system
  index.html          # Application entry point
```

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Start dev server with proxy at port 4200 |
| `npm run build` | Build production bundle to `dist/` |
| `npm test` | Run unit tests with Vitest |
| `ng generate component <name>` | Generate new component |

### API Proxy

During development, API requests to `/api/*` are proxied to the backend server. This is configured in `proxy.conf.json`:

```json
{
    "/api": {
        "target": "http://localhost:8000",
        "secure": false,
        "changeOrigin": true
    }
}
```

### Environment Configuration

Development settings are in `src/environments/environment.ts`:

```typescript
export const environment = {
    production: false,
    apiUrl: 'http://localhost:8000/api/v1',
    appName: 'Promethium',
    appVersion: '1.0.0',
    pollingInterval: 5000
};
```

## Backend Setup

The frontend connects to a FastAPI backend. To run the full stack locally:

```bash
# From repository root
cd ..

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix

# Install Python dependencies
pip install -r requirements.txt

# Configure environment (copy and edit)
copy .env.example .env

# Start the backend
uvicorn src.promethium.api.main:app --reload --port 8000
```

### Backend Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/api/v1/datasets/` | GET, POST | List and create datasets |
| `/api/v1/datasets/{id}` | GET, DELETE | Get or delete dataset |
| `/api/v1/jobs/` | GET, POST | List and create jobs |
| `/api/v1/jobs/{id}` | GET | Get job details |
| `/api/v1/ml/train` | POST | Start model training |
| `/api/v1/ml/predict` | POST | Run inference |

## Design System

The application uses a custom design system defined in `src/styles.css`:

### Color Palette

| Variable | Value | Usage |
|----------|-------|-------|
| `--pm-primary-dark` | #050B24 | Main background |
| `--pm-accent-cyan` | #00F0FF | Primary accent, interactive elements |
| `--pm-success` | #10B981 | Success states |
| `--pm-warning` | #F59E0B | Warning states |
| `--pm-error` | #EF4444 | Error states |

### Component Classes

- `.pm-btn`, `.pm-btn-primary`, `.pm-btn-secondary` - Buttons
- `.pm-input`, `.pm-select`, `.pm-textarea` - Form elements
- `.pm-card` - Card containers
- `.pm-table` - Data tables
- `.pm-badge` - Status badges

## Building for Production

```bash
# Build optimized bundle
npm run build

# Output in dist/web/browser/
```

The production build uses relative API URLs (`/api/v1`) for deployment behind a reverse proxy.

## Troubleshooting

### API Connection Issues

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS configuration in backend `main.py`
3. Ensure proxy config matches backend port

### Build Errors

1. Clear node_modules: `rm -rf node_modules && npm install`
2. Check Angular CLI version: `ng version`
3. Verify TypeScript compatibility

## License

See repository root LICENSE file.
