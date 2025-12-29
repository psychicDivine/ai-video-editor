# Start Podman Databases - Redis & PostgreSQL

Write-Host "🐳 Starting Podman Databases..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Podman is installed
try {
    $podmanVersion = podman --version
    Write-Host "✅ Podman installed: $podmanVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Podman not installed. Install from: https://podman.io/" -ForegroundColor Red
    exit 1
}

# Start Podman machine
Write-Host ""
Write-Host "🚀 Starting Podman machine..." -ForegroundColor Cyan
podman machine start
Write-Host "✅ Podman machine started" -ForegroundColor Green

# Start services
Write-Host ""
Write-Host "🐘 Starting PostgreSQL & Redis..." -ForegroundColor Cyan
podman-compose -f docker-compose.yml up -d

# Wait for services to be ready
Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check status
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
podman-compose -f docker-compose.yml ps

# Display connection details
Write-Host ""
Write-Host "✅ Databases Ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Connection Details:" -ForegroundColor Cyan
Write-Host ""
Write-Host "PostgreSQL:" -ForegroundColor White
Write-Host "  Host:     localhost" -ForegroundColor Gray
Write-Host "  Port:     5432" -ForegroundColor Gray
Write-Host "  Database: ai_video_editor" -ForegroundColor Gray
Write-Host "  User:     editor" -ForegroundColor Gray
Write-Host "  Password: editor_pass" -ForegroundColor Gray
Write-Host ""
Write-Host "Redis:" -ForegroundColor White
Write-Host "  Host:     localhost" -ForegroundColor Gray
Write-Host "  Port:     6379" -ForegroundColor Gray
Write-Host ""

# Test connections
Write-Host "🧪 Testing Connections..." -ForegroundColor Cyan
Write-Host ""

# Test Redis
try {
    $redisTest = redis-cli -h localhost ping
    if ($redisTest -eq "PONG") {
        Write-Host "✅ Redis: Connected" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Redis: Could not test (redis-cli not installed)" -ForegroundColor Yellow
}

# Test PostgreSQL
try {
    $pgTest = podman exec ai_video_editor_postgres pg_isready -U editor
    Write-Host "✅ PostgreSQL: Ready" -ForegroundColor Green
} catch {
    Write-Host "⚠️  PostgreSQL: Could not test" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📖 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Update backend/.env with connection strings" -ForegroundColor White
Write-Host "  2. Connect DBeaver to PostgreSQL (see README.md)" -ForegroundColor White
Write-Host "  3. Start backend: uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "  4. Start Celery worker: celery -A app.celery_app worker --loglevel=info" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop databases:" -ForegroundColor Cyan
Write-Host "  podman-compose -f docker-compose.yml down" -ForegroundColor White
Write-Host ""
