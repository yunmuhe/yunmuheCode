@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  KEYHUB Web UI - Startup Check
echo ============================================
echo.

REM --- Check Python ---
echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  [OK] %%v

REM --- Check Flask ---
echo [2/3] Checking Flask...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo  [MISSING] Flask not installed.
    set /p _kh_install_flask=  Install Flask now? [y/n]:
    if /I "%_kh_install_flask%"=="y" (
        echo  Installing Flask...
        pip install flask
        if errorlevel 1 (
            echo  [ERROR] Failed to install Flask. Run: pip install flask
            pause
            exit /b 1
        )
        echo  [OK] Flask installed.
    ) else (
        echo  Aborted. Run: pip install flask
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%v in ('python -c "import flask; print(flask.__version__)"') do echo  [OK] Flask %%v
)

REM --- Check project files ---
echo [3/3] Checking project files...
if not exist "run_keyhub_web.py" (
    echo  [ERROR] run_keyhub_web.py not found in %CD%
    pause
    exit /b 1
)
echo  [OK] Project files found.

echo.
echo ============================================
echo  Starting KEYHUB Web UI (silent mode)...
echo ============================================
echo.

REM Launch Flask silently via pythonw (no console window)
start "" /B pythonw run_keyhub_web.py --no-debug

REM Wait for server to be ready
echo  Waiting for server to start...
timeout /t 2 /nobreak >nul

REM Open browser
echo  Opening http://127.0.0.1:5000 ...
start "" "http://127.0.0.1:5000"

echo  Done. KEYHUB is running silently in the background.
echo  Use KEYHUB-Stop-Windows.bat to stop, or KEYHUB-Restart-Windows.bat to restart.
timeout /t 2 /nobreak >nul
exit
