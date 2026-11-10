@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_tamil_font.ps1"
if errorlevel 1 (
    echo.
    echo Font installation failed. Please check the error above.
    pause
    exit /b 1
)
echo.
pause
