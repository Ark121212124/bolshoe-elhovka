@echo off
echo Checking backend...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 5 | Select-Object -ExpandProperty Content } catch { Write-Host 'Backend is not running or port 8000 is unavailable'; exit 1 }"
pause
