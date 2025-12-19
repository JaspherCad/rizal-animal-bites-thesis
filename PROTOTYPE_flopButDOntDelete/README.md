# Rabies Alert System - Setup Instructions

## ✅ UPDATED: Now Using Your Latest Trained Models!

Your prototype has been updated to use:
- ✅ NEW NeuralProphet + XGBoost hybrid models
- ✅ SAME prediction method as training phase
- ✅ LIVE forecasting (not just validation results)
- ✅ Multi-month ahead predictions

---

## 🚀 Quick Start Guide

### ⚡ FASTEST METHOD (Windows)

1. **Start Backend:**
   - Double-click `start_backend.bat`
   - Wait for: "✅ Loaded X barangay models"

2. **Start Frontend (new terminal):**
   ```powershell
   cd frontend
   npm start
   ```

3. **Done!** Open http://localhost:3000

---

### 📋 MANUAL SETUP

### Backend Setup (FastAPI)

1. **Navigate to backend directory:**
   ```powershell
   cd PROTOTYPE\backend
   ```

2. **Create virtual environment (optional but recommended):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **⚠️ IMPORTANT: Train Models First (if not done):**
   - Open: `Best So Far.ipynb`
   - Run: Cell 35 (training loop)
   - Models save to: `saved_models/trained_models_TIMESTAMP/`

5. **Verify model files exist:**
   - Check: `../saved_models/trained_models_YYYYMMDD_HHMMSS/`
   - Should contain folders: CAINTA/, ANGONO/, TAYTAY/, CITY_OF_ANTIPOLO/
   - Backend auto-detects latest trained_models folder

6. **Start the FastAPI server:**
   ```powershell
   python main.py
   ```
   
   Server will start at: **http://localhost:8000**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000
   
   **You should see:**
   ```
   📂 Using models from: trained_models_20241027_XXXXXX
   ✅ Loaded 38 barangay models
   🚀 Starting Rabies Alert System API...
   ```

### Frontend Setup (React)

1. **Navigate to frontend directory (in a NEW terminal):**
   ```powershell
   cd PROTOTYPE\frontend
   ```

2. **Install Node.js dependencies:**
   ```powershell
   npm install
   ```

3. **Start React development server:**
   ```powershell
   npm start
   ```
   
   Frontend will start at: **http://localhost:3000**
   - Dashboard will automatically open in browser

---

## 📡 API Endpoints

### Backend (http://localhost:8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check & system status |
| `/api/alerts` | GET | Get all active alerts (filter by `?municipality=NAME`) |
| `/api/municipalities` | GET | Get summary stats per municipality |
| `/api/barangay/{municipality}/{barangay}` | GET | Get detailed forecast data for specific barangay |
| `/api/forecast/{municipality}/{barangay}?months=6` | GET | **NEW!** Multi-month forecast (1-12 months ahead) |
| `/api/thresholds` | GET | Get municipality-specific alert thresholds |

### Example Requests:

```powershell
# Get all alerts (uses LIVE predictions now!)
curl http://localhost:8000/api/alerts

# Get alerts for TAYTAY only
curl "http://localhost:8000/api/alerts?municipality=TAYTAY"

# Get municipality summaries (real-time forecasts)
curl http://localhost:8000/api/municipalities

# Get specific barangay details
curl "http://localhost:8000/api/barangay/TAYTAY/Dolores"

# NEW: Get 6-month forecast for specific barangay
curl "http://localhost:8000/api/forecast/CAINTA/San_Isidro?months=6"
```

### 🆕 NEW: Multi-Month Forecast Endpoint

```
GET /api/forecast/{municipality}/{barangay}?months=6
```

**Returns:**
```json
{
  "municipality": "CAINTA",
  "barangay": "San_Isidro",
  "forecast_months": 6,
  "predictions": [
    {
      "month_ahead": 1,
      "month_date": "2025-02-01",
      "predicted_cases": 15.2,
      "alert_level": "medium",
      "confidence": "high"
    },
    // ... 5 more months
  ],
  "model_metrics": {
    "hybrid_mae": 4.32,
    "np_mae": 6.11,
    "xgb_mae": 5.87
  }
}
```

**Use Cases:**
- Planning vaccination campaigns
- Resource allocation forecasting
- Multi-month trend analysis
- Budget planning

---

## 🎯 Alert System Logic

### Municipality-Specific Thresholds (cases/month)

| Municipality | High Alert | Medium Alert | Low Alert |
|--------------|-----------|--------------|-----------|
| CITY OF ANTIPOLO | > 50 | > 30 | > 15 |
| TAYTAY | > 30 | > 20 | > 10 |
| CAINTA | > 40 | > 25 | > 12 |
| ANGONO | > 35 | > 20 | > 10 |

### Seasonal Surge Detection

- **Dry Season:** January-May (higher rabies risk)
- **Surge Criteria:**
  - Dry season: Predicted > 1.5× historical average
  - Wet season: Predicted > 2.0× historical average

---

## 🖥️ Dashboard Features

### 1. Alert Summary Banner
- Total active alerts
- Count by priority: HIGH 🔴, MEDIUM 🟡, LOW 🟢

### 2. Municipality Overview Cards
- Total barangays monitored
- Predicted cases for current forecast period
- Average MAE (model accuracy)
- Alert breakdown by priority

### 3. Alert List
- Filterable by alert level
- Sortable by level, predicted cases, location
- Shows forecast date, predicted cases, historical average
- Displays seasonal surge warnings

### 4. Interactive Features
- Click municipality cards to filter alerts
- Auto-refresh every 5 minutes
- Manual refresh button
- Last updated timestamp

---

## 📊 Model Information

- **Architecture:** Hybrid NeuralProphet + XGBoost
- **Training:** 38 barangays across 4 municipalities
- **Performance:** Average MAE improvement 30-40%
- **Best Performers:** Beverly Hills (MAE=2.96), Calawis (MAE=5.25)

---

## 🛠️ Troubleshooting

### Backend Issues:

**"ModuleNotFoundError: No module named 'neuralprophet'"**
- Solution: Run `pip install -r requirements.txt`
- New dependencies: neuralprophet, xgboost, requests

**"FileNotFoundError: Model directory not found"**
- Solution 1: Train models first (Jupyter Cell 35 in Best So Far.ipynb)
- Solution 2: Check saved_models/ folder exists with trained_models_TIMESTAMP folder
- Backend auto-detects latest timestamp folder

**"Model directory is empty"**
- Solution: Run training notebook Cell 35
- Models will save to: saved_models/trained_models_YYYYMMDD_HHMMSS/

