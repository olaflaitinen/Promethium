# Promethium Local Development Script
# Usage: ./run_local.ps1 [backend|frontend|all|docker]

param(
    [Parameter(Position=0)]
    [ValidateSet("backend", "frontend", "all", "docker")]
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Promethium Local Development Runner  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Start-Backend {
    Write-Host "[BACKEND] Starting FastAPI server..." -ForegroundColor Yellow
    
    # Check if venv exists
    if (-not (Test-Path "$ProjectRoot\.venv")) {
        Write-Host "[BACKEND] Creating virtual environment..." -ForegroundColor Yellow
        python -m venv "$ProjectRoot\.venv"
    }
    
    # Activate venv and install dependencies
    Write-Host "[BACKEND] Activating environment and installing dependencies..." -ForegroundColor Yellow
    & "$ProjectRoot\.venv\Scripts\Activate.ps1"
    pip install -e ".[dev]" --quiet
    
    # Create data directory if not exists
    if (-not (Test-Path "$ProjectRoot\data")) {
        New-Item -ItemType Directory -Path "$ProjectRoot\data" | Out-Null
    }
    
    # Copy .env.example to .env if .env doesn't exist
    if (-not (Test-Path "$ProjectRoot\.env") -and (Test-Path "$ProjectRoot\.env.example")) {
        Copy-Item "$ProjectRoot\.env.example" "$ProjectRoot\.env"
        Write-Host "[BACKEND] Created .env from .env.example" -ForegroundColor Green
    }
    
    # Start the server
    Write-Host "[BACKEND] Starting uvicorn on http://localhost:8000" -ForegroundColor Green
    Write-Host "[BACKEND] API Docs: http://localhost:8000/docs" -ForegroundColor Green
    uvicorn promethium.api.main:app --reload --port 8000
}

function Start-Frontend {
    Write-Host "[FRONTEND] Starting Angular development server..." -ForegroundColor Yellow
    
    Set-Location "$ProjectRoot\frontend"
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Host "[FRONTEND] Installing npm dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    Write-Host "[FRONTEND] Starting Angular on http://localhost:4200" -ForegroundColor Green
    npm start
}

function Start-Docker {
    Write-Host "[DOCKER] Starting Docker Compose stack..." -ForegroundColor Yellow
    
    Set-Location $ProjectRoot
    docker compose -f docker/docker-compose.yml up --build -d
    
    Write-Host ""
    Write-Host "[DOCKER] Services starting..." -ForegroundColor Green
    Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  - API:      http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[DOCKER] Run 'docker compose -f docker/docker-compose.yml logs -f' to see logs" -ForegroundColor Gray
}

switch ($Mode) {
    "backend" {
        Start-Backend
    }
    "frontend" {
        Start-Frontend
    }
    "all" {
        Write-Host "[INFO] Starting both backend and frontend..." -ForegroundColor Cyan
        Write-Host "[INFO] Open two terminals and run:" -ForegroundColor Gray
        Write-Host "  Terminal 1: ./run_local.ps1 backend" -ForegroundColor White
        Write-Host "  Terminal 2: ./run_local.ps1 frontend" -ForegroundColor White
        Write-Host ""
        Write-Host "Or use Docker mode: ./run_local.ps1 docker" -ForegroundColor Gray
    }
    "docker" {
        Start-Docker
    }
}
