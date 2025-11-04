@echo off
:: ==============================================================================
:: SETUP AUTOMATIC MAINTENANCE - Fees Management System
:: This script sets up Windows Task Scheduler for automated data maintenance
:: ==============================================================================

title Setup Automatic Maintenance

:: Check for administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] This script requires administrator privileges.
    echo [INFO] Right-click and select "Run as administrator"
    pause
    exit /b 1
)

color 0E
echo.
echo ===============================================================================
echo                      SETUP AUTOMATIC MAINTENANCE
echo ===============================================================================
echo.
echo This will create Windows scheduled tasks for automatic data maintenance:
echo.
echo   1. Daily Quick Check    - Every day at 9:00 AM
echo   2. Weekly Deep Check    - Every Sunday at 2:00 AM
echo   3. Emergency Fix        - On-demand manual trigger
echo.

set /p confirm="Do you want to proceed? (y/N): "
if /i not "%confirm%"=="y" (
    echo Setup cancelled.
    pause
    exit /b 0
)

:: Get the current directory (project root)
set "project_path=%~dp0"
set "project_path=%project_path:~0,-1%"

echo.
echo [INFO] Project path: %project_path%
echo [INFO] Setting up scheduled tasks...

:: Task 1: Daily Quick Check
echo.
echo [INFO] Creating daily quick check task...
schtasks /create /tn "FeesSystem_DailyCheck" /tr "\"%project_path%\quick_data_check.bat\"" /sc daily /st 09:00 /ru "SYSTEM" /f
if %errorlevel% equ 0 (
    echo [SUCCESS] ✅ Daily check task created
) else (
    echo [ERROR] ❌ Failed to create daily check task
)

:: Task 2: Weekly Deep Maintenance
echo.
echo [INFO] Creating weekly maintenance task...
schtasks /create /tn "FeesSystem_WeeklyMaintenance" /tr "\"%project_path%\scheduled_maintenance.bat\"" /sc weekly /d SUN /st 02:00 /ru "SYSTEM" /f
if %errorlevel% equ 0 (
    echo [SUCCESS] ✅ Weekly maintenance task created
) else (
    echo [ERROR] ❌ Failed to create weekly maintenance task
)

:: Task 3: Emergency Fix (Manual)
echo.
echo [INFO] Creating emergency fix task...
schtasks /create /tn "FeesSystem_EmergencyFix" /tr "\"%project_path%\auto_fix_data_issues.bat\"" /sc once /st 23:59 /sd 01/01/2030 /ru "SYSTEM" /f
if %errorlevel% equ 0 (
    echo [SUCCESS] ✅ Emergency fix task created (manual trigger only)
) else (
    echo [ERROR] ❌ Failed to create emergency fix task
)

echo.
echo ===============================================================================
echo                              SETUP COMPLETE
echo ===============================================================================
echo.
echo Scheduled tasks created:
echo.
echo 📅 DAILY CHECK (9:00 AM)
echo    Task Name: FeesSystem_DailyCheck
echo    Action: Quick data validation and auto-fix
echo    Command: schtasks /run /tn "FeesSystem_DailyCheck"
echo.
echo 📅 WEEKLY MAINTENANCE (Sunday 2:00 AM)
echo    Task Name: FeesSystem_WeeklyMaintenance
echo    Action: Comprehensive data check and maintenance
echo    Command: schtasks /run /tn "FeesSystem_WeeklyMaintenance"
echo.
echo 🚨 EMERGENCY FIX (Manual only)
echo    Task Name: FeesSystem_EmergencyFix
echo    Action: Complete data integrity check and fix
echo    Command: schtasks /run /tn "FeesSystem_EmergencyFix"
echo.
echo ===============================================================================
echo                               USAGE COMMANDS
echo ===============================================================================
echo.
echo To manually run tasks:
echo   schtasks /run /tn "FeesSystem_DailyCheck"
echo   schtasks /run /tn "FeesSystem_WeeklyMaintenance"
echo   schtasks /run /tn "FeesSystem_EmergencyFix"
echo.
echo To view task status:
echo   schtasks /query /tn "FeesSystem_DailyCheck"
echo.
echo To delete tasks (if needed):
echo   schtasks /delete /tn "FeesSystem_DailyCheck" /f
echo   schtasks /delete /tn "FeesSystem_WeeklyMaintenance" /f
echo   schtasks /delete /tn "FeesSystem_EmergencyFix" /f
echo.

:: Test the daily check task
set /p test_run="Do you want to test the daily check task now? (y/N): "
if /i "%test_run%"=="y" (
    echo.
    echo [INFO] Running test of daily check task...
    schtasks /run /tn "FeesSystem_DailyCheck"
    echo [INFO] Task started. Check Task Scheduler for results.
)

echo.
echo [SUCCESS] Automatic maintenance setup completed!
echo [INFO] Your system will now automatically check for data issues daily.
echo [INFO] Logs will be stored in the 'logs' folder.
echo.
pause
