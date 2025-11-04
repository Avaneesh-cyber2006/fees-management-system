@echo off
title Quick Django Dashboard - Pillay Sir's ICSE Classes
color 0B

echo ==========================================
echo  🚀 Quick Django Dashboard Launcher
echo  Pillay Sir's ICSE Classes
echo ==========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo ✅ Python found
echo ✅ Starting Django server...
echo.

REM Start Django server
start "Django Server" cmd /k "python manage.py runserver 127.0.0.1:8000"

REM Wait and open browser
echo Waiting 5 seconds for server to start...
timeout /t 5 /nobreak >nul

echo Opening dashboard in browser...
start "" "http://127.0.0.1:8000/dashboard/"

echo.
echo ==========================================
echo  ✅ Dashboard launched!
echo ==========================================
echo.
echo 🌐 Dashboard URL: http://127.0.0.1:8000/dashboard/
echo 🔧 Admin Panel: http://127.0.0.1:8000/admin/
echo.
echo The server is running in a separate window.
echo You can close this window now.
echo.
pause
