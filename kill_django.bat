@echo off
echo.
echo ============================================================
echo   HYPERVOLT - KILL DJANGO PROCESS
echo ============================================================
echo.
echo Searching for Django/Python processes on port 8000...
echo.

REM Find and kill process using port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Found process ID: %%a
    taskkill /F /PID %%a
    echo Process killed!
)

echo.
echo ============================================================
echo   DJANGO PROCESS KILLED
echo ============================================================
echo.
echo Now you can restart Django with:
echo.
echo    cd D:\Projects\HyperVolt\api
echo    daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
echo.
echo ============================================================
pause
