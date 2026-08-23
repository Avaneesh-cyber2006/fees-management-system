@echo off
title Django Dashboard and WhatsApp Reminders Launcher
color 0A

echo ========================================
echo  Django Dashboard and WhatsApp Launcher
echo ========================================
echo.

REM Use relative paths so it works on any computer
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if Django project files exist
if not exist "manage.py" (
    echo ERROR: manage.py not found. Please run this script from the Django project root.
    pause
    exit /b 1
)

if not exist "send_whatsapp_reminders.py" (
    echo ERROR: send_whatsapp_reminders.py not found.
    pause
    exit /b 1
)

echo [%TIME%] Checking MySQL server connection...
REM Try to start MySQL service (common service names)
net start mysql >nul 2>&1
net start mysql80 >nul 2>&1
net start mysql57 >nul 2>&1
net start "MySQL80" >nul 2>&1

REM Test database connection
python manage.py check --database default >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo  DATABASE CONNECTION ERROR
    echo ========================================
    echo.
    echo ERROR: Cannot connect to MySQL database 'pclasses'
    echo.
    echo Please ensure:
    echo 1. MySQL server is running
    echo 2. Database 'pclasses' exists
    echo 3. User 'root' has access with password 'Root'
    echo.
    echo To start MySQL manually:
    echo - Run Command Prompt as Administrator and execute: net start MySQL80
    echo - Or open MySQL Workbench or phpMyAdmin
    echo - Or start XAMPP/WAMP if you're using them
    echo.
    echo Alternatively, use start_dashboard_sqlite.bat for SQLite development.
    echo.
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo [%TIME%] Starting Django development server in new terminal...
echo.

REM Start Django development server in a new terminal
start "Django Server" cmd /k "python manage.py runserver"

echo [%TIME%] Waiting 10 seconds for Django server to start...
timeout /t 10 /nobreak >nul

echo [%TIME%] Opening dashboard in default browser...
REM Open browser at dashboard URL
start "" "http://127.0.0.1:8000/dashboard/"

echo [%TIME%] Waiting 5 seconds before starting WhatsApp reminders...
REM Wait another 5 seconds
timeout /t 5 /nobreak >nul

echo [%TIME%] Running WhatsApp reminder script in new terminal...
echo.

REM Run WhatsApp reminder script in a new terminal with logging
start "WhatsApp Reminders" cmd /k "python send_whatsapp_reminders.py >> logs\reminder_log.txt 2>&1 & echo. & echo WhatsApp Reminder script completed. Check logs\reminder_log.txt for details. & pause"

echo.
echo ========================================
echo  SUCCESS!
echo ========================================
echo.
echo ✅ Django Dashboard launched and WhatsApp Reminders started successfully!
echo.
echo Services Running:
echo - Django Server: http://127.0.0.1:8000/dashboard/
echo - WhatsApp Reminders: Running in separate window
echo - Logs: logs\reminder_log.txt
echo.
echo Both terminals will remain open and running independently.
echo You can close this window safely.
echo.
pause
