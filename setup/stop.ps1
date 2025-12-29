# Stop Docker services
Write-Host "🛑 Stopping Services..." -ForegroundColor Cyan
Write-Host ""

Set-Location ".."
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Services stopped" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to stop services" -ForegroundColor Red
    exit 1
}
