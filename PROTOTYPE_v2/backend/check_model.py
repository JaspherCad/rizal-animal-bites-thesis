import pickle
import pandas as pd

# Load a sample model
with open(r'..\..\saved_models_v2\FINALIZED_barangay_models_20251028_030053\TAYTAY\San_Juan.pkl', 'rb') as f:
    data = pickle.load(f)

print("="*50)
print("MODEL DATA STRUCTURE")
print("="*50)
print("\nAll Keys:", list(data.keys()))

print("\n" + "="*50)
print("METRICS")
print("="*50)
for key in ['mae', 'rmse', 'mape', 'r2', 'mase', 'val_mae', 'val_rmse', 'val_mape', 'val_r2', 'val_mase']:
    if key in data:
        print(f"{key}: {data[key]}")

print("\n" + "="*50)
print("DATA ARRAYS")
print("="*50)
print(f"train_dates: {len(data.get('train_dates', []))} items")
print(f"train_actuals: {len(data.get('train_actuals', []))} items")
print(f"train_predictions: {len(data.get('train_predictions', []))} items")
print(f"dates: {len(data.get('dates', []))} items")
print(f"actuals: {len(data.get('actuals', []))} items")
print(f"predictions: {len(data.get('predictions', []))} items")

print("\n" + "="*50)
print("SAMPLE DATA")
print("="*50)
if 'train_dates' in data and len(data['train_dates']) > 0:
    print("\nFirst 3 training points:")
    for i in range(min(3, len(data['train_dates']))):
        print(f"  {data['train_dates'][i]}: actual={data['train_actuals'][i]}, pred={data['train_predictions'][i]}")

if 'dates' in data and len(data['dates']) > 0:
    print("\nFirst 3 validation points:")
    for i in range(min(3, len(data['dates']))):
        print(f"  {data['dates'][i]}: actual={data['actuals'][i]}, pred={data['predictions'][i]}")
