@echo off
echo.
echo ============================================================
echo   HYPERVOLT - DEBUG MODE ACTIVATION
echo ============================================================
echo.
echo I've added comprehensive debug logging to find why
echo AI Decisions = 0
echo.
echo ============================================================
echo   STEP 1: CREATING HISTORICAL DATA (RECOMMENDED)
echo ============================================================
echo.
echo This creates 24 hours of fake sensor data so the AI has
echo something to work with.
echo.
set /p CREATE_DATA="Create fake historical data? (y/n): "
if /i "%CREATE_DATA%"=="y" (
    echo.
    echo Creating historical data...
    ..\.venv\Scripts\python.exe scripts\create_historical_data.py
    if errorlevel 1 (
        echo.
        echo Failed to create data automatically.
        echo Please check if:
        echo   - Virtual environment is activated
        echo   - Django database is accessible
        echo   - You're in the HyperVolt directory
    ) else (
        echo.
        echo ✓ Historical data created successfully!
    )
)

echo.
echo ============================================================
echo   STEP 2: KILLING DJANGO
echo ============================================================
echo.

REM Kill Django on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a...
    taskkill /F /PID %%a >nul 2>&1
)
echo ✓ Django killed

echo.
echo ============================================================
echo   STEP 3: START DJANGO WITH DEBUG LOGGING
echo ============================================================
echo.
echo In Terminal 2, run:
echo.
echo    cd D:\Projects\HyperVolt\api
echo    daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
echo.
echo Watch for debug output like:
echo    🔍 [DEBUG] AI decide endpoint called
echo    🔍 [DEBUG] Available flag: True/False
echo.
echo ============================================================
echo   STEP 4: RUN SIMULATION
echo ============================================================
echo.
echo In Terminal 4, run:
echo.
echo    cd D:\Projects\HyperVolt
echo    .\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
echo.
echo Watch for debug output at iteration 6:
echo    🔍 [DEBUG] Iteration 6: Checking AI decision trigger...
echo    🔍 [DEBUG] Available flag: True/False
echo    ✅ [DEBUG] AI Decisions: 1
echo.
echo ============================================================
echo   WHAT TO LOOK FOR
echo ============================================================
echo.
echo If you see:
echo   "Available flag: False"
echo   "AI returned error: [error message]"
echo.
echo Then that's the reason AI decisions aren't working!
echo.
echo Common errors:
echo   - "Insufficient historical data" - Need more sensor readings
echo   - "Invalid frequency: H" - Django not restarted after fix
echo   - "Error fetching..." - Something wrong with database
echo.
echo ============================================================
echo.
echo Read DEBUG_MODE_INSTRUCTIONS.md for full details!
echo.
pause
