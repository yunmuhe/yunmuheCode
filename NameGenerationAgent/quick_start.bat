@echo off
chcp 65001 >nul
setlocal

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%" >nul

echo ========================================
echo Name Generation Agent - Quick Start
echo ========================================
echo.

echo [1/2] Checking .env file...
if not exist ".env" (
    echo [INFO] .env was not found. Creating it from env.example...
    copy "env.example" ".env" >nul
    echo [INFO] .env created. Update it with your configuration before continuing.
    echo.
    popd
    pause
    exit /b 1
) else (
    echo [OK] .env already exists.
)

echo.
echo [2/2] Starting web service...
echo.

for %%I in ("%SCRIPT_DIR%..") do set "ROOT_DIR=%%~fI"
set "PYTHON_EXE=%ROOT_DIR%\.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Required virtual environment was not found:
    echo         %PYTHON_EXE%
    echo [HINT] Create or repair the root .venv before starting the app.
    popd
    pause
    exit /b 1
)

echo [INFO] Using Python: %PYTHON_EXE%
"%PYTHON_EXE%" "%SCRIPT_DIR%main.py"

popd
pause
