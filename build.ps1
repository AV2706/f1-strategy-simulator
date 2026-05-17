# Build script to produce frontend production build and prepare backend venv
# Run from repository root in PowerShell: .\build.ps1

$ErrorActionPreference = 'Stop'

Write-Host "Starting build: Frontend (Vite) + prepare integration venv"

# Frontend
if (Test-Path "Frontend") {
    Push-Location "Frontend"
    if (Test-Path "package-lock.json") {
        Write-Host "Installing frontend dependencies (ci)..."
        npm ci
    } else {
        Write-Host "Installing frontend dependencies (install)..."
        npm install
    }

    Write-Host "Building frontend (production)..."
    npm run build
    Pop-Location
} else {
    Write-Host "Frontend folder not found; skipping frontend build"
}

# Backend
if (Test-Path "integration") {
    Push-Location "integration"
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating Python venv..."
        python -m venv .venv
    }
    Write-Host "Installing backend requirements..."
    .\.venv\Scripts\pip install -r requirements.txt
    Pop-Location
} else {
    Write-Host "integration folder not found; skipping backend prep"
}

Write-Host "Build script completed. Frontend dist/ and backend venv prepared."
