@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_auth.ps1"
echo.
echo Exit code: %errorlevel%
pause
