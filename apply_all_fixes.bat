@echo off
echo.
echo ============================================================
echo   HYPERVOLT - COMPLETE FIX APPLICATION
echo ============================================================
echo.
echo Applying all fixes:
echo   1. Killing stuck Django process
echo   2. Pandas frequency bug (H to h) - ALREADY FIXED IN CODE
echo.
echo ============================================================
echo   STEP 1: KILLING DJANGO ON PORT 8000
echo ============================================================
echo.

REM Find and kill process using port 8000
set FOUND=0
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Found Django process ID: %%a
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   Could not kill process %%a (may need admin rights)
    ) else (
        echo   ✓ Process %%a killed successfully!
        set FOUND=1
    )
)

if %FOUND%==0 (
    echo   No Django process found on port 8000
    echo   This is OK - port is free!
)

echo.
echo ============================================================
echo   STEP 2: CODE FIXES ALREADY APPLIED
echo ============================================================
echo.
echo The following bugs have been fixed in the code:
echo   ✓ Pandas frequency 'H' changed to 'h' (2 places)
echo   ✓ Missing AI features added (is_peak_hour, occupancy_factor)
echo   ✓ Feature name fixed (grid_price_per_kwh)
echo   ✓ Keras model loading compatibility
echo   ✓ WebSocket broadcasting enabled
echo.
echo ============================================================
echo   NEXT STEPS - RUN THESE COMMANDS:
echo ============================================================
echo.
echo 1. START DJANGO (in Terminal 2):
echo.
echo    cd D:\Projects\HyperVolt\api
echo    daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
echo.
echo    Watch for:
echo      ✓ Model loaded successfully
echo      ✓ AI models initialized successfully
echo      INFO Listening on TCP address 0.0.0.0:8000
echo.
echo    Should NOT see:
echo      ✗ Error fetching historical data: Invalid frequency: H
echo.
echo 2. RUN SIMULATION (in Terminal 4):
echo.
echo    cd D:\Projects\HyperVolt
echo    .\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
echo.
echo 3. WAIT FOR ITERATION 6 (about 75 seconds):
echo.
echo    Iteration 1-5: No AI decisions (NORMAL)
echo    Iteration 6:   First AI Decision appears!
echo    Iteration 12:  Second AI Decision
echo    Iteration 18:  Third AI Decision
echo.
echo ============================================================
echo   EXPECTED OUTPUT AT ITERATION 6:
echo ============================================================
echo.
echo    AI Decision:
echo       Predicted Demand: 0.125 kWh
echo       Source Allocation:
echo         - grid: 0.125 kW
echo       Cost: Rs 0.48
echo       Carbon: 60 gCO2eq
echo.
echo    AI Decisions: 1  (was 0 - NOW WORKING!)
echo.
echo ============================================================
echo.
pause
