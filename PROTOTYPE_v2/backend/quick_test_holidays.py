"""
Quick test to check what holiday components are in the new models
"""
import pickle
import pandas as pd
from pathlib import Path

MODEL_DIR = "../../saved_models_v2/FINALIZED_barangay_models_20251031_140501"

# Load one test model
test_model_path = Path(MODEL_DIR) / "CITY_OF_ANTIPOLO" / "Bagong_Nayon_TEST_ONLY.pkl"

with open(test_model_path, 'rb') as f:
    model_data = pickle.load(f)

np_model = model_data['np_model']

# Get some data for prediction
dates = pd.to_datetime(model_data['train_dates'][:10])
actuals = model_data['train_actuals'][:10]

df = pd.DataFrame({'ds': dates, 'y': actuals})

# Predict to see components
forecast = np_model.predict(df)

print("🔍 Forecast columns:")
for col in forecast.columns:
    print(f"   - {col}")

print("\n📊 Sample values:")
print(forecast[['ds', 'yhat1']].head())

# Check for holiday columns
holiday_cols = [col for col in forecast.columns if 'holiday' in col.lower() or 'event' in col.lower()]
print(f"\n🎉 Holiday columns found: {holiday_cols}")

if holiday_cols:
    print("\n🎊 Holiday effects:")
    for col in holiday_cols:
        print(f"\n   {col}:")
        print(forecast[['ds', col]].head(10))
