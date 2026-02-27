@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PID_FILE=.keyhub.pid"

if not exist "%PID_FILE%" (
  echo [INFO] %PID_FILE% not found in %CD%
  echo        KEYHUB may not be running, or it was started elsewhere.
  exit /b 0
)

set /p KH_PID=<"%PID_FILE%"
for /f "tokens=*" %%a in ("%KH_PID%") do set "KH_PID=%%a"

echo [INFO] Stopping KEYHUB (PID %KH_PID%)...

REM Validate PID is numeric
echo %KH_PID%| findstr /r "^[0-9][0-9]*$" >nul
if errorlevel 1 (
  echo [ERROR] Invalid PID in %PID_FILE%: "%KH_PID%"
  exit /b 1
)

taskkill /PID %KH_PID% /T /F >nul 2>&1
if errorlevel 1 (
  echo [WARN] taskkill failed for PID %KH_PID%.
  echo        The process may already be stopped, or permission was denied.
) else (
  echo [OK] taskkill sent.
)

REM Best-effort cleanup; run_keyhub_web.py also cleans up on atexit.
del /f /q "%PID_FILE%" >nul 2>&1

echo [INFO] Done.
exit /b 0
