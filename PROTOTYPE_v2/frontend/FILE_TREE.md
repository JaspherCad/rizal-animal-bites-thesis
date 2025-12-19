# 📂 Complete Project Structure

## Visual File Tree

```
PROTOTYPE_v2/frontend/
│
├── 📄 package.json                     # Dependencies with react-router-dom@^6.20.0
├── 📄 .env.example                     # Environment variable template
├── 📄 README.md                        # 📖 FULL DOCUMENTATION (read first!)
├── 📄 QUICK_START.md                   # 🚀 3-minute setup guide
├── 📄 MIGRATION_GUIDE.md               # 🔄 Old → New structure guide
├── 📄 REFACTORING_SUMMARY.md           # 📊 Complete refactoring overview
│
├── 📁 public/
│   └── index.html                      # HTML template
│
└── 📁 src/
    │
    ├── 📄 index.jsx                    # ⚡ ENTRY POINT (mounts BrowserRouter)
    │
    ├── 📁 app/                         # 🏗️ APPLICATION CORE
    │   ├── App.jsx                     # Root component with MainLayout
    │   └── AppRoutes.jsx               # Route definitions (/, /forecasting/*, 404)
    │
    ├── 📁 features/                    # 🎯 FEATURE MODULES
    │   │
    │   ├── 📁 forecasting/             # 📊 Forecasting Feature
    │   │   ├── ForecastingRoutes.jsx   # Nested routes (/forecasting/*)
    │   │   ├── MunicipalityList.jsx    # Municipality grid with barangays
    │   │   ├── BarangayDetails.jsx     # Detailed forecast view
    │   │   │
    │   │   ├── 📁 components/
    │   │   │   ├── MetricsHelpBanner.jsx    # MAE/RMSE/MASE explanation
    │   │   │   └── RiskExplanation.jsx      # Risk level guide
    │   │   │
    │   │   ├── hooks.js                # Custom hooks:
    │   │   │                           #   - useMunicipalities()
    │   │   │                           #   - useBarangayData()
    │   │   │                           #   - useForecast()
    │   │   │                           #   - useInterpretability()
    │   │   │
    │   │   ├── api.js                  # API functions:
    │   │   │                           #   - getMunicipalities()
    │   │   │                           #   - getBarangayData()
    │   │   │                           #   - getForecast()
    │   │   │                           #   - getInterpretability()
    │   │   │                           #   - downloadCSVReport()
    │   │   │                           #   - downloadPDFReport()
    │   │   │                           #   - downloadInsightsPDF()
    │   │   │
    │   │   └── styles.css              # Feature-specific styles
    │   │
    │   ├── 📁 insights/                # 🔍 Model Insights Feature
    │   │   ├── ModelInsights.jsx       # Interpretability component:
    │   │   │                           #   - Trend decomposition
    │   │   │                           #   - Seasonality analysis
    │   │   │                           #   - Holiday effects
    │   │   │                           #   - Weather regressors
    │   │   │                           #   - Vaccination impact
    │   │   │                           #   - Feature importance
    │   │   │
    │   │   └── ModelInsights.css       # Insights styling
    │   │
    │   └── 📁 home/                    # 🏠 Home Page
    │       ├── Home.jsx                # Landing page:
    │       │                           #   - Welcome message
    │       │                           #   - Feature cards
    │       │                           #   - Getting started
    │       │                           #   - Tech stack
    │       │                           #   - Data coverage
    │       │
    │       └── Home.css                # Home page styles
    │
    ├── 📁 components/                  # ♻️ REUSABLE COMPONENTS
    │   │
    │   ├── 📁 Layout/
    │   │   ├── MainLayout.jsx          # Header + main content + footer
    │   │   ├── AppHeader.jsx           # Navigation header (Home, Forecasting)
    │   │   └── Layout.css              # Layout styles
    │   │
    │   └── 📁 charts/
    │       └── BarangayChart.jsx       # Recharts line chart:
    │                                   #   - Training data (black line)
    │                                   #   - Validation data (blue dashed)
    │                                   #   - Forecast data (red dashed)
    │                                   #   - Reference lines for splits
    │
    ├── 📁 api/
    │   └── axiosInstance.js            # Axios configuration:
    │                                   #   - baseURL from env
    │                                   #   - Request interceptor (auth token)
    │                                   #   - Response interceptor (401 handling)
    │
    ├── 📁 utils/
    │   └── formatDate.js               # Date utilities:
    │                                   #   - formatDate(isoDate, format)
    │                                   #   - formatMonthYear(dateString)
    │                                   #   - getRelativeTime(dateString)
    │
    ├── 📁 styles/
    │   └── App.css                     # Global styles (reset, body, loading)
    │
    └── 📁 OLD FILES (can be deleted after testing)
        ├── App.js                      # ❌ OLD monolithic component
        ├── App.css                     # ❌ OLD massive CSS file
        ├── BarangayChart.js            # ❌ OLD chart (now in components/)
        ├── ModelInsights.js            # ❌ OLD insights (now in features/)
        ├── ModelInsights.css           # ❌ OLD CSS (now in features/)
        └── index.js                    # ❌ OLD entry (replaced by index.jsx)

```

