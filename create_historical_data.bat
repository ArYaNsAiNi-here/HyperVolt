@echo off
echo.
echo ============================================================
echo   CREATING 24 HOURS OF HISTORICAL SENSOR DATA
echo ============================================================
echo.
echo This will populate the database with fake sensor readings
echo so the AI has data to make predictions.
echo.

cd /d "%~dp0"
.\.venv\Scripts\python.exe scripts\create_historical_data.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo   ERROR: Failed to create historical data
    echo ============================================================
    echo.
    echo Possible reasons:
    echo   1. Virtual environment not found
    echo   2. Django database not accessible
    echo   3. Missing dependencies
    echo.
    echo Try running manually:
    echo   .\.venv\Scripts\python.exe scripts\create_historical_data.py
    echo.
) else (
    echo.
    echo ============================================================
    echo   SUCCESS! Historical data created
    echo ============================================================
    echo.
    echo Now you can:
    echo   1. Restart Django
    echo   2. Run the simulation
    echo   3. AI will make decisions at iteration 6
    echo.
)

pause
