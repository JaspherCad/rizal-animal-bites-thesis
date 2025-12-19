@echo off
echo ====================================
echo 🚀 Starting Rabies Alert System
echo ====================================
echo.

cd backend

echo 1️⃣ Activating virtual environment...
call ..\venvprototyp\Scripts\activate.bat

echo.
echo 2️⃣ Checking dependencies...
pip install -r requirements.txt --quiet

echo.
echo 3️⃣ Starting API server...
echo    📊 Backend will run on: http://localhost:8000
echo    📖 API docs available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause
