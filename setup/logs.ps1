# View Docker logs
Write-Host "📋 Docker Logs..." -ForegroundColor Cyan
Write-Host ""

Set-Location ".."
docker-compose logs -f
