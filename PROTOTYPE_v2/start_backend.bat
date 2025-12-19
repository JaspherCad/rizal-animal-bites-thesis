@echo off
echo ========================================
echo  RABIES DASHBOARD - Backend Startup
echo ========================================
echo.

cd backend

echo Checking virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server...
python main.py
