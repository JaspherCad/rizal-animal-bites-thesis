"""
Package Verification Script for Rabies Forecasting Environment
===============================================================
Run this after installation to verify all packages work correctly.
Usage: python verify_packages.py
"""

import sys
from datetime import datetime

def test_import(package_name, import_name=None, version_attr='__version__'):
    """Test importing a package and print its version."""
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, version_attr, 'N/A')
        print(f"✓ {package_name:20s} {version}")
        return True
    except ImportError as e:
        print(f"✗ {package_name:20s} FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"? {package_name:20s} WARNING: {str(e)}")
        return True  # Imported but version check failed

def test_numpy_compatibility():
    """Test numpy/pmdarima compatibility specifically."""
    print("\n" + "="*70)
    print("CRITICAL COMPATIBILITY TEST: numpy + pmdarima + tbats")
    print("="*70)
    
    try:
        import numpy as np
        print(f"  numpy version: {np.__version__}")
        
        # Check numpy dtype size (the root cause of the original error)
        dtype = np.dtype('float64')
        print(f"  numpy.dtype size: {dtype.itemsize} bytes")
        
        from pmdarima.arima import auto_arima
        print("  ✓ pmdarima.arima.auto_arima imported successfully")
        
        from tbats import TBATS
        print("  ✓ tbats.TBATS imported successfully")
        
        print("\n  ✓✓✓ COMPATIBILITY TEST PASSED! ✓✓✓")
        return True
        
    except ValueError as e:
        if "dtype size changed" in str(e):
            print(f"\n  ✗✗✗ COMPATIBILITY ERROR ✗✗✗")
            print(f"  {str(e)}")
            print(f"\n  Solution: Run 'pip uninstall -y numpy pmdarima tbats'")
            print(f"           Then: 'pip install \"numpy<1.27\" pmdarima tbats'")
            return False
        else:
            raise
    except Exception as e:
        print(f"\n  ✗ Unexpected error: {str(e)}")
        return False

def main():
    print("="*70)
    print("RABIES FORECASTING - PACKAGE VERIFICATION")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print("="*70)
    print()
    
    packages_to_test = [
        # Core
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scipy", "scipy"),
        
        # Statistical Time Series
        ("statsmodels", "statsmodels"),
        ("pmdarima", "pmdarima"),
        ("tbats", "tbats"),
        ("sktime", "sktime"),
        
        # Deep Learning Time Series
        ("prophet", "prophet"),
        ("neuralprophet", "neuralprophet"),
        ("torch", "torch"),
        ("pytorch-lightning", "pytorch_lightning"),
        
        # Machine Learning
        ("xgboost", "xgboost"),
        ("lightgbm", "lightgbm"),
        ("scikit-learn", "sklearn"),
        
        # Deep Learning
        ("tensorflow", "tensorflow"),
        ("keras", "keras"),
        
        # Visualization
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("plotly", "plotly"),
        
        # Utilities
        ("joblib", "joblib"),
        ("tqdm", "tqdm"),
    ]
    
    print("PACKAGE VERSIONS")
    print("-"*70)
    
    results = []
    for package_name, import_name in packages_to_test:
        result = test_import(package_name, import_name)
        results.append((package_name, result))
    
    # Run compatibility test
    compat_result = test_numpy_compatibility()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"Packages imported: {passed}/{total}")
    print(f"Compatibility test: {'PASSED' if compat_result else 'FAILED'}")
    
    if passed == total and compat_result:
        print("\n✓✓✓ ALL TESTS PASSED - READY TO USE! ✓✓✓")
        return 0
    else:
        print("\n✗✗✗ SOME TESTS FAILED - CHECK ERRORS ABOVE ✗✗✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
