# 🎯 RABIES FORECASTING BACKEND - COMPREHENSIVE DOCUMENTATION

**Version:** 2.1.0  
**Author:** Rabies Forecasting System  
**Date:** December 23, 2025

---

## 📚 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Model Prediction Flow](#model-prediction-flow)
5. [Feature Engineering Pipeline](#feature-engineering-pipeline)
6. [Model Interpretability System](#model-interpretability-system)
7. [Backend-to-Frontend Data Flow](#backend-to-frontend-data-flow)
8. [Troubleshooting Guide](#troubleshooting-guide)

---

## 📖 SYSTEM OVERVIEW

### What is This Backend?

This is a **FastAPI-based REST API** that serves rabies forecasting predictions using **pre-trained NeuralProphet + XGBoost hybrid models**. The backend:

- ✅ Loads saved `.pkl` model files on startup
- ✅ Provides predictions for next month and future 8 months
- ✅ Calculates risk levels (HIGH/MEDIUM/LOW)
- ✅ Decomposes predictions into trend, seasonality, and holiday effects
- ✅ Generates CSV and PDF reports

### Key Technologies

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **NeuralProphet** | Time series baseline prediction |
| **XGBoost** | Residual correction (hybrid model) |
| **Pandas** | Data manipulation |
| **NumPy** | Numerical operations |
| **ReportLab** | PDF generation |
| **Uvicorn** | ASGI server |

---

## 🏗️ ARCHITECTURE

### Directory Structure

```
PROTOTYPE_v2/backend/
│
├── main.py                          # Main FastAPI application
├── test_seasonal_features.py        # Feature validation script
├── requirements.txt                 # Python dependencies
│
└── venv/                            # Virtual environment
```

### Model Storage

```
saved_models_v2/Latest_FINALIZED_barangay_models_20251223_201700/
│
├── ANGONO/
│   ├── Bagumbayan_TEST_ONLY.pkl
│   ├── Kalayaan_TEST_ONLY.pkl
│   └── ... (10 barangays)
│
├── CAINTA/
│   ├── San_Roque_TEST_ONLY.pkl
│   ├── Santa_Rosa_TEST_ONLY.pkl
│   └── ... (7 barangays)
│
├── CITY OF ANTIPOLO/
│   └── ... (18 barangays)
│
└── TAYTAY/
    └── ... (7 barangays)
```

### Model File Structure (`.pkl`)

Each `.pkl` file contains a **dictionary** with:

```python
{
    'np_model': <NeuralProphet object>,        # Time series model
    'xgb_model': <XGBoost object>,             # Residual correction model
    'municipality': 'ANGONO',                  # Municipality name
    'barangay': 'Bagumbayan',                  # Barangay name
    'training_end': Timestamp('2024-12-31'),   # Last training date
    'validation_end': Timestamp('2025-06-30'), # Last validation date
    
    # Historical data for visualization
    'train_dates': [...],                      # Training dates
    'train_actuals': [...],                    # Training actual values
    'train_predictions': [...],                # Training predictions
    'dates': [...],                            # Validation dates
    'actuals': [...],                          # Validation actual values
    'predictions': [...],                      # Validation predictions
    
    # Model metrics
    'hybrid_mae': 1.23,                        # Mean Absolute Error
    'hybrid_rmse': 1.89,                       # Root Mean Squared Error
    'hybrid_mase': 0.87,                       # Mean Absolute Scaled Error
    
    # Regressor metadata (for CAINTA/ANGONO)
    'regressors': {
        'seasonal': ['may_peak', 'low_season', ...],
        'weather': [],
        'vaccination': []
    }
}
```

---

## 🔌 API ENDPOINTS REFERENCE

### 1. **Health Check**

```http
GET /
```

**Purpose:** Check if API is running and how many models loaded.

**Response:**
```json
{
  "status": "operational",
  "version": "2.1.0",
  "models_loaded": 42,
  "features": ["forecasting", "risk_assessment", "model_interpretability"]
}
```

---

### 2. **Get All Municipalities**

```http
GET /api/municipalities
```

**Purpose:** List all municipalities with barangay summaries and risk levels.

**What It Does:**
1. Loops through ALL loaded models
2. Calculates risk level for each barangay (compares past 8 months vs future 8 months)
3. Groups barangays by municipality
4. Returns sorted list (highest risk first)

**Response Example:**
```json
{
  "success": true,
  "municipalities": [
    {
      "municipality": "ANGONO",
      "total_barangays": 10,
      "avg_mae": 1.45,
      "risk_summary": {
        "HIGH": 3,
        "MEDIUM": 5,
        "LOW": 2
      },
      "barangays": [
        {
          "name": "Bagumbayan",
          "mae": 1.23,
          "predicted_next": 5.6,
          "risk_level": "HIGH",
          "risk_color": "#d32f2f",
          "risk_icon": "🔴"
        },
        ...
      ]
    }
  ]
}
```

**Frontend Uses This For:**
- `MunicipalityList.jsx` displays cards with barangay lists
- Risk badges showing 🔴 HIGH, 🟡 MEDIUM, 🟢 LOW counts

---

### 3. **Get Barangay Details**

```http
GET /api/barangay/{municipality}/{barangay}
```

**Example:** `/api/barangay/ANGONO/Bagumbayan`

**Purpose:** Get detailed historical data and metrics for ONE barangay.

**What It Does:**
1. Finds the model by key: `"ANGONO_Bagumbayan"`
2. Extracts metrics (MAE, RMSE, MASE)
3. Extracts historical training data (for blue line in chart)
4. Extracts historical validation data (for green line in chart)
5. Predicts next month (single value)

**Response Example:**
```json
{
  "success": true,
  "barangay": {
    "municipality": "ANGONO",
    "barangay": "Bagumbayan",
    "metrics": {
      "mae": 1.23,
      "rmse": 1.89,
      "mase": 0.87
    },
    "training_data": [
      {"date": "2022-01", "actual": 3, "predicted": 2.8},
      {"date": "2022-02", "actual": 5, "predicted": 4.9},
      ...
    ],
    "validation_data": [
      {"date": "2024-01", "actual": 4, "predicted": 4.2},
      {"date": "2024-02", "actual": 6, "predicted": 5.8},
      ...
    ],
    "next_month_prediction": 5.6,
    "has_chart_data": true
  }
}
```

**Frontend Uses This For:**
- `BarangayDetails.jsx` displays metrics
- `BarangayChart.jsx` plots historical data (blue + green lines)
- Shows "Next Month Prediction: 5.6 cases"

---

### 4. **Get Future Forecast (8 Months)**

```http
GET /api/forecast/{municipality}/{barangay}?months=8
```

**Example:** `/api/forecast/ANGONO/Bagumbayan?months=8`

**Purpose:** Predict future 8 months (or more).

**What It Does:**
1. Calls `predict_future_months(model_data, months_ahead=8)`
2. Returns list of monthly predictions

**Response Example:**
```json
{
  "success": true,
  "forecast": {
    "municipality": "ANGONO",
    "barangay": "Bagumbayan",
    "validation_end": "2025-06",
    "forecast_start": "2025-07",
    "forecast_end": "2026-02",
    "predictions": [
      {"date": "2025-07", "predicted": 5.2},
      {"date": "2025-08", "predicted": 6.1},
      {"date": "2025-09", "predicted": 4.8},
      ...
    ]
  }
}
```

**Frontend Uses This For:**
- `BarangayDetails.jsx` displays forecast grid (monthly predictions)
- `BarangayChart.jsx` adds orange forecast line
- Risk alert calculation (compares future avg vs historical avg)

---

### 5. **Get Model Interpretability**

```http
GET /api/interpretability/{municipality}/{barangay}
```

**Example:** `/api/interpretability/ANGONO/Bagumbayan`

**Purpose:** Decompose model predictions into understandable components.

**What It Does:**
1. Calls `extract_model_components(model_data)`
2. Uses NeuralProphet to decompose historical predictions into:
   - **Trend:** Long-term direction (upward/downward)
   - **Seasonality:** Yearly repeating patterns (high months/low months)
   - **Holidays:** Philippine holiday effects (New Year, Christmas, etc.)
3. Extracts XGBoost feature importance (which factors matter most)

**Response Example:**
```json
{
  "success": true,
  "interpretability": {
    "municipality": "ANGONO",
    "barangay": "Bagumbayan",
    
    "trend": {
      "dates": ["2022-01", "2022-02", ...],
      "values": [2.5, 2.6, 2.7, ...],
      "description": "Long-term direction of rabies cases"
    },
    
    "seasonality": {
      "dates": ["2022-01", "2022-02", ...],
      "values": [0.5, -0.3, 1.2, ...],
      "description": "Recurring yearly patterns"
    },
    
    "holidays": {
      "dates": ["2022-01", "2022-02", ...],
      "values": [0.8, 0.0, 0.0, ...],
      "description": "Philippine public holiday effects",
      "significant_effects": [
        {"date": "2023-01", "holiday": "New Year", "effect": 1.2}
      ],
      "has_holidays": true
    },
    
    "seasonal_regressors": {
      "data": {
        "may_peak": [0, 0, 1, ...],
        "low_season": [1, 1, 0, ...]
      },
      "description": "Custom seasonal patterns specific to this municipality",
      "columns": ["may_peak", "low_season", "spring_ramp", ...]
    },
    
    "feature_importance": {
      "features": [
        {
          "feature": "np_prediction",
          "importance": 0.3245,
          "percentage": 32.45
        },
        {
          "feature": "Month",
          "importance": 0.1823,
          "percentage": 18.23
        },
        ...
      ],
      "top_3_features": [...]
    }
  }
}
```

**Frontend Uses This For:**
- `ModelInsights.jsx` displays decomposition charts
- Shows trend line, seasonality line, holiday effects
- Shows feature importance bar chart
- Explains WHY predictions are made (not black box!)

---

### 6. **Download CSV Report**

```http
GET /api/report/csv/{municipality}/{barangay}
```

**Purpose:** Generate downloadable CSV with 180-day forecast.

**Returns:** CSV file with columns:
- Date
- Predicted_Cases
- Risk_Level
- Trend_Component
- Seasonal_Component
- Holiday_Effect

---

### 7. **Download PDF Report**

```http
GET /api/report/pdf/{municipality}/{barangay}
```

**Purpose:** Generate comprehensive PDF report with:
- Executive summary
- 180-day forecast visualization
- Barangay comparison table (ranking)
- Recommendations

---

### 8. **Download Insights PDF**

```http
GET /api/report/insights-pdf/{municipality}/{barangay}
```

**Purpose:** Generate detailed interpretability PDF with:
- Trend/seasonality/holiday decomposition charts
- Feature importance analysis
- Model configuration details

---

## 🎯 MODEL PREDICTION FLOW

### Step-by-Step: How Prediction Works

#### **Phase 1: Model Loading (On Startup)**

```python
# main.py line ~680
MODELS = load_all_models()
```

**What Happens:**
1. Reads `MODEL_DIR` path
2. Loops through municipality folders (ANGONO, CAINTA, etc.)
3. For each `.pkl` file:
   - Unpickles the model dictionary
   - Stores in `MODELS` dict with key `"MUNICIPALITY_BARANGAY"`
4. Prints: `✅ Loaded 42 barangay models`

**Critical:** Models are loaded ONCE on startup, kept in memory for fast access.

---

#### **Phase 2: Single Month Prediction**

```python
def predict_next_month(model_data):
```

**Input:** `model_data` (dictionary from `.pkl` file)

**Output:** Single float (predicted cases for next month)

**Step-by-Step Process:**

```python
# 1. Extract models and metadata
np_model = model_data['np_model']        # NeuralProphet
xgb_model = model_data['xgb_model']      # XGBoost
training_end = model_data['training_end'] # Last date in training
municipality = model_data['municipality'] # e.g., "ANGONO"

# 2. Generate next month date
next_month = training_end + pd.DateOffset(months=1)
# Example: If training_end = 2025-06-30, next_month = 2025-07-01

# 3. Create prediction DataFrame (NeuralProphet format)
future_df = pd.DataFrame({
    'ds': [next_month],  # Date column (required by NeuralProphet)
    'y': [0]             # Placeholder (not used in prediction)
})

# 4. ADD MUNICIPALITY-SPECIFIC SEASONAL FEATURES
# 🚨 CRITICAL STEP! Models were trained WITH these features,
#    so prediction MUST include them too!
if municipality == "CAINTA":
    future_df = add_cainta_seasonal_features(future_df)
    # Adds: may_peak, low_season, spring_ramp, january_holiday, post_may_decline
    
elif municipality == "ANGONO":
    future_df = add_angono_seasonal_features(future_df)
    # Adds: high_season, july_dip, august_rise, low_season, post_april_2024

# Example result for July (month=7) in ANGONO:
# ds         | y | high_season | july_dip | august_rise | low_season | post_april_2024
# 2025-07-01 | 0 | 0           | 1        | 0           | 0          | 1

# 5. Get NeuralProphet baseline prediction
np_forecast = np_model.predict(future_df)
np_baseline = np_forecast['yhat1'].values[0]
# Example: np_baseline = 4.8

# 6. Prepare XGBoost features (EXACT 11 features in training order)
X_future = pd.DataFrame({
    'Year': [next_month.year],              # 2025
    'Month': [next_month.month],            # 7
    'lag_1': [0],                           # Previous month (unknown)
    'lag_2': [0],                           # 2 months ago (unknown)
    'rolling_mean_3': [0],                  # 3-month average (unknown)
    'rolling_std_3': [0],                   # 3-month std dev (unknown)
    'lag_12': [0],                          # Same month last year (unknown)
    'month_sin': [np.sin(2 * np.pi * 7 / 12)],  # Seasonal sine
    'month_cos': [np.cos(2 * np.pi * 7 / 12)],  # Seasonal cosine
    'rate_of_change_1': [0],                # Rate of change (unknown)
    'np_prediction': [np_baseline]          # NeuralProphet output (4.8)
})

# 7. Get XGBoost residual correction
xgb_residual = xgb_model.predict(X_future)[0]
# Example: xgb_residual = +0.8 (corrects NeuralProphet up)

# 8. Combine predictions (hybrid approach)
hybrid_pred = max(0, np_baseline + xgb_residual)
# Example: 4.8 + 0.8 = 5.6 cases

# 9. Return final prediction
return hybrid_pred  # 5.6
```

**Key Points:**
- ✅ **NeuralProphet** captures trend, seasonality, holidays
- ✅ **XGBoost** corrects systematic errors in NeuralProphet
- ✅ **Seasonal features** MUST be added for CAINTA/ANGONO
- ✅ **Lag features** are set to 0 (unknown future values)
- ✅ **np_prediction** is the bridge between two models

---

#### **Phase 3: Multi-Month Prediction**

```python
def predict_future_months(model_data, months_ahead=12):
```

**Input:** 
- `model_data`: Model dictionary
- `months_ahead`: Number of months to predict (default 12)

**Output:** List of predictions:
```python
[
    {'date': '2025-07', 'predicted': 5.2},
    {'date': '2025-08', 'predicted': 6.1},
    ...
]
```

**Process:**

```python
# 1. Generate multiple future dates
start_date = validation_end + pd.DateOffset(months=1)
future_dates = pd.date_range(start=start_date, periods=months_ahead, freq='MS')
# MS = Month Start: [2025-07-01, 2025-08-01, 2025-09-01, ...]

# 2. Create template DataFrame
future_df = pd.DataFrame({
    'ds': future_dates,
    'y': [0] * months_ahead
})

# 3. Add seasonal features (SAME as single prediction)
if municipality == "CAINTA":
    future_df = add_cainta_seasonal_features(future_df)
elif municipality == "ANGONO":
    future_df = add_angono_seasonal_features(future_df)

# 4. Get NeuralProphet predictions for ALL months at once
np_forecast = np_model.predict(future_df)
np_predictions = np_forecast['yhat1'].values
# [4.8, 5.2, 4.9, 5.5, ...]

# 5. Loop through each month for XGBoost correction
predictions = []
for i, future_date in enumerate(future_dates):
    # Prepare XGBoost features
    X_future = pd.DataFrame({
        'Year': [future_date.year],
        'Month': [future_date.month],
        'lag_1': [0],
        'lag_2': [0],
        'rolling_mean_3': [0],
        'rolling_std_3': [0],
        'lag_12': [0],
        'month_sin': [np.sin(2 * np.pi * future_date.month / 12)],
        'month_cos': [np.cos(2 * np.pi * future_date.month / 12)],
        'rate_of_change_1': [0],
        'np_prediction': [np_predictions[i]]  # Use NP prediction for this month
    })
    
    # Get XGBoost correction
    xgb_residual = xgb_model.predict(X_future)[0]
    
    # Hybrid prediction
    hybrid_pred = max(0, float(np_predictions[i] + xgb_residual))
    
    predictions.append({
        'date': future_date.strftime('%Y-%m'),
        'predicted': round(hybrid_pred, 1)
    })

return predictions
```

---

## 🔧 FEATURE ENGINEERING PIPELINE

### What is Feature Engineering?

**Feature engineering** is the process of transforming raw data into meaningful inputs that the model can understand.

### Two Types of Features

#### **1. Seasonal Features (CAINTA & ANGONO only)**

These are **binary flags** (0 or 1) that capture municipality-specific patterns.

**CAINTA Seasonal Features:**

```python
def add_cainta_seasonal_features(df):
    # MAY PEAK: May is consistently highest across all years
    df['may_peak'] = (df['ds'].dt.month == 5).astype(int)
    
    # LOW SEASON: Jan-Feb-March-April consistently lowest
    df['low_season'] = ((df['ds'].dt.month >= 1) & (df['ds'].dt.month <= 4)).astype(int)
    
    # SPRING RAMP-UP: March-April-May increasing pattern
    df['spring_ramp'] = ((df['ds'].dt.month >= 3) & (df['ds'].dt.month <= 5)).astype(int)
    
    # HOLIDAY EFFECT: January specifically (New Year impact)
    df['january_holiday'] = (df['ds'].dt.month == 1).astype(int)
    
    # POST-MAY DECLINE: June onwards typically lower than May
    df['post_may_decline'] = ((df['ds'].dt.month >= 6) & (df['ds'].dt.month <= 12)).astype(int)
    
    return df
```

**Example Output:**

| ds         | may_peak | low_season | spring_ramp | january_holiday | post_may_decline |
|------------|----------|------------|-------------|-----------------|------------------|
| 2025-01-01 | 0        | 1          | 0           | 1               | 0                |
| 2025-05-01 | 1        | 0          | 1           | 0               | 0                |
| 2025-07-01 | 0        | 0          | 0           | 0               | 1                |

**ANGONO Seasonal Features:**

```python
def add_angono_seasonal_features(df):
    # HIGH SEASON: April-May-June (consistently high across 2022-2025)
    df['high_season'] = df['ds'].dt.month.isin([4, 5, 6]).astype(int)
    
    # JULY DIP: Always drops after high season
    df['july_dip'] = (df['ds'].dt.month == 7).astype(int)
    
    # AUGUST RISE: Increases again after July dip
    df['august_rise'] = (df['ds'].dt.month == 8).astype(int)
    
    # LOW SEASON: December-January (consistently lowest)
    df['low_season'] = df['ds'].dt.month.isin([12, 1]).astype(int)
    
    # POST-APRIL 2024 REGIME: Higher volatility period
    df['post_april_2024'] = (df['ds'] >= pd.Timestamp('2024-04-01')).astype(int)
    
    return df
```

**Why These Features?**
- 📊 CAINTA and ANGONO have **unique seasonal patterns**
- 🚨 **CRITICAL:** Models were trained WITH these features
- ❌ **Without them:** Prediction will FAIL with "Unexpected column" error
- ✅ **With them:** Model understands seasonal context

---

#### **2. XGBoost Engineered Features**

These are **numeric features** derived from the data and NeuralProphet output.

**Feature List (11 total):**

| Feature | Description | Example Value |
|---------|-------------|---------------|
| `Year` | Year (2025, 2026, etc.) | 2025 |
| `Month` | Month number (1-12) | 7 |
| `lag_1` | Previous month cases | 0 (unknown) |
| `lag_2` | 2 months ago cases | 0 (unknown) |
| `rolling_mean_3` | 3-month average | 0 (unknown) |
| `rolling_std_3` | 3-month std dev | 0 (unknown) |
| `lag_12` | Same month last year | 0 (unknown) |
| `month_sin` | Seasonal sine wave | 0.866 |
| `month_cos` | Seasonal cosine wave | 0.5 |
| `rate_of_change_1` | Case change rate | 0 (unknown) |
| `np_prediction` | NeuralProphet output | 4.8 |

**Why Lag Features are 0?**
- 🔮 We're predicting the **future**
- ❓ We don't know future case counts yet
- 🧠 XGBoost learned to use `np_prediction` instead
- ✅ `np_prediction` carries all the context from NeuralProphet

**Feature Importance Ranking:**
```
1. np_prediction      (32.45%) ← Most important!
2. Month              (18.23%)
3. lag_1              (12.87%)
4. rolling_mean_3     (10.54%)
5. lag_12             (8.91%)
...
```

---

### When to Add Features?

**Training (Jupyter Notebook):**
```python
# DURING MODEL TRAINING
if municipality == "ANGONO":
    bgy_data = add_angono_seasonal_features(bgy_data)
    # Add features BEFORE fitting NeuralProphet
```

**Prediction (Backend):**
```python
# DURING PREDICTION
if municipality == "ANGONO":
    future_df = add_angono_seasonal_features(future_df)
    # Add features BEFORE calling np_model.predict()
```

**⚠️ RULE:** Training features MUST match prediction features!

---

## 🔍 MODEL INTERPRETABILITY SYSTEM

### What is Interpretability?

**Interpretability** means understanding **WHY** the model made a specific prediction, not just **WHAT** it predicted.

### Component Extraction Process

```python
def extract_model_components(model_data):
```

**Step-by-Step:**

#### **Step 1: Collect Historical Data**

```python
# Get all historical dates and actual values
dates_list = []
actuals_list = []

# Training data (2022-2024)
if 'train_dates' in model_data:
    dates_list.extend(model_data['train_dates'])
    actuals_list.extend(model_data['train_actuals'])

# Validation data (2024-2025)
if 'dates' in model_data:
    dates_list.extend(model_data['dates'])
    actuals_list.extend(model_data['actuals'])

# Create DataFrame
df_components = pd.DataFrame({
    'ds': dates_list,
    'y': actuals_list
})
```

**Result:** DataFrame with ALL historical data (36 months)

---

#### **Step 2: Add Seasonal Features (CAINTA/ANGONO)**

```python
municipality = model_data.get('municipality', '')

# 🔥 CRITICAL: Add same features used in training
if municipality == "CAINTA":
    df_components = add_cainta_seasonal_features(df_components)
elif municipality == "ANGONO":
    df_components = add_angono_seasonal_features(df_components)
```

**Why?**
- NeuralProphet was trained WITH seasonal features
- Without them, `.predict()` will fail
- Same principle as prediction!

---

#### **Step 3: Get NeuralProphet Decomposition**

```python
# NeuralProphet internally decomposes predictions
forecast_df = np_model.predict(df_components)

# Forecast columns available:
# - 'yhat1': Overall prediction
# - 'trend': Long-term trend component
# - 'season_yearly': Yearly seasonality
# - 'events_additive': Holiday effects
# - 'future_regressor_X': Custom regressor contributions
```

**NeuralProphet Magic:**
- Automatically decomposes predictions into interpretable parts
- Separates trend from seasonality from holidays
- Each component is independent

---

#### **Step 4: Extract Components**

```python
components = {
    'trend': [],
    'yearly_seasonality': [],
    'holidays': [],
    'seasonal_regressors': {},
    'dates': []
}

for i in range(len(df_components)):
    date = df_components['ds'].iloc[i]
    components['dates'].append(date.strftime('%Y-%m'))
    
    # Trend
    if 'trend' in forecast_df.columns:
        components['trend'].append(float(forecast_df['trend'].iloc[i]))
    
    # Seasonality
    if 'season_yearly' in forecast_df.columns:
        components['yearly_seasonality'].append(float(forecast_df['season_yearly'].iloc[i]))
    
    # Holidays
    if 'events_additive' in forecast_df.columns:
        components['holidays'].append(float(forecast_df['events_additive'].iloc[i]))
    
    # Seasonal regressors (CAINTA/ANGONO)
    for col in seasonal_cols:
        regressor_col = f'future_regressor_{col}'
        if regressor_col in forecast_df.columns:
            components['seasonal_regressors'][col].append(
                float(forecast_df[regressor_col].iloc[i])
            )
```

**Result:**
```python
{
    'trend': [2.5, 2.6, 2.7, 2.8, ...],
    'yearly_seasonality': [0.5, -0.3, 1.2, 0.8, ...],
    'holidays': [0.8, 0.0, 0.0, 1.5, ...],
    'dates': ['2022-01', '2022-02', '2022-03', ...]
}
```

---

#### **Step 5: XGBoost Feature Importance**

```python
importance_scores = xgb_model.feature_importances_
# [0.3245, 0.1823, 0.1287, ...]

feature_importance = [
    {
        'feature': 'np_prediction',
        'importance': 0.3245,
        'percentage': 32.45
    },
    ...
]
```

**Interpretation:**
- `np_prediction` (32.45%) = NeuralProphet baseline is most important
- `Month` (18.23%) = Time of year matters
- `lag_1` (12.87%) = Recent history matters

---

### What Does Each Component Mean?

#### **Trend**
```
[2.5, 2.6, 2.7, 2.8, 2.9, ...]
```
- **Meaning:** Long-term direction of rabies cases
- **Example:** Increasing trend means cases are slowly rising over years
- **Causes:** Population growth, dog ownership increase, policy changes

#### **Seasonality**
```
[0.5, -0.3, 1.2, 0.8, -0.5, ...]
```
- **Meaning:** Repeating yearly pattern
- **Example:** High in summer, low in winter
- **Causes:** Weather, breeding cycles, human behavior

#### **Holidays**
```
[0.8, 0.0, 0.0, 1.5, 0.0, ...]
```
- **Meaning:** Spike/dip during Philippine holidays
- **Example:** +1.5 cases during Christmas (more outdoor activity)
- **Causes:** Holiday behavior changes

#### **Seasonal Regressors (CAINTA/ANGONO)**
```
{
    'may_peak': [0, 0, 1, 0, 0, ...],
    'high_season': [0, 1, 1, 1, 0, ...]
}
```
- **Meaning:** Custom municipality patterns
- **Example:** ANGONO has high cases in April-May-June every year
- **Causes:** Local factors (environment, events, population)

---

## 🔄 BACKEND-TO-FRONTEND DATA FLOW

### Complete Journey of a Prediction

#### **Scenario:** User clicks on "Bagumbayan, ANGONO" barangay

---

### **Step 1: Frontend Request (MunicipalityList.jsx)**

```javascript
// User clicks on barangay
const handleBarangayClick = (municipality, barangay) => {
    navigate(`/forecasting/${municipality}/${barangay}`);
};
```

**Result:** URL changes to `/forecasting/ANGONO/Bagumbayan`

---

### **Step 2: Load Barangay Details (BarangayDetails.jsx)**

```javascript
const { municipality, barangay } = useParams();
// municipality = "ANGONO"
// barangay = "Bagumbayan"

// Custom hook fetches data
const { barangayData, loading } = useBarangayData(municipality, barangay);
```

**useBarangayData Hook:**
```javascript
const [data, setData] = useState(null);

useEffect(() => {
    fetch(`http://localhost:8000/api/barangay/${municipality}/${barangay}`)
        .then(res => res.json())
        .then(result => setData(result.barangay));
}, [municipality, barangay]);
```

**Backend Receives:**
```http
GET /api/barangay/ANGONO/Bagumbayan
```

---

### **Step 3: Backend Processes Request (main.py)**

```python
@app.get("/api/barangay/{municipality}/{barangay}")
async def get_barangay_details(municipality: str, barangay: str):
    # 1. Find model
    key = f"{municipality}_{barangay}"  # "ANGONO_Bagumbayan"
    model_data = MODELS[key]
    
    # 2. Extract metrics
    metrics = {
        'mae': model_data['hybrid_mae'],
        'rmse': model_data['hybrid_rmse'],
        'mase': model_data['hybrid_mase']
    }
    
    # 3. Extract historical training data
    train_data = [
        {
            'date': model_data['train_dates'][i],
            'actual': model_data['train_actuals'][i],
            'predicted': model_data['train_predictions'][i]
        }
        for i in range(len(model_data['train_dates']))
    ]
    
    # 4. Extract historical validation data
    val_data = [
        {
            'date': model_data['dates'][i],
            'actual': model_data['actuals'][i],
            'predicted': model_data['predictions'][i]
        }
        for i in range(len(model_data['dates']))
    ]
    
    # 5. Predict next month
    next_pred = predict_next_month(model_data)
    # Calls add_angono_seasonal_features() internally!
    
    # 6. Return response
    return {
        'success': True,
        'barangay': {
            'municipality': municipality,
            'barangay': barangay,
            'metrics': metrics,
            'training_data': train_data,
            'validation_data': val_data,
            'next_month_prediction': next_pred,
            'has_chart_data': True
        }
    }
```

---

### **Step 4: Frontend Displays Data (BarangayDetails.jsx)**

```javascript
// Display metrics
<div className="metrics-grid">
  <div className="metric">
    <span className="metric-label">MAE</span>
    <span className="metric-value">{barangayData.metrics.mae}</span>
  </div>
  <div className="metric">
    <span className="metric-label">RMSE</span>
    <span className="metric-value">{barangayData.metrics.rmse}</span>
  </div>
  <div className="metric">
    <span className="metric-label">MASE</span>
    <span className="metric-value">{barangayData.metrics.mase}</span>
  </div>
</div>

// Display next month prediction
{barangayData.next_month_prediction && (
  <div className="next-prediction">
    <strong>Next Month Prediction:</strong> {barangayData.next_month_prediction} cases
  </div>
)}

// Pass data to chart component
<BarangayChart
  trainingData={barangayData.training_data}
  validationData={barangayData.validation_data}
  forecastData={null}  // Not loaded yet
/>
```

---

### **Step 5: User Clicks "Show Future Forecast" Button**

```javascript
const handleForecastClick = async () => {
    await fetchForecast();  // Custom hook
    setShowForecast(true);
};
```

**useForecast Hook:**
```javascript
const fetchForecast = async () => {
    const response = await fetch(
        `http://localhost:8000/api/forecast/${municipality}/${barangay}?months=8`
    );
    const result = await response.json();
    setForecastData(result.forecast);
};
```

**Backend Receives:**
```http
GET /api/forecast/ANGONO/Bagumbayan?months=8
```

---

### **Step 6: Backend Generates Forecast**

```python
@app.get("/api/forecast/{municipality}/{barangay}")
async def get_future_forecast(municipality: str, barangay: str, months: int = 8):
    model_data = MODELS[f"{municipality}_{barangay}"]
    
    # Call multi-month prediction
    future_predictions = predict_future_months(model_data, months_ahead=months)
    # [
    #     {'date': '2025-07', 'predicted': 5.2},
    #     {'date': '2025-08', 'predicted': 6.1},
    #     ...
    # ]
    
    return {
        'success': True,
        'forecast': {
            'municipality': municipality,
            'barangay': barangay,
            'predictions': future_predictions
        }
    }
```

---

### **Step 7: Frontend Displays Forecast**

```javascript
// Display forecast grid
<div className="forecast-grid">
  {forecastData.predictions.map((pred, idx) => (
    <div key={idx} className="forecast-item">
      <span className="forecast-date">{pred.date}</span>
      <span className="forecast-value">{pred.predicted} cases</span>
    </div>
  ))}
</div>

// Update chart with forecast line
<BarangayChart
  trainingData={barangayData.training_data}
  validationData={barangayData.validation_data}
  forecastData={forecastData.predictions}  // Orange line added!
/>
```

---

### **Step 8: User Clicks "Model Insights" Tab**

```javascript
const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'insights' && !interpretabilityData) {
        fetchInterpretability();  // Lazy load
    }
};
```

**useInterpretability Hook:**
```javascript
const fetchInterpretability = async () => {
    const response = await fetch(
        `http://localhost:8000/api/interpretability/${municipality}/${barangay}`
    );
    const result = await response.json();
    setInterpretabilityData(result.interpretability);
};
```

**Backend Receives:**
```http
GET /api/interpretability/ANGONO/Bagumbayan
```

---

### **Step 9: Backend Extracts Components**

```python
@app.get("/api/interpretability/{municipality}/{barangay}")
async def get_model_interpretability(municipality: str, barangay: str):
    model_data = MODELS[f"{municipality}_{barangay}"]
    
    # Extract all components
    interpretability_data = extract_model_components(model_data)
    # Internally calls add_angono_seasonal_features() for decomposition!
    
    return {
        'success': True,
        'interpretability': {
            'municipality': municipality,
            'barangay': barangay,
            'trend': {
                'dates': [...],
                'values': [...]
            },
            'seasonality': {
                'dates': [...],
                'values': [...]
            },
            'holidays': {
                'dates': [...],
                'values': [...]
            },
            'seasonal_regressors': {
                'data': {
                    'may_peak': [...],
                    'high_season': [...]
                }
            },
            'feature_importance': {
                'features': [...]
            }
        }
    }