**Port 8000 already in use:**
- Solution: Change port in `main.py` (last line):
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
  ```

**Models not loading / "Loaded 0 barangay models"**
- Check: saved_models/trained_models_TIMESTAMP/ exists
- Check: Folders inside (CAINTA/, ANGONO/, etc.)
- Check: .pkl files inside each folder
- Re-run: Jupyter training Cell 35 if needed

### Frontend Issues:

**"npm command not found"**
- Solution: Install Node.js from https://nodejs.org/

**"Network Error" or "Failed to fetch"**
- Solution: Ensure backend is running on http://localhost:8000
- Check CORS settings in `main.py` (lines 23-30)

**Port 3000 already in use:**
- Solution: React will prompt to use different port (press Y)

---

## 📝 File Structure

```
PROTOTYPE/
├── backend/
│   ├── main.py              # FastAPI application + RabiesAlertSystem
│   ├── requirements.txt     # Python dependencies (updated!)
│   └── test_api.py          # NEW: API testing script
│
├── frontend/
│   ├── public/
│   │   └── index.html       # HTML template
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js       # Main dashboard
│   │   │   ├── Dashboard.css
│   │   │   ├── AlertList.js       # Alert table/cards
│   │   │   ├── AlertList.css
│   │   │   ├── MunicipalityCard.js  # Municipality summary
│   │   │   └── MunicipalityCard.css
│   │   ├── services/
│   │   │   └── api.js        # API client (axios)
│   │   ├── App.js            # Main React component
│   │   ├── App.css
│   │   ├── index.js          # React entry point
│   │   └── index.css
│   └── package.json          # Node.js dependencies
│
├── start_backend.bat         # NEW: One-click backend startup (Windows)
├── start_backend.ps1         # NEW: PowerShell startup script
├── UPDATED_README.md         # NEW: Detailed implementation guide
├── IMPLEMENTATION_COMPLETE.md # NEW: Complete change summary
└── README.md                 # This file
```

---

## 🎓 For Thesis Defense

### Key Talking Points:

1. **Hybrid Model Architecture:**
   - NeuralProphet captures time series patterns (seasonality, trends)
   - XGBoost corrects residuals for improved accuracy
   - Ensemble combines both: `hybrid = np_baseline + xgb_residuals`
   - ✅ Uses IDENTICAL prediction method in training and production

2. **Alert System Design:**
   - Municipality-specific thresholds based on historical patterns
   - Seasonal surge detection for proactive warnings
   - Color-coded priority system for rapid response
   - Real-time forecasting (not pre-computed results)

3. **Web Dashboard:**
   - Real-time monitoring of 38 barangays
   - Interactive filtering and sorting
   - API-first architecture for scalability
   - Multi-month ahead forecasting capability

4. **Performance Metrics:**
   - MAE/RMSE provide actionable insights (cases ± error)
   - 100% model success rate (38/38)
   - Strong validation performance (avg 30-40% improvement)
   - Production-ready with saved model artifacts

5. **Technical Implementation:**
   - FastAPI backend with auto-discovery of latest models
   - React frontend for user interface
   - Persistent model storage (saved_models/)
   - Reproducible predictions (same method as training)

---

## 🧪 Testing Your Setup

### Quick Test:
```powershell
cd backend
python test_api.py
```

**Expected Output:**
```
✅ Health check passed
✅ Alerts endpoint working
✅ Municipalities endpoint working
✅ Forecast endpoint working (NEW!)
```

### Manual API Tests:

1. **Health Check:**
   - Visit: http://localhost:8000
   - Should see: System status with model count

2. **API Documentation:**
   - Visit: http://localhost:8000/docs
   - Try out the new `/api/forecast` endpoint

3. **Test Forecast:**
   ```powershell
   curl "http://localhost:8000/api/forecast/CAINTA/San_Isidro?months=3"
   ```

---

## 📊 What's Different from Old Version?

### Before (Old):
- ❌ Used pre-computed validation results
- ❌ Complex prediction preprocessing
- ❌ Different logic than training phase
- ❌ Hard-coded model paths
- ❌ No multi-month forecasting

### After (NEW):
- ✅ Uses LIVE model predictions
- ✅ Simple: load model → predict → return
- ✅ IDENTICAL to training phase logic
- ✅ Auto-detects latest trained models
- ✅ Can forecast 1-12 months ahead
- ✅ Real-time forecasting on demand

**Key Formula (Training & Production):**
```python
hybrid_prediction = np_baseline + xgb_residuals
hybrid_prediction = max(hybrid_prediction, 0)  # No negative cases
```

---

## 🔗 Additional Resources

- **Implementation Details:** See `IMPLEMENTATION_COMPLETE.md`
- **API Usage Guide:** See `UPDATED_README.md`
- **Test Script:** Run `backend/test_api.py`
- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- NeuralProphet: https://neuralprophet.com/
- XGBoost: https://xgboost.readthedocs.io/

---

**Version:** 2.0.0 (UPDATED!)  
**Last Updated:** 2025-01-27  
**Changes:** Integrated new NeuralProphet + XGBoost hybrid models with live forecasting

**Need Help?** Check `IMPLEMENTATION_COMPLETE.md` for detailed explanations!