---

## 🎯 Component Hierarchy

```
index.jsx
└── <BrowserRouter>
    └── <App>                           // app/App.jsx
        └── <MainLayout>                // components/Layout/MainLayout.jsx
            ├── <AppHeader>             // components/Layout/AppHeader.jsx
            │   └── Navigation Links
            │
            ├── <main>
            │   └── <AppRoutes>         // app/AppRoutes.jsx
            │       │
            │       ├── Route: "/"
            │       │   └── <Home>                      // features/home/Home.jsx
            │       │
            │       ├── Route: "/forecasting/*"
            │       │   └── <ForecastingRoutes>         // features/forecasting/ForecastingRoutes.jsx
            │       │       │
            │       │       ├── Route: index
            │       │       │   └── <MunicipalityList>  // features/forecasting/MunicipalityList.jsx
            │       │       │
            │       │       └── Route: ":municipality/:barangay"
            │       │           └── <BarangayDetails>   // features/forecasting/BarangayDetails.jsx
            │       │               ├── <MetricsHelpBanner>
            │       │               ├── <RiskExplanation>
            │       │               ├── <BarangayChart>
            │       │               └── <ModelInsights>
            │       │
            │       └── Route: "*"
            │           └── <NotFound>                  // 404 Page
            │
            └── <footer>
```

---

## 📊 Data Flow Diagram

```
User Interaction
      ↓
[React Component]
      ↓
[Custom Hook]                    Example: useBarangayData(municipality, barangay)
      ├─ useState                  - data, loading, error
      ├─ useEffect
      └─ API Call
            ↓
[API Function]                   Example: getBarangayData(municipality, barangay)
      ↓
[axios Instance]                 - Adds auth token
      ├─ Request Interceptor     - Sets headers
      └─ Response Interceptor    - Handles 401
            ↓
[Backend API]                    http://localhost:8000/api/barangay/...
      ↓
[Response]
      ↓
[React State Update]
      ↓
[UI Re-render]
```

---

## 🔗 Import Path Examples

### ✅ Correct Import Paths (New Structure)

```javascript
// In features/forecasting/BarangayDetails.jsx
import { useBarangayData, useForecast } from './hooks';
import { downloadCSVReport } from './api';
import BarangayChart from '../../components/charts/BarangayChart';
import ModelInsights from '../insights/ModelInsights';
import MetricsHelpBanner from './components/MetricsHelpBanner';

// In app/AppRoutes.jsx
import Home from '../features/home/Home';
import ForecastingRoutes from '../features/forecasting/ForecastingRoutes';

// In components/Layout/MainLayout.jsx
import AppHeader from './AppHeader';
import './Layout.css';

// In features/forecasting/api.js
import axiosInstance from '../../api/axiosInstance';
```

---

## 📝 File Purposes at a Glance

