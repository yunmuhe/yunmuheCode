@echo off
setlocal
cd /d "%~dp0"

call "%~dp0KEYHUB-Stop-Windows.bat"

REM small delay to allow port and process cleanup
timeout /t 1 /nobreak >nul

call "%~dp0KEYHUB-Start-Windows.bat"
