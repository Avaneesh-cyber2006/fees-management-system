@echo off
title System Troubleshoot - Pillay Sir's ICSE Classes
color 0C

echo ==========================================
echo  🔧 System Troubleshoot & Diagnostics
echo  Pillay Sir's ICSE Classes
echo ==========================================
echo.

cd /d "%~dp0"

echo 🔍 Running system diagnostics...
echo.

echo [CHECK 1] Python Installation:
python --version 2>nul
if errorlevel 1 (
    echo ❌ Python NOT found
    echo   Solution: Install Python from https://python.org/downloads/
    echo   Make sure to check "Add Python to PATH"
) else (
    echo ✅ Python is installed
)

echo.
echo [CHECK 2] Django Project Files:
if exist "manage.py" (
    echo ✅ manage.py found
) else (
    echo ❌ manage.py NOT found
    echo   Solution: Run this script from the Django project folder
)

if exist "requirements.txt" (
    echo ✅ requirements.txt found
) else (
    echo ⚠️  requirements.txt missing
)

echo.
echo [CHECK 3] Database Connection:
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings'); import django; django.setup(); from django.db import connection; connection.ensure_connection(); print('✅ Database connection OK')" 2>nul
if errorlevel 1 (
    echo ❌ Database connection FAILED
    echo   Solutions:
    echo   1. Start MySQL server (XAMPP/WAMP/MySQL Workbench)
    echo   2. Check database name: 'pclasses'
    echo   3. Check username: 'root', password: 'Root'
)

echo.
echo [CHECK 4] Required Python Packages:
python -c "import django; print('✅ Django installed')" 2>nul || echo ❌ Django missing
python -c "import pymysql; print('✅ PyMySQL installed')" 2>nul || echo ❌ PyMySQL missing
python -c "import pandas; print('✅ Pandas installed')" 2>nul || echo ❌ Pandas missing

echo.
echo [CHECK 5] Port Availability:
netstat -an | find "8000" >nul
if errorlevel 1 (
    echo ✅ Port 8000 is available
) else (
    echo ⚠️  Port 8000 may be in use
    echo   Solution: Close other Django servers or use a different port
)

echo.
echo ==========================================
echo  🛠️  QUICK FIXES
echo ==========================================
echo.
echo If you see errors above, try these solutions:
echo.
echo 1. Install missing packages:
echo    pip install -r requirements.txt
echo.
echo 2. Start MySQL server:
echo    - Open XAMPP Control Panel and start MySQL
echo    - Or open MySQL Workbench
echo    - Or start MySQL service in Windows Services
echo.
echo 3. Run database migrations:
echo    python manage.py migrate
echo.
echo 4. Create superuser (if needed):
echo    python manage.py createsuperuser
echo.
echo 5. Test server manually:
echo    python manage.py runserver
echo.
echo ==========================================
echo.
echo Press any key to exit...
pause >nul