| File | Purpose | Lines | Key Contents |
|------|---------|-------|--------------|
| **index.jsx** | Entry point | ~15 | Mounts BrowserRouter → App |
| **app/App.jsx** | Root component | ~20 | MainLayout → AppRoutes |
| **app/AppRoutes.jsx** | Route config | ~50 | /, /forecasting/*, 404 |
| **features/forecasting/MunicipalityList.jsx** | Municipality grid | ~70 | useMunicipalities hook |
| **features/forecasting/BarangayDetails.jsx** | Forecast details | ~300 | Multiple hooks, tabs, charts |
| **features/forecasting/hooks.js** | Custom hooks | ~150 | 4 hooks for data fetching |
| **features/forecasting/api.js** | API functions | ~100 | 8 API endpoint wrappers |
| **features/insights/ModelInsights.jsx** | Interpretability | ~450 | Trend/seasonality/weather charts |
| **features/home/Home.jsx** | Landing page | ~100 | Welcome, features, info |
| **components/Layout/MainLayout.jsx** | Layout wrapper | ~30 | Header + main + footer |
| **components/Layout/AppHeader.jsx** | Navigation | ~30 | Logo, nav links |
| **components/charts/BarangayChart.jsx** | Chart component | ~130 | Recharts line chart |
| **api/axiosInstance.js** | HTTP config | ~50 | Axios with interceptors |
| **utils/formatDate.js** | Date utils | ~70 | 3 formatting functions |

---

## 🎨 CSS Organization

```
Global Styles
└── styles/App.css                     # Body, reset, loading states

Layout Styles
└── components/Layout/Layout.css       # Header, nav, footer

Feature Styles
├── features/forecasting/styles.css    # Municipality list, barangay details
├── features/insights/ModelInsights.css # Insights charts, tooltips
└── features/home/Home.css             # Home page, cards, badges
```

---

## 🧩 Key Patterns Used

### 1. Custom Hooks Pattern
```javascript
export const useBarangayData = (municipality, barangay) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    // Fetch logic
  }, [municipality, barangay]);
  
  return { data, loading, error, refetch };
};
```

### 2. API Layer Pattern
```javascript
export const getBarangayData = async (municipality, barangay) => {
  const response = await axiosInstance.get(
    `/api/barangay/${encodeURIComponent(municipality)}/${encodeURIComponent(barangay)}`
  );
  return response.data;
};
```

### 3. Nested Routing Pattern
```javascript
<Route path="/forecasting/*" element={<ForecastingRoutes />} />

// In ForecastingRoutes.jsx
<Routes>
  <Route index element={<MunicipalityList />} />
  <Route path=":municipality/:barangay" element={<BarangayDetails />} />
</Routes>
```

### 4. Feature-Based Organization
```
features/[feature-name]/
├── [Feature]Routes.jsx        # Routes
├── [Component1].jsx           # Components
├── [Component2].jsx
├── components/                # Sub-components
├── hooks.js                   # Custom hooks
├── api.js                     # API calls
└── styles.css                 # Styles
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Complete documentation with setup, API, usage |
| **QUICK_START.md** | 3-minute setup guide |
| **MIGRATION_GUIDE.md** | Old → New structure explanation |
| **REFACTORING_SUMMARY.md** | Overview of all changes |
| **FILE_TREE.md** | This file - visual structure guide |

---

## ✅ Testing Checklist by Feature

### Home Feature
- [ ] Home page loads at `/`
- [ ] Feature cards display
- [ ] Navigation links work

### Forecasting Feature
- [ ] Municipality list loads at `/forecasting`
- [ ] Barangay cards are clickable
- [ ] URL changes when clicking barangay
- [ ] Metrics display correctly
- [ ] Forecast button works
- [ ] Risk alert appears
- [ ] Charts render
- [ ] Downloads work (CSV, PDF)

### Insights Feature
- [ ] Model insights tab loads
- [ ] Trend chart renders
- [ ] Seasonality chart renders
- [ ] Holiday effects show (if available)
- [ ] Weather chart shows (if available)
- [ ] Vaccination chart shows (if available)
- [ ] Feature importance displays
- [ ] Insights PDF downloads

### Layout & Navigation
- [ ] Header shows on all pages
- [ ] Footer shows on all pages
- [ ] Navigation links work
- [ ] Browser back/forward work
- [ ] 404 page shows for invalid URLs

---

**This document provides a complete visual overview of the project structure!**

Refer to `README.md` for detailed setup instructions and `MIGRATION_GUIDE.md` for understanding the refactoring changes.
