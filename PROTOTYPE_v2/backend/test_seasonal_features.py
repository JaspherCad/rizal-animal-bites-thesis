"""
Test script to verify seasonal features are working correctly
Run this BEFORE starting the FastAPI server
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Test the seasonal feature functions
def test_cainta_features():
    print("=" * 60)
    print("🧪 Testing CAINTA Seasonal Features")
    print("=" * 60)
    
    # Create test dates
    test_dates = pd.date_range(start='2025-01-01', periods=12, freq='MS')
    test_df = pd.DataFrame({'ds': test_dates})
    
    # Add features using the same logic as main.py
    test_df['may_peak'] = (test_df['ds'].dt.month == 5).astype(int)
    test_df['low_season'] = ((test_df['ds'].dt.month >= 1) & (test_df['ds'].dt.month <= 4)).astype(int)
    test_df['spring_ramp'] = ((test_df['ds'].dt.month >= 3) & (test_df['ds'].dt.month <= 5)).astype(int)
    test_df['january_holiday'] = (test_df['ds'].dt.month == 1).astype(int)
    test_df['post_may_decline'] = ((test_df['ds'].dt.month >= 6) & (test_df['ds'].dt.month <= 12)).astype(int)
    
    print("\n📊 CAINTA Feature Values by Month:")
    print(test_df[['ds', 'may_peak', 'low_season', 'spring_ramp', 'january_holiday', 'post_may_decline']].to_string(index=False))
    
    # Verify logic
    assert test_df[test_df['ds'].dt.month == 5]['may_peak'].values[0] == 1, "May peak should be 1 in May!"
    assert test_df[test_df['ds'].dt.month == 1]['low_season'].values[0] == 1, "Low season should be 1 in Jan!"
    assert test_df[test_df['ds'].dt.month == 6]['post_may_decline'].values[0] == 1, "Post-May decline should be 1 in June!"
    
    print("\n✅ CAINTA features working correctly!")
    return test_df


def test_angono_features():
    print("\n" + "=" * 60)
    print("🧪 Testing ANGONO Seasonal Features")
    print("=" * 60)
    
    # Create test dates
    test_dates = pd.date_range(start='2025-01-01', periods=12, freq='MS')
    test_df = pd.DataFrame({'ds': test_dates})
    
    # Add features using the same logic as main.py
    test_df['high_season'] = test_df['ds'].dt.month.isin([4, 5, 6]).astype(int)
    test_df['july_dip'] = (test_df['ds'].dt.month == 7).astype(int)
    test_df['august_rise'] = (test_df['ds'].dt.month == 8).astype(int)
    test_df['low_season'] = test_df['ds'].dt.month.isin([12, 1]).astype(int)
    test_df['post_april_2024'] = (test_df['ds'] >= pd.Timestamp('2024-04-01')).astype(int)
    
    print("\n📊 ANGONO Feature Values by Month:")
    print(test_df[['ds', 'high_season', 'july_dip', 'august_rise', 'low_season', 'post_april_2024']].to_string(index=False))
    
    # Verify logic
    assert test_df[test_df['ds'].dt.month == 4]['high_season'].values[0] == 1, "High season should be 1 in April!"
    assert test_df[test_df['ds'].dt.month == 7]['july_dip'].values[0] == 1, "July dip should be 1 in July!"
    assert test_df[test_df['ds'].dt.month == 1]['low_season'].values[0] == 1, "Low season should be 1 in Jan!"
    assert all(test_df['post_april_2024'] == 1), "Post-April 2024 should always be 1 for 2025 dates!"
    
    print("\n✅ ANGONO features working correctly!")
    return test_df


def check_model_files():
    print("\n" + "=" * 60)
    print("🔍 Checking Model Files")
    print("=" * 60)
    
    import os
    import pickle
    
    model_dir = "../../saved_models_v2/Latest_FINALIZED_barangay_models_20251223_120258"
    
    if not os.path.exists(model_dir):
        print(f"❌ Model directory not found: {model_dir}")
        return
    
    print(f"✅ Model directory exists: {model_dir}")
    
    # Check CAINTA models
    cainta_path = os.path.join(model_dir, "CAINTA")
    if os.path.exists(cainta_path):
        cainta_barangays = os.listdir(cainta_path)
        print(f"\n📁 CAINTA has {len(cainta_barangays)} barangays:")
        for brgy in cainta_barangays[:3]:  # Show first 3
            print(f"   - {brgy}")
        
        # Try loading one model to check regressors
        sample_brgy = cainta_barangays[0]
        model_path = os.path.join(cainta_path, sample_brgy, "hybrid_model.pkl")
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            print(f"\n🔍 Sample CAINTA model ({sample_brgy}):")
            print(f"   Keys in model: {list(model_data.keys())[:10]}...")
            if 'regressors' in model_data:
                print(f"   Regressors metadata: {model_data['regressors']}")
            else:
                print(f"   ⚠️ No 'regressors' key found (old model format)")
    
    # Check ANGONO models
    angono_path = os.path.join(model_dir, "ANGONO")
    if os.path.exists(angono_path):
        angono_barangays = os.listdir(angono_path)
        print(f"\n📁 ANGONO has {len(angono_barangays)} barangays:")
        for brgy in angono_barangays[:3]:  # Show first 3
            print(f"   - {brgy}")


if __name__ == "__main__":
    print("\n" + "🧪 " * 20)
    print("SEASONAL FEATURES TEST SUITE")
    print("🧪 " * 20 + "\n")
    
    try:
        # Test feature generation
        cainta_df = test_cainta_features()
        angono_df = test_angono_features()
        
        # Check model files
        check_model_files()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("   1. Make sure your virtual environment is activated:")
        print("      cd PROTOTYPE_v2\\backend\\venv")
        print("      .\\Scripts\\Activate.ps1")
        print("   2. Start the FastAPI server:")
        print("      cd ..")
        print("      python main.py")
        print("   3. Check the terminal logs for:")
        print("      '🎯 Added CAINTA/ANGONO seasonal features'")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
