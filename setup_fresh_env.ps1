# ============================================================================
# CREATE FRESH PYTHON ENVIRONMENT FOR RABIES FORECASTING
# ============================================================================
# This script creates a brand new virtual environment with compatible packages
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FRESH ENVIRONMENT SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if old environment exists
Write-Host "[1/8] Checking for old environment..." -ForegroundColor Yellow
if (Test-Path ".\prophetneural_clean") {
    Write-Host "    Old 'prophetneural_clean' environment found. Removing..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".\prophetneural_clean"
    Write-Host "    Old environment removed" -ForegroundColor Green
} else {
    Write-Host "    No old environment found (good!)" -ForegroundColor Green
}
Write-Host ""

# Step 2: Create new virtual environment
Write-Host "[2/8] Creating new virtual environment 'prophetneural_clean'..." -ForegroundColor Yellow
python -m venv prophetneural_clean
if ($LASTEXITCODE -ne 0) {
    Write-Host "    ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "    Virtual environment created" -ForegroundColor Green
Write-Host ""

# Step 3: Activate the new environment
Write-Host "[3/8] Activating new environment..." -ForegroundColor Yellow
& .\prophetneural_clean\Scripts\Activate.ps1
Write-Host "    Environment activated: prophetneural_clean" -ForegroundColor Green
Write-Host ""

# Step 4: Upgrade pip
Write-Host "[4/8] Upgrading pip, setuptools, wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel
Write-Host "    Build tools upgraded" -ForegroundColor Green
Write-Host ""

# Step 5: Install core dependencies FIRST (critical for compatibility)
Write-Host "[5/8] Installing core dependencies (numpy, scipy, pandas)..." -ForegroundColor Yellow
Write-Host "    This ensures binary compatibility..." -ForegroundColor Cyan
pip install --no-cache-dir "numpy>=1.21.0,<1.27.0" "scipy>=1.10.0,<1.14.0" "pandas>=2.0.0,<2.4.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "    ERROR: Failed to install core dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "    Core dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 6: Install problematic packages (pmdarima, tbats) with compatible numpy
Write-Host "[6/8] Installing statistical packages (pmdarima, tbats, statsmodels)..." -ForegroundColor Yellow
pip install --no-cache-dir pmdarima tbats "statsmodels>=0.14.0,<0.15.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "    ERROR: Failed to install statistical packages" -ForegroundColor Red
    exit 1
}
Write-Host "    Statistical packages installed" -ForegroundColor Green
Write-Host ""

# Step 7: Install all remaining requirements
Write-Host "[7/8] Installing all remaining packages from requirements_v2.txt..." -ForegroundColor Yellow
Write-Host "    This may take 5-10 minutes. Please be patient..." -ForegroundColor Cyan
pip install --no-cache-dir -r requirements_v2.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "    WARNING: Some packages may have failed, but continuing..." -ForegroundColor Yellow
}
Write-Host "    All packages installed" -ForegroundColor Green
Write-Host ""

# Step 8: Verify installation
Write-Host "[8/8] Verifying installation..." -ForegroundColor Yellow
Write-Host ""

$verification = python -c "import sys; import numpy; import pandas; import tbats; import neuralprophet; import prophet; import xgboost; import pmdarima; import lightgbm; import statsmodels; import sklearn; import tensorflow; print('[OK] numpy:', numpy.__version__); print('[OK] pandas:', pandas.__version__); print('[OK] tbats: OK'); print('[OK] neuralprophet: OK'); print('[OK] prophet: OK'); print('[OK] xgboost:', xgboost.__version__); print('[OK] pmdarima: OK'); print('[OK] lightgbm:', lightgbm.__version__); print('[OK] statsmodels:', statsmodels.__version__); print('[OK] scikit-learn:', sklearn.__version__); print('[OK] tensorflow:', tensorflow.__version__); print(); print('=== ALL PACKAGES WORKING ==='); sys.exit(0)" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host $verification -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SUCCESS! ENVIRONMENT READY" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "To use this environment:" -ForegroundColor Cyan
    Write-Host "  1. Close and reopen VS Code" -ForegroundColor White
    Write-Host "  2. Or manually activate:" -ForegroundColor White
    Write-Host "     .\prophetneural_clean\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Then select kernel in Jupyter: 'prophetneural_clean'" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host $verification -ForegroundColor Red
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  INSTALLATION HAD ERRORS" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Running detailed verification..." -ForegroundColor Yellow
    python verify_packages.py
}

Write-Host ""
Write-Host "Environment location: $PWD\prophetneural_clean" -ForegroundColor Cyan
Write-Host ""
