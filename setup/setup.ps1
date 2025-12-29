# AI Video Editor - Setup Script
# Run: .\setup.ps1

Write-Host "🚀 AI Video Editor - Setup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  This script should ideally run as Administrator" -ForegroundColor Yellow
    Write-Host "   Continuing anyway..." -ForegroundColor Yellow
    Write-Host ""
}

# Function to run commands
function Run-Command {
    param(
        [string]$Description,
        [scriptblock]$Command
    )
    Write-Host "📦 $Description..." -ForegroundColor Green
    try {
        & $Command
        Write-Host "✅ $Description - Complete" -ForegroundColor Green
        Write-Host ""
        return $true
    }
    catch {
        Write-Host "❌ $Description - Failed: $_" -ForegroundColor Red
        Write-Host ""
        return $false
    }
}

# Setup Backend
Write-Host "🔧 Setting up Backend..." -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

$backendPath = "..\backend"
if (-not (Test-Path $backendPath)) {
    Write-Host "❌ Backend directory not found at $backendPath" -ForegroundColor Red
    exit 1
}

# Create venv
Run-Command "Creating Python virtual environment" {
    Set-Location $backendPath
    python -m venv venv
    Set-Location ..\setup
}

# Activate venv and upgrade pip
Run-Command "Upgrading pip" {
    Set-Location $backendPath
    & ".\venv\Scripts\python.exe" -m pip install --upgrade pip
    Set-Location ..\setup
}

# Install UV
Run-Command "Installing UV package manager" {
    Set-Location $backendPath
    & ".\venv\Scripts\pip.exe" install uv
    Set-Location ..\setup
}

# Install dependencies
Run-Command "Installing backend dependencies" {
    Set-Location $backendPath
    & ".\venv\Scripts\uv.exe" pip install -e ".[dev]"
    Set-Location ..\setup
}

# Setup Frontend
Write-Host "🎨 Setting up Frontend..." -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

$frontendPath = "..\frontend"
if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ Frontend directory not found at $frontendPath" -ForegroundColor Red
    exit 1
}

Run-Command "Installing frontend dependencies" {
    Set-Location $frontendPath
    npm install
    Set-Location ..\setup
}

# Summary
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Start backend:   ..\dev-backend.ps1" -ForegroundColor White
Write-Host "  2. Start frontend:  ..\dev-frontend.ps1" -ForegroundColor White
Write-Host "  3. Or start all:    ..\dev.ps1" -ForegroundColor White
Write-Host ""
Write-Host "For more commands, see:" -ForegroundColor Cyan
Write-Host "  - ..\dev.ps1              (Start all services)" -ForegroundColor White
Write-Host "  - ..\dev-backend.ps1      (Start backend only)" -ForegroundColor White
Write-Host "  - ..\dev-frontend.ps1     (Start frontend only)" -ForegroundColor White
Write-Host "  - ..\test.ps1             (Run tests)" -ForegroundColor White
Write-Host "  - ..\lint.ps1             (Lint code)" -ForegroundColor White
Write-Host "  - ..\format.ps1           (Format code)" -ForegroundColor White
Write-Host ""
