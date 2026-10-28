# VerifyAI - Live Public Tunnel Launcher (Auto-Reconnecting)
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "   VerifyAI AICTE Platform - Live Public Tunnel" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

$serverRunning = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if (-not $serverRunning) {
    Write-Host "Starting VerifyAI backend & frontend on port 8000..." -ForegroundColor Yellow
    $env:PYTHONPATH = "d:\26261 SIH\backend"
    Start-Process -FilePath "C:\Users\abdul\AppData\Local\Programs\Python\Python313\python.exe" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

Write-Host "Local Server active at: http://localhost:8000" -ForegroundColor Green
Write-Host "Launching persistent HTTPS tunnel (auto-reconnects on timeout)..." -ForegroundColor Cyan

while ($true) {
    ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -o ServerAliveInterval=10 -R0:127.0.0.1:8000 a.pinggy.io "b:http"
    Write-Host "Tunnel disconnected. Reconnecting in 3 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}
