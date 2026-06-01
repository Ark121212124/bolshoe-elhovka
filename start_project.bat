@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo  DIPLOM APPEALS CRM - SAFE START
echo ==================================================
echo.
echo This script starts backend first and waits until it is ready.
echo Do not close Backend API CRM and Frontend Site windows while testing.
echo.

echo [1/3] Starting backend in a new window...
start "Backend API CRM" cmd /k ""%~dp0start_backend.bat""

echo.
echo [2/3] Waiting for backend: http://127.0.0.1:8000/api/health
echo This can take 1-3 minutes on first run while Python packages are installed.

timeout /t 5 /nobreak >nul
set "READY=0"
for /l %%i in (1,1,60) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>nul
  if not errorlevel 1 (
    set "READY=1"
    goto backend_ready
  )
  echo Waiting... %%i/60
  timeout /t 2 /nobreak >nul
)

:backend_ready
if not "%READY%"=="1" (
  echo.
  echo [ERROR] Backend did not start.
  echo Open the black window named "Backend API CRM" and send the FIRST red error from it.
  echo Also check file: backend_start_log.txt if it exists.
  echo.
  pause
  exit /b 1
)

echo Backend is ready.
echo.
echo [3/3] Starting frontend in a new window...
start "Frontend Site" cmd /k ""%~dp0start_frontend.bat""
timeout /t 2 /nobreak >nul

start http://127.0.0.1:5500
start http://127.0.0.1:8000/crm
start http://127.0.0.1:8000/docs

echo.
echo ==================================================
echo Started successfully.
echo Site: http://127.0.0.1:5500
echo CRM:  http://127.0.0.1:8000/crm
echo API:  http://127.0.0.1:8000/docs
echo Login: admin / admin123
echo ==================================================
echo.
pause
