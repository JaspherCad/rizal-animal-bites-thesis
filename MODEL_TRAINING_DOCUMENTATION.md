# 🎓 RABIES FORECASTING - MODEL TRAINING DOCUMENTATION

**Notebook:** `MODEL TRAINING Angono Safe Save Before AR IMPLEMENTATION copy 4.ipynb`  
**Purpose:** Train barangay-level NeuralProphet + XGBoost hybrid models for rabies case forecasting  
**Date Created:** December 26, 2025  
**Framework:** NeuralProphet (PyTorch), XGBoost, Pandas

---

## 📚 TABLE OF CONTENTS

1. [Quick Start Guide](#quick-start-guide)
2. [Overall Workflow](#overall-workflow)
3. [Data Requirements](#data-requirements)
4. [Feature Engineering](#feature-engineering)
5. [Model Architecture](#model-architecture)
6. [Municipality-Specific Configurations](#municipality-specific-configurations)
7. [Training Process](#training-process)
8. [Model Saving Structure](#model-saving-structure)
9. [Calibration & Adjustments](#calibration--adjustments)
10. [Troubleshooting Guide](#troubleshooting-guide)

---

## 🚀 QUICK START GUIDE

### Prerequisites

```bash
# Install required packages
pip install neuralprophet xgboost pandas numpy matplotlib seaborn scikit-learn statsmodels
```

### Running the Notebook

```python
# 1. Load data
df = preprocess_rabies_data("CORRECT_rabies_weather_merged_V2_withmuncode.csv")

# 2. Train models (set municipalities to train)
municipalities = ['ANGONO', 'CAINTA', 'TAYTAY', 'CITY OF ANTIPOLO']  # or specific ones

# 3. Run training loop (Cell 45 - the main training cell)
# Models auto-save to: saved_models_v2/Latest_FINALIZED_barangay_models_TIMESTAMP/

# 4. Models are ready for backend use!
```

### Expected Output Structure

```
saved_models_v2/
└── Latest_FINALIZED_barangay_models_20251223_201700/
    ├── ANGONO/
    │   ├── Bagumbayan.pkl
    │   ├── Kalayaan.pkl
    │   └── ... (10 barangays)
    ├── CAINTA/
    │   ├── San Andres (Pob.).pkl
    │   └── ... (7 barangays)
    ├── TAYTAY/
    │   ├── San Isidro.pkl
    │   └── San Juan.pkl
    └── CITY OF ANTIPOLO/
        ├── Cupang.pkl
        ├── San Roque (Pob.).pkl
        └── ... (16 barangays)
```

---

## 🔄 OVERALL WORKFLOW

### Phase 1: Data Preparation

```
Raw CSV Data
    ↓
preprocess_rabies_data()
    ├→ Parse dates (MM/DD/YYYY format)
    ├→ Calculate RAB_ANIMBITE_TOTAL (M + F)
    ├→ Extract Year, Month
    ├→ Filter 2020-2025
    ├→ Mark structural break (Dec 2021)
    └→ Return clean DataFrame
    ↓
Preprocessed DataFrame (ready for modeling)
```

### Phase 2: Feature Engineering

```
Base DataFrame
    ↓
add_seasonal_regressors()
    ├→ CAINTA: 5 binary features (may_peak, low_season, spring_ramp, january_holiday, post_may_decline)
    ├→ ANGONO: 5 binary features (high_season, july_dip, august_rise, low_season, post_april_2024)
    ├→ Weather: 5 continuous features (tmean_c, rh_pct, precip_mm, pct_humid_days, pct_rainy_days)
    └→ Return enhanced DataFrame
    ↓
DataFrame with seasonal + weather features
```

### Phase 3: Model Training (Per Barangay)

```
Barangay Data
    ↓
train_simple_neuralprophet_model()
    ├→ Split: 80% train, 20% validation
    ├→ Train NeuralProphet (with seasonal features)
    ├→ Generate predictions
    ├→ Apply calibration (ANTIPOLO, CAINTA, TAYTAY, ANGONO)
    ├→ Calculate residuals
    ├→ Train XGBoost on residuals
    ├→ Combine: NeuralProphet + XGBoost
    └→ Return (np_result, hybrid_result, np_model, xgb_model)
    ↓
Trained Models + Predictions
```

### Phase 4: Model Persistence

```
Training Results
    ↓
save_barangay_models_from_results()
    ├→ Create directory: saved_models_v2/Latest_FINALIZED_barangay_models_TIMESTAMP/
    ├→ For each barangay:
    │   ├→ Prepare model_data dict
    │   ├→ Include: np_model, xgb_model, training_data, validation_data, metrics
    │   └→ Save as MUNICIPALITY/BARANGAY.pkl
    └→ Return save directory path
    ↓
.pkl files ready for backend deployment
```

---

## 📊 DATA REQUIREMENTS

### Input CSV Format

**File:** `CORRECT_rabies_weather_merged_V2_withmuncode.csv`

**Required Columns:**
```python
[
    'DATE',                    # MM/DD/YYYY format (e.g., "01/15/2022")
    'MUN_CODE',                # Municipality name (e.g., "ANGONO", "CAINTA")
    'BGY_CODE',                # Barangay name (e.g., "Bagumbayan", "San Isidro")
    'RAB_ANIMBITE_M',          # Rabies animal bite cases (Male)
    'RAB_ANIMBITE_F',          # Rabies animal bite cases (Female)
    'tmean_c',                 # Mean temperature (°C) - optional
    'rh_pct',                  # Relative humidity (%) - optional
    'precip_mm',               # Precipitation (mm) - optional
    'pct_humid_days',          # % humid days - optional
    'pct_rainy_days'           # % rainy days - optional
]
```

### Data Preprocessing Details

```python
def preprocess_rabies_data(file_path):
    # 1. Load CSV
    df = pd.read_csv(file_path)
    
    # 2. Parse dates (CRITICAL: Use correct format)
    df["DATE"] = pd.to_datetime(df["DATE"], format='%m/%d/%Y', errors='coerce')
    
    # 3. Calculate total cases
    df["RAB_ANIMBITE_TOTAL"] = df["RAB_ANIMBITE_M"] + df["RAB_ANIMBITE_F"]
    
    # 4. Extract temporal features
    df["Year"] = df["DATE"].dt.year.astype(int)
    df["Month"] = df["DATE"].dt.month.astype(int)
    
    # 5. Filter date range (2020-2025)
    df = df[(df["Year"] >= 2020) & (df["Year"] <= 2025)].copy()
    
    # 6. Mark structural break
    df['is_pre_break'] = df['DATE'] < pd.Timestamp('2021-12-31')
    
    return df
```

**Key Points:**
- ✅ Dates MUST be in `MM/DD/YYYY` format
- ✅ `MUN_CODE` must match: "ANGONO", "CAINTA", "TAYTAY", "CITY OF ANTIPOLO"
- ✅ Missing weather columns are optional (models work without them)
- ✅ Training uses data from **January 2022 onwards** (post-structural break)

---

## 🎨 FEATURE ENGINEERING

### Seasonal Features (Municipality-Specific)

#### CAINTA Seasonal Features

```python
# 1. May Peak (Cases spike in May)
df['may_peak'] = ((df['MUN_CODE'] == 'CAINTA') & (df['DATE'].dt.month == 5)).astype(int)

# 2. Low Season (Cases drop in Dec-Feb)
df['low_season'] = ((df['MUN_CODE'] == 'CAINTA') & 
                     (df['DATE'].dt.month.isin([12, 1, 2]))).astype(int)

# 3. Spring Ramp (Cases increase Mar-Apr)
df['spring_ramp'] = ((df['MUN_CODE'] == 'CAINTA') & 
                      (df['DATE'].dt.month.isin([3, 4]))).astype(int)

# 4. January Holiday (Post-holiday spike)
df['january_holiday'] = ((df['MUN_CODE'] == 'CAINTA') & 
                          (df['DATE'].dt.month == 1)).astype(int)

# 5. Post-May Decline (Cases fall after May)
df['post_may_decline'] = ((df['MUN_CODE'] == 'CAINTA') & 
                           (df['DATE'].dt.month.isin([6, 7, 8]))).astype(int)
```

**Why these features?**
- CAINTA has distinct seasonal pattern with May peak
- Low winter activity (Dec-Feb)
- Spring ramp-up period (Mar-Apr)

---

#### ANGONO Seasonal Features

```python
# 1. High Season (Peak cases: Feb-Jun)
df['high_season'] = ((df['MUN_CODE'] == 'ANGONO') & 
                      (df['DATE'].dt.month.isin([2, 3, 4, 5, 6]))).astype(int)

# 2. July Dip (Cases drop in July)
df['july_dip'] = ((df['MUN_CODE'] == 'ANGONO') & 
                   (df['DATE'].dt.month == 7)).astype(int)

# 3. August Rise (Cases rebound in August)
df['august_rise'] = ((df['MUN_CODE'] == 'ANGONO') & 
                      (df['DATE'].dt.month == 8)).astype(int)

# 4. Low Season (Cases drop: Sep-Jan)
df['low_season'] = ((df['MUN_CODE'] == 'ANGONO') & 
                     (df['DATE'].dt.month.isin([9, 10, 11, 12, 1]))).astype(int)

# 5. Post-April 2024 Shift (Pattern change after Apr 2024)
df['post_april_2024'] = ((df['MUN_CODE'] == 'ANGONO') & 
                          (df['DATE'] >= pd.Timestamp('2024-04-01'))).astype(int)
```

**Why these features?**
- ANGONO has different peak season (Feb-Jun, not May only)
- Unique July dip followed by August rebound
- Pattern shift detected after April 2024

---

### Weather Features (All Municipalities)

```python
weather_features = [
    'tmean_c',           # Mean temperature (°C)
    'rh_pct',            # Relative humidity (%)
    'precip_mm',         # Precipitation (mm)
    'pct_humid_days',    # % of humid days in month
    'pct_rainy_days'     # % of rainy days in month
]

# Added as future regressors in NeuralProphet
for col in weather_features:
    if col in df.columns:
        model.add_future_regressor(col, mode='additive')
```

**Why weather features?**
- Temperature affects animal behavior
- Humidity influences disease transmission
- Rainfall impacts outdoor activities (exposure risk)

---

### XGBoost Features (Residual Learning)

```python
def create_simple_features(df):
    features = df[['Year', 'Month']].copy()
    
    # Lag features
    features['lag_1'] = df['RAB_ANIMBITE_TOTAL'].shift(1).fillna(0)
    features['lag_2'] = df['RAB_ANIMBITE_TOTAL'].shift(2).fillna(0)
    features['lag_12'] = df['RAB_ANIMBITE_TOTAL'].shift(12).fillna(df['RAB_ANIMBITE_TOTAL'].mean())
    
    # Rolling statistics
    features['rolling_mean_3'] = df['RAB_ANIMBITE_TOTAL'].rolling(window=3, min_periods=1).mean()
    features['rolling_std_3'] = df['RAB_ANIMBITE_TOTAL'].rolling(window=3, min_periods=1).std().fillna(0)
    
    # Cyclical encoding
    features['month_sin'] = np.sin(2 * np.pi * features['Month'] / 12)
    features['month_cos'] = np.cos(2 * np.pi * features['Month'] / 12)
    
    # Rate of change
    features['rate_of_change_1'] = df['RAB_ANIMBITE_TOTAL'].pct_change(1).fillna(0).replace([np.inf, -np.inf], 0)
    
    # NeuralProphet baseline
    features['np_prediction'] = np_predictions  # Added later
    
    return features
```

**Why these features for XGBoost?**
- **Lag features**: Capture recent trends
- **Rolling stats**: Capture moving averages and volatility
- **Cyclical encoding**: Capture seasonality mathematically
- **Rate of change**: Capture momentum
- **NP prediction**: XGBoost learns corrections to NeuralProphet baseline

---

## 🏗️ MODEL ARCHITECTURE

### NeuralProphet (Base Model)

```python
from neuralprophet import NeuralProphet

model = NeuralProphet(
    growth='linear',                  # Linear trend (not exponential)
    changepoints_range=0.95,          # Allow changepoints in 95% of data
    n_changepoints=10,                # 10 potential trend changes
    
    # Seasonality
    yearly_seasonality=12,            # 12 Fourier terms for yearly pattern
    weekly_seasonality=False,         # Disabled (monthly data)
    daily_seasonality=False,          # Disabled (monthly data)
    
    # Regularization (adaptive based on data length)
    trend_reg=trend_reg,              # L2 penalty on trend changes
    seasonality_reg=seasonality_reg,  # L2 penalty on seasonality
    
    # Training
    epochs=500,                       # 500 training epochs
    learning_rate=0.1,                # Adam optimizer learning rate
    batch_size=len(train_data),       # Full-batch training
    
    # Loss function
    loss_func='Huber'                 # Robust to outliers
)
```

**Architecture Details:**

```
Input: DataFrame with columns [ds, y, seasonal_features, weather_features]
    ↓
Trend Component (Linear + Changepoints)
    ↓
Seasonal Component (Fourier Series)
    ↓
Regressor Components (Seasonal + Weather)
    ↓
Combine All Components
    ↓
Output: Predicted Cases (ŷ)
```

**Why NeuralProphet?**
- ✅ Handles non-stationary time series
- ✅ Automatic trend changepoint detection
- ✅ Flexible regressor system
- ✅ Robust to outliers (Huber loss)
- ✅ Fast training on monthly data

---

### XGBoost (Residual Learner)

```python
from xgboost import XGBRegressor

# Municipality-specific hyperparameters
XGBOOST_PARAMS = {
    "ANGONO": {
        'n_estimators': 50,
        'max_depth': 3,
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.2,      # L1 regularization
        'reg_lambda': 0.2      # L2 regularization
    },
    "CAINTA": {
        'n_estimators': 50,
        'max_depth': 3,
        'learning_rate': 0.1,
        'subsample': 0.7,      # Lower subsample (less data)
        'colsample_bytree': 0.7,
        'reg_alpha': 0.3,      # Higher regularization
        'reg_lambda': 0.2
    },
    "CITY OF ANTIPOLO": {
        'n_estimators': 80,     # More trees (more data)
        'max_depth': 4,         # Deeper trees
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.2,
        'reg_lambda': 0.2
    },
    "TAYTAY": {
        'n_estimators': 50,
        'max_depth': 3,
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.3,
        'reg_lambda': 0.2
    }
}

xgb_model = XGBRegressor(**xgb_params)
xgb_model.fit(X_train, train_residuals)
```

**XGBoost Architecture:**

```
Input: Features [Year, Month, lags, rolling stats, month_sin, month_cos, rate_change, np_prediction]
    ↓
Decision Tree 1 (Residual_1)
    ↓
Decision Tree 2 (Residual_2 - learns errors from Tree 1)
    ↓
Decision Tree 3 (Residual_3 - learns errors from Trees 1+2)
    ↓
... (n_estimators trees)
    ↓
Sum All Trees → Predicted Residual
```

**Why XGBoost?**
- ✅ Learns complex non-linear residual patterns
- ✅ Captures sudden spikes/drops NeuralProphet misses
- ✅ Uses lag features (NeuralProphet doesn't)
- ✅ Fast training and inference
- ✅ Built-in regularization prevents overfitting

---

### Hybrid Model (Final Predictions)

```python
# Step 1: NeuralProphet baseline
np_predictions = model.predict(df_prophet)[['yhat1']].values.flatten()

# Step 2: Apply calibration (for ANTIPOLO, CAINTA, TAYTAY, ANGONO)
if municipality in ["CITY OF ANTIPOLO", "CAINTA", "TAYTAY", "ANGONO"]:
    # Calculate offset
    actual_mean = actual_train.mean()
    pred_mean = np_predictions.mean()
    offset = actual_mean - pred_mean
    
    # Apply offset + variance adjustment
    np_predictions_calibrated = np_predictions + offset + additional_adjustments

# Step 3: Calculate residuals
residuals = actuals - np_predictions_calibrated

# Step 4: XGBoost learns residuals
xgb_residual_predictions = xgb_model.predict(X_features)

# Step 5: Combine
hybrid_predictions = np_predictions_calibrated + xgb_residual_predictions

# Step 6: Ensure non-negative
hybrid_predictions = np.maximum(hybrid_predictions, 0)
```

**Why Hybrid?**
- ✅ NeuralProphet captures trend + seasonality
- ✅ XGBoost captures residual patterns (spikes, anomalies)
- ✅ Calibration fixes systematic bias
- ✅ Best of both worlds: interpretability + accuracy

---

## ⚙️ MUNICIPALITY-SPECIFIC CONFIGURATIONS

### Why Different Settings?

Each municipality has:
- Different data volumes (ANTIPOLO: 16 barangays, TAYTAY: 2 barangays)
- Different seasonal patterns (CAINTA peaks in May, ANGONO peaks Feb-Jun)
- Different volatility levels (some barangays are stable, others are erratic)

---

### ANGONO Configuration

**Data Profile:**
- **Barangays:** 10
- **Date Range:** Jan 2022 - Jul 2025
- **Pattern:** High season (Feb-Jun), July dip, August rise, low season (Sep-Jan)

**Model Settings:**
```python
# NeuralProphet
trend_reg = 0.2          # Moderate trend regularization
seasonality_reg = 0.2    # Moderate seasonality regularization

# XGBoost
n_estimators = 50
max_depth = 3
learning_rate = 0.1
subsample = 0.8
colsample_bytree = 0.8
reg_alpha = 0.2
reg_lambda = 0.2

# Seasonal Features (5)
['high_season', 'july_dip', 'august_rise', 'low_season', 'post_april_2024']

# Weather Features (5 - if available)
['tmean_c', 'rh_pct', 'precip_mm', 'pct_humid_days', 'pct_rainy_days']
```

**Calibration Adjustments:**
```python
POSITION_ADJUST = {
    "ANGONO|Bagumbayan": 0.30,
    "ANGONO|Kalayaan": 0.35,
    "ANGONO|Poblacion Ibaba": 0.25,
    "ANGONO|San Isidro": 0.40,
    # ... etc
}

VARIANCE_ADJUST = {
    "ANGONO|Bagumbayan": 3.0,      # Amplify fluctuations
    "ANGONO|Kalayaan": 9.3,        # Strong amplification
    "ANGONO|San Pedro": 4.3,
    # ... etc
}
```

---

### CAINTA Configuration

**Data Profile:**
- **Barangays:** 7
- **Date Range:** Jan 2022 - Jul 2025
- **Pattern:** May peak, low season (Dec-Feb), spring ramp (Mar-Apr)

**Model Settings:**
```python
# NeuralProphet
trend_reg = 0.2
seasonality_reg = 0.2

# XGBoost (slightly higher regularization - less data)
n_estimators = 50
max_depth = 3
learning_rate = 0.1
subsample = 0.7          # Lower due to smaller dataset
colsample_bytree = 0.7
reg_alpha = 0.3          # Higher L1 regularization
reg_lambda = 0.2

# Seasonal Features (5)
['may_peak', 'low_season', 'spring_ramp', 'january_holiday', 'post_may_decline']

# Weather Features (5 - if available)
['tmean_c', 'rh_pct', 'precip_mm', 'pct_humid_days', 'pct_rainy_days']
```

**Calibration Adjustments:**
```python
POSITION_ADJUST = {
    "CAINTA|San Roque": 0.25,
    # ... etc
}

VARIANCE_ADJUST = {
    "CAINTA|San Roque": 0.3,       # Dampen fluctuations
    # ... etc
}
```

---

### TAYTAY Configuration

**Data Profile:**
- **Barangays:** 2 (San Isidro, San Juan)
- **Date Range:** Jan 2022 - Jul 2025
- **Pattern:** Highly volatile, limited data

**Model Settings:**
```python
# NeuralProphet
trend_reg = 0.3          # Higher regularization (less data)
seasonality_reg = 0.3

# XGBoost
n_estimators = 50
max_depth = 3
learning_rate = 0.1
subsample = 0.8
colsample_bytree = 0.8
reg_alpha = 0.3          # Higher regularization
reg_lambda = 0.2

# No custom seasonal features (uses only weather if available)
```

**Calibration Adjustments:**
```python
VARIANCE_ADJUST = {
    "TAYTAY|San Isidro": 0.2,      # Strong dampening (very volatile)
}
```

---

### CITY OF ANTIPOLO Configuration

**Data Profile:**
- **Barangays:** 16 (largest dataset)
- **Date Range:** Jan 2022 - Jul 2025
- **Pattern:** Stable, high volume

**Model Settings:**
```python
# NeuralProphet
trend_reg = 0.1          # Lower regularization (more data)
seasonality_reg = 0.1

# XGBoost (more capacity - more data)
n_estimators = 80        # More trees
max_depth = 4            # Deeper trees
learning_rate = 0.1
subsample = 0.8
colsample_bytree = 0.8
reg_alpha = 0.2
reg_lambda = 0.2

# No custom seasonal features (uses only weather if available)
```

**Calibration Adjustments:**
```python
POSITION_ADJUST = {
    "CITY OF ANTIPOLO|Cupang": 0.20,
    "CITY OF ANTIPOLO|Santa Cruz": 0.15,
    "CITY OF ANTIPOLO|Dalig": 0.25,
    # ... etc (16 barangays)
}

VARIANCE_ADJUST = {
    "CITY OF ANTIPOLO|Cupang": 1.2,          # Amplify
    "CITY OF ANTIPOLO|Dela Paz (Pob.)": 0.4, # Dampen
    "CITY OF ANTIPOLO|Mayamot": 0.6,         # Dampen
    "CITY OF ANTIPOLO|San Roque (Pob.)": 1.3, # Amplify
    # ... etc
}
```

---

## 🎯 TRAINING PROCESS

### Main Training Loop (Cell 45)

```python
# ============================================
# MAIN TRAINING LOOP
# ============================================

municipalities = ['ANGONO', 'CAINTA', 'TAYTAY', 'CITY OF ANTIPOLO']
all_results = []

for municipality in municipalities:
    print(f"\n{'='*100}")
    print(f"🏛️  TRAINING MUNICIPALITY: {municipality}")
    print(f"{'='*100}\n")
    
    # Filter barangays for this municipality (post-2022 data only)
    municipality_data = df[
        (df['MUN_CODE'] == municipality) & 
        (df['DATE'] >= '2022-01-01')
    ]
    
    barangays = municipality_data['BGY_CODE'].unique()
    print(f"📍 Found {len(barangays)} barangays: {list(barangays)}\n")
    
    for barangay in barangays:
        print(f"\n🔹 Training: {municipality} | {barangay}")
        print("-" * 80)
        
        # Filter data for this barangay
        bgy_data = municipality_data[
            municipality_data['BGY_CODE'] == barangay
        ].copy()
        
        # Sort by date
        bgy_data = bgy_data.sort_values('DATE').reset_index(drop=True)
        
        # Train model
        np_result, hybrid_result, np_model, xgb_model = train_simple_neuralprophet_model(
            bgy_data, 
            barangay, 
            municipality, 
            validation_periods=5  # Use last 5 months for validation
        )
        
        if np_result is None:
            print(f"❌ Failed to train: {barangay}")
            continue
        
        # Store results
        all_results.append({
            'np_result': np_result,
            'hybrid_result': hybrid_result,
            'np_model': np_model,
            'xgb_model': xgb_model,
            'barangay_data': bgy_data
        })
        
        print(f"✅ Completed: {barangay}")
        print(f"   NP MAE: {np_result['mae']:.2f}, MASE: {np_result['mase']:.3f}")
        print(f"   Hybrid MAE: {hybrid_result['mae']:.2f}, MASE: {hybrid_result['mase']:.3f}")

# Save all models
save_directory = save_barangay_models_from_results(all_results)
print(f"\n✅ All models saved to: {save_directory}")
```

---

### Training Workflow (Per Barangay)

```
1. Data Filtering
   └→ Get barangay data (post-2022)
   
2. Train/Validation Split (80/20)
   └→ Last 5 months = validation
   
3. NeuralProphet Training
   ├→ Prepare DataFrame (ds, y, regressors)
   ├→ Add seasonal features (if CAINTA/ANGONO)
   ├→ Add weather features (if available)
   ├→ Fit model (500 epochs)
   └→ Generate predictions
   
4. Calibration (if ANTIPOLO/CAINTA/TAYTAY/ANGONO)
   ├→ Calculate offset (actual_mean - pred_mean)
   ├→ Apply position adjustment
   ├→ Apply variance adjustment
   └→ Get calibrated predictions
   
5. XGBoost Training
   ├→ Calculate residuals (actual - calibrated_np_pred)
   ├→ Create features (lags, rolling, cyclical, np_pred)
   ├→ Train XGBoost on residuals
   └→ Generate residual predictions
   
6. Hybrid Predictions
   └→ hybrid = calibrated_np_pred + xgb_residuals
   
7. Metrics Calculation
   ├→ MAE, MASE, RMSE, MAPE, R²
   └→ Improvement percentage
   
8. Return Results
   └→ (np_result, hybrid_result, np_model, xgb_model)
```

---

## 💾 MODEL SAVING STRUCTURE

### .pkl File Contents

Each barangay's `.pkl` file contains:

```python
model_data = {
    # Model objects
    'np_model': np_model,              # NeuralProphet model object
    'xgb_model': xgb_model,            # XGBoost model object
    
    # Data
    'barangay_data': bgy_data,         # Full DataFrame
    'training_data': train_data,       # Training split
    'validation_data': val_data,       # Validation split
    
    # Predictions
    'np_predictions': {
        'training': np_train_preds,
        'validation': np_val_preds
    },
    'hybrid_predictions': {
        'training': hybrid_train_preds,
        'validation': hybrid_val_preds
    },
    
    # Metrics
    'metrics': {
        'np_mae': np_val_mae,
        'np_mase': np_val_mase,
        'np_rmse': np_val_rmse,
        'np_mape': np_val_mape,
        'np_r2': np_val_r2,
        'hybrid_mae': hybrid_val_mae,
        'hybrid_mase': hybrid_val_mase,
        'hybrid_rmse': hybrid_val_rmse,
        'hybrid_mape': hybrid_val_mape,
        'hybrid_r2': hybrid_val_r2,
        'improvement': val_improvement
    },
    
    # Metadata
    'barangay': barangay_name,
    'municipality': municipality,
    'train_size': len(train_data),
    'val_size': len(val_data),
    'saved_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}
```

---

### Directory Structure

```
saved_models_v2/
└── Latest_FINALIZED_barangay_models_20251223_201700/
    ├── ANGONO/
    │   ├── Bagumbayan.pkl           # Contains: model + data + metrics
    │   ├── Kalayaan.pkl
    │   ├── Mahabang Parang.pkl
    │   ├── Poblacion Ibaba.pkl
    │   ├── Poblacion Itaas.pkl
    │   ├── San Isidro.pkl
    │   ├── San Pedro.pkl
    │   ├── San Roque.pkl
    │   ├── San Vicente.pkl
    │   └── Santo Niño.pkl
    │
    ├── CAINTA/
    │   ├── San Andres (Pob.).pkl
    │   ├── San Isidro.pkl
    │   ├── San Juan.pkl
    │   ├── San Roque.pkl
    │   ├── Santo Domingo.pkl
    │   ├── Santo Niño.pkl
    │   └── San Vicente.pkl
    │
    ├── TAYTAY/
    │   ├── San Isidro.pkl
    │   └── San Juan.pkl
    │
    └── CITY OF ANTIPOLO/
        ├── Bagong Nayon.pkl
        ├── Beverly Hills.pkl
        ├── Calawis.pkl
        ├── Cupang.pkl
        ├── Dalig.pkl
        ├── Dela Paz (Pob.).pkl
        ├── Inarawan.pkl
        ├── Mambugan.pkl
        ├── Mayamot.pkl
        ├── Muntingdilaw.pkl
        ├── San Isidro (Pob.).pkl
        ├── San Jose (Pob.).pkl
        ├── San Juan.pkl
        ├── San Luis.pkl
        ├── San Roque (Pob.).pkl
        └── Santa Cruz.pkl
```

**Total:** 42 barangay models (10 ANGONO + 7 CAINTA + 2 TAYTAY + 16 ANTIPOLO + 7 CAINTA)

---

## 🔧 CALIBRATION & ADJUSTMENTS

### Why Calibration?

**Problem:** NeuralProphet predictions are sometimes systematically biased:
- **ANTIPOLO:** Predictions are 30-40% too low
- **ANGONO:** Predictions are 20-30% too low
- **CAINTA:** Predictions are 15-25% too low
- **TAYTAY:** Predictions are 10-20% too low

**Solution:** Apply calibration to correct systematic bias.

---

### Position Adjustment (Shift Up/Down)

**Purpose:** Fix mean prediction level

```python
# Example: ANGONO|San Isidro
POSITION_ADJUST = {
    "ANGONO|San Isidro": 0.40  # Shift UP by 40%
}

# How it works:
actual_mean = 150
pred_mean = 100
offset = actual_mean - pred_mean  # 50

position_factor = 0.40
additional_offset = offset * position_factor  # 50 * 0.40 = 20

# Apply shift
calibrated_predictions = raw_predictions + additional_offset
# Before: [90, 100, 110] (mean=100)
# After:  [110, 120, 130] (mean=120)
```

**Effect:** Moves entire prediction curve up/down

---

### Variance Adjustment (Scale Range)

**Purpose:** Fix fluctuation magnitude

```python
# Example: ANGONO|Kalayaan
VARIANCE_ADJUST = {
    "ANGONO|Kalayaan": 9.3  # Amplify fluctuations by 9.3x
}

# How it works:
pred_mean = 100
predictions = [90, 100, 110]  # Range = 20

# Calculate deviations
deviations = predictions - pred_mean  # [-10, 0, 10]

# Scale deviations
variance_factor = 9.3
adjusted_deviations = deviations * variance_factor  # [-93, 0, 93]

# Reconstruct
calibrated = pred_mean + adjusted_deviations  # [7, 100, 193]
```

**Effect:** Changes range/spread of fluctuations (NOT position)

---

### Calibration Examples

#### Example 1: ANGONO|Bagumbayan

```python
POSITION_ADJUST["ANGONO|Bagumbayan"] = 0.30   # Shift UP 30%
VARIANCE_ADJUST["ANGONO|Bagumbayan"] = 3.0    # Amplify 3x

# Before calibration:
raw_predictions = [10, 12, 14, 16]
mean = 13, range = 6

# After position adjustment (+30% of offset):
position_adjusted = [15, 17, 19, 21]
mean = 18, range = 6  # Range unchanged

# After variance adjustment (3x):
final_predictions = [9, 18, 27, 36]
mean = 18, range = 27  # Range amplified!
```

#### Example 2: CITY OF ANTIPOLO|Dela Paz (Pob.)

```python
POSITION_ADJUST["CITY OF ANTIPOLO|Dela Paz (Pob.)"] = 0.15  # Shift UP 15%
VARIANCE_ADJUST["CITY OF ANTIPOLO|Dela Paz (Pob.)"] = 0.4   # Dampen to 40%

# Before calibration:
raw_predictions = [200, 240, 260, 220]
mean = 230, range = 60

# After position adjustment (+15%):
position_adjusted = [215, 255, 275, 235]
mean = 245, range = 60

# After variance adjustment (0.4x = dampen):
final_predictions = [233, 249, 257, 241]
mean = 245, range = 24  # Range reduced!
```

---

## 🛠️ TROUBLESHOOTING GUIDE

### Problem 1: "Import Error: No module named 'neuralprophet'"

**Cause:** Package not installed

**Solution:**
```bash
pip install neuralprophet
# or
pip install neuralprophet==0.8.1  # Specific version
```

---

### Problem 2: "Date parsing errors"

**Symptoms:**
```
TypeError: to_datetime() got an unexpected keyword argument 'format'
```

**Cause:** Wrong date format in CSV

**Solution:**
```python
# Check your CSV date format
df = pd.read_csv("data.csv")
print(df["DATE"].head())

# Common formats:
# MM/DD/YYYY → format='%m/%d/%Y'
# YYYY-MM-DD → format='%Y-%m-%d'
# DD/MM/YYYY → format='%d/%m/%Y'

# Update preprocess_rabies_data() accordingly
df["DATE"] = pd.to_datetime(df["DATE"], format='%m/%d/%Y', errors='coerce')
```

---

### Problem 3: "Training extremely slow"

**Cause:** Too many epochs or large dataset

**Solution:**
```python
# Reduce epochs for testing
model = NeuralProphet(
    epochs=100,  # Instead of 500
    # ... other params
)

# Or train on fewer barangays
municipalities = ['ANGONO']  # Test on one municipality first
```

---

### Problem 4: "High MASE (>1.5)"

**Cause:** Model performs worse than naive baseline

**Possible Solutions:**

1. **Check data quality:**
   ```python
   # Look for missing values
   print(bgy_data['RAB_ANIMBITE_TOTAL'].isnull().sum())
   
   # Look for outliers
   print(bgy_data['RAB_ANIMBITE_TOTAL'].describe())
   ```

2. **Increase regularization:**
   ```python
   trend_reg = 0.5  # Higher (was 0.2)
   seasonality_reg = 0.5
   ```

3. **Add calibration adjustments:**
   ```python
   POSITION_ADJUST["MUNICIPALITY|BARANGAY"] = 0.25
   VARIANCE_ADJUST["MUNICIPALITY|BARANGAY"] = 0.8
   ```

---

### Problem 5: "Models not saving"

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'saved_models_v2/...'
```

**Cause:** Directory doesn't exist

**Solution:**
```python
# Add to save function
import os
os.makedirs(save_dir, exist_ok=True)
```

---

### Problem 6: "XGBoost predictions are NaN"

**Cause:** Invalid features (inf, NaN)

**Solution:**
```python
# Check features before training
X_train = create_simple_features(train_data)
print(X_train.isnull().sum())
print(X_train.isin([np.inf, -np.inf]).sum())

# Fix rate_of_change feature
features['rate_of_change_1'] = (
    df['RAB_ANIMBITE_TOTAL']
    .pct_change(1)
    .fillna(0)
    .replace([np.inf, -np.inf], 0)  # Replace inf with 0
)
```

---

## 📖 KEY CONCEPTS FOR AI ASSISTANTS

### 1. **Training Data = Post-2022 Only**

```python
# ✅ Correct: Filter for post-structural break data
df_train = df[df['DATE'] >= '2022-01-01']

# ❌ Wrong: Using all data (includes pre-break 2020-2021)
df_train = df  # Includes structural break - will bias predictions
```

**Why?** There was a structural break in December 2021. Pre-break patterns are different.

---

### 2. **Seasonal Features MUST Match Municipality**

```python
# ✅ Correct: CAINTA gets CAINTA features
if municipality == "CAINTA":
    df = add_cainta_seasonal_features(df)

# ❌ Wrong: CAINTA gets ANGONO features
if municipality == "CAINTA":
    df = add_angono_seasonal_features(df)  # WRONG FEATURES!
```

**Why?** Each municipality has unique seasonal patterns.

---

### 3. **XGBoost Learns Residuals, NOT Cases**

```python
# ✅ Correct: Train on residuals
residuals = actuals - np_predictions
xgb_model.fit(X_train, residuals)

# ❌ Wrong: Train on actual cases
xgb_model.fit(X_train, actuals)  # XGBoost will overfit!
```

**Why?** XGBoost refines NeuralProphet predictions, not learning from scratch.

---

### 4. **Calibration Happens BEFORE XGBoost**

```python
# ✅ Correct Order:
# 1. NeuralProphet raw predictions
np_raw = model.predict(df)

# 2. Apply calibration
np_calibrated = np_raw + position_offset
np_calibrated = apply_variance_adjustment(np_calibrated)

# 3. Calculate residuals from calibrated
residuals = actuals - np_calibrated

# 4. Train XGBoost on residuals
xgb_model.fit(X, residuals)

# ❌ Wrong Order:
# If you calculate residuals from RAW predictions,
# XGBoost has to learn BOTH bias correction AND residuals
```

---

### 5. **Model Saving MUST Include Both np_model AND xgb_model**

```python
# ✅ Correct: Save both models
model_data = {
    'np_model': np_model,      # NeuralProphet object
    'xgb_model': xgb_model,    # XGBoost object
    # ... other data
}

# ❌ Wrong: Only save predictions
model_data = {
    'predictions': preds,  # Can't make NEW predictions!
}
```

**Why?** Backend needs model objects to predict future months.

---

## 🎓 SUMMARY

### Training Pipeline (5 Steps)

```
1. DATA PREPARATION
   • Load CSV
   • Parse dates (MM/DD/YYYY)
   • Filter post-2022
   • Add seasonal features (CAINTA/ANGONO specific)
   • Add weather features (all municipalities)
   
2. MODEL TRAINING (Per Barangay)
   • Split train/validation (80/20)
   • Train NeuralProphet (trend + seasonality + regressors)
   • Generate predictions
   
3. CALIBRATION (ANTIPOLO/CAINTA/TAYTAY/ANGONO)
   • Calculate offset (actual_mean - pred_mean)
   • Apply position adjustment (shift up/down)
   • Apply variance adjustment (amplify/dampen)
   
4. RESIDUAL LEARNING
   • Calculate residuals (actual - calibrated_np_pred)
   • Create XGBoost features (lags, rolling, cyclical, np_pred)
   • Train XGBoost on residuals
   
5. MODEL PERSISTENCE
   • Combine results
   • Save to .pkl (np_model + xgb_model + data + metrics)
   • Organize by MUNICIPALITY/BARANGAY.pkl
```

---

### Key Files

| File | Purpose |
|------|---------|
| `MODEL TRAINING Angono Safe Save... .ipynb` | Main training notebook |
| `CORRECT_rabies_weather_merged_V2_withmuncode.csv` | Input data |
| `saved_models_v2/Latest_FINALIZED_barangay_models_TIMESTAMP/` | Output models |

---

### Key Functions

| Function | Purpose |
|----------|---------|
| `preprocess_rabies_data()` | Load and clean CSV |
| `add_cainta_seasonal_features()` | Add CAINTA-specific binary features |
| `add_angono_seasonal_features()` | Add ANGONO-specific binary features |
| `train_simple_neuralprophet_model()` | Train NP + XGBoost hybrid |
| `create_simple_features()` | Generate XGBoost features |
| `save_barangay_models_from_results()` | Save trained models to .pkl |

---

### Important Constants

```python
# Municipalities
MUNICIPALITIES = ['ANGONO', 'CAINTA', 'TAYTAY', 'CITY OF ANTIPOLO']

# Date ranges
TRAINING_START = '2022-01-01'  # Post-structural break
STRUCTURAL_BREAK = '2021-12-31'

# Seasonal feature counts
CAINTA_FEATURES = 5  # may_peak, low_season, spring_ramp, january_holiday, post_may_decline
ANGONO_FEATURES = 5  # high_season, july_dip, august_rise, low_season, post_april_2024
WEATHER_FEATURES = 5  # tmean_c, rh_pct, precip_mm, pct_humid_days, pct_rainy_days

# Total models
TOTAL_BARANGAYS = 42  # 10 ANGONO + 7 CAINTA + 2 TAYTAY + 16 ANTIPOLO + 7 CAINTA
```

---

**END OF DOCUMENTATION**

*Generated on December 26, 2025*  
*For questions, refer to: BACKEND_DOCUMENTATION.md, FRONTEND_DOCUMENTATION_PART1.md, FRONTEND_DOCUMENTATION_PART2.md*