```

---

### **Step 10: Frontend Displays Insights (ModelInsights.jsx)**

```javascript
// Trend chart
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={trendData}>
    <XAxis dataKey="date" />
    <YAxis />
    <Tooltip />
    <Line type="monotone" dataKey="value" stroke="#3498db" />
  </LineChart>
</ResponsiveContainer>

// Seasonality chart
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={seasonalityData}>
    <Line type="monotone" dataKey="value" stroke="#e74c3c" />
  </LineChart>
</ResponsiveContainer>

// Holiday effects chart
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={holidayData}>
    <Line type="monotone" dataKey="value" stroke="#f39c12" />
  </LineChart>
</ResponsiveContainer>

// Feature importance bar chart
<ResponsiveContainer width="100%" height={400}>
  <BarChart data={featureImportance}>
    <XAxis dataKey="feature" />
    <YAxis />
    <Bar dataKey="percentage" fill="#2ecc71" />
  </BarChart>
</ResponsiveContainer>
```

---

## 📊 COMPLETE DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  MunicipalityList.jsx → BarangayDetails.jsx → ModelInsights.jsx│
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ HTTP Requests
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ GET /api/municipalities                                   │  │
│  │ → Loop all models → calculate_risk_level()               │  │
│  │ → Return: Municipality list with barangays + risk        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ GET /api/barangay/{mun}/{brgy}                           │  │
│  │ → Load model from MODELS dict                            │  │
│  │ → Extract metrics, historical data                       │  │
│  │ → predict_next_month() → add_seasonal_features()         │  │
│  │ → Return: Metrics + train/val data + next prediction     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ GET /api/forecast/{mun}/{brgy}                           │  │
│  │ → predict_future_months(model, 8)                        │  │
│  │   → Add seasonal features                                │  │
│  │   → NeuralProphet batch predict                          │  │
│  │   → XGBoost loop corrections                             │  │
│  │ → Return: 8 monthly predictions                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ GET /api/interpretability/{mun}/{brgy}                   │  │
│  │ → extract_model_components(model)                        │  │
│  │   → Add seasonal features                                │  │
│  │   → NeuralProphet decompose                              │  │
│  │   → Extract trend/seasonality/holidays                   │  │
│  │   → XGBoost feature importance                           │  │
│  │ → Return: All components + importance                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Loads on startup
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SAVED MODELS (.pkl)                          │
│  saved_models_v2/Latest_FINALIZED.../                           │
│  ├── ANGONO/                                                    │
│  │   ├── Bagumbayan_TEST_ONLY.pkl                              │
│  │   │   ├── np_model (NeuralProphet)                          │
│  │   │   ├── xgb_model (XGBoost)                               │
│  │   │   ├── Historical data (train/val)                       │
│  │   │   └── Metrics (MAE, RMSE, MASE)                         │
│  │   └── ...                                                    │
│  ├── CAINTA/                                                    │
│  ├── CITY OF ANTIPOLO/                                          │
│  └── TAYTAY/                                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚨 TROUBLESHOOTING GUIDE

### Problem 1: "Unexpected column may_peak in data"

**Symptoms:**
- Prediction fails
- Error mentions column name (e.g., `may_peak`, `high_season`)

**Cause:**
- Model was trained WITH seasonal features
- Prediction is NOT adding them

**Solution:**
```python
# Check municipality and add features
if municipality == "CAINTA":
    future_df = add_cainta_seasonal_features(future_df)
