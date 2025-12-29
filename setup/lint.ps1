# Lint code
Write-Host "🔍 Linting Code..." -ForegroundColor Cyan
Write-Host ""

$backendPath = "..\backend"
$venvPath = "$backendPath\venv\Scripts\activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment not found. Run .\setup\setup.ps1 first" -ForegroundColor Red
    exit 1
}

# Backend linting
Write-Host "Backend Linting:" -ForegroundColor Green
Set-Location $backendPath
& ".\venv\Scripts\activate.ps1"
ruff check app/
Set-Location ..\setup

Write-Host ""
Write-Host "Frontend Linting:" -ForegroundColor Green
Set-Location "..\frontend"
npm run lint
Set-Location ..\setup

Write-Host ""
Write-Host "✅ Linting complete" -ForegroundColor Green
