@echo off
title VerifyAI Full-Stack Platform (SIH26261)
cd /d "d:\26261 SIH\backend"
set PYTHONPATH=d:\26261 SIH\backend
echo ========================================================
echo Starting VerifyAI Platform on http://localhost:8000
echo ========================================================
"C:\Users\abdul\AppData\Local\Programs\Python\Python313\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
