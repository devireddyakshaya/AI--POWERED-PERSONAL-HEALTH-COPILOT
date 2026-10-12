@echo off
echo ========================================================
echo   MediMitra AI — Startup Script (Windows)
echo   Team TEKSQUADS ^| HacXLerate 2026
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python Environment...
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not detected in your PATH. Please install Python 3.10+
    pause
    exit /b 1
)

echo [2/4] Installing / Verifying Backend Dependencies...
pip install -r requirements.txt

echo.
echo [3/4] Installing / Verifying Frontend Dependencies...
cd frontend
call npm install
cd ..

echo.
echo [4/4] Starting MediMitra AI Services...
echo.
echo Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "MediMitra Backend (FastAPI)" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 >nul

echo Launching React Frontend on http://localhost:5173 ...
start "MediMitra Frontend (Vite)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================================
echo   MediMitra AI is starting up!
echo   Frontend: http://localhost:5173
echo   Backend Docs: http://127.0.0.1:8000/docs
echo ========================================================
echo.
pause
