<#
Check full stack status:
 - Detect Podman or Docker containers named 'postgres' and 'redis'
 - Check TCP ports 5432 (Postgres), 6379 (Redis), 8000 (backend), 3000 (frontend)
 - Check HTTP health endpoints for backend and frontend
 - Optionally start frontend dev server
#>

function Get-ContainerStatus($name) {
    if (Get-Command podman -ErrorAction SilentlyContinue) {
        try {
            $out = podman ps --filter "name=$name" --format "{{.Names}}|{{.Status}}" 2>$null
            if ($out) { return $out }
        } catch { }
    }
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        try {
            $out = docker ps --filter "name=$name" --format "{{.Names}}|{{.Status}}" 2>$null
            if ($out) { return $out }
        } catch { }
    }
    return $null
}

function Test-TcpPort($hostname, $port, $timeoutMs = 1000) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect($hostname, $port, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne($timeoutMs)
        if (-not $wait) { $client.Close(); return $false }
        $client.EndConnect($iar)
        $client.Close()
        return $true
    } catch {
        return $false
    }
}

function Test-HttpOk($url, $timeoutSec = 3) {
    try {
        $wc = New-Object System.Net.WebClient
        $wc.Encoding = [System.Text.Encoding]::UTF8
        $wc.Proxy = $null
        $wc.DownloadString($url) | Out-Null
        return $true
    } catch {
        return $false
    }
}

Write-Host "Checking stack components..." -ForegroundColor Cyan

$components = @(
    @{ Name='postgres'; Port=5432; ContainerName='postgres' },
    @{ Name='redis'; Port=6379; ContainerName='redis' },
    @{ Name='backend'; Port=8000; Health='http://localhost:8000/health' },
    @{ Name='frontend'; Port=3000; Health='http://localhost:3000' }
)

$allGood = $true

foreach ($c in $components) {
    $name = $c.Name
    $port = $c.Port
    $containerName = $c.ContainerName
    $health = $c.Health

    if ($containerName) {
        $status = Get-ContainerStatus $containerName
        if ($status) {
            Write-Host ("Container found for {0}: {1}" -f $name, $status) -ForegroundColor Green
        } else {
            # fall back to port check
                if (Test-TcpPort 'localhost' $port) {
                Write-Host ("{0} port {1} is open" -f $name, $port) -ForegroundColor Green
            } else {
                Write-Host ("{0} not running (no container and port {1} closed)" -f $name, $port) -ForegroundColor Yellow
                $allGood = $false
            }
        }
    } elseif ($health) {
        # services without containers
        if (Test-TcpPort 'localhost' $port) {
            if (Test-HttpOk $health) {
                Write-Host ("{0} responded OK at {1}" -f $name, $health) -ForegroundColor Green
            } else {
                Write-Host ("{0} port {1} is open but HTTP health failed" -f $name, $port) -ForegroundColor Yellow
                $allGood = $false
            }
        } else {
            Write-Host ("{0} not responding on port {1}" -f $name, $port) -ForegroundColor Yellow
            $allGood = $false
        }
    }
}

if (-not $allGood) {
    Write-Host "\nSome services are not running. Recommendations:" -ForegroundColor Red
    Write-Host " - Start databases: .\start-databases.ps1 or docker-compose up -d (see docker/)" -ForegroundColor Yellow
    Write-Host " - Start backend: cd backend; uv run uvicorn app.main:app --reload" -ForegroundColor Yellow
    Write-Host " - Start frontend: cd frontend; npm run dev" -ForegroundColor Yellow

    # Offer to start frontend interactively
    $startFront = Read-Host "Start frontend dev server now? (y/N)"
    if ($startFront -and $startFront.ToLower().StartsWith('y')) {
        Write-Host "Starting frontend (npm run dev) in new window..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$PWD\frontend`"; npm run dev" -WorkingDirectory (Get-Location)
    }
    exit 2
} else {
    Write-Host "All checked services appear healthy." -ForegroundColor Green
    exit 0
}
