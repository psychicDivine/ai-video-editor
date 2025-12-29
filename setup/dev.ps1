# Start all services (Docker)
Write-Host "🚀 Starting all services with Docker..." -ForegroundColor Cyan
Write-Host ""

Set-Location ".."
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Services started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access points:" -ForegroundColor Cyan
    Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "View logs:" -ForegroundColor Cyan
    Write-Host "  .\setup\logs.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Stop services:" -ForegroundColor Cyan
    Write-Host "  .\setup\stop.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}
