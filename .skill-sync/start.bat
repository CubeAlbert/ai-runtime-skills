@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

set "PY=%PYTHON%"
if "%PY%"=="" set "PY=python"

rem Verify Python is available before running.
where %PY% >nul 2>&1
if errorlevel 1 (
    echo [skill-sync] ERROR: '%PY%' not found on PATH.
    echo [skill-sync] Install Python from https://python.org, or set the PYTHON env var.
    echo.
    pause >nul
    exit /b 1
)

%PY% "%SCRIPT_DIR%skill-sync.py" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
    echo.
    echo [skill-sync] exited with code %RC%. Press any key to close.
    pause >nul
) else (
    echo.
    timeout /t 5 2>nul
)
endlocal & exit /b %RC%
