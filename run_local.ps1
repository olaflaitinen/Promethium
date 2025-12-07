# Promethium Local Launcher
Write-Host "Starting Promethium v1.0.0..." -ForegroundColor Cyan

# Check for Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not in PATH. Please install Docker Desktop."
    exit 1
}

# Build and Run
Write-Host "Building and starting containers... (This may take a while)" -ForegroundColor Yellow
docker compose up --build -d

# Check Status
if ($?) {
    Write-Host "Services started successfully!" -ForegroundColor Green
    Write-Host "- Backend API: http://localhost:8000/docs"
    Write-Host "- Web Dashboard: http://localhost:8000 (if served statically) or npm run dev for local frontend"
    
    # Check if frontend needs to be run separately (since docker-compose usually just serves backend API in this setup)
    # Note: production deployment would serve frontend static files via Nginx, 
    # but for local dev with this docker-compose, we might need to run vite locally if not dockerized.
    # The current docker-compose only has 'api', 'worker', 'db', 'redis'. 
    # It does NOT have a frontend container.
    
    Write-Host "NOTE: The Docker stack only runs the Backend/DB/Worker." -ForegroundColor Magenta
    Write-Host "To access the UI, open a new terminal in 'web/' and run: npm run dev" -ForegroundColor Magenta
} else {
    Write-Error "Failed to start services."
}
