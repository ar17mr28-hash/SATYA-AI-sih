@echo off
title VerifyAI Public Tunnel Launcher
echo Starting VerifyAI Auto-Reconnecting Tunnel...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_tunnel.ps1"
pause
