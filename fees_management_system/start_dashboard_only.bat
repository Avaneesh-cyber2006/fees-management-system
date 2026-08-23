@echo off
title Django Dashboard Launcher - Pillay Sir's ICSE Classes
color 0A

echo ========================================
echo  Django Dashboard Launcher
echo  Pillay Sir's ICSE Classes
echo ========================================
echo.

REM Use relative paths so it works on any computer
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Check if Python is available
echo [%TIME%] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
) else (
    echo ✅ Python found
)

REM Check if Django project files exist
if not exist "manage.py" (
    echo ERROR: manage.py not found. Please run this script from the Django project root.
    pause
    exit /b 1
) else (
    echo ✅ Django project files found
)

echo.
echo [%TIME%] Checking MySQL server connection...
REM Try to start MySQL service (common service names)
net start mysql >nul 2>&1
net start mysql80 >nul 2>&1
net start mysql57 >nul 2>&1
net start "MySQL80" >nul 2>&1

REM Set Django settings module
set DJANGO_SETTINGS_MODULE=fees_management_system.settings

REM Test database connection with proper error handling
echo Testing database connection...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings'); import django; django.setup(); from django.db import connection; connection.ensure_connection(); print('✅ Database connection successful')" 2>nul
if errorlevel 1 (
    echo.
    echo ========================================
    echo  DATABASE CONNECTION ERROR
    echo ========================================
    echo.
    echo ❌ Cannot connect to MySQL database 'pclasses'
    echo.
    echo Please ensure:
    echo 1. MySQL server is running
    echo 2. Database 'pclasses' exists
    echo 3. User 'root' has access with password 'Root'
    echo.
    echo To start MySQL manually:
    echo - Open MySQL Workbench or phpMyAdmin
    echo - Or start XAMPP/WAMP if you're using them
    echo.
    echo Press any key to continue anyway or Ctrl+C to exit...
    pause
)

echo.
echo [%TIME%] Installing/updating Python dependencies...
pip install -r requirements.txt >nul 2>&1

echo [%TIME%] Running Django migrations...
python manage.py migrate >nul 2>&1

echo [%TIME%] Collecting static files...
python manage.py collectstatic --noinput >nul 2>&1

echo.
echo [%TIME%] Starting Django development server...
echo.

REM Start Django development server in a new window
start "Django Server - Pillay Sir's ICSE Classes" cmd /k "echo Starting Django Server... && python manage.py runserver 127.0.0.1:8000"

echo [%TIME%] Waiting 8 seconds for Django server to start...
timeout /t 8 /nobreak >nul

echo [%TIME%] Opening dashboard in default browser...
REM Try multiple browsers and URLs
start "" "http://127.0.0.1:8000/dashboard/" 2>nul
timeout /t 2 /nobreak >nul
start "" "http://localhost:8000/dashboard/" 2>nul

echo.
echo ========================================
echo  🎉 SUCCESS!
echo ========================================
echo.
echo ✅ Django Dashboard launched successfully!
echo.
echo 🌐 Service URLs:
echo - Dashboard: http://127.0.0.1:8000/dashboard/
echo - Admin Panel: http://127.0.0.1:8000/admin/
echo - API Endpoints: http://127.0.0.1:8000/api/
echo.
echo 📱 Features Available:
echo - Student Registration
echo - Fee Management with Mark as Paid
echo - Blacklisted Students Panel
echo - Custom WhatsApp Messages
echo - Automated Birthday Wishes
echo - 5-Level Reminder System
echo.
echo 💡 The Django server is running in a separate window.
echo    You can close this window safely.
echo.
echo Press any key to exit this launcher...
pause >nul
