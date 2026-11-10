@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 senthamil_app.py
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        python senthamil_app.py
    ) else if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
        "%LocalAppData%\Programs\Python\Python312\python.exe" senthamil_app.py
    ) else (
        echo Python was not found. Install Python 3.12, then try again.
        pause
        exit /b 1
    )
)
if errorlevel 1 pause
