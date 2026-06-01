@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "ROOT=%CD%"
set "BACKEND=%ROOT%\backend"
set "VENV=%BACKEND%\.venv"
set "LOG=%ROOT%\backend_start_log.txt"

echo ================================================== > "%LOG%"
echo BACKEND START LOG >> "%LOG%"
echo Date: %DATE% %TIME% >> "%LOG%"
echo Root: %ROOT% >> "%LOG%"
echo Backend: %BACKEND% >> "%LOG%"
echo ================================================== >> "%LOG%"
echo. >> "%LOG%"

echo ==================================================
echo  Backend API CRM
echo ==================================================
echo Log file: %LOG%
echo.

if not exist "%BACKEND%\requirements.txt" (
  echo [ERROR] requirements.txt was not found here:
  echo %BACKEND%\requirements.txt
  echo [ERROR] requirements.txt was not found here: %BACKEND%\requirements.txt >> "%LOG%"
  pause
  exit /b 1
)

set "PYTHON_CMD="
where py >nul 2>nul
if %errorlevel%==0 set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
  where python >nul 2>nul
  if %errorlevel%==0 set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
  echo [ERROR] Python was not found.
  echo Install Python 3.11 or 3.12 from python.org and tick Add Python to PATH.
  echo [ERROR] Python was not found. >> "%LOG%"
  pause
  exit /b 1
)

echo [1/4] Python version:
echo [1/4] Python version: >> "%LOG%"
%PYTHON_CMD% --version
%PYTHON_CMD% --version >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERROR] Python exists, but it cannot be started.
  echo [ERROR] Python exists, but it cannot be started. >> "%LOG%"
  pause
  exit /b 1
)

echo.
echo [2/4] Creating virtual environment if needed...
echo [2/4] Creating virtual environment if needed... >> "%LOG%"
if not exist "%VENV%\Scripts\python.exe" (
  %PYTHON_CMD% -m venv "%VENV%" >> "%LOG%" 2>&1
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    echo See backend_start_log.txt
    pause
    exit /b 1
  )
)

echo.
echo [3/4] Installing backend dependencies...
echo [3/4] Installing backend dependencies... >> "%LOG%"
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERROR] Failed to upgrade pip.
  echo See backend_start_log.txt
  pause
  exit /b 1
)
"%VENV%\Scripts\python.exe" -m pip install -r "%BACKEND%\requirements.txt" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ERROR] Failed to install requirements.
  echo See backend_start_log.txt
  pause
  exit /b 1
)

cd /d "%BACKEND%"
set "DATABASE_URL=sqlite:///./appeals.db"
set "SECRET_KEY=local-dev-secret-key-change-for-production"
set "CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000"

echo.
echo [4/4] Starting FastAPI backend...
echo API docs: http://127.0.0.1:8000/docs
echo CRM:      http://127.0.0.1:8000/crm
echo Health:   http://127.0.0.1:8000/api/health
echo Demo CRM login: admin / admin123
echo.
echo [4/4] Starting FastAPI backend... >> "%LOG%"
"%VENV%\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo.
echo [ERROR] Backend stopped. If you did not close it manually, send a screenshot of this window.
echo [ERROR] Backend stopped. >> "%LOG%"
pause