elif municipality == "ANGONO":
    future_df = add_angono_seasonal_features(future_df)
```

---

### Problem 2: "Model Insights" fails but Forecast works

**Symptoms:**
- Forecast tab works fine
- Model Insights tab shows error or blank

**Cause:**
- `extract_model_components()` not adding seasonal features

**Solution:**
```python
# In extract_model_components() function
municipality = model_data.get('municipality', '')

# BEFORE calling np_model.predict()
if municipality == "CAINTA":
    df_components = add_cainta_seasonal_features(df_components)
elif municipality == "ANGONO":
    df_components = add_angono_seasonal_features(df_components)
```

---

### Problem 3: Model loading fails on startup

**Symptoms:**
```
KeyboardInterrupt
Traceback (most recent call last):
  File "main.py", line 681, in <module>
    MODELS = load_all_models()
```

**Cause:**
- Model files too large
- Wrong MODEL_DIR path
- Corrupted .pkl files

**Solution:**
1. Check MODEL_DIR path:
```python
MODEL_DIR = "../../saved_models_v2/Latest_FINALIZED_barangay_models_20251223_201700"
```

2. Verify directory exists:
```bash
ls -la ../../saved_models_v2/
```

3. Test loading ONE model:
```python
import pickle
with open('path/to/model.pkl', 'rb') as f:
    model = pickle.load(f)
    print(model.keys())
