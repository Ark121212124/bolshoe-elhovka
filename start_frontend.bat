@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "FRONTEND=%CD%\frontend"

if not exist "%FRONTEND%\index.html" (
  echo [ERROR] index.html was not found here:
  echo %FRONTEND%\index.html
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
  pause
  exit /b 1
)

cd /d "%FRONTEND%"
echo Starting frontend site...
echo Site: http://127.0.0.1:5500
echo.
%PYTHON_CMD% -m http.server 5500 --bind 127.0.0.1
pause
