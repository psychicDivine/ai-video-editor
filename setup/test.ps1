# Run all tests
Write-Host "🧪 Running Tests..." -ForegroundColor Cyan
Write-Host ""

$backendPath = "..\backend"
$venvPath = "$backendPath\venv\Scripts\activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment not found. Run .\setup\setup.ps1 first" -ForegroundColor Red
    exit 1
}

# Run backend tests
Write-Host "Backend Tests:" -ForegroundColor Green
Set-Location $backendPath
& ".\venv\Scripts\activate.ps1"
pytest tests/ -v --cov=app
Set-Location ..\setup

Write-Host ""
Write-Host "Frontend Tests:" -ForegroundColor Green
Set-Location "..\frontend"
npm run test
Set-Location ..\setup

Write-Host ""
Write-Host "✅ Tests complete" -ForegroundColor Green
