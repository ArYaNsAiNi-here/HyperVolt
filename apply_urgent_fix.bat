@echo off
echo.
echo ============================================================
echo   HYPERVOLT - QUICK FIX DEPLOYMENT
echo ============================================================
echo.
echo This script will apply the urgent fixes:
echo   1. Add 'voltage' sensor type to database
echo   2. Fix API endpoint URLs
echo.
echo STEP 1: Running database migration...
echo --------------------------------------------------------
cd api
..\. venv\Scripts\python.exe manage.py makemigrations
if errorlevel 1 (
    echo ERROR: Failed to create migrations!
    pause
    exit /b 1
)

..\. venv\Scripts\python.exe manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to apply migrations!
    pause
    exit /b 1
)

echo.
echo ✅ Database migration completed!
echo.
echo ============================================================
echo   NEXT STEPS:
echo ============================================================
echo.
echo 1. RESTART Django with:
echo    cd api
echo    daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
echo.
echo 2. Run simulation:
echo    .\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
echo.
echo 3. Expected output:
echo    API Success Rate: 5/5  (not 0/5!)
echo    AI Decisions: 1+       (increasing)
echo.
echo ============================================================
echo.
pause
