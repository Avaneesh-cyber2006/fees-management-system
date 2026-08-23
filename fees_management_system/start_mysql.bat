@echo off
title Start MySQL Service
color 0A

echo ========================================
echo  Starting MySQL Service
echo ========================================
echo.

echo Attempting to start MySQL80 service...
net start MySQL80
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start MySQL service.
    echo This usually means:
    echo 1. You need to run this as Administrator
    echo 2. MySQL is already running
    echo 3. MySQL service is not installed properly
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
) else (
    echo.
    echo ✅ MySQL service started successfully!
    echo You can now run start_dashboard_and_reminders.bat
    echo.
)

pause
