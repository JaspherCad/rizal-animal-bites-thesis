# 🎨 RABIES FORECASTING FRONTEND - COMPREHENSIVE DOCUMENTATION (PART 2)

**Version:** 1.0.0  
**Framework:** React.js  
**Date:** December 23, 2025

---

## 📚 TABLE OF CONTENTS (PART 2)

1. [Advanced Features: Report Downloads](#advanced-features-report-downloads)
2. [State Management Patterns](#state-management-patterns)
3. [Custom React Hooks Deep Dive](#custom-react-hooks-deep-dive)
4. [Error Handling Strategies](#error-handling-strategies)
5. [CSS Styling System](#css-styling-system)
6. [Risk Level Calculation (Frontend)](#risk-level-calculation-frontend)
7. [Tab System Implementation](#tab-system-implementation)
8. [Deployment Guide](#deployment-guide)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Best Practices & Tips](#best-practices--tips)

---

## 📥 ADVANCED FEATURES: REPORT DOWNLOADS

### How Report Downloads Work

The frontend triggers downloads by fetching binary data (Blob) from the backend and creating temporary download links.

### Component: Report Download Buttons

```javascript
// BarangayDetails.jsx
import { downloadCSVReport, downloadPDFReport, downloadInsightsPDF } from './api';

function BarangayDetails() {
  const [downloadLoading, setDownloadLoading] = useState(false);
  
  // ============================================
  // CSV REPORT DOWNLOAD
  // ============================================
  const handleDownloadCSV = async () => {
    try {
      setDownloadLoading(true);
      
      // 1. Fetch binary data from backend
      const blob = await downloadCSVReport(municipality, barangay);
      
      // 2. Create temporary URL for the blob
      const url = window.URL.createObjectURL(blob);
      
      // 3. Create invisible <a> element
      const a = document.createElement('a');
      a.href = url;
      a.download = `rabies_forecast_${municipality}_${barangay}_${new Date().toISOString().split('T')[0]}.csv`;
      
      // 4. Trigger click to download
      document.body.appendChild(a);
      a.click();
      
      // 5. Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (error) {
      console.error('Error downloading CSV:', error);
      alert(`Failed to download CSV report: ${error.message}`);
    } finally {
      setDownloadLoading(false);
    }
  };
  
  // ============================================
  // PDF REPORT DOWNLOAD
  // ============================================
  const handleDownloadPDF = async () => {
    try {
      setDownloadLoading(true);
      const blob = await downloadPDFReport(municipality, barangay);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rabies_forecast_${municipality}_${barangay}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert(`Failed to download PDF report: ${error.message}`);
    } finally {
      setDownloadLoading(false);
    }
  };
  
  // ============================================
  // INSIGHTS PDF DOWNLOAD
  // ============================================
  const handleDownloadInsightsPDF = async () => {
    try {
      setDownloadLoading(true);
      const blob = await downloadInsightsPDF(municipality, barangay);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rabies_model_insights_${municipality}_${barangay}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading Insights PDF:', error);
      alert(`Failed to download Insights PDF: ${error.message}`);
    } finally {
      setDownloadLoading(false);
    }
  };
  
  // ============================================
  // RENDER DOWNLOAD BUTTONS
  // ============================================
  return (
    <div className="report-section">
      <h3>📑 Download Reports</h3>
      <p>Generate comprehensive forecast reports for stakeholders and decision-makers</p>
      
      <div className="report-buttons">
        <button 
          className="report-btn report-btn-csv"
          onClick={handleDownloadCSV}
          disabled={downloadLoading}
        >
          {downloadLoading ? '⏳ Generating...' : '📊 Download CSV Report'}
        </button>
        
        <button 
          className="report-btn report-btn-pdf"
          onClick={handleDownloadPDF}
          disabled={downloadLoading}
        >
          {downloadLoading ? '⏳ Generating...' : '📄 Download PDF Report'}
        </button>
      </div>
    </div>
  );
}
```

### API Functions for Downloads

```javascript
// api.js
export const downloadCSVReport = async (municipality, barangay) => {
  const response = await fetch(
    `${API_BASE_URL}/api/report/csv/${municipality}/${barangay}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to download CSV');
  }
  
  // Return binary blob
  return await response.blob();
};

export const downloadPDFReport = async (municipality, barangay) => {
  const response = await fetch(
    `${API_BASE_URL}/api/report/pdf/${municipality}/${barangay}`
  );
  
  if (!response.ok) {
    throw new Error('Failed to download PDF');
  }
  
  return await response.blob();
};

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

### Download Flow Diagram

```
User clicks "Download CSV Report"
    ↓
handleDownloadCSV() triggered
    ↓
setDownloadLoading(true)  ← Show loading state
    ↓
API call: downloadCSVReport(municipality, barangay)
    ↓
Backend: GET /api/report/csv/ANGONO/Bagumbayan
    ├→ Generate CSV data (180-day forecast)
    ├→ Add metadata headers
    └→ Return blob (binary data)
    ↓
Frontend receives blob
    ↓
Create temporary URL: window.URL.createObjectURL(blob)
    ↓
Create <a> element with download attribute
    ↓
Trigger click: a.click()
    ↓
Browser downloads file: "rabies_forecast_ANGONO_Bagumbayan_2025-12-23.csv"
    ↓
Cleanup: Remove URL and <a> element
    ↓
setDownloadLoading(false)  ← Hide loading state
```

### Why This Approach?

✅ **No page refresh** - Downloads happen in background  
✅ **Dynamic filenames** - Includes municipality, barangay, and date  
✅ **Loading states** - User sees feedback during generation  
✅ **Error handling** - Shows alert if download fails  
✅ **Memory cleanup** - Revokes temporary URLs to prevent memory leaks

---

## 🔄 STATE MANAGEMENT PATTERNS

### React State Management Overview

The app uses **React Hooks** for state management (no Redux needed for this scale).

### Types of State

#### 1. **Local Component State** (`useState`)

Used for UI-specific state that doesn't need to be shared.

```javascript
// BarangayDetails.jsx
function BarangayDetails() {
  // Loading state
  const [downloadLoading, setDownloadLoading] = useState(false);
  
  // Toggle state
  const [showForecast, setShowForecast] = useState(false);
  
  // Tab state
  const [activeTab, setActiveTab] = useState('forecast');
  
  // ... component logic
}
```

**When to use:**
- UI toggles (show/hide)
- Form inputs
- Loading indicators
- Active tab tracking

---

#### 2. **API Data State** (Custom Hooks)

Used for data fetched from backend.

```javascript
// hooks.js
export function useMunicipalities() {
  const [municipalities, setMunicipalities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const loadMunicipalities = async () => {
      try {
        const data = await fetchMunicipalities();
        setMunicipalities(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    loadMunicipalities();
  }, []);
  
  return { municipalities, loading, error };
}
```

**When to use:**
- Data from backend API
- Need loading/error states
- Data shared across multiple renders

---

#### 3. **URL Parameters** (`useParams`)

Used for routing and navigation.

```javascript
// BarangayDetails.jsx
import { useParams } from 'react-router-dom';

function BarangayDetails() {
  const { municipality, barangay } = useParams();
  // municipality = "ANGONO"
  // barangay = "Bagumbayan"
  
  // Use in API calls
  const { barangayData } = useBarangayData(municipality, barangay);
}
```

**When to use:**
- Page navigation
- Shareable URLs
- Browser back/forward navigation

---

### State Lifecycle Example

**Scenario:** User views barangay details

```javascript
// Initial State (Component Mount)
{
  barangayData: null,          // Not loaded yet
  loading: true,               // Fetching data
  error: null,                 // No error yet
  showForecast: false,         // Forecast hidden
  forecastData: null,          // Not loaded yet
  activeTab: 'forecast'        // Default tab
}

// After API Response
{
  barangayData: { ... },       // ✅ Data loaded
  loading: false,              // ✅ Done loading
  error: null,                 // ✅ No error
  showForecast: false,         // Still hidden
  forecastData: null,          // Not loaded yet
  activeTab: 'forecast'        // Default tab
}

// After User Clicks "Show Forecast"
{
  barangayData: { ... },       // Same
  loading: false,              // Same
  error: null,                 // Same
  showForecast: true,          // ✅ Now visible
  forecastData: { ... },       // ✅ Loaded
  activeTab: 'forecast'        // Same
}

// After User Switches to "Insights" Tab
{
  barangayData: { ... },       // Same
  loading: false,              // Same
  error: null,                 // Same
  showForecast: true,          // Same
  forecastData: { ... },       // Same
  activeTab: 'insights',       // ✅ Changed
  interpretabilityData: null   // Will load lazily
}
```

---

## 🪝 CUSTOM REACT HOOKS DEEP DIVE

### Hook 1: `useMunicipalities`

**Purpose:** Fetch and manage municipality list with risk levels.

```javascript
// hooks.js
export function useMunicipalities() {
  const [municipalities, setMunicipalities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadMunicipalities = async () => {
      try {
        setLoading(true);
        const data = await fetchMunicipalities();
        setMunicipalities(data);
        setError(null);
      } catch (err) {
        console.error('Error loading municipalities:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadMunicipalities();
  }, []);  // Empty dependency array = run once on mount

  return { municipalities, loading, error };
}
```

**Usage:**
```javascript
// MunicipalityList.jsx
const { municipalities, loading, error } = useMunicipalities();

if (loading) return <div>Loading...</div>;
if (error) return <div>Error: {error}</div>;
return <div>{/* Render municipalities */}</div>;
```

**Key Points:**
- ✅ Runs automatically on component mount
- ✅ Returns loading/error states for UI feedback
- ✅ Data cached in state (doesn't refetch on re-render)

---

### Hook 2: `useBarangayData`

**Purpose:** Fetch barangay details (metrics, historical data, next month prediction).

```javascript
// hooks.js
export function useBarangayData(municipality, barangay) {
  const [barangayData, setBarangayData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchBarangayDetails(municipality, barangay);
        setBarangayData(data);
        setError(null);
      } catch (err) {
        console.error('Error loading barangay data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (municipality && barangay) {
      loadData();
    }
  }, [municipality, barangay]);  // Re-fetch when params change

  return { barangayData, loading, error };
}
```

**Usage:**
```javascript
// BarangayDetails.jsx
const { municipality, barangay } = useParams();
const { barangayData, loading, error } = useBarangayData(municipality, barangay);
```

**Key Points:**
- ✅ Dependency array `[municipality, barangay]` = re-fetch when URL changes
- ✅ Handles navigation between barangays automatically
- ✅ Guards against empty parameters

---

### Hook 3: `useForecast`

**Purpose:** Lazy-load future forecast (only when user clicks button).

```javascript
// hooks.js
export function useForecast(municipality, barangay) {
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchForecastData = async () => {
    try {
      setLoading(true);
      const data = await fetchForecast(municipality, barangay, 8);
      setForecastData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching forecast:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { 
    forecastData, 
    loading, 
    error,
    fetchForecast: fetchForecastData  // Return function for manual trigger
  };
}
```

**Usage:**
```javascript
// BarangayDetails.jsx
const { forecastData, loading, fetchForecast } = useForecast(municipality, barangay);

const handleForecastClick = async () => {
  if (!forecastData) {
    await fetchForecast();  // Manually trigger fetch
  }
  setShowForecast(!showForecast);
};
```

**Key Points:**
- ✅ **Lazy loading** = doesn't fetch until user requests
- ✅ Returns function to manually trigger fetch
- ✅ Caches data (doesn't refetch on re-render)

---

### Hook 4: `useInterpretability`

**Purpose:** Lazy-load model insights (only when user switches to Insights tab).

```javascript
// hooks.js
export function useInterpretability(municipality, barangay) {
  const [interpretabilityData, setInterpretabilityData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchInterpretabilityData = async () => {
    try {
      setLoading(true);
      const data = await fetchInterpretability(municipality, barangay);
      setInterpretabilityData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching interpretability:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { 
    interpretabilityData, 
    loading, 
    error,
    fetchInterpretability: fetchInterpretabilityData 
  };
}
```

**Usage:**
```javascript
// BarangayDetails.jsx
const { interpretabilityData, loading, fetchInterpretability } = useInterpretability(municipality, barangay);

const handleTabChange = (tab) => {
  setActiveTab(tab);
  if (tab === 'insights' && !interpretabilityData) {
    fetchInterpretability();  // Lazy load on first tab switch
  }
};
```

**Key Points:**
- ✅ **Lazy loading** = saves bandwidth (not everyone views insights)
- ✅ Only fetches once (cached after first load)
- ✅ Performance optimization

---

## ⚠️ ERROR HANDLING STRATEGIES

### Level 1: Try-Catch in API Functions

```javascript
// api.js
export const fetchBarangayDetails = async (municipality, barangay) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/barangay/${municipality}/${barangay}`
    );
    
    if (!response.ok) {
      // HTTP error (404, 500, etc.)
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.barangay;
    
  } catch (error) {
    console.error('API Error:', error);
    throw error;  // Re-throw to let hook handle it
  }
};
```

---

### Level 2: Error State in Hooks

```javascript
// hooks.js
export function useBarangayData(municipality, barangay) {
  const [barangayData, setBarangayData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);  // Error state

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);  // Clear previous errors
        const data = await fetchBarangayDetails(municipality, barangay);
        setBarangayData(data);
      } catch (err) {
        console.error('Error loading barangay data:', err);
        setError(err.message);  // Store error
        setBarangayData(null);  // Clear stale data
      } finally {
        setLoading(false);
      }
    };

    if (municipality && barangay) {
      loadData();
    }
  }, [municipality, barangay]);

  return { barangayData, loading, error };
}
```

---

### Level 3: Error Display in Components

```javascript
// BarangayDetails.jsx
function BarangayDetails() {
  const { municipality, barangay } = useParams();
  const { barangayData, loading, error } = useBarangayData(municipality, barangay);
  
  // Loading state
  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading barangay data...</p>
      </div>
    );
  }
  
  // Error state
  if (error) {
    return (
      <div className="error-container">
        <h2>❌ Error Loading Data</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          🔄 Retry
        </button>
      </div>
    );
  }
  
  // No data state
  if (!barangayData) {
    return (
      <div className="no-data-container">
        <h2>📭 No Data Available</h2>
        <p>Barangay data not found for {barangay}, {municipality}</p>
        <button onClick={() => navigate('/forecasting')}>
          ← Back to Municipality List
        </button>
      </div>
    );
  }
  
  // Success state - render normal UI
  return (
    <div className="barangay-details">
      {/* Normal content */}
    </div>
  );
}
```

---

### Level 4: User-Friendly Error Messages

```javascript
// Download error handling with user feedback
const handleDownloadPDF = async () => {
  try {
    setDownloadLoading(true);
    const blob = await downloadPDFReport(municipality, barangay);
    
    // Success! Download file
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${municipality}_${barangay}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    // Show success message
    alert('✅ Report downloaded successfully!');
    
  } catch (error) {
    console.error('Error downloading PDF:', error);
    
    // User-friendly error message
    let errorMessage = 'Failed to download PDF report.';
    
    if (error.message.includes('404')) {
      errorMessage = 'Barangay not found. Please try again.';
    } else if (error.message.includes('500')) {
      errorMessage = 'Server error. Please contact support.';
    } else if (error.message.includes('Network')) {
      errorMessage = 'Network error. Check your internet connection.';
    }
    
    alert(`❌ ${errorMessage}\n\nDetails: ${error.message}`);
    
  } finally {
    setDownloadLoading(false);
  }
};
```

---

## 🎨 CSS STYLING SYSTEM

### File Structure

```
features/forecasting/styles.css       # Municipality & Barangay styles
features/insights/styles.css          # Model Insights styles
```

---

### Key CSS Classes

#### **Municipality Cards**

```css
/* styles.css */