```

---

### Problem 4: Frontend shows "Unpredictable" (grey)

**Symptoms:**
- Some barangays show grey color
- No risk icon (🔴🟡🟢)

**Cause:**
- `predict_next_month()` returning `None`
- Prediction exception caught silently

**Solution:**
1. Check backend terminal logs
2. Look for error messages
3. Verify seasonal features are added

---

### Problem 5: Risk level calculation wrong

**Symptoms:**
- All barangays showing same risk level
- Risk levels don't make sense

**Cause:**
- `calculate_risk_level()` logic error
- Thresholds too strict/loose

**Solution:**
```python
# Risk thresholds (comparing 8-to-8)
max_threshold = recent_max * 0.8  # 80% of recent max
avg_threshold = recent_avg * 1.2  # 20% above recent average

if forecast_avg > max_threshold:
    return 'HIGH', '#d32f2f', '🔴'
elif forecast_avg > avg_threshold:
    return 'MEDIUM', '#f57c00', '🟡'
else:
    return 'LOW', '#388e3c', '🟢'
```

---

## ✅ CHECKLIST: Before You Can Predict

### Step 1: Environment Setup
- [ ] Python virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] FastAPI, NeuralProphet, XGBoost installed

### Step 2: Model Files
- [ ] Models saved in `saved_models_v2/` directory
- [ ] Each `.pkl` file contains NeuralProphet + XGBoost
- [ ] MODEL_DIR path is correct in `main.py`

### Step 3: Seasonal Features
- [ ] `add_cainta_seasonal_features()` function defined
- [ ] `add_angono_seasonal_features()` function defined
- [ ] Features are added in `predict_next_month()`
- [ ] Features are added in `predict_future_months()`
- [ ] Features are added in `extract_model_components()`

### Step 4: Backend Running
- [ ] Start server: `python main.py`
- [ ] Check: `http://localhost:8000/` shows status
- [ ] Models loaded successfully (check terminal)

