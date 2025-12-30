# Production startup script for Rabies Forecasting API
# This script runs the server in production mode with optimized settings

Write-Host "🚀 Starting API in PRODUCTION mode..." -ForegroundColor Green

# Set environment to production
$env:ENV = "production"

# Option 1: Run with uvicorn (single worker)
Write-Host "⚡ Running with uvicorn (recommended for testing)..." -ForegroundColor Yellow
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --no-reload

# Option 2: For better performance, install and use gunicorn (multiple workers)
# Uncomment below and run: pip install gunicorn
# Write-Host "⚡ Running with gunicorn (4 workers)..." -ForegroundColor Yellow
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
