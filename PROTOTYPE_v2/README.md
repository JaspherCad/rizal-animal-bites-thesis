# 🐕 Rabies Forecasting Dashboard v2.0

Clean React + FastAPI prototype with working graphs and metrics.

## 🚀 Quick Start

### Step 1: Start Backend
```powershell
# Double-click this file:
start_backend.bat

# OR manually:
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Backend will run on:** http://localhost:8000

### Step 2: Start Frontend (New Terminal)
```powershell
# Double-click this file:
start_frontend.bat

# OR manually:
cd frontend
npm install
npm start
```

**Frontend will open:** http://localhost:3000

---

## ✅ Features

- ✅ **Municipality Cards** - Overview of all barangays
- ✅ **Click to View Details** - See metrics and graphs
- ✅ **Interactive Charts** - Using Recharts library
- ✅ **Training/Validation Visualization** - See model performance
- ✅ **Real Metrics Display** - MAE, RMSE, R², MASE
- ✅ **Next Month Prediction** - Live forecast
- ✅ **Clean UI** - Modern, responsive design

---

## 📊 What You'll See

### Main Dashboard:
- 4 municipality cards (CITY OF ANTIPOLO, CAINTA, TAYTAY, ANGONO)
- Each card shows barangays with predicted cases
- Click any barangay to see details

### Barangay Details:
- **Metrics**: MAE, RMSE, R², MASE
- **Graph**: Training data + Validation data
  - Black line = Actual cases
  - Blue dashed = Predicted cases
  - Orange line = Train/Val split
- **Next Month Prediction**: Future forecast

---

## 🔧 Troubleshooting

**Backend not starting?**
- Check: Python installed (`python --version`)
- Check: Models exist in `saved_models_v2/FINALIZED_barangay_models_20251028_005355/`

**Frontend not starting?**
- Check: Node.js installed (`node --version`)
- Run: `npm install` in frontend folder

**Graphs not showing?**
- Check: Backend running on port 8000
- Check: Browser console for errors (F12)
- Verify: API returns data at http://localhost:8000/docs

---

## 📁 Structure

```
PROTOTYPE_v2/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── requirements.txt     # Python dependencies
│   └── venv/               # Virtual environment
│
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main dashboard component
│   │   ├── BarangayChart.js # Graph component
│   │   ├── App.css         # Styles
│   │   └── index.js        # React entry point
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── node_modules/
│
├── start_backend.bat       # Backend startup script
├── start_frontend.bat      # Frontend startup script
└── README.md              # This file
```

---

## 🎯 Key Differences from v1

| Feature | Old (PROTOTYPE) | New (PROTOTYPE_v2) |
|---------|----------------|-------------------|
| Graphs | ❌ Broken | ✅ Working with Recharts |
| Metrics | ❌ Showing 0 | ✅ Displaying correctly |
| UI | ⚠️ Complex | ✅ Clean & simple |
| Code | ⚠️ Messy | ✅ Organized |
| Backend | ⚠️ Over-engineered | ✅ Simplified |

---

## 💡 Usage

1. **Start both backend and frontend**
2. **Click on any municipality card** to expand barangays
3. **Click on a barangay** to see:
   - Performance metrics
   - Training/validation graph
   - Next month prediction
4. **Click X button** to close details

---

**Version:** 2.0.0  
**Date:** October 28, 2025  
**Models:** FINALIZED_barangay_models_20251028_005355

🎉 **Enjoy your working dashboard!**
