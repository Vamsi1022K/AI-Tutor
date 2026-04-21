@echo off
echo ==============================================
echo   AI Compiler Tutor - Unified Full Stack Launcher
echo ==============================================
echo.

echo [1/4] Starting Vamsi's AI Engine (Port 5000)...
start "Vamsi AI Engine" cmd /c "py -3.12 src/server.py"
timeout /t 2 /nobreak >nul

echo [2/4] Starting Friend's Backend (Port 8000)...
start "Friend Backend" cmd /c "cd friends_project\cdproject\backend && py -3.12 run.py"
timeout /t 2 /nobreak >nul

echo [3/4] Starting Friend's Frontend (Port 5173)...
start "Friend Frontend" cmd /c "cd friends_project\cdproject\frontend && npm run dev"
timeout /t 2 /nobreak >nul

echo [4/4] Starting Central Hub (Port 8080)...
start "Unified Hub Server" cmd /c "py -3.12 hub_server.py"
timeout /t 2 /nobreak >nul

echo.
echo ==============================================
echo   Services are starting up...
echo   Opening Unified Hub in 3 seconds
echo ==============================================
timeout /t 3 /nobreak >nul

start http://localhost:8080
