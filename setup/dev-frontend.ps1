# Start frontend development server
Write-Host "🚀 Starting Frontend (React + Vite)..." -ForegroundColor Cyan
Write-Host ""

$frontendPath = "..\frontend"
$nodeModulesPath = "$frontendPath\node_modules"

if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "❌ Dependencies not found. Run .\setup\setup.ps1 first" -ForegroundColor Red
    exit 1
}

Set-Location $frontendPath
Write-Host "Starting Vite dev server on http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

npm run dev
