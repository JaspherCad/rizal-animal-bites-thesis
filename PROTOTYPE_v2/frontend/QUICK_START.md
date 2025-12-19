# 🚀 Quick Start Guide

## Get Up and Running in 3 Minutes

### Step 1: Install Dependencies
```powershell
cd "d:\CleanThesis\DONT DEELTE THESE FILES\PROTOTYPE_v2\frontend"
npm install
```

### Step 2: (Optional) Configure Environment
```powershell
# Only if your backend is NOT on http://localhost:8000
Copy-Item .env.example .env
# Then edit .env and set REACT_APP_API_URL
```

### Step 3: Start the App
```powershell
npm start
```

**That's it!** Your browser will automatically open to http://localhost:3000

---

## First-Time User Flow

1. **See the Home Page**
   - Welcome message and feature overview
   - Click "📊 Forecasting" in the header

2. **Browse Municipalities**
   - See 4 municipalities (ANTIPOLO, CAINTA, TAYTAY, ANGONO)
   - Each shows barangays color-coded by risk level

3. **Click a Barangay**
   - View detailed metrics (MAE, RMSE, MASE)
   - See next month prediction
   - Click "🔮 Show Future Forecast" for 8-month predictions

4. **Explore Model Insights**
   - Click "🔍 Model Insights" tab
   - See trend, seasonality, weather, and vaccination impacts
   - Understand how the model makes predictions

5. **Download Reports**
   - CSV for spreadsheet analysis
   - PDF for presentations
   - Insights PDF for technical documentation

---

## Troubleshooting

### "Cannot find module 'react-router-dom'"
```powershell
npm install
```

### "API connection failed"
Make sure backend is running:
```powershell
# In a separate terminal
cd "d:\CleanThesis\DONT DEELTE THESE FILES\PROTOTYPE_v2\backend"
uvicorn main:app --reload
```

### "Port 3000 already in use"
```powershell
# Windows: Find and kill process
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port
$env:PORT=3001; npm start
```

---

## Key Shortcuts

| Action | Path |
|--------|------|
| Home | http://localhost:3000 |
| Forecasting | http://localhost:3000/forecasting |
| Direct to Barangay | http://localhost:3000/forecasting/ANTIPOLO/BAGONG_NAYON |

---

## Need Help?

1. Check `README.md` for full documentation
2. See `MIGRATION_GUIDE.md` for structure details
3. Review `REFACTORING_SUMMARY.md` for overview

---

**Pro Tip**: Use browser DevTools (F12) to see API calls and debug issues!
