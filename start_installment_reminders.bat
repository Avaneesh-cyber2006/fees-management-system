@echo off
title Installment WhatsApp Reminders - Pillay Sir's ICSE Classes
color 0E

echo ========================================
echo  📱 Installment WhatsApp Reminders
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

if not exist "send_whatsapp_reminders_installments.py" (
    echo ERROR: send_whatsapp_reminders_installments.py not found.
    pause
    exit /b 1
) else (
    echo ✅ Installment reminder script found
)

echo.
echo [%TIME%] Checking database connection...
REM Test database connection
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
    echo Press any key to continue anyway or Ctrl+C to exit...
    pause
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo.
echo [%TIME%] Starting Enhanced Installment WhatsApp Reminders...
echo.
echo ⚠️  IMPORTANT NOTES:
echo - This script sends reminders based on installment status (Due/Pending only)
echo - Paid installments will NOT receive reminders
echo - WhatsApp Web must be logged in on your default browser
echo - Messages will be sent automatically after confirmation
echo.

echo Press any key to continue or Ctrl+C to cancel...
pause

echo.
echo [%TIME%] Running installment-based WhatsApp reminder script...
echo.

REM Run the enhanced WhatsApp reminder script
python send_whatsapp_reminders_installments.py

echo.
echo [%TIME%] Installment reminder script completed.
echo.

REM Check if log files were created
if exist "logs\whatsapp_reminders_installments_*.xlsx" (
    echo ✅ Excel log files created in logs folder
    echo.
    echo Opening logs folder...
    start "" "logs"
) else (
    echo ℹ️  No log files created (possibly no reminders were sent)
)

echo.
echo ========================================
echo  📊 INSTALLMENT REMINDERS COMPLETED
echo ========================================
echo.
echo 📱 Features of Enhanced System:
echo - ✅ Only sends to Due/Pending installments
echo - ✅ Automatic status updates (Due → Pending)
echo - ✅ Smart message templates based on overdue days
echo - ✅ Database logging of all messages
echo - ✅ Excel report generation
echo - ✅ Multiple parent contact support
echo.
echo 💡 Tips:
echo - Check logs folder for detailed Excel reports
echo - Use Django admin to view message logs
echo - Run installment management panel for status updates
echo.
echo Press any key to exit...
pause
