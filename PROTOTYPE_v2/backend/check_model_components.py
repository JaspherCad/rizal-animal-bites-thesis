"""
Diagnostic script to check ALL available NeuralProphet components
in the trained models (holidays, seasonality types, etc.)
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path

MODEL_DIR = "../../saved_models_v2/FINALIZED_barangay_models_20251028_030053"

def inspect_neuralprophet_model(model_path):
    """Deep inspection of NeuralProphet model configuration."""
    
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    np_model = model_data['np_model']
    
    print("=" * 70)
    print(f"📊 MODEL: {model_data['municipality']} - {model_data['barangay']}")
    print("=" * 70)
    
    # Check model configuration
    print("\n🔧 MODEL CONFIGURATION:")
    print(f"   - Model type: {type(np_model).__name__}")
    
    # Check seasonality settings
    if hasattr(np_model, 'config_seasonality'):
        config = np_model.config_seasonality
        print(f"\n🌊 SEASONALITY CONFIGURATION:")
        print(f"   - Yearly seasonality: {config.yearly_arg if hasattr(config, 'yearly_arg') else 'N/A'}")
        print(f"   - Weekly seasonality: {config.weekly_arg if hasattr(config, 'weekly_arg') else 'N/A'}")
        print(f"   - Daily seasonality: {config.daily_arg if hasattr(config, 'daily_arg') else 'N/A'}")
        
    # Check holiday configuration
    if hasattr(np_model, 'config_holidays'):
        config = np_model.config_holidays
        print(f"\n🎉 HOLIDAYS CONFIGURATION:")
        if config is None or (hasattr(config, 'holiday_names') and not config.holiday_names):
            print(f"   ❌ NO HOLIDAYS CONFIGURED")
        else:
            print(f"   ✅ HOLIDAYS ENABLED")
            if hasattr(config, 'holiday_names'):
                print(f"   - Holiday names: {config.holiday_names}")
    else:
        print(f"\n🎉 HOLIDAYS: ❌ Not configured in this model")
    
    # Check trend configuration
    if hasattr(np_model, 'config_trend'):
        config = np_model.config_trend
        print(f"\n📈 TREND CONFIGURATION:")
        print(f"   - Growth type: {config.growth if hasattr(config, 'growth') else 'linear'}")
        print(f"   - Changepoints range: {config.changepoints_range if hasattr(config, 'changepoints_range') else 'N/A'}")
        print(f"   - N changepoints: {config.n_changepoints if hasattr(config, 'n_changepoints') else 'N/A'}")
    
    # Test prediction to see available components
    print(f"\n🔍 TESTING PREDICTION TO SEE AVAILABLE COMPONENTS:")
    
    # Get some historical data
    dates_list = []
    actuals_list = []
    
    if 'train_dates' in model_data:
        dates_list.extend(pd.to_datetime(model_data['train_dates']))
        actuals_list.extend(model_data['train_actuals'])
    
    if len(dates_list) >= 10:
        test_df = pd.DataFrame({
            'ds': dates_list[:10],
            'y': actuals_list[:10]
        })
        
        forecast = np_model.predict(test_df)
        
        print(f"   📋 Available columns in forecast:")
        for col in forecast.columns:
            print(f"      - {col}")
        
        # Check for specific components
        components_found = []
        if 'trend' in forecast.columns:
            components_found.append('✅ trend')
        if 'season_yearly' in forecast.columns:
            components_found.append('✅ season_yearly')
        if 'season_weekly' in forecast.columns:
            components_found.append('✅ season_weekly')
        if 'season_daily' in forecast.columns:
            components_found.append('✅ season_daily')
        
        # Check for holiday components
        holiday_cols = [col for col in forecast.columns if 'holiday' in col.lower()]
        if holiday_cols:
            for hcol in holiday_cols:
                components_found.append(f'✅ {hcol}')
        
        print(f"\n   🎯 Components found:")
        if components_found:
            for comp in components_found:
                print(f"      {comp}")
        else:
            print(f"      ❌ No decomposition components found (only predictions)")
    
    return forecast.columns.tolist() if len(dates_list) >= 10 else []

def main():
    print("=" * 70)
    print("🔍 NEURALPROPHET MODEL COMPONENTS DIAGNOSTIC")
    print("=" * 70)
    
    model_dir = Path(MODEL_DIR)
    
    if not model_dir.exists():
        print(f"❌ Model directory not found: {MODEL_DIR}")
        return
    
    # Check first model from each municipality
    checked = 0
    all_columns = set()
    
    for mun_dir in model_dir.iterdir():
        if mun_dir.is_dir():
            # Get first model in this municipality
            models = list(mun_dir.glob("*.pkl"))
            if models:
                columns = inspect_neuralprophet_model(models[0])
                all_columns.update(columns)
                checked += 1
                
                if checked >= 3:  # Check 3 models as sample
                    break
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY OF ALL AVAILABLE COMPONENTS:")
    print("=" * 70)
    
    if all_columns:
        for col in sorted(all_columns):
            print(f"   - {col}")
    
    print("\n" + "=" * 70)
    print("💡 INTERPRETATION POSSIBILITIES:")
    print("=" * 70)
    
    interpretability_options = {
        'trend': '✅ AVAILABLE - Long-term direction',
        'season_yearly': '✅ AVAILABLE - Yearly patterns (12-month cycle)',
        'season_weekly': '⚠️  Requires weekly data (not applicable for monthly)',
        'season_daily': '⚠️  Requires daily data (not applicable for monthly)',
        'holidays': '❓ Check if configured during training',
        'changepoints': '✅ AVAILABLE - Detected from trend changes',
        'feature_importance': '✅ AVAILABLE - From XGBoost model'
    }
    
    for option, status in interpretability_options.items():
        print(f"   {option:20s}: {status}")
    
    print("\n" + "=" * 70)
    print("🎯 RECOMMENDATIONS:")
    print("=" * 70)
    print("""
    ✅ ALREADY IMPLEMENTED:
       - Trend decomposition
       - Yearly seasonality (12-month cycle)
       - Feature importance (XGBoost)
       - Changepoint detection (statistical)
    
    ⚠️  NOT APPLICABLE (Monthly Data):
       - Weekly seasonality (need daily/weekly data)
       - Daily seasonality (need daily data)
    
    ❓ DEPENDS ON TRAINING:
       - Holidays: Only if you added Philippine holidays during NeuralProphet training
         Example: model = NeuralProphet()
                  model.add_country_holidays('PH')
    
    💡 TO ADD HOLIDAYS IN FUTURE:
       1. Re-train models with: model.add_country_holidays('PH')
       2. Or manually add specific holidays:
          model.add_events(['New Year', 'Christmas', 'Holy Week'])
       3. Then the forecast will have 'holiday_effect' columns
    
    🌊 ABOUT "4 SEASONS":
       - Philippines has 2 main seasons (wet/dry), not 4
       - Already captured in 'season_yearly' (12-month pattern)
       - Shows which months have higher/lower cases
       - No need for separate seasonal component
    """)

if __name__ == "__main__":
    main()
