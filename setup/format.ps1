# Format code
Write-Host "✨ Formatting Code..." -ForegroundColor Cyan
Write-Host ""

$backendPath = "..\backend"
$venvPath = "$backendPath\venv\Scripts\activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment not found. Run .\setup\setup.ps1 first" -ForegroundColor Red
    exit 1
}

# Backend formatting
Write-Host "Backend Formatting:" -ForegroundColor Green
Set-Location $backendPath
& ".\venv\Scripts\activate.ps1"
black app/
Set-Location ..\setup

Write-Host ""
Write-Host "Frontend Formatting:" -ForegroundColor Green
Set-Location "..\frontend"
npm run format
Set-Location ..\setup

Write-Host ""
Write-Host "✅ Formatting complete" -ForegroundColor Green
