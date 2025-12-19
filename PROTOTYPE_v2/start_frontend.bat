@echo off
echo ========================================
echo  RABIES DASHBOARD - Frontend Startup
echo ========================================
echo.

cd frontend

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
)

echo.
echo Starting React development server...
npm start
