# 🎨 RABIES FORECASTING FRONTEND - COMPREHENSIVE DOCUMENTATION (PART 1)

**Version:** 1.0.0  
**Framework:** React.js  
**Date:** December 23, 2025

---

## 📚 TABLE OF CONTENTS (PART 1)

1. [Frontend Overview](#frontend-overview)
2. [Architecture & File Structure](#architecture--file-structure)
3. [Component Hierarchy](#component-hierarchy)
4. [API Integration Layer](#api-integration-layer)
5. [Data Flow: Backend → Frontend](#data-flow-backend--frontend)
6. [Chart Rendering System](#chart-rendering-system)
7. [Model Insights Visualization](#model-insights-visualization)
8. [Complete User Journey Examples](#complete-user-journey-examples)

---

## 📖 FRONTEND OVERVIEW

### What is This Frontend?

This is a **React-based Single Page Application (SPA)** that provides an interactive dashboard for rabies forecasting. The frontend:

- ✅ Displays list of municipalities with risk-colored barangays
- ✅ Shows detailed barangay forecasts with interactive charts
- ✅ Visualizes model interpretability (trend, seasonality, holidays)
- ✅ Generates downloadable reports (CSV, PDF)
- ✅ Provides real-time predictions by communicating with FastAPI backend

### Key Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **React** | UI framework | 18.x |
| **React Router** | Page navigation | 6.x |
| **Recharts** | Chart visualization | 2.x |
| **Axios** | HTTP requests | 1.x |
| **CSS3** | Styling | - |

---

## 🏗️ ARCHITECTURE & FILE STRUCTURE

### Complete Directory Structure

```
PROTOTYPE_v2/frontend/
│
├── public/
│   ├── index.html                  # HTML template
│   └── favicon.ico
│
├── src/
│   ├── index.js                    # React entry point
│   ├── App.js                      # Main app component
│   │
│   ├── components/
│   │   ├── charts/
│   │   │   └── BarangayChart.jsx   # 📊 Main forecast chart
│   │   │
│   │   └── layout/
│   │       ├── Header.jsx          # Top navigation
│   │       └── Footer.jsx
│   │
│   ├── features/
│   │   ├── forecasting/
│   │   │   ├── MunicipalityList.jsx          # 📋 Municipality cards
│   │   │   ├── BarangayDetails.jsx           # 📈 Barangay detail view
│   │   │   ├── api.js                        # 🔌 Backend API calls
│   │   │   ├── hooks.js                      # 🪝 Custom React hooks
│   │   │   ├── styles.css                    # 🎨 Component styles
│   │   │   │
│   │   │   └── components/
│   │   │       ├── MetricsHelpBanner.jsx     # ℹ️ Metrics explanation
│   │   │       └── RiskExplanation.jsx       # 🔴 Risk level guide
│   │   │
│   │   └── insights/
│   │       ├── ModelInsights.jsx             # 🔍 Interpretability view
│   │       └── styles.css
│   │
│   ├── pages/
│   │   ├── Home.jsx
│   │   └── ForecastingDashboard.jsx
│   │
│   └── utils/
│       └── constants.js
│
├── package.json                    # Dependencies
└── README.md
```

---

## 🧩 COMPONENT HIERARCHY

### Visual Component Tree

```
App.js
│
├── Header.jsx
│
├── Router
│   │
│   ├── Home.jsx
│   │
│   └── ForecastingDashboard.jsx
│       │
│       └── MunicipalityList.jsx
│           │
│           ├── Municipality Card (ANGONO)
│           │   ├── Risk Summary Badges
│           │   └── Barangay Items (clickable)
│           │       │
│           │       └── onClick → navigate to BarangayDetails
│           │
│           └── BarangayDetails.jsx
│               │
│               ├── Tab System
│               │   ├── Forecast Tab (default)
│               │   └── Model Insights Tab
│               │
│               ├── MetricsHelpBanner.jsx
│               ├── RiskExplanation.jsx
│               │
│               ├── Metrics Grid (MAE, RMSE, MASE)
│               │
│               ├── Next Month Prediction
│               │
│               ├── Forecast Button
│               │   └── onClick → fetchForecast()
│               │
│               ├── Report Download Buttons
│               │   ├── CSV Report
│               │   ├── PDF Report
│               │   └── Insights PDF
│               │
│               ├── Risk Alert (if HIGH/MEDIUM)
│               │
│               ├── Forecast Grid (8 months)
│               │
│               ├── BarangayChart.jsx
│               │   ├── Training Data Line (blue)
│               │   ├── Validation Data Line (green)
│               │   └── Forecast Data Line (orange)
│               │
│               └── ModelInsights.jsx
│                   ├── Trend Chart
│                   ├── Seasonality Chart
│                   ├── Holiday Effects Chart
│                   ├── Seasonal Regressors (CAINTA/ANGONO)
│                   └── Feature Importance Bar Chart
│
└── Footer.jsx
```

---

## 🔌 API INTEGRATION LAYER

### File: `api.js`

This file handles ALL communication with the backend.

```javascript
// features/forecasting/api.js

const API_BASE_URL = 'http://localhost:8000';

// ============================================
// FUNCTION 1: Fetch all municipalities
// ============================================
export const fetchMunicipalities = async () => {
    const response = await fetch(`${API_BASE_URL}/api/municipalities`);
    if (!response.ok) {
        throw new Error('Failed to fetch municipalities');
    }
    const data = await response.json();
    return data.municipalities;  // Array of municipality objects
};

// ============================================
// FUNCTION 2: Fetch barangay details
// ============================================
export const fetchBarangayDetails = async (municipality, barangay) => {
    const response = await fetch(
        `${API_BASE_URL}/api/barangay/${municipality}/${barangay}`
    );
    if (!response.ok) {
        throw new Error(`Failed to fetch barangay details`);
    }
    const data = await response.json();
    return data.barangay;  // Barangay object
};

// ============================================
// FUNCTION 3: Fetch future forecast (8 months)
// ============================================
export const fetchForecast = async (municipality, barangay, months = 8) => {
    const response = await fetch(
        `${API_BASE_URL}/api/forecast/${municipality}/${barangay}?months=${months}`
    );
    if (!response.ok) {
        throw new Error('Failed to fetch forecast');
    }
    const data = await response.json();
    return data.forecast;  // Forecast object
};

// ============================================
// FUNCTION 4: Fetch interpretability data
// ============================================
export const fetchInterpretability = async (municipality, barangay) => {
    const response = await fetch(
        `${API_BASE_URL}/api/interpretability/${municipality}/${barangay}`
    );
    if (!response.ok) {
        throw new Error('Failed to fetch interpretability');
    }
    const data = await response.json();
    return data.interpretability;  // Interpretability object
};

// ============================================
// FUNCTION 5: Download CSV report
// ============================================
export const downloadCSVReport = async (municipality, barangay) => {
    const response = await fetch(
        `${API_BASE_URL}/api/report/csv/${municipality}/${barangay}`
    );
    if (!response.ok) {
        throw new Error('Failed to download CSV');
    }
    return await response.blob();  // Binary file data
};

// ============================================
// FUNCTION 6: Download PDF report
// ============================================
export const downloadPDFReport = async (municipality, barangay) => {
    const response = await fetch(
        `${API_BASE_URL}/api/report/pdf/${municipality}/${barangay}`
    );
    if (!response.ok) {
        throw new Error('Failed to download PDF');
    }
    return await response.blob();
};

// ============================================
// FUNCTION 7: Download insights PDF
// ============================================
export const downloadInsightsPDF = async (municipality, barangay) => {
    const response = await fetch(
        `${API_BASE_URL}/api/report/insights-pdf/${municipality}/${barangay}`
    );
    if (!response.ok) {
        throw new Error('Failed to download insights PDF');
    }
    return await response.blob();
};
```

### Key Points

✅ **No preprocessing needed!** Frontend sends raw municipality/barangay names  
✅ **Backend does ALL the work** (feature engineering, prediction, etc.)  
✅ **Frontend just displays** the results  
✅ **Error handling** with try-catch in consuming components

---

## 📊 DATA FLOW: BACKEND → FRONTEND

### Flow 1: Loading Municipality List

#### Step 1: Component Mounts

```javascript
// MunicipalityList.jsx
import { useMunicipalities } from './hooks';

function MunicipalityList() {
  const { municipalities, loading, error } = useMunicipalities();
  
  // municipalities will contain data from backend
}
```

#### Step 2: Custom Hook Fetches Data

```javascript
// hooks.js
export function useMunicipalities() {
  const [municipalities, setMunicipalities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadMunicipalities = async () => {
      try {
        const data = await fetchMunicipalities();  // Call api.js
        setMunicipalities(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadMunicipalities();
  }, []);  // Run once on mount

  return { municipalities, loading, error };
}
```

#### Step 3: Backend Response

```json
[
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
  },
  ...
]
```

#### Step 4: Component Renders Data

```javascript
// MunicipalityList.jsx
return (
  <div className="municipalities-grid">
    {municipalities.map((mun) => (
      <div key={mun.municipality} className="municipality-card">
        <h2>{mun.municipality}</h2>
        
        {/* Risk Summary */}
        <div className="risk-summary">
          <span className="risk-badge risk-high">
            🔴 {mun.risk_summary.HIGH || 0}
          </span>
          <span className="risk-badge risk-medium">
            🟡 {mun.risk_summary.MEDIUM || 0}
          </span>
          <span className="risk-badge risk-low">
            🟢 {mun.risk_summary.LOW || 0}
          </span>
        </div>
        
        {/* Barangay List */}
        <div className="barangay-list">
          {mun.barangays.map((brgy) => (
            <div
              key={brgy.name}
              className={`barangay-item risk-${brgy.risk_level?.toLowerCase()}`}
              onClick={() => handleBarangayClick(mun.municipality, brgy.name)}
              style={{ borderLeft: `4px solid ${brgy.risk_color}` }}
            >
              <span className="risk-indicator">{brgy.risk_icon}</span>
              <span className="barangay-name">{brgy.name}</span>
              <span className="predicted-cases">{brgy.predicted_next} cases</span>
            </div>
          ))}
        </div>
      </div>
    ))}
  </div>
);
```

**Visual Result:**

```
╔═══════════════════════════════════════════╗
║           ANGONO                          ║
║  10 Barangays | MAE: 1.45                 ║
║                                           ║
║  Risk Summary:  🔴 3  🟡 5  🟢 2          ║
║                                           ║
║  🔴 Bagumbayan              5.6 cases     ║
║  🟡 Kalayaan                3.2 cases     ║
║  🟢 San Isidro              2.1 cases     ║
║  ...                                      ║
╚═══════════════════════════════════════════╝
```

---

### Flow 2: Loading Barangay Details

#### Step 1: User Clicks Barangay

```javascript
// MunicipalityList.jsx
const handleBarangayClick = (municipality, barangay) => {
  navigate(`/forecasting/${municipality}/${barangay}`);
};

// Example: User clicks "Bagumbayan" in ANGONO
// URL becomes: /forecasting/ANGONO/Bagumbayan
```

#### Step 2: BarangayDetails Component Loads

```javascript
// BarangayDetails.jsx
import { useParams } from 'react-router-dom';
import { useBarangayData, useForecast, useInterpretability } from './hooks';

function BarangayDetails() {
  const { municipality, barangay } = useParams();
  // municipality = "ANGONO"
  // barangay = "Bagumbayan"
  
  // Load barangay data (automatic on mount)
  const { barangayData, loading: dataLoading } = useBarangayData(municipality, barangay);
  
  // Lazy load forecast (only when user clicks button)
  const { forecastData, loading: forecastLoading, fetchForecast } = useForecast(municipality, barangay);
  
  // Lazy load insights (only when user switches to Insights tab)
  const { interpretabilityData, loading: insightsLoading, fetchInterpretability } = useInterpretability(municipality, barangay);
  
  // ... rendering logic
}
```

#### Step 3: useBarangayData Hook

```javascript
// hooks.js
export function useBarangayData(municipality, barangay) {
  const [barangayData, setBarangayData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        // Call backend API
        const data = await fetchBarangayDetails(municipality, barangay);
        setBarangayData(data);
      } catch (err) {
        console.error('Error loading barangay data:', err);
      } finally {
        setLoading(false);
      }
    };

    if (municipality && barangay) {
      loadData();
    }
  }, [municipality, barangay]);  // Re-fetch when params change

  return { barangayData, loading };
}
```

#### Step 4: Backend Response

```json
{
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
```

#### Step 5: Component Renders Details

```javascript
// BarangayDetails.jsx
return (
  <div className="barangay-details">
    <div className="details-header">
      <h2>{barangay}, {municipality}</h2>
    </div>

    {/* Metrics Grid */}
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

    {/* Next Month Prediction */}
    <div className="next-prediction">
      <strong>Next Month Prediction:</strong> {barangayData.next_month_prediction} cases
    </div>

    {/* Chart */}
    <BarangayChart
      trainingData={barangayData.training_data}
      validationData={barangayData.validation_data}
      forecastData={null}  // Not loaded yet
    />
  </div>
);
```

**Visual Result:**

```
╔═══════════════════════════════════════════════════════╗
║  Bagumbayan, ANGONO                           [✕]     ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  MAE: 1.23    RMSE: 1.89    MASE: 0.87               ║
║                                                       ║
║  Next Month Prediction: 5.6 cases                    ║
║                                                       ║
║  [🔮 Show Future Forecast (8 Months)]                 ║
║                                                       ║
║  📊 CHART:                                            ║
║    _______________________________________________    ║
║   |                                               |   ║
║   | [BLUE LINE] = Training Data (2022-2024)      |   ║
║   | [GREEN LINE] = Validation Data (2024-2025)   |   ║
║   |_______________________________________________|   ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
```

---

### Flow 3: Loading Future Forecast

#### Step 1: User Clicks Forecast Button

```javascript
// BarangayDetails.jsx
const [showForecast, setShowForecast] = useState(false);

const handleForecastClick = async () => {
  if (!showForecast && !forecastData) {
    // First time clicking - fetch data
    await fetchForecast();
  }
  setShowForecast(!showForecast);
};

return (
  <button className="forecast-btn" onClick={handleForecastClick}>
    🔮 {showForecast ? 'Hide' : 'Show'} Future Forecast (8 Months)
  </button>
);
```

#### Step 2: useForecast Hook

```javascript
// hooks.js
export function useForecast(municipality, barangay) {
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchForecastData = async () => {
    setLoading(true);
    try {
      // Call backend API
      const data = await fetchForecast(municipality, barangay, 8);
      setForecastData(data);
    } catch (err) {
      console.error('Error fetching forecast:', err);
    } finally {
      setLoading(false);
    }
  };

  return { 
    forecastData, 
    loading, 
    fetchForecast: fetchForecastData  // Return function to manually trigger
  };
}
```

#### Step 3: Backend Processes Request

**What Frontend Sends:**
```
GET http://localhost:8000/api/forecast/ANGONO/Bagumbayan?months=8
```

**What Backend Does:**
1. Loads model: `MODELS["ANGONO_Bagumbayan"]`
2. Calls `predict_future_months(model_data, months_ahead=8)`
3. **Automatically adds seasonal features** (ANGONO = high_season, july_dip, etc.)
4. NeuralProphet predicts 8 months
5. XGBoost corrects each month
6. Returns predictions

**Backend Response:**
```json
{
  "municipality": "ANGONO",
  "barangay": "Bagumbayan",
  "validation_end": "2025-06",
  "forecast_start": "2025-07",
  "forecast_end": "2026-02",
  "predictions": [
    {"date": "2025-07", "predicted": 5.2},
    {"date": "2025-08", "predicted": 6.1},
    {"date": "2025-09", "predicted": 4.8},
    {"date": "2025-10", "predicted": 5.5},
    {"date": "2025-11", "predicted": 4.2},
    {"date": "2025-12", "predicted": 3.9},
    {"date": "2026-01", "predicted": 4.7},
    {"date": "2026-02", "predicted": 5.3}
  ]
}
```

#### Step 4: Frontend Displays Forecast

```javascript
// BarangayDetails.jsx
{showForecast && forecastData && (
  <div className="forecast-section">
    <h3>📈 Future Forecast</h3>
    <p className="forecast-info">
      Predictions from <strong>{forecastData.forecast_start}</strong> to{' '}
      <strong>{forecastData.forecast_end}</strong>
    </p>
    
    {/* Forecast Grid */}
    <div className="forecast-grid">
      {forecastData.predictions.map((pred, idx) => (
        <div key={idx} className="forecast-item">
          <span className="forecast-date">{pred.date}</span>
          <span className="forecast-value">{pred.predicted} cases</span>
        </div>
      ))}
    </div>
  </div>
)}

{/* Update Chart with Forecast */}
<BarangayChart
  trainingData={barangayData.training_data}
  validationData={barangayData.validation_data}
  forecastData={showForecast && forecastData ? forecastData.predictions : null}
/>
```

**Visual Result:**

```
╔═══════════════════════════════════════════════════════╗
║  📈 Future Forecast                                   ║
║  Predictions from 2025-07 to 2026-02                  ║
║                                                       ║
║  ┌─────────┬─────────┬─────────┬─────────┐           ║
║  │ 2025-07 │ 2025-08 │ 2025-09 │ 2025-10 │           ║
║  │ 5.2     │ 6.1     │ 4.8     │ 5.5     │           ║
║  └─────────┴─────────┴─────────┴─────────┘           ║
║  ┌─────────┬─────────┬─────────┬─────────┐           ║
║  │ 2025-11 │ 2025-12 │ 2026-01 │ 2026-02 │           ║
║  │ 4.2     │ 3.9     │ 4.7     │ 5.3     │           ║
║  └─────────┴─────────┴─────────┴─────────┘           ║
║                                                       ║
║  📊 CHART:                                            ║
║    _______________________________________________    ║
║   |                                               |   ║
║   | [BLUE LINE] = Training (historical)          |   ║
║   | [GREEN LINE] = Validation (historical)       |   ║
║   | [ORANGE LINE] = Forecast (future 8 months)   |   ║
║   |_______________________________________________|   ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
```

---

## 📈 CHART RENDERING SYSTEM

### Component: `BarangayChart.jsx`

This component renders the interactive time series chart.

```javascript
// components/charts/BarangayChart.jsx
import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

function BarangayChart({ trainingData, validationData, forecastData }) {
  
  // ============================================
  // STEP 1: Combine all data into one array
  // ============================================
  const chartData = [
    // Training data (blue line)
    ...trainingData.map(d => ({
      date: d.date,
      training_actual: d.actual,
      training_predicted: d.predicted,
      validation_actual: null,
      validation_predicted: null,
      forecast: null
    })),
    
    // Validation data (green line)
    ...validationData.map(d => ({
      date: d.date,
      training_actual: null,
      training_predicted: null,
      validation_actual: d.actual,
      validation_predicted: d.predicted,
      forecast: null
    })),
    
    // Forecast data (orange line) - if available
    ...(forecastData || []).map(d => ({
      date: d.date,
      training_actual: null,
      training_predicted: null,
      validation_actual: null,
      validation_predicted: null,
      forecast: d.predicted
    }))
  ];

  // ============================================
  // STEP 2: Render Recharts component
  // ============================================
  return (
    <div className="chart-container">
      <h3>📊 Rabies Cases Over Time</h3>
      
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          {/* Grid background */}
          <CartesianGrid strokeDasharray="3 3" />
          
          {/* X-axis (dates) */}
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          
          {/* Y-axis (case counts) */}
          <YAxis 
            label={{ value: 'Cases', angle: -90, position: 'insideLeft' }}
          />
          
          {/* Tooltip on hover */}
          <Tooltip 
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
          />
          
          {/* Legend */}
          <Legend />
          
          {/* TRAINING ACTUAL (blue dots) */}
          <Line 
            type="monotone" 
            dataKey="training_actual" 
            stroke="#2196F3" 
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Training Actual"
            connectNulls={false}
          />
          
          {/* TRAINING PREDICTED (blue line) */}
          <Line 
            type="monotone" 
            dataKey="training_predicted" 
            stroke="#2196F3" 
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="Training Predicted"
            connectNulls={false}
          />
          
          {/* VALIDATION ACTUAL (green dots) */}
          <Line 
            type="monotone" 
            dataKey="validation_actual" 
            stroke="#4CAF50" 
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Validation Actual"
            connectNulls={false}
          />
          
          {/* VALIDATION PREDICTED (green line) */}
          <Line 
            type="monotone" 
            dataKey="validation_predicted" 
            stroke="#4CAF50" 
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="Validation Predicted"
            connectNulls={false}
          />
          
          {/* FORECAST (orange line) */}
          {forecastData && (
            <Line 
              type="monotone" 
              dataKey="forecast" 
              stroke="#FF9800" 
              strokeWidth={3}
              dot={{ r: 5 }}
              name="Future Forecast"
              connectNulls={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      
      {/* Chart Legend Explanation */}
      <div className="chart-legend-info">
        <p><strong>📘 Blue:</strong> Training data (2022-2024) - Model learned from this</p>
        <p><strong>📗 Green:</strong> Validation data (2024-2025) - Model tested on this</p>
        {forecastData && (
          <p><strong>📙 Orange:</strong> Future forecast (2025-2026) - Predictions</p>
        )}
      </div>
    </div>
  );
}

export default BarangayChart;
```

### How Chart Updates

**Initial Load:**
```javascript
<BarangayChart
  trainingData={[...]}      // Backend provides this
  validationData={[...]}    // Backend provides this
  forecastData={null}       // Not loaded yet
/>
```
**Result:** Chart shows blue + green lines only

**After Clicking Forecast Button:**
```javascript
<BarangayChart
  trainingData={[...]}      // Same
  validationData={[...]}    // Same
  forecastData={[...]}      // NOW LOADED!
/>
```
**Result:** Chart shows blue + green + orange lines

**React Re-Render:**
- When `forecastData` prop changes from `null` to array
- React automatically re-renders `BarangayChart`
- Recharts updates the chart smoothly (animated!)

---

## 🔍 MODEL INSIGHTS VISUALIZATION

### Component: `ModelInsights.jsx`

This component visualizes the model interpretability data (trend, seasonality, holidays, feature importance).

```javascript
// features/insights/ModelInsights.jsx
import React from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

function ModelInsights({ interpretabilityData, loading }) {
  
  if (loading) {
    return <div className="loading">Loading model insights...</div>;
  }

  if (!interpretabilityData) {
    return <div className="no-data">No interpretability data available</div>;
  }

  // ============================================
  // PREPARE DATA FOR CHARTS
  // ============================================
  
  // 1. Trend + Seasonality + Holidays combined
  const decompositionData = interpretabilityData.trend.dates.map((date, idx) => ({
    date: date,
    trend: interpretabilityData.trend.values[idx],
    seasonality: interpretabilityData.seasonality.values[idx],
    holidays: interpretabilityData.holidays.values[idx]
  }));

  // 2. Feature importance
  const featureImportanceData = interpretabilityData.feature_importance.features.map(f => ({
    feature: f.feature,
    percentage: f.percentage
  }));

  // 3. Seasonal regressors (if CAINTA/ANGONO)
  const seasonalRegressorsData = [];
  if (interpretabilityData.seasonal_regressors.columns.length > 0) {
    const dates = interpretabilityData.trend.dates;
    const regressorColumns = interpretabilityData.seasonal_regressors.columns;
    
    dates.forEach((date, idx) => {
      const dataPoint = { date };
      regressorColumns.forEach(col => {
        dataPoint[col] = interpretabilityData.seasonal_regressors.data[col][idx];
      });
      seasonalRegressorsData.push(dataPoint);
    });
  }

  // ============================================
  // RENDER CHARTS
  // ============================================
  return (
    <div className="model-insights">
      
      {/* ========== TREND CHART ========== */}
      <div className="insight-section">
        <h3>📈 Trend Component</h3>
        <p className="description">{interpretabilityData.trend.description}</p>
        
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={decompositionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="trend" 
              stroke="#3498db" 
              strokeWidth={3}
              name="Trend"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
        
        <div className="insight-explanation">
          <p>
            The trend line shows the <strong>long-term direction</strong> of rabies cases.
            An upward trend means cases are slowly increasing over years.
            This could indicate population growth, more pet ownership, or policy changes.
          </p>
        </div>
      </div>

      {/* ========== SEASONALITY CHART ========== */}
      <div className="insight-section">
        <h3>🌊 Seasonality Component</h3>
        <p className="description">{interpretabilityData.seasonality.description}</p>
        
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={decompositionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="seasonality" 
              stroke="#e74c3c" 
              strokeWidth={3}
              name="Seasonality"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
        
        <div className="insight-explanation">
          <p>
            Seasonality shows <strong>recurring yearly patterns</strong>.
            For example, cases might be higher in summer months due to more outdoor activities.
            This pattern repeats every year (12-month cycle).
          </p>
        </div>
      </div>

      {/* ========== HOLIDAYS CHART ========== */}
      <div className="insight-section">
        <h3>🎉 Holiday Effects</h3>
        <p className="description">{interpretabilityData.holidays.description}</p>
        
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={decompositionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="holidays" 
              stroke="#f39c12" 
              strokeWidth={3}
              name="Holiday Effects"
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
        
        <div className="insight-explanation">
          <p>
            Holiday spikes show how <strong>Philippine public holidays</strong> affect rabies cases.
            During holidays like Christmas and New Year, people are more active outdoors,
            which can lead to more dog-human interactions.
          </p>
        </div>
        
        {/* Significant Holiday Effects Table */}
        {interpretabilityData.holidays.significant_effects.length > 0 && (
          <div className="significant-holidays">
            <h4>🔍 Significant Holiday Effects:</h4>
            <table className="holidays-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Holiday</th>
                  <th>Effect (cases)</th>
                </tr>
              </thead>
              <tbody>
                {interpretabilityData.holidays.significant_effects.slice(0, 10).map((effect, idx) => (
                  <tr key={idx}>
                    <td>{effect.date}</td>
                    <td>{effect.holiday}</td>
                    <td className={effect.effect > 0 ? 'positive' : 'negative'}>
                      {effect.effect > 0 ? '+' : ''}{effect.effect.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ========== SEASONAL REGRESSORS (CAINTA/ANGONO) ========== */}
      {seasonalRegressorsData.length > 0 && (
        <div className="insight-section">
          <h3>🎯 Custom Seasonal Features</h3>
          <p className="description">{interpretabilityData.seasonal_regressors.description}</p>
          
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={seasonalRegressorsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Legend />
              
              {/* Plot each regressor as a line */}
              {interpretabilityData.seasonal_regressors.columns.map((col, idx) => {
                const colors = ['#9b59b6', '#16a085', '#d35400', '#c0392b', '#2980b9'];
                return (
                  <Line 
                    key={col}
                    type="stepAfter" 
                    dataKey={col} 
                    stroke={colors[idx % colors.length]} 
                    strokeWidth={2}
                    name={col.replace(/_/g, ' ').toUpperCase()}
                    dot={false}
                  />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
          
          <div className="insight-explanation">
            <p>
              These are <strong>municipality-specific patterns</strong> that the model learned.
              For example, ANGONO has a "high season" in April-May-June every year.
              These binary flags (0 or 1) help the model understand local context.
            </p>
          </div>
        </div>
      )}

      {/* ========== FEATURE IMPORTANCE BAR CHART ========== */}
      <div className="insight-section">
        <h3>🎯 Feature Importance</h3>
        <p className="description">
          {interpretabilityData.feature_importance.description}
        </p>
        
        <ResponsiveContainer width="100%" height={400}>
          <BarChart 
            data={featureImportanceData.slice(0, 10)}  // Top 10 only
            layout="vertical"
            margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis 
              dataKey="feature" 
              type="category" 
              tick={{ fontSize: 12 }}
            />
            <Tooltip 
              formatter={(value) => `${value.toFixed(2)}%`}
            />
            <Bar 
              dataKey="percentage" 
              fill="#2ecc71"
              label={{ position: 'right', formatter: (value) => `${value.toFixed(1)}%` }}
            />
          </BarChart>
        </ResponsiveContainer>
        
        <div className="insight-explanation">
          <p>
            Feature importance shows <strong>which factors contribute most</strong> to predictions.
            The top 3 most important features are:
          </p>
          <ul>
            {interpretabilityData.feature_importance.top_3_features.map((feat, idx) => (
              <li key={idx}>
                <strong>{feat.feature}:</strong> {feat.percentage}% importance
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* ========== MODEL CONFIGURATION ========== */}
      <div className="insight-section">
        <h3>⚙️ Model Configuration</h3>
        <table className="config-table">
          <tbody>
            <tr>
              <td><strong>Holidays Configured:</strong></td>
              <td>{interpretabilityData.model_config.holidays_configured}</td>
            </tr>
            <tr>
              <td><strong>Weather Regressors:</strong></td>
              <td>{interpretabilityData.model_config.weather_regressors_count}</td>
            </tr>
            <tr>
              <td><strong>Seasonal Features:</strong></td>
              <td>{interpretabilityData.model_config.seasonal_regressors_count}</td>
            </tr>
            <tr>
              <td><strong>XGBoost Estimators:</strong></td>
              <td>{interpretabilityData.model_config.xgboost_n_estimators}</td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  );
}

export default ModelInsights;
```

### How Insights Load

#### Step 1: User Clicks "Model Insights" Tab

```javascript
// BarangayDetails.jsx
const [activeTab, setActiveTab] = useState('forecast');

const handleTabChange = (tab) => {
  setActiveTab(tab);
  
  if (tab === 'insights' && !interpretabilityData) {
    // Lazy load insights only when needed
    fetchInterpretability();
  }
};

return (
  <div className="tabs">
    <button 
      className={`tab ${activeTab === 'forecast' ? 'active' : ''}`}
      onClick={() => handleTabChange('forecast')}
    >
      📊 Forecast
    </button>
    <button 
      className={`tab ${activeTab === 'insights' ? 'active' : ''}`}
      onClick={() => handleTabChange('insights')}
    >
      🔍 Model Insights
    </button>
  </div>
);
```

#### Step 2: useInterpretability Hook

```javascript
// hooks.js
export function useInterpretability(municipality, barangay) {
  const [interpretabilityData, setInterpretabilityData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchInterpretabilityData = async () => {
    setLoading(true);
    try {
      const data = await fetchInterpretability(municipality, barangay);
      setInterpretabilityData(data);
    } catch (err) {
      console.error('Error fetching interpretability:', err);
    } finally {
      setLoading(false);
    }
  };

  return { 
    interpretabilityData, 
    loading, 
    fetchInterpretability: fetchInterpretabilityData 
  };
}
```

#### Step 3: Backend Extracts Components

**What Frontend Sends:**
```
GET http://localhost:8000/api/interpretability/ANGONO/Bagumbayan
```

**What Backend Does:**
1. Loads model: `MODELS["ANGONO_Bagumbayan"]`
2. Calls `extract_model_components(model_data)`
3. Collects ALL historical data (training + validation)
4. **Automatically adds seasonal features** (ANGONO = high_season, july_dip, etc.)
5. NeuralProphet decomposes predictions into trend/seasonality/holidays
6. XGBoost provides feature importance
7. Returns all components

**Backend Response:**
```json
{
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
      {"date": "2023-01", "holiday": "New Year", "effect": 1.2},
      {"date": "2023-12", "holiday": "Christmas", "effect": 0.9}
    ]
  },
  "seasonal_regressors": {
    "data": {
      "high_season": [0, 0, 0, 1, 1, 1, 0, ...],
      "july_dip": [0, 0, 0, 0, 0, 0, 1, ...],
      "august_rise": [0, 0, 0, 0, 0, 0, 0, 1, ...],
      "low_season": [1, 0, 0, 0, 0, 0, 0, 0, ...],
      "post_april_2024": [0, 0, ..., 1, 1, 1, ...]
    },
    "columns": ["high_season", "july_dip", "august_rise", "low_season", "post_april_2024"]
  },
  "feature_importance": {
    "features": [
      {"feature": "np_prediction", "importance": 0.3245, "percentage": 32.45},
      {"feature": "Month", "importance": 0.1823, "percentage": 18.23},
      ...
    ],
    "top_3_features": [...]
  },
  "model_config": {
    "holidays_configured": "Yes",
    "weather_regressors_count": 0,
    "seasonal_regressors_count": 5,
    "xgboost_n_estimators": 100
  }
}
```

#### Step 4: Frontend Renders Charts

```javascript
// BarangayDetails.jsx
{activeTab === 'insights' && (
  <ModelInsights 
    interpretabilityData={interpretabilityData} 
    loading={insightsLoading} 
  />
)}
```

**Visual Result:**

```
╔═══════════════════════════════════════════════════════╗
║  🔍 MODEL INSIGHTS                                    ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  📈 Trend Component                                   ║
║  Long-term direction of rabies cases                  ║
║   _______________________________________________     ║
║  | [BLUE LINE] showing gradual increase          |    ║
║  |_______________________________________________|    ║
║                                                       ║
║  🌊 Seasonality Component                             ║
║  Recurring yearly patterns                            ║
║   _______________________________________________     ║
║  | [RED LINE] showing peaks in summer months     |    ║
║  |_______________________________________________|    ║
║                                                       ║
║  🎉 Holiday Effects                                   ║
║  Philippine public holiday impacts                    ║
║   _______________________________________________     ║
║  | [ORANGE LINE] showing spikes during holidays  |    ║
║  |_______________________________________________|    ║
║                                                       ║
║  🎯 Custom Seasonal Features (ANGONO)                 ║
║  Municipality-specific patterns                       ║
║   _______________________________________________     ║
║  | [PURPLE] high_season                          |    ║
║  | [TEAL] july_dip                               |    ║
║  | [ORANGE] august_rise                          |    ║
║  |_______________________________________________|    ║
║                                                       ║
║  🎯 Feature Importance                                ║
║  Which factors contribute most                        ║
║   _______________________________________________     ║
║  | np_prediction      ████████████ 32.45%        |    ║
║  | Month              ██████ 18.23%              |    ║
║  | lag_1              ████ 12.87%                |    ║
║  |_______________________________________________|    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
```

---

## 🔄 COMPLETE USER JOURNEY EXAMPLES

### Journey 1: Viewing Municipality List

**User Action → Frontend → Backend → Response → Display**

```
1. User opens app
   └→ React Router loads: <ForecastingDashboard />
      └→ Renders: <MunicipalityList />
         └→ Hook: useMunicipalities()
            └→ API call: fetchMunicipalities()
               └→ Backend: GET /api/municipalities
                  ├→ Loop all 42 models
                  ├→ Calculate risk for each
                  └→ Return grouped by municipality
               └→ Response: [{ municipality, barangays, risk_summary }, ...]
            └→ State update: setMunicipalities(data)
         └→ Re-render with data
            └→ Display: Municipality cards with barangays
```

---

### Journey 2: Viewing Barangay Forecast

**Complete Flow:**

```
1. User clicks "Bagumbayan" in ANGONO card
   └→ handleBarangayClick('ANGONO', 'Bagumbayan')
      └→ navigate('/forecasting/ANGONO/Bagumbayan')
         └→ Router loads: <BarangayDetails />
            └→ useParams(): { municipality: 'ANGONO', barangay: 'Bagumbayan' }
            └→ Hook: useBarangayData('ANGONO', 'Bagumbayan')
               └→ API call: fetchBarangayDetails('ANGONO', 'Bagumbayan')
                  └→ Backend: GET /api/barangay/ANGONO/Bagumbayan
                     ├→ Load model: MODELS["ANGONO_Bagumbayan"]
                     ├→ Extract metrics, historical data
                     ├→ predict_next_month()
                     │  ├→ Add seasonal features (high_season, july_dip, etc.)
                     │  ├→ NeuralProphet predict
                     │  └→ XGBoost correct
                     └→ Return: { metrics, training_data, validation_data, next_month_prediction }
                  └→ Response: {...}
               └→ State update: setBarangayData(data)
            └→ Re-render with data
               └→ Display: 
                  ├→ Metrics (MAE, RMSE, MASE)
                  ├→ Next month prediction
                  └→ Chart (training + validation lines)

2. User clicks "Show Future Forecast" button
   └→ handleForecastClick()
      └→ Hook: fetchForecast()
         └→ API call: fetchForecast('ANGONO', 'Bagumbayan', 8)
            └→ Backend: GET /api/forecast/ANGONO/Bagumbayan?months=8
               ├→ Load model: MODELS["ANGONO_Bagumbayan"]
               ├→ predict_future_months(model, 8)
               │  ├→ Add seasonal features
               │  ├→ NeuralProphet batch predict (8 months)
               │  └→ XGBoost loop corrections
               └→ Return: { predictions: [{ date, predicted }, ...] }
            └→ Response: {...}
         └→ State update: setForecastData(data)
      └→ Re-render with forecast
         └→ Display:
            ├→ Forecast grid (8 months)
            └→ Chart (training + validation + forecast lines)
```

---

### Journey 3: Viewing Model Insights

**Complete Flow:**

```
1. User clicks "Model Insights" tab
   └→ handleTabChange('insights')
      └→ Hook: fetchInterpretability()
         └→ API call: fetchInterpretability('ANGONO', 'Bagumbayan')
            └→ Backend: GET /api/interpretability/ANGONO/Bagumbayan
               ├→ Load model: MODELS["ANGONO_Bagumbayan"]
               ├→ extract_model_components(model)
               │  ├→ Collect historical data (36 months)
               │  ├→ Add seasonal features (ANGONO)
               │  ├→ NeuralProphet decompose
               │  │  ├→ Extract trend component
               │  │  ├→ Extract seasonality component
               │  │  ├→ Extract holiday effects
               │  │  └→ Extract seasonal regressor contributions
               │  └→ XGBoost feature importance
               └→ Return: { trend, seasonality, holidays, seasonal_regressors, feature_importance }
            └→ Response: {...}
         └→ State update: setInterpretabilityData(data)
      └→ Re-render with insights
         └→ Display:
            ├→ Trend chart (blue line)
            ├→ Seasonality chart (red line)
            ├→ Holiday effects chart (orange line)
            ├→ Seasonal regressors chart (multiple lines)
            └→ Feature importance bar chart
```

---

## 🎯 KEY TAKEAWAYS

### Frontend Responsibilities

✅ **Display data** from backend (NO calculations)  
✅ **Handle user interactions** (clicks, tab switches)  
✅ **Make API calls** when needed (lazy loading)  
✅ **Render charts** using Recharts library  
✅ **Show loading states** while fetching  
✅ **Handle errors** gracefully

### Backend Responsibilities

✅ **Load models** on startup  
✅ **Add seasonal features** automatically (CAINTA/ANGONO)  
✅ **Run predictions** (NeuralProphet + XGBoost)  
✅ **Extract components** (trend, seasonality, holidays)  
✅ **Calculate risk levels** (HIGH/MEDIUM/LOW)  
✅ **Return JSON data** to frontend

### No Preprocessing Needed!

**Frontend sends:**
```
GET /api/forecast/ANGONO/Bagumbayan?months=8
```

**Backend automatically:**
1. Loads model
2. Adds seasonal features (ANGONO-specific)
3. Runs NeuralProphet prediction
4. Runs XGBoost correction
5. Returns predictions

**Frontend just displays** the results!

---

## 📝 EXPECTED INPUT/OUTPUT SUMMARY

### API Call: Get Barangay Details

**Input (Frontend → Backend):**
```
GET /api/barangay/ANGONO/Bagumbayan
```

**Processing (Backend):**
- No preprocessing required
- Backend extracts municipality and barangay from URL
- Backend adds seasonal features automatically

**Output (Backend → Frontend):**
```json
{
  "municipality": "ANGONO",
  "barangay": "Bagumbayan",
  "metrics": { "mae": 1.23, "rmse": 1.89, "mase": 0.87 },
  "training_data": [...],
  "validation_data": [...],
  "next_month_prediction": 5.6
}
```

---

### API Call: Get Forecast

**Input (Frontend → Backend):**
```
GET /api/forecast/ANGONO/Bagumbayan?months=8
```

**Processing (Backend):**
- Automatically adds seasonal features
- NeuralProphet predicts 8 months
- XGBoost corrects each month

**Output (Backend → Frontend):**
```json
{
  "predictions": [
    {"date": "2025-07", "predicted": 5.2},
    {"date": "2025-08", "predicted": 6.1},
    ...
  ]
}
```

---

### API Call: Get Interpretability

**Input (Frontend → Backend):**
```
GET /api/interpretability/ANGONO/Bagumbayan
```

**Processing (Backend):**
- Collects historical data
- Adds seasonal features
- NeuralProphet decomposes components
- XGBoost provides feature importance

**Output (Backend → Frontend):**
```json
{
  "trend": { "dates": [...], "values": [...] },
  "seasonality": { "dates": [...], "values": [...] },
  "holidays": { "dates": [...], "values": [...] },
  "seasonal_regressors": { "data": {...}, "columns": [...] },
  "feature_importance": { "features": [...] }
}
```

---

## ✅ SUMMARY

### How Backend & Frontend Work Together

1. **Frontend makes HTTP request** (simple URL with parameters)
2. **Backend receives request** and extracts municipality/barangay
3. **Backend loads model** from memory
4. **Backend adds seasonal features** automatically (if CAINTA/ANGONO)
5. **Backend runs prediction** (NeuralProphet + XGBoost)
6. **Backend returns JSON** with results
7. **Frontend displays data** in charts and tables

### No Manual Feature Engineering!

✅ Frontend NEVER needs to calculate features  
✅ Backend handles ALL feature engineering  
✅ Frontend just sends municipality/barangay names  
✅ Backend automatically knows which features to add

---

**End of Part 1**

*Part 2 will cover: Advanced features, State management, Error handling, Report downloads, Styling, and Deployment*

---

*Generated on December 23, 2025*
