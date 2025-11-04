@echo off
:: ==============================================================================
:: SCHEDULED MAINTENANCE - Fees Management System
:: For automated weekly/daily maintenance via Windows Task Scheduler
:: ==============================================================================

setlocal enabledelayedexpansion

:: Set working directory to script location
cd /d "%~dp0"

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Set log file with timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"
set "logfile=logs\maintenance_%timestamp%.log"

:: Start logging
echo =============================================================================== > "%logfile%"
echo SCHEDULED MAINTENANCE - %timestamp% >> "%logfile%"
echo =============================================================================== >> "%logfile%"
echo. >> "%logfile%"

:: Check if Python and Django are available
python --version >> "%logfile%" 2>&1
if errorlevel 1 (
    echo [ERROR] Python not available >> "%logfile%"
    exit /b 1
)

if not exist "manage.py" (
    echo [ERROR] Django project not found in %CD% >> "%logfile%"
    exit /b 1
)

:: Run data validation
echo [%time%] Starting data validation... >> "%logfile%"
python manage.py validate_data >> "%logfile%" 2>&1
set validation_result=%errorlevel%

if %validation_result% neq 0 (
    echo [%time%] Issues detected, applying fixes... >> "%logfile%"
    python manage.py validate_data --fix >> "%logfile%" 2>&1
    
    :: Final verification
    echo [%time%] Final verification... >> "%logfile%"
    python manage.py validate_data >> "%logfile%" 2>&1
    set final_result=%errorlevel%
    
    if %final_result% equ 0 (
        echo [%time%] SUCCESS: All issues resolved automatically >> "%logfile%"
    ) else (
        echo [%time%] WARNING: Some issues require manual attention >> "%logfile%"
    )
else (
    echo [%time%] SUCCESS: No issues found, system is healthy >> "%logfile%"
)

:: Get system statistics
echo [%time%] Collecting system statistics... >> "%logfile%"
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings'); import django; django.setup(); from core.models import Student, FeeDetails, FeeInstallments; print(f'Students: {Student.objects.count()}'); print(f'Fee Records: {FeeDetails.objects.count()}'); print(f'Installments: {FeeInstallments.objects.count()}')" >> "%logfile%" 2>&1

echo. >> "%logfile%"
echo [%time%] Maintenance completed >> "%logfile%"
echo =============================================================================== >> "%logfile%"

:: Exit with appropriate code
if %validation_result% equ 0 (
    exit /b 0
) else (
    exit /b 1
)
