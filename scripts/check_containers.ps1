# Check if postgres and redis containers are running using Podman or Docker
# Usage: .\check_containers.ps1
param()

function Check-With-Podman {
    $names = @('postgres','redis')
    $found = $false
    try {
        $ps = podman ps --format "{{.Names}}|{{.Status}}" 2>$null
        foreach ($line in $ps) {
            $parts = $line -split '\|'
            if ($parts.Count -ge 2) {
                $name = $parts[0]
                $status = $parts[1]
                if ($names -contains $name) {
                    Write-Host "Podman: $name => $status"
                    $found = $true
                }
            }
        }
        return $found
    } catch {
        return $false
    }
}

function Check-With-Docker {
    $names = @('postgres','redis')
    $found = $false
    try {
        $ps = docker ps --format "{{.Names}}|{{.Status}}" 2>$null
        foreach ($line in $ps) {
            $parts = $line -split '\|'
            if ($parts.Count -ge 2) {
                $name = $parts[0]
                $status = $parts[1]
                if ($names -contains $name) {
                    Write-Host "Docker: $name => $status"
                    $found = $true
                }
            }
        }
        return $found
    } catch {
        return $false
    }
}

Write-Host "Checking for Podman/Docker containers: postgres, redis" -ForegroundColor Cyan

if (Get-Command podman -ErrorAction SilentlyContinue) {
    Write-Host "Podman found, checking containers..."
    $ok = Check-With-Podman
    if ($ok) { exit 0 } else { Write-Host "No matching Podman containers found." -ForegroundColor Yellow }
}

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Docker found, checking containers..."
    $ok = Check-With-Docker
    if ($ok) { exit 0 } else { Write-Host "No matching Docker containers found." -ForegroundColor Yellow }
}

Write-Host "Neither Podman nor Docker reported running postgres/redis containers." -ForegroundColor Red
exit 2