/* Grid layout for municipality cards */
.municipalities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  padding: 24px;
}

/* Individual municipality card */
.municipality-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.municipality-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

/* Risk summary badges */
.risk-summary {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.risk-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 14px;
}

.risk-badge.risk-high {
  background: #ffebee;
  color: #d32f2f;
}

.risk-badge.risk-medium {
  background: #fff8e1;
  color: #f57c00;
}

.risk-badge.risk-low {
  background: #e8f5e9;
  color: #388e3c;
}

/* Barangay list items */
.barangay-list {
  margin-top: 16px;
}

.barangay-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: #f5f5f5;
  border-radius: 8px;
  border-left: 4px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.barangay-item:hover {
  background: #e0e0e0;
  transform: translateX(4px);
}

/* Risk-specific border colors */
.barangay-item.risk-high {
  border-left-color: #d32f2f;
}

.barangay-item.risk-medium {
  border-left-color: #f57c00;
}

.barangay-item.risk-low {
  border-left-color: #388e3c;
}
```

---

#### **Barangay Details Page**

```css
/* Metrics grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.metric {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.metric-label {
  display: block;
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.metric-value {
  display: block;
  font-size: 32px;
  font-weight: bold;
}

/* Forecast button */
.forecast-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: bold;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s;
}

.forecast-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.forecast-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Forecast grid */
.forecast-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.forecast-item {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  border: 2px solid #e0e0e0;
}

