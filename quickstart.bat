@echo off
echo.
echo ============================================================
echo   HYPERVOLT QUICK START CHECK
echo ============================================================
echo.

echo Checking Redis...
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Redis is running
) else (
    echo [!!] Redis is NOT running - Start with: redis-server
)

echo.
echo Checking Django API...
curl -s http://localhost:8000/api/ai/status/ >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo [OK] Django API is running
) else (
    echo [!!] Django is NOT running
    echo     Start with: cd api ^&^& daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
)

echo.
echo Checking Frontend...
curl -s http://localhost:3000 >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo [OK] Frontend is running
) else (
    echo [!!] Frontend is NOT running
    echo     Start with: cd website ^&^& npm run dev
)

echo.
echo ============================================================
echo   See TROUBLESHOOTING.md for detailed instructions
echo ============================================================
echo.
pause
