# ============================================================================
# CLEAN INSTALLATION SCRIPT FOR RABIES FORECASTING ENVIRONMENT
# ============================================================================
# Usage: .\install_clean.ps1
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RABIES FORECASTING - CLEAN INSTALL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python version
Write-Host "[1/6] Checking Python version..." -ForegroundColor Yellow
python --version
$pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "    Python $pythonVersion detected" -ForegroundColor Green
Write-Host ""

# Step 2: Upgrade pip
Write-Host "[2/6] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "    pip upgraded successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Clean problematic packages
Write-Host "[3/6] Removing potentially conflicting packages..." -ForegroundColor Yellow
pip uninstall -y numpy pmdarima tbats scipy statsmodels 2>$null
Write-Host "    Old packages removed" -ForegroundColor Green
Write-Host ""

# Step 4: Install core dependencies first (numpy compatibility critical)
Write-Host "[4/6] Installing core dependencies (numpy, scipy)..." -ForegroundColor Yellow
pip install --no-cache-dir "numpy>=1.21.0,<1.27.0" "scipy>=1.10.0,<1.14.0"
Write-Host "    Core dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 5: Install all requirements
Write-Host "[5/6] Installing all requirements from requirements_v2.txt..." -ForegroundColor Yellow
Write-Host "    This may take 5-10 minutes..." -ForegroundColor Cyan
pip install --no-cache-dir -r requirements_v2.txt
Write-Host "    All packages installed" -ForegroundColor Green
Write-Host ""

# Step 6: Verify installation
Write-Host "[6/6] Verifying installation..." -ForegroundColor Yellow
python -c "import sys; import numpy; import pandas; import tbats; import neuralprophet; import prophet; import xgboost; import pmdarima; import lightgbm; import statsmodels; import sklearn; import tensorflow; print('[OK] numpy:', numpy.__version__); print('[OK] pandas:', pandas.__version__); print('[OK] tbats: Imported'); print('[OK] neuralprophet: Imported'); print('[OK] prophet: Imported'); print('[OK] xgboost:', xgboost.__version__); print('[OK] pmdarima: Imported'); print('[OK] lightgbm:', lightgbm.__version__); print('[OK] statsmodels:', statsmodels.__version__); print('[OK] scikit-learn:', sklearn.__version__); print('[OK] tensorflow:', tensorflow.__version__); print(); print('SUCCESS: ALL PACKAGES LOADED!'); sys.exit(0)"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ INSTALLATION COMPLETED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run your notebook!" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ✗ INSTALLATION FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
    Write-Host ""
}