.forecast-date {
  display: block;
  font-weight: bold;
  color: #666;
  margin-bottom: 8px;
}

.forecast-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #FF9800;
}

/* Risk alert */
.risk-alert {
  padding: 20px;
  border-radius: 8px;
  margin: 24px 0;
  border-left: 6px solid;
}

.risk-alert.risk-high {
  background: #ffebee;
  border-left-color: #d32f2f;
  color: #b71c1c;
}

.risk-alert.risk-medium {
  background: #fff8e1;
  border-left-color: #f57c00;
  color: #e65100;
}

.risk-alert.risk-low {
  background: #e8f5e9;
  border-left-color: #388e3c;
  color: #1b5e20;
}

.risk-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.risk-icon {
  font-size: 32px;
}

.risk-level {
  font-size: 20px;
  font-weight: bold;
}

.risk-message {
  font-size: 16px;
  line-height: 1.6;
}
```

---

#### **Tab System**

```css
/* Tabs container */
.tabs-container {
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 24px;
}

.tabs {
  display: flex;
  gap: 8px;
}

.tab {
  padding: 12px 24px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 16px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.tab:hover {
  color: #333;
  background: #f5f5f5;
}

.tab.active {
  color: #667eea;
  border-bottom-color: #667eea;
  font-weight: bold;
}
```

---

#### **Loading States**

```css
/* Loading spinner */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error container */
.error-container {
  text-align: center;
  padding: 48px;
  background: #ffebee;
  border-radius: 12px;
  margin: 24px;
}

.error-container h2 {
  color: #d32f2f;
  margin-bottom: 16px;
}

.error-container button {
  margin-top: 24px;
  padding: 12px 24px;
  background: #d32f2f;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}
```

---

## 🎯 RISK LEVEL CALCULATION (FRONTEND)

### Why Calculate Risk in Frontend?

The backend calculates risk for the municipality list, but the frontend **re-calculates** risk when showing the forecast with specific context.

### Risk Calculation Logic

```javascript
// BarangayDetails.jsx
const calculateRiskLevel = (barangayData, forecastData) => {
  if (!barangayData || !barangayData.validation_data) {
    return null;
  }

  // 1. Get historical average from validation data
  const historicalAvg = barangayData.validation_data.reduce((sum, d) => sum + d.actual, 0) / 
                        barangayData.validation_data.length;

  // 2. Get forecast average
  const forecastAvg = forecastData && forecastData.predictions 
    ? forecastData.predictions.reduce((sum, d) => sum + d.predicted, 0) / forecastData.predictions.length
    : barangayData.next_month_prediction || 0;

  // 3. Get historical maximum
  const historicalMax = Math.max(...barangayData.validation_data.map(d => d.actual));

  // 4. Calculate thresholds
  const avgThreshold = historicalAvg * 1.2;  // 20% above average
  const maxThreshold = historicalMax * 0.8;  // 80% of historical max

  // 5. Determine risk level
  if (forecastAvg > maxThreshold) {
    return {
      level: 'HIGH',
      color: '#d32f2f',
      message: `⚠️ HIGH RISK: Forecast (${forecastAvg.toFixed(1)}) exceeds 80% of historical max (${historicalMax})`,
      icon: '🔴'
    };
  } else if (forecastAvg > avgThreshold) {
    return {
      level: 'MEDIUM',
      color: '#f57c00',
      message: `⚡ MEDIUM RISK: Forecast (${forecastAvg.toFixed(1)}) is 20% above historical average (${historicalAvg.toFixed(1)})`,
      icon: '🟡'
    };
  } else {
    return {
      level: 'LOW',
      color: '#388e3c',
      message: `✓ LOW RISK: Forecast (${forecastAvg.toFixed(1)}) is within normal range`,
      icon: '🟢'
    };
  }
};
```

### Usage in Component

```javascript
// BarangayDetails.jsx
const riskInfo = barangayData && showForecast 
  ? calculateRiskLevel(barangayData, forecastData) 
  : null;

return (
  <>
    {/* Show risk alert if HIGH or MEDIUM */}
    {showForecast && riskInfo && riskInfo.level !== 'LOW' && (
      <div className={`risk-alert risk-${riskInfo.level.toLowerCase()}`}>
        <div className="risk-header">
          <span className="risk-icon">{riskInfo.icon}</span>
          <span className="risk-level">{riskInfo.level} RISK ALERT</span>
        </div>
        <p className="risk-message">{riskInfo.message}</p>
      </div>
    )}
  </>
);
```

### Why Both Backend AND Frontend?

**Backend Risk Calculation:**
- Used for municipality list display
- Calculated once for all barangays
- Based on next 8 months forecast

**Frontend Risk Calculation:**
- Used for detailed barangay view
- Calculated with specific context (historical + forecast)
- Shows detailed explanation message

---

## 📑 TAB SYSTEM IMPLEMENTATION

### Tab State Management

```javascript
// BarangayDetails.jsx
function BarangayDetails() {
  const [activeTab, setActiveTab] = useState('forecast');  // Default tab
  
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    
    // Lazy load insights when switching to insights tab
    if (tab === 'insights' && !interpretabilityData) {
      fetchInterpretability();
    }
  };
  
  return (
    <>
      {/* Tab Buttons */}
      <div className="tabs-container">
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
      </div>
      
      {/* Tab Content */}
      {activeTab === 'forecast' && (
        <div className="forecast-tab-content">
          {/* Metrics, chart, forecast grid, etc. */}
        </div>
      )}
      
      {activeTab === 'insights' && (
        <div className="insights-tab-content">
          <ModelInsights 
            interpretabilityData={interpretabilityData} 
            loading={insightsLoading} 
          />
        </div>
      )}
    </>
  );
}
```

### Conditional Rendering

**Key Pattern:**
```javascript
{activeTab === 'forecast' && <ForecastContent />}
{activeTab === 'insights' && <InsightsContent />}
```

**Why not `display: none`?**
- ❌ `display: none` still renders components (slower)
- ✅ Conditional rendering doesn't mount components until needed
- ✅ Better performance, especially for heavy charts

---

## 🚀 DEPLOYMENT GUIDE

### Step 1: Build Production Bundle

```bash
# Navigate to frontend directory
cd PROTOTYPE_v2/frontend

# Install dependencies (if not already)
npm install

# Create production build
npm run build
```

**Result:** Creates `build/` folder with optimized static files.

---

### Step 2: Configure Backend for Production

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Development CORS (localhost only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Production: Serve React build folder
app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")
```

---

### Step 3: Run Production Server

```bash
# Start backend (serves both API and frontend)
cd PROTOTYPE_v2/backend
python main.py

# Access application
# Open browser: http://localhost:8000
```

**How it works:**
- Backend serves API endpoints at `/api/*`
- Backend serves React app at `/`
- Single server for both frontend and backend!

---

### Step 4: Environment Variables

Create `.env` file for configuration:

```bash
# .env
API_BASE_URL=http://localhost:8000
MODEL_DIR=../../saved_models_v2/Latest_FINALIZED_barangay_models_20251223_201700
PORT=8000
```

Load in React:

```javascript
// src/utils/constants.js
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
```

---

### Step 5: Testing Production Build

```bash
# Install serve (static file server)
npm install -g serve

# Serve production build
cd PROTOTYPE_v2/frontend/build
serve -s . -p 3000

# Open browser: http://localhost:3000
```

---

## 🔧 TROUBLESHOOTING GUIDE

### Problem 1: "Cannot connect to backend"

**Symptoms:**
- Frontend shows loading forever
- Console error: `Failed to fetch`

**Causes & Solutions:**

1. **Backend not running**
   ```bash
   # Start backend
   cd PROTOTYPE_v2/backend
   python main.py
   ```

2. **Wrong API URL**
   ```javascript
   // Check api.js
   const API_BASE_URL = 'http://localhost:8000';  // Must match backend port
   ```

3. **CORS error**
   ```python
   # Check main.py CORS settings
   allow_origins=["http://localhost:3000"]  # Must include frontend URL
   ```

---

### Problem 2: "Chart not displaying"

**Symptoms:**
- Page loads but chart is blank
- Console error: `Cannot read property 'map' of undefined`

**Causes & Solutions:**

1. **No data returned from backend**
   ```javascript
   // Add null checks
   if (!barangayData || !barangayData.training_data) {
     return <div>No chart data available</div>;
   }
   ```

2. **Recharts not installed**
   ```bash
   npm install recharts
   ```

3. **Data format mismatch**
   ```javascript
   // Check data structure
   console.log('Training data:', barangayData.training_data);
   // Should be: [{ date: '2022-01', actual: 3, predicted: 2.8 }, ...]
   ```

---

### Problem 3: "Tab switching not working"

**Symptoms:**
- Clicking tab doesn't change content

**Cause:** State not updating properly

**Solution:**
```javascript
// Check activeTab state
const [activeTab, setActiveTab] = useState('forecast');

// Ensure onClick updates state
<button onClick={() => setActiveTab('insights')}>
  🔍 Model Insights
</button>

// Ensure conditional rendering uses state
{activeTab === 'insights' && <ModelInsights />}
```

---

### Problem 4: "Forecast button does nothing"

**Symptoms:**
- Clicking "Show Future Forecast" has no effect

**Causes & Solutions:**

1. **Function not defined**
   ```javascript
   const handleForecastClick = async () => {
     if (!forecastData) {
       await fetchForecast();  // Make sure this is called
     }
     setShowForecast(!showForecast);
   };
   ```

2. **Hook not returning function**
   ```javascript
   // Check hooks.js
   return { 
     forecastData, 
     loading, 
     fetchForecast: fetchForecastData  // Make sure this is returned
   };
   ```

---

### Problem 5: "Download not working"

**Symptoms:**
- Clicking download button does nothing
- Or downloads corrupted file

**Causes & Solutions:**

1. **Backend not returning blob**
   ```python
   # Check main.py
   return StreamingResponse(
       pdf_buffer,
       media_type="application/pdf",
       headers={"Content-Disposition": f"attachment; filename={filename}"}
   )
   ```

2. **Frontend not handling blob correctly**
   ```javascript
   const blob = await downloadPDFReport(municipality, barangay);
   const url = window.URL.createObjectURL(blob);  // Must create URL
   ```

3. **Browser blocking download**
   - Check browser console for security errors
   - Try different browser

---

## 💡 BEST PRACTICES & TIPS

### 1. **Lazy Loading**

✅ **Do:** Load data only when needed
```javascript
// Good: Load forecast when user clicks button
const handleForecastClick = async () => {
  if (!forecastData) {
    await fetchForecast();
  }
};
```

❌ **Don't:** Load all data on page load
```javascript
// Bad: Loads even if user doesn't view
useEffect(() => {
  fetchForecast();
  fetchInterpretability();
  // ... loads everything
}, []);
```

---

### 2. **Loading States**

✅ **Do:** Show feedback during loading
```javascript
if (loading) return <div className="spinner">Loading...</div>;
```

❌ **Don't:** Leave user wondering
```javascript
// Bad: No feedback
const { data } = useFetch();
return <div>{data?.value}</div>;  // Blank while loading
```

---

### 3. **Error Handling**

✅ **Do:** Handle all error cases
```javascript
try {
  await fetchData();
} catch (error) {
  console.error('Error:', error);
  setError(error.message);
  // Show user-friendly message
}
```

❌ **Don't:** Ignore errors
```javascript
// Bad: No error handling
await fetchData();  // What if it fails?
```

---

### 4. **Null Checks**

✅ **Do:** Check data exists before using
```javascript
if (!barangayData) return <div>No data</div>;
return <div>{barangayData.metrics.mae}</div>;
```

❌ **Don't:** Access without checking
```javascript
// Bad: Crashes if null
return <div>{barangayData.metrics.mae}</div>;
```

---

### 5. **Memoization for Charts**

✅ **Do:** Memoize expensive chart data
```javascript
const chartData = useMemo(() => {
  return [...trainingData, ...validationData, ...forecastData];
}, [trainingData, validationData, forecastData]);
```

❌ **Don't:** Recreate on every render
```javascript
// Bad: Recreates array every render
const chartData = [...trainingData, ...validationData, ...forecastData];
```

---

### 6. **Clean Up Resources**

✅ **Do:** Clean up URLs and timers
```javascript
const url = window.URL.createObjectURL(blob);
// ... use URL
window.URL.revokeObjectURL(url);  // Clean up!
```

❌ **Don't:** Leave memory leaks
```javascript
// Bad: URL never cleaned up
const url = window.URL.createObjectURL(blob);
// ... no cleanup
```

---

## 📋 CHECKLIST: Production Ready

### Code Quality
- [ ] All console.log() statements removed (or behind debug flag)
- [ ] No hardcoded values (use constants/config)
- [ ] Error handling in all API calls
- [ ] Loading states for all async operations
- [ ] Null checks before accessing data

### Performance
- [ ] Lazy loading for forecast and insights
- [ ] Memoization for expensive calculations
- [ ] Conditional rendering (not `display: none`)
- [ ] Optimized images/assets

### User Experience
- [ ] Loading spinners during data fetches
- [ ] Error messages are user-friendly
- [ ] Success feedback for downloads
- [ ] Responsive design (mobile-friendly)
- [ ] Keyboard navigation support

### Testing
- [ ] Test all municipalities load correctly
- [ ] Test barangay details for each municipality
- [ ] Test forecast button works
- [ ] Test tab switching works
- [ ] Test downloads work
- [ ] Test error cases (backend down, 404, etc.)

### Deployment
- [ ] Production build created (`npm run build`)
- [ ] Environment variables configured
- [ ] CORS configured for production domain
- [ ] Backend serves static files
- [ ] SSL certificate (if deploying publicly)

---

## 🎓 SUMMARY

### How Frontend Works (Complete Picture)

1. **User opens app** → React loads `MunicipalityList`
2. **Hook fetches municipalities** → Backend calculates risk levels
3. **Frontend displays cards** → Sorted by risk (red, yellow, green)
4. **User clicks barangay** → Navigate to `BarangayDetails`
5. **Hook fetches barangay data** → Backend adds seasonal features, predicts
6. **Frontend shows metrics + chart** → Historical data visualized
7. **User clicks "Show Forecast"** → Hook fetches 8-month predictions
8. **Frontend updates chart** → Orange line added
9. **User switches to "Insights"** → Hook fetches decomposition
10. **Frontend shows interpretability** → Trend, seasonality, holidays charts

### Key Principles

✅ **Frontend displays, Backend computes**  
✅ **No preprocessing in frontend** - just pass municipality/barangay  
✅ **Lazy loading** - fetch data when needed  
✅ **Error handling** - always catch and show feedback  
✅ **Loading states** - never leave user wondering  
✅ **Responsive design** - works on all screen sizes

---

## 🎉 CONGRATULATIONS!

You now understand:
- ✅ How frontend and backend communicate
- ✅ How data flows from API to charts
- ✅ How model insights are visualized
- ✅ How to handle errors and loading states
- ✅ How to deploy the application

**Next Steps:**
1. Experiment with the code
2. Add new features
3. Customize styling
4. Deploy to production

---

**End of Frontend Documentation (Part 2)**

*Generated on December 23, 2025*
