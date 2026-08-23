@echo off
:: ==============================================================================
:: QUICK DATA CHECK & FIX - Fees Management System
:: For daily maintenance and quick issue resolution
:: ==============================================================================

title Quick Data Check & Fix

color 0B
echo.
echo ===============================================================================
echo                        QUICK DATA CHECK & FIX
echo ===============================================================================
echo.

:: Check if we're in the right directory
if not exist "manage.py" (
    echo [ERROR] Please run this from the project root directory.
    pause
    exit /b 1
)

:: Quick validation check
echo [INFO] Running quick data validation...
python manage.py validate_data

:: Check the result
if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] ✅ All data is clean! No issues found.
    echo [INFO] Your system is running perfectly.
) else (
    echo.
    echo [WARNING] ⚠️  Issues detected. Running auto-fix...
    echo.
    
    :: Apply fixes
    python manage.py validate_data --fix
    
    echo.
    echo [INFO] Auto-fix completed. Running final check...
    python manage.py validate_data
    
    if %errorlevel% equ 0 (
        echo.
        echo [SUCCESS] ✅ All issues resolved!
    ) else (
        echo.
        echo [WARNING] ⚠️  Some issues may need manual attention.
        echo [INFO] Run 'auto_fix_data_issues.bat' for comprehensive fix.
    )
)

echo.
echo [INFO] Quick check completed!
timeout /t 3 /nobreak > nul
