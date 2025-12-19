# Start Rabies Alert System Backend
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Rabies Alert System" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

Set-Location backend

Write-Host "1️⃣ Activating virtual environment..." -ForegroundColor Yellow
& "..\venvprototyp\Scripts\Activate.ps1"

Write-Host ""
Write-Host "2️⃣ Checking dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "3️⃣ Starting API server..." -ForegroundColor Yellow
Write-Host "   📊 Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "   📖 API docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

python main.py
