@echo off
:: ==============================================================================
:: DATA MAINTENANCE MENU - Fees Management System
:: Master control panel for all data integrity operations
:: ==============================================================================

title Data Maintenance Control Panel

:menu
cls
color 0B
echo.
echo ===============================================================================
echo                      DATA MAINTENANCE CONTROL PANEL
echo                         Fees Management System
echo ===============================================================================
echo.
echo Select an option:
echo.
echo   1. 🚀 Quick Data Check           - Fast validation and auto-fix
echo   2. 🔧 Comprehensive Fix          - Full system check and repair
echo   3. 📊 View System Status         - Check current data integrity
echo   4. 📅 Setup Automatic Tasks      - Configure scheduled maintenance
echo   5. 📋 View Maintenance Logs      - Review past maintenance activities
echo   6. 🎯 Check Specific Student     - Validate individual student data
echo   7. 🚨 Emergency Recovery         - Advanced troubleshooting
echo   8. 📖 View Documentation         - Open data integrity guide
echo   9. 🌐 Start Django Server        - Launch the web application
echo   0. ❌ Exit
echo.
echo ===============================================================================

set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto quick_check
if "%choice%"=="2" goto comprehensive_fix
if "%choice%"=="3" goto system_status
if "%choice%"=="4" goto setup_tasks
if "%choice%"=="5" goto view_logs
if "%choice%"=="6" goto check_student
if "%choice%"=="7" goto emergency_recovery
if "%choice%"=="8" goto view_docs
if "%choice%"=="9" goto start_server
if "%choice%"=="0" goto exit
goto invalid_choice

:quick_check
cls
echo.
echo ===============================================================================
echo                              QUICK DATA CHECK
echo ===============================================================================
echo.
call quick_data_check.bat
echo.
pause
goto menu

:comprehensive_fix
cls
echo.
echo ===============================================================================
echo                           COMPREHENSIVE FIX
echo ===============================================================================
echo.
call auto_fix_data_issues.bat
echo.
pause
goto menu

:system_status
cls
echo.
echo ===============================================================================
echo                             SYSTEM STATUS
echo ===============================================================================
echo.
echo [INFO] Checking system status...
python manage.py validate_data
echo.
echo [INFO] Getting system statistics...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings'); import django; django.setup(); from core.models import Student, FeeDetails, FeeInstallments; print(f'📊 System Statistics:'); print(f'   Students: {Student.objects.count()}'); print(f'   Fee Records: {FeeDetails.objects.count()}'); print(f'   Installments: {FeeInstallments.objects.count()}'); print(f'   Status: All systems operational ✅')"
echo.
pause
goto menu

:setup_tasks
cls
echo.
echo ===============================================================================
echo                           SETUP AUTOMATIC TASKS
echo ===============================================================================
echo.
echo [WARNING] This requires administrator privileges.
echo [INFO] Right-click this file and select "Run as administrator" if needed.
echo.
pause
call setup_automatic_maintenance.bat
echo.
pause
goto menu

:view_logs
cls
echo.
echo ===============================================================================
echo                           MAINTENANCE LOGS
echo ===============================================================================
echo.
if exist "logs" (
    echo [INFO] Available log files:
    echo.
    dir logs\*.log /b /o-d 2>nul
    echo.
    set /p log_choice="Enter log filename to view (or press Enter to skip): "
    if not "!log_choice!"=="" (
        if exist "logs\!log_choice!" (
            echo.
            echo [INFO] Opening log file: !log_choice!
            notepad "logs\!log_choice!"
        ) else (
            echo [ERROR] Log file not found: !log_choice!
        )
    )
) else (
    echo [INFO] No logs directory found. Run maintenance tasks to generate logs.
)
echo.
pause
goto menu

:check_student
cls
echo.
echo ===============================================================================
echo                          CHECK SPECIFIC STUDENT
echo ===============================================================================
echo.
set /p student_id="Enter student registration number: "
if not "%student_id%"=="" (
    echo.
    echo [INFO] Checking student ID: %student_id%
    python manage.py validate_data --student-id %student_id%
) else (
    echo [ERROR] No student ID provided.
)
echo.
pause
goto menu

:emergency_recovery
cls
echo.
echo ===============================================================================
echo                            EMERGENCY RECOVERY
echo ===============================================================================
echo.
echo [WARNING] This will run advanced data recovery procedures.
echo [INFO] Use this only if you're experiencing serious data issues.
echo.
set /p emergency_confirm="Are you sure you want to proceed? (y/N): "
if /i "%emergency_confirm%"=="y" (
    echo.
    echo [INFO] Running emergency recovery...
    python data_consistency_checker.py
    echo.
    echo [INFO] Running Django fixes...
    python manage.py validate_data --fix
    echo.
    echo [INFO] Emergency recovery completed.
) else (
    echo [INFO] Emergency recovery cancelled.
)
echo.
pause
goto menu

:view_docs
cls
echo.
echo ===============================================================================
echo                             DOCUMENTATION
echo ===============================================================================
echo.
if exist "DATA_INTEGRITY_GUIDE.md" (
    echo [INFO] Opening Data Integrity Guide...
    notepad DATA_INTEGRITY_GUIDE.md
) else (
    echo [ERROR] Documentation file not found: DATA_INTEGRITY_GUIDE.md
)
echo.
pause
goto menu

:start_server
cls
echo.
echo ===============================================================================
echo                            START DJANGO SERVER
echo ===============================================================================
echo.
echo [INFO] Starting Django development server...
echo [INFO] Server will be available at: http://127.0.0.1:8000/
echo [INFO] Press Ctrl+C to stop the server.
echo.
timeout /t 3 /nobreak > nul
python manage.py runserver
echo.
pause
goto menu

:invalid_choice
cls
color 0C
echo.
echo ===============================================================================
echo                               INVALID CHOICE
echo ===============================================================================
echo.
echo [ERROR] Please enter a valid option (0-9).
echo.
timeout /t 2 /nobreak > nul
goto menu

:exit
cls
echo.
echo ===============================================================================
echo                                 GOODBYE
echo ===============================================================================
echo.
echo [INFO] Thank you for using the Data Maintenance Control Panel!
echo [INFO] Your system's data integrity is protected.
echo.
timeout /t 2 /nobreak > nul
exit /b 0
