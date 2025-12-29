# Start backend development server
Write-Host "🚀 Starting Backend (FastAPI)..." -ForegroundColor Cyan
Write-Host ""

$backendPath = "..\backend"
$venvPath = "$backendPath\venv\Scripts\activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment not found. Run .\setup\setup.ps1 first" -ForegroundColor Red
    exit 1
}

# Activate venv and start server
Set-Location $backendPath
& ".\venv\Scripts\activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
