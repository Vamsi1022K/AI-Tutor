@echo off
echo.
echo   ============================================
echo   AI Compiler Tutor - Web Interface
echo   ============================================
echo.
echo   Installing Flask if needed...
py -3.12 -m pip install flask -q
echo.
echo   Starting server at http://localhost:5000
echo   Opening browser in 2 seconds...
timeout /t 2 /nobreak >nul
start http://localhost:5000
echo.
py -3.12 src/server.py
pause
