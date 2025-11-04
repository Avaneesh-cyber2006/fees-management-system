@echo off
setlocal enabledelayedexpansion

:: ==============================================================================
:: AUTOMATIC DATA INTEGRITY CHECKER AND FIXER
:: Fees Management System - Data Corruption Prevention & Auto-Fix
:: ==============================================================================

title Fees Management System - Auto Data Fix

:: Set colors for better visibility
color 0A

echo.
echo ===============================================================================
echo                    FEES MANAGEMENT SYSTEM - AUTO DATA FIX
echo ===============================================================================
echo.
echo This tool will automatically:
echo   1. Check for data corruption issues
echo   2. Apply automatic fixes where possible
echo   3. Generate detailed reports
echo   4. Validate all student records
echo.
echo Starting in 3 seconds... (Press Ctrl+C to cancel)
timeout /t 3 /nobreak > nul

:: Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Check if we're in the correct directory
if not exist "manage.py" (
    echo.
    echo [ERROR] manage.py not found. Please run this script from the project root directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Set log file with timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"
set "logfile=logs\data_fix_%timestamp%.log"

echo.
echo ===============================================================================
echo                              PHASE 1: INITIAL CHECK
echo ===============================================================================
echo.
echo [INFO] Running initial data validation check...
echo [INFO] Log file: %logfile%

:: Run Django validation command
echo [%time%] Starting Django data validation... >> "%logfile%"
python manage.py validate_data > temp_validation.txt 2>&1
set validation_result=%errorlevel%

:: Display validation results
type temp_validation.txt
type temp_validation.txt >> "%logfile%"

if %validation_result% neq 0 (
    echo.
    echo [ERROR] Django validation failed. Check the log file for details.
    echo [ERROR] Log: %logfile%
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo                        PHASE 2: COMPREHENSIVE DATA CHECK
echo ===============================================================================
echo.
echo [INFO] Running comprehensive data consistency check...

:: Run the comprehensive data consistency checker
echo [%time%] Starting comprehensive data check... >> "%logfile%"
echo y | python data_consistency_checker.py > temp_checker.txt 2>&1
set checker_result=%errorlevel%

:: Display checker results
type temp_checker.txt
type temp_checker.txt >> "%logfile%"

if %checker_result% neq 0 (
    echo.
    echo [WARNING] Data consistency checker completed with warnings.
    echo [INFO] Check the output above for details.
)

echo.
echo ===============================================================================
echo                           PHASE 3: APPLY AUTO-FIXES
echo ===============================================================================
echo.
echo [INFO] Applying automatic fixes for detected issues...

:: Run Django validation with auto-fix
echo [%time%] Applying Django auto-fixes... >> "%logfile%"
python manage.py validate_data --fix > temp_fix.txt 2>&1
set fix_result=%errorlevel%

:: Display fix results
type temp_fix.txt
type temp_fix.txt >> "%logfile%"

echo.
echo ===============================================================================
echo                          PHASE 4: FINAL VERIFICATION
echo ===============================================================================
echo.
echo [INFO] Running final verification to ensure all issues are resolved...

:: Final validation check
echo [%time%] Final verification check... >> "%logfile%"
python manage.py validate_data > temp_final.txt 2>&1
set final_result=%errorlevel%

:: Display final results
type temp_final.txt
type temp_final.txt >> "%logfile%"

echo.
echo ===============================================================================
echo                              SUMMARY REPORT
echo ===============================================================================
echo.

:: Generate summary
echo [%time%] Generating summary report... >> "%logfile%"

if %final_result% equ 0 (
    echo [SUCCESS] All data integrity checks passed!
    echo [SUCCESS] No corruption issues found in the system.
    echo [SUCCESS] All data integrity checks passed! >> "%logfile%"
) else (
    echo [WARNING] Some issues may still exist. Please review the log file.
    echo [WARNING] Log file: %logfile%
    echo [WARNING] Some issues may still exist. >> "%logfile%"
)

:: Count students processed
for /f "tokens=*" %%i in ('python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings'); import django; django.setup(); from core.models import Student; print(Student.objects.count())"') do set student_count=%%i

echo.
echo Statistics:
echo   - Students processed: %student_count%
echo   - Log file created: %logfile%
echo   - Timestamp: %timestamp%
echo.

:: Log final statistics
echo [%time%] Process completed. Students: %student_count% >> "%logfile%"

:: Cleanup temporary files
del temp_validation.txt 2>nul
del temp_checker.txt 2>nul
del temp_fix.txt 2>nul
del temp_final.txt 2>nul

echo ===============================================================================
echo                                NEXT STEPS
echo ===============================================================================
echo.
echo 1. Review the log file if any warnings were shown: %logfile%
echo 2. Test the system by accessing student records
echo 3. Run this script weekly for ongoing maintenance
echo 4. For manual checks, use: python manage.py validate_data
echo.
echo [INFO] Data integrity maintenance completed!
echo.

:: Ask if user wants to open the log file
set /p open_log="Do you want to open the log file? (y/N): "
if /i "%open_log%"=="y" (
    if exist "%logfile%" (
        notepad "%logfile%"
    ) else (
        echo Log file not found: %logfile%
    )
)

:: Ask if user wants to start the Django server
echo.
set /p start_server="Do you want to start the Django development server? (y/N): "
if /i "%start_server%"=="y" (
    echo.
    echo [INFO] Starting Django development server...
    echo [INFO] The server will start at http://127.0.0.1:8000/
    echo [INFO] Press Ctrl+C to stop the server when done.
    echo.
    timeout /t 3 /nobreak > nul
    python manage.py runserver
)

echo.
echo [INFO] Auto-fix process completed. Press any key to exit.
pause > nul
