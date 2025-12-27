# 🦠 Rabies Forecasting System - AI Navigation Guide

## 📋 System Architecture (3-Tier)

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   TRAINING      │ ──→  │    BACKEND      │ ←──→ │    FRONTEND     │
│   (Notebook)    │      │    (FastAPI)    │      │    (React)      │
└─────────────────┘      └─────────────────┘      └─────────────────┘
   Model Creation        Model Serving/API         User Interface
```

---

## 🧠 1. TRAINING NOTEBOOK
**File:** `MODEL TRAINING Angono Safe Save Before AR IMPLEMENTATION copy 4.ipynb`

### Key Functions

#### `add_antipolo_vaccination_campaigns(df)` - Lines 1620-1660
- Creates **15 vaccination regressors** (5 campaigns × 3 lags each)
- Base columns (`vaccination_jan2023`) are INTERMEDIATE - used to calculate lags
- **Only lag columns** (`vaccination_jan2023_lag1/2/3`) are registered as future regressors
- Returns DataFrame with lag columns only (base columns dropped)

#### `train_simple_neuralprophet_model()` - Lines 1932-2745
- Main training function for NeuralProphet + XGBoost hybrid
- **Municipality-specific configuration:**
  - ANTIPOLO: Holidays + 15 vaccination regressors
  - CAINTA: Holidays + Fourier seasonality only
  - ANGONO: Holidays + Fourier seasonality only  
  - TAYTAY: Holidays + Fourier seasonality only
- **Returns:** `np_simple_result, hybrid_result, model, xgb_model, valid_vax_cols`
  - `valid_vax_cols` is the list of vaccination columns (needed for metadata export)

#### Model Export - Lines 2920-2945
```python
model_data = {
    'np_model': np_model,
    'xgb_model': xgb_model,
    'regressors': {
        'vaccination': list(valid_vax_cols),  # ANTIPOLO only
        'weather': [],                         # Not used
        'seasonal': []                         # Removed
    }
}
```

### Important Concepts
- **Future Regressors:** External variables with known future values (vaccination campaigns)
- **AR Terms:** Auto-regressive (lag features from target variable) - NOT used in current models
- **Structural Break:** Dec 2021 - training starts Jan 2022+
- **Calibration Factor:** 2.5x for ANTIPOLO (scale up predictions to match actual levels)

---

## 🔌 2. BACKEND (FastAPI)
**File:** `PROTOTYPE_v2/backend/main.py`

### Key Functions

#### `add_antipolo_vaccination_campaigns(df)` - Lines 90-158
- **CRITICAL:** Initializes ALL 20 columns (5 base + 15 lags) as zeros
- Calculates lags using `.shift()`
- **Drops base columns** before returning (lines 154-156)
- Must match training notebook behavior exactly

#### `extract_model_components(model_data)` - Lines 162-506
- Extracts trend, seasonality, holidays, regressors from trained model
- For ANTIPOLO: Calls `add_antipolo_vaccination_campaigns()` to recreate features
- Uses model metadata: `model_data.get('regressors', {}).get('vaccination', [])`

#### `predict_next_month(model_data)` - Lines 509-564
- Predicts 1 month ahead
- For ANTIPOLO: Adds vaccination features via function call

#### `predict_future_months(model_data, months_ahead=12)` - Lines 567-655
- Predicts multiple months (default 8, max 24)
- For ANTIPOLO: Adds vaccination features via function call

### API Endpoints
- `GET /` - Health check
- `GET /api/municipalities` - List all municipalities with risk levels
- `GET /api/barangay/{municipality}/{barangay}` - Detailed barangay data
- `GET /api/forecast/{municipality}/{barangay}` - Future predictions
- `GET /api/interpretability/{municipality}/{barangay}` - Model decomposition
- `GET /api/report/csv/{municipality}/{barangay}` - CSV report
- `GET /api/report/pdf/{municipality}/{barangay}` - PDF report

### Model Loading
```python
MODEL_DIR = "../../saved_models_v2/Latest_FINALIZED_barangay_models_20251228_000045"
```
Each model is a `.pkl` file containing:
- `np_model`: NeuralProphet model object
- `xgb_model`: XGBoost model object
- `regressors`: Metadata dict with `vaccination`, `weather`, `seasonal` lists

---

## 🎨 3. FRONTEND (React)
**File:** `PROTOTYPE_v2/frontend/src/components/ModelInsights.js`

### Key Components

#### Vaccination Regressor Chart - Lines 247-280
- Displays 15 vaccination campaign impacts over time
- Color-coded by campaign (Jan2023=blue, Feb2023=green, etc.)
- Shows 1-3 month lagged effects

#### Trend/Seasonality/Holiday Charts - Lines 150-245
- Line charts showing model decomposition
- Helps users understand prediction drivers

### Data Flow
1. Fetch from `/api/interpretability/{municipality}/{barangay}`
2. Parse `vaccination_regressors` object (15 keys, each with array of values)
3. Render time series charts using Recharts library

---

## 🔑 Key Concepts for AI

### Vaccination Regressors (ANTIPOLO ONLY)
- **Purpose:** Capture effect of mass anti-rabies vaccination campaigns (2023-2024)
- **Implementation:** Binary indicators (0/1) + 1-3 month lags
- **Count:** 15 features (5 campaigns × 3 lags)
- **Training:** Registered with `model.add_future_regressor(col, mode='additive')`
- **Prediction:** Function recreates features for future dates (all zeros for dates without campaigns)

### Why Base Columns Are Dropped
```python
# TRAINING (Notebook)
df['vaccination_jan2023'] = 0  # Mark campaign month
df['vaccination_jan2023_lag1'] = df['vaccination_jan2023'].shift(1)  # Use base to create lag
model.add_future_regressor('vaccination_jan2023_lag1')  # Register LAG only
# Base column NOT registered, so must be dropped before prediction

