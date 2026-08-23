@echo off
title WhatsApp Reminders Launcher
color 0E

echo ========================================
echo  WhatsApp Reminders Launcher
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

REM Check if WhatsApp reminder script exists
if not exist "send_whatsapp_reminders.py" (
    echo ERROR: send_whatsapp_reminders.py not found.
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo [%TIME%] Starting WhatsApp reminder script...
echo.

REM Run WhatsApp reminder script with logging
start "WhatsApp Reminders" cmd /k "python send_whatsapp_reminders.py >> logs\reminder_log.txt 2>&1 & echo. & echo WhatsApp Reminder script completed. Check logs\reminder_log.txt for details. & pause"

echo.
echo ========================================
echo  SUCCESS!
echo ========================================
echo.
echo ✅ WhatsApp Reminders started successfully!
echo.
echo Service Running:
echo - WhatsApp Reminders: Running in separate window
echo - Logs: logs\reminder_log.txt
echo.
echo The reminder script will run in its own window.
echo You can close this window safely.
echo.
pause
