# VerifyAI - Live Public Tunnel Launcher
# This script ensures the local server and public tunnel are running.

Write-Host "Checking if VerifyAI server is running on port 8000..." -ForegroundColor Cyan

$serverRunning = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if (-not $serverRunning) {
    Write-Host "Starting VerifyAI backend & frontend on port 8000..." -ForegroundColor Yellow
    $env:PYTHONPATH = "d:\26261 SIH\backend"
    Start-Process -FilePath "C:\Users\abdul\AppData\Local\Programs\Python\Python313\python.exe" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

Write-Host "VerifyAI Server is Active on http://localhost:8000" -ForegroundColor Green
Write-Host "Connecting to public HTTPS tunnel..." -ForegroundColor Cyan

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=15 -R 80:127.0.0.1:8000 serveo.net