# PREDICTION (Backend)
df = add_antipolo_vaccination_campaigns(df)  # Creates base + lags
df = df.drop(columns=['vaccination_jan2023', ...])  # Drop base (not in model)
np_model.predict(df)  # Only lag columns present
```

### Municipality Differences
| Municipality | Holidays | Vaccination | Weather | Seasonal |
|-------------|----------|-------------|---------|----------|
| ANTIPOLO    | ✅       | ✅ (15)     | ❌      | ❌       |
| CAINTA      | ✅       | ❌          | ❌      | ❌       |
| ANGONO      | ✅       | ❌          | ❌      | ❌       |
| TAYTAY      | ✅       | ❌          | ❌      | ❌       |

---

## 📂 File Locations

```
d:\CleanThesis\DONT DEELTE THESE FILES\
├── MODEL TRAINING Angono Safe Save Before AR IMPLEMENTATION copy 4.ipynb  # Training
├── saved_models_v2/
│   └── Latest_FINALIZED_barangay_models_20251228_000045/  # Model storage
│       ├── CITY_OF_ANTIPOLO/
│       ├── CAINTA/
│       ├── ANGONO/
│       └── TAYTAY/
└── PROTOTYPE_v2/
    ├── backend/
    │   └── main.py  # FastAPI server
    └── frontend/
        └── src/
            └── components/
                └── ModelInsights.js  # React UI
```

---

## 🚀 Quick Start for AI

1. **Modifying Training:** Edit notebook → Update return values → Re-export metadata
2. **Modifying Backend:** Update `add_antipolo_vaccination_campaigns()` → Match notebook exactly
3. **Modifying Frontend:** Change chart configs in ModelInsights.js → Update data parsing

**Critical Rule:** Backend `add_antipolo_vaccination_campaigns()` must return EXACT same columns as training notebook registers with `model.add_future_regressor()`
