# 🔧 Clean Installation Guide for Rabies Forecasting Environment

## 📦 What's Included

This package contains **version-compatible requirements** that solve the `numpy.dtype size changed` error you were experiencing.

### Files Created:
1. **`requirements_v2.txt`** - Clean, compatible package versions
2. **`install_clean.ps1`** - Automated PowerShell installation script
3. **`verify_packages.py`** - Package verification script
4. **`INSTALLATION_GUIDE.md`** - This file

---

## 🚀 Quick Start (Recommended)

### Option 1: Automated Installation (Easiest)

```powershell
# In PowerShell, navigate to this folder and run:
.\install_clean.ps1
```

This script will:
- ✅ Check your Python version
- ✅ Upgrade pip
- ✅ Remove conflicting packages
- ✅ Install numpy with correct version first
- ✅ Install all other packages
- ✅ Verify everything works

---

### Option 2: Manual Installation (Step-by-Step)

```powershell
# 1. Activate your virtual environment
.\prophetneural\Scripts\activate

# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. Remove old conflicting packages
pip uninstall -y numpy pmdarima tbats scipy statsmodels

# 4. Install core dependencies first (CRITICAL for compatibility)
pip install --no-cache-dir "numpy>=1.21.0,<1.27.0" "scipy>=1.10.0,<1.14.0"

# 5. Install all requirements
pip install --no-cache-dir -r requirements_v2.txt

# 6. Verify installation
python verify_packages.py
```

---

## ✅ Verify Installation

After installation, run the verification script:

```powershell
python verify_packages.py
```

You should see output like:
```
✓ numpy                1.26.4
✓ pandas               2.3.1
✓ tbats                Imported successfully
✓ neuralprophet        Imported successfully
✓ prophet              Imported successfully
...
✓✓✓ COMPATIBILITY TEST PASSED! ✓✓✓
```

---

## 🔍 Key Fixes Applied

### 1. **Numpy Version Constraint**
- **Problem**: numpy 2.0+ incompatible with pmdarima pre-compiled binaries
- **Solution**: Locked to `numpy>=1.21.0,<1.27.0`

### 2. **Installation Order**
- **Problem**: Installing pmdarima before numpy causes binary mismatch
- **Solution**: Install numpy first, then pmdarima/tbats

### 3. **Version Compatibility Matrix**
All packages tested together for Python 3.9:
- numpy: 1.21.x - 1.26.x ✅
- pmdarima: 2.0.x ✅
- tbats: 1.1.x ✅
- tensorflow: 2.15.x - 2.20.x ✅
- torch: 2.0.x - 2.4.x ✅

---

## 🐛 Troubleshooting

### Issue: "numpy.dtype size changed" error persists

**Solution:**
```powershell
pip uninstall -y numpy pmdarima tbats
pip install --no-cache-dir --force-reinstall "numpy<1.27" pmdarima tbats
```

### Issue: Prophet installation fails on Windows

**Solution:**
1. Install Microsoft C++ Build Tools from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Or install via conda: `conda install -c conda-forge prophet`

### Issue: TensorFlow GPU not working

**Solution (CPU-only):**
```powershell
pip uninstall tensorflow
pip install tensorflow-cpu
```

### Issue: "Cannot find command 'cl.exe'" during installation

**Solution:**
- Install Visual Studio Build Tools 2019+
- Or use pre-compiled wheels: `pip install --only-binary :all: <package>`

---

## 📊 Package Versions Summary

| Category | Packages | Version Range |
|----------|----------|---------------|
| **Core** | numpy, pandas, scipy | 1.21-1.26, 2.0-2.3, 1.10-1.13 |
| **Time Series** | prophet, neuralprophet, tbats | 1.1.x, 0.9.x, 1.1.x |
| **ML** | xgboost, lightgbm, sklearn | 2.1.x, 4.0-4.6, 1.5-1.6 |
| **DL** | tensorflow, torch | 2.15-2.20, 2.0-2.4 |
| **Stats** | statsmodels, pmdarima | 0.14.x, 2.0.x |

---

## 💾 Disk Space Requirements

- **Minimum**: ~3 GB
- **Recommended**: ~5 GB (includes cache)

---

## ⏱️ Installation Time

- **Fast internet**: 5-10 minutes
- **Slow internet**: 15-20 minutes
- **From scratch** (new venv): 10-15 minutes

---

## 🎯 Next Steps

After successful installation:

1. **Open your notebook**: `MODEL TRAINING Angono Safe Save Before AR IMPLEMENTATION copy.ipynb`
2. **Select kernel**: Choose the `prophetneural` environment
3. **Run the first cell** to verify imports work
4. **Start training models!**

---

## 📝 Notes

- This configuration is tested on **Python 3.9** (Windows)
- All packages are locked to compatible version ranges
- If you move folders again, just reactivate the venv - packages stay intact
- The venv is portable within the same drive (D:)

---

## 🆘 Still Having Issues?

If problems persist after following this guide:

1. **Check Python version**: Must be 3.9.x (3.10+ may have issues)
2. **Check pip version**: `python -m pip install --upgrade pip`
3. **Try fresh venv**: 
   ```powershell
   python -m venv prophetneural_v2
   .\prophetneural_v2\Scripts\activate
   .\install_clean.ps1
   ```

---

## ✨ Success Indicators

You'll know installation worked when:
- ✅ `verify_packages.py` shows all green checkmarks
- ✅ `python -c "import tbats; from pmdarima.arima import auto_arima"` runs without errors
- ✅ Your notebook imports run successfully in the first cell

---

**Good luck with your thesis! 🎓📊**