### Step 5: Test Prediction
- [ ] Call: `GET /api/municipalities` (should return list)
- [ ] Call: `GET /api/barangay/ANGONO/Bagumbayan` (should return data)
- [ ] Call: `GET /api/forecast/ANGONO/Bagumbayan` (should return predictions)

### Step 6: Frontend Integration
- [ ] Frontend running: `npm start` in frontend folder
- [ ] CORS enabled for `http://localhost:3000`
- [ ] API endpoints accessible from React

---

## 🎓 SUMMARY

### How Backend Works (Simple Explanation)

1. **Startup:**
   - Load ALL 42 barangay models into memory
   - Each model = NeuralProphet + XGBoost

2. **User Request:**
   - Frontend sends HTTP request to API endpoint
   - Backend finds the right model

3. **Prediction:**
   - Add seasonal features (if CAINTA/ANGONO)
   - NeuralProphet predicts baseline
   - XGBoost corrects the prediction
   - Return hybrid prediction

4. **Interpretability:**
   - Add seasonal features
   - NeuralProphet decomposes into trend/seasonality/holidays
   - XGBoost shows feature importance
   - Return all components

5. **Frontend Display:**
   - React receives JSON data
   - Displays charts, metrics, predictions
   - User understands WHY prediction was made

---

### Key Takeaways

✅ **Seasonal features are CRITICAL** for CAINTA/ANGONO  
✅ **Always add features before prediction** (same as training)  
✅ **NeuralProphet** handles time patterns (trend, seasonality, holidays)  
✅ **XGBoost** corrects systematic errors using engineered features  
✅ **Interpretability** breaks predictions into understandable parts  
✅ **Backend loads models ONCE** (fast predictions)  
✅ **Frontend requests data on-demand** (lazy loading)

---

## 📞 NEXT STEPS

Now that you understand the backend:

1. **Test the system:**
   - Start backend: `python main.py`
   - Open: `http://localhost:8000/docs`
   - Try API endpoints manually

2. **Read frontend documentation** (coming next!)

3. **Experiment with predictions:**
   - Modify seasonal features
   - Adjust risk thresholds
   - Add new municipalities

4. **Extend the system:**
   - Add weather regressors
   - Add vaccination campaigns
   - Add real-time data updates

---

**End of Backend Documentation**

*Generated on December 23, 2025*
