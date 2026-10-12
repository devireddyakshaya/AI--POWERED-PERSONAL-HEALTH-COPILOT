# MediMitra AI - PowerShell Startup Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  MediMitra AI - Startup Script (PowerShell)" -ForegroundColor Cyan
Write-Host "  Team TEKSQUADS | HacXLerate 2026" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not installed or not in system PATH." -ForegroundColor Red
    exit 1
}

Write-Host "[1/3] Installing / Verifying Python Requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "[2/3] Installing / Verifying Node Modules..." -ForegroundColor Yellow
Set-Location "$ScriptDir\frontend"
npm install
Set-Location $ScriptDir

Write-Host "[3/3] Starting Services in Parallel..." -ForegroundColor Green
# Start backend job or process
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir'; python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 2

# Start frontend dev server
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir\frontend'; npm run dev"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  MediMitra AI is running!" -ForegroundColor Green
Write-Host "  Frontend:     http://localhost:5173" -ForegroundColor White
Write-Host "  Backend API:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Green
