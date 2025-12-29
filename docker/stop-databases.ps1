# Stop Podman Databases - Redis & PostgreSQL

Write-Host "🛑 Stopping Podman Databases..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Stop services
Write-Host "Stopping services..." -ForegroundColor Yellow
podman-compose -f docker-compose.yml down

Write-Host ""
Write-Host "✅ Databases stopped" -ForegroundColor Green
Write-Host ""
Write-Host "💾 Data is preserved in volumes" -ForegroundColor Cyan
Write-Host "   Run 'podman-compose -f docker-compose.yml down -v' to delete data" -ForegroundColor Gray
Write-Host ""
