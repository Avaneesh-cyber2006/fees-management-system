@echo off
title Complete System Launcher - Pillay Sir's ICSE Classes
color 0E

echo ==========================================
echo  🎓 Pillay Sir's ICSE Classes
echo  Complete System Launcher
echo ==========================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo 📁 Current directory: %CD%
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do echo ✅ %%i found
)

REM Check Django project
echo.
echo [2/6] Checking Django project files...
if not exist "manage.py" (
    echo ❌ ERROR: manage.py not found
    echo Please run this script from the Django project root directory
    pause
    exit /b 1
) else (
    echo ✅ Django project files found
)

REM Install/Update dependencies
echo.
echo [3/6] Installing/updating dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet --disable-pip-version-check
    echo ✅ Dependencies updated
) else (
    echo ⚠️  requirements.txt not found, skipping dependency installation
)

REM Check and start MySQL
echo.
echo [4/6] Checking MySQL server...
net start mysql >nul 2>&1
net start mysql80 >nul 2>&1
net start mysql57 >nul 2>&1
net start "MySQL80" >nul 2>&1

REM Test database connection
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings'); import django; django.setup(); from django.db import connection; connection.ensure_connection()" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Database connection failed - continuing anyway
    echo   (You may need to start MySQL manually)
) else (
    echo ✅ Database connection successful
)

REM Run migrations
echo.
echo [5/6] Running database migrations...
python manage.py migrate --verbosity=0 >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Migration warning - continuing anyway
) else (
    echo ✅ Database migrations completed
)

REM Collect static files
python manage.py collectstatic --noinput --verbosity=0 >nul 2>&1

REM Start Django server
echo.
echo [6/6] Starting Django development server...
echo.

start "Django Server - Pillay Sir's ICSE Classes" cmd /k "echo 🚀 Starting Django Server for Pillay Sir's ICSE Classes... && echo. && python manage.py runserver 127.0.0.1:8000"

echo ⏳ Waiting for server to start...
timeout /t 6 /nobreak >nul

echo 🌐 Opening dashboard in browser...
start "" "http://127.0.0.1:8000/dashboard/"

REM Try backup URL after a delay
timeout /t 2 /nobreak >nul
start "" "http://localhost:8000/dashboard/" >nul 2>&1

echo.
echo ==========================================
echo  🎉 SYSTEM LAUNCHED SUCCESSFULLY!
echo ==========================================
echo.
echo 🌐 Access Points:
echo   📊 Main Dashboard: http://127.0.0.1:8000/dashboard/
echo   👨‍💼 Admin Panel:    http://127.0.0.1:8000/admin/
echo   📝 Registration:   http://127.0.0.1:8000/register/
echo   💰 Fee Management: http://127.0.0.1:8000/fees/
echo   ⚠️  Blacklisted:    http://127.0.0.1:8000/blacklisted/
echo   📱 WhatsApp Panel: http://127.0.0.1:8000/custom-whatsapp/
echo.
echo 🚀 New Features Available:
echo   ✅ Blacklisted Students Panel
echo   ✅ Mark as Paid Functionality  
echo   ✅ Custom WhatsApp Messages
echo   ✅ Birthday Wishes Automation
echo   ✅ 5-Level Reminder System
echo   ✅ Updated Course Dropdowns (8th/9th/10th ICSE)
echo   ✅ Updated Branch Options (Sadar/New Katol Naka)
echo.
echo 💡 Tips:
echo   - The Django server runs in a separate window
echo   - Keep that window open while using the system
echo   - You can safely close this launcher window
echo   - Use Ctrl+C in the server window to stop the system
echo.
echo 📞 For support: Contact Pillay Sir
echo.
echo Press any key to close this launcher...
pause >nul
