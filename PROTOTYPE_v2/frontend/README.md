# 🐕 Animal Bite Incident Forecasting Dashboard

A modern React-based dashboard for forecasting animal bite incidents using a hybrid NeuralProphet + XGBoost machine learning model. This application provides comprehensive forecasting, risk assessment, and model interpretability features for public health decision-makers in Rizal Province, Philippines.

## 🚀 Features

- **Municipality & Barangay Forecasting**: Browse 40+ barangays across 4 municipalities with real-time predictions
- **8-Month Ahead Forecasts**: Future predictions with confidence levels and risk classifications
- **Model Interpretability**: Decompose predictions into trend, seasonality, weather, vaccination, and holiday effects
- **Risk Assessment**: Automatic classification (High/Medium/Low) with actionable recommendations
- **Interactive Charts**: Visualize historical data, predictions, and forecasts using Recharts
- **Comprehensive Reports**: Download CSV and PDF reports for stakeholders
- **Weather Integration**: Incorporate temperature, humidity, and precipitation impacts
- **Vaccination Tracking**: Measure the effect of mass vaccination campaigns

## 📁 Project Structure

```
src/
├── index.jsx                          # Application entry point (mounts BrowserRouter)
├── app/
│   ├── App.jsx                        # Root app component with layout
│   └── AppRoutes.jsx                  # Main routing configuration
├── features/
│   ├── forecasting/
│   │   ├── ForecastingRoutes.jsx      # Nested routes for forecasting feature
│   │   ├── MunicipalityList.jsx       # List of municipalities with barangays
│   │   ├── BarangayDetails.jsx        # Detailed forecast view for single barangay
│   │   ├── components/
│   │   │   ├── MetricsHelpBanner.jsx  # Educational metrics explanation
│   │   │   └── RiskExplanation.jsx    # Risk level guide
│   │   ├── hooks.js                   # Custom React hooks (useMunicipalities, useBarangayData, etc.)
│   │   ├── api.js                     # API functions for forecasting endpoints
│   │   └── styles.css                 # Forecasting feature styles
│   ├── insights/
│   │   ├── ModelInsights.jsx          # Model interpretability component
│   │   └── ModelInsights.css          # Insights styling
│   └── home/
│       ├── Home.jsx                   # Landing page with welcome content
│       └── Home.css                   # Home page styles
├── components/
│   ├── Layout/
│   │   ├── MainLayout.jsx             # Main layout wrapper with header and footer
│   │   ├── AppHeader.jsx              # Navigation header
│   │   └── Layout.css                 # Layout styles
│   └── charts/
│       └── BarangayChart.jsx          # Recharts line chart component
├── api/
│   └── axiosInstance.js               # Axios configuration with interceptors
├── utils/
│   └── formatDate.js                  # Date formatting utilities
└── styles/
    └── App.css                        # Global styles
```

## 🛠️ Technology Stack

- **Frontend Framework**: React 18.2.0
- **Routing**: React Router DOM 6.20.0
- **HTTP Client**: Axios 1.6.0
- **Charts**: Recharts 2.10.0
- **Build Tool**: Create React App (react-scripts 5.0.1)
- **Styling**: CSS (modular approach with feature-based organization)

## 📋 Prerequisites

- **Node.js**: v16.0.0 or higher
- **npm**: v7.0.0 or higher
- **Backend API**: Running FastAPI backend (default: http://localhost:8000)

## 🔧 Installation

### 1. Clone the repository

```powershell
git clone <repository-url>
cd PROTOTYPE_v2/frontend
```

### 2. Install dependencies

```powershell
npm install
```

### 3. Configure environment variables

Create a `.env` file in the frontend root directory:

```env
# API Base URL (backend server)
REACT_APP_API_URL=http://localhost:8000
```

**Note**: If you don't create a `.env` file, the app will default to `http://localhost:8000`.

### 4. Start the development server

```powershell
npm start
```

The app will open automatically at http://localhost:3000

## 📦 Available Scripts

### Development

```powershell
npm start          # Start development server (http://localhost:3000)
npm run build      # Create production build in /build folder
npm test           # Run tests
npm run eject      # Eject from Create React App (irreversible!)
```

## 🔌 API Endpoints Used

The frontend expects the following backend API endpoints:

### Municipalities & Barangays

```
GET /api/municipalities
Response: {
  municipalities: [
    {
      municipality: "ANTIPOLO",
      total_barangays: 10,
      avg_mae: 1.23,
      risk_summary: { HIGH: 2, MEDIUM: 3, LOW: 5 },
      barangays: [
        {
          name: "BARANGAY_NAME",
          risk_level: "HIGH",
          risk_icon: "🔴",
          predicted_next: 5
        }
      ]
    }
  ]
}
```

### Barangay Details

```
GET /api/barangay/{municipality}/{barangay}
Response: {
  barangay: {
    metrics: { mae: 1.5, rmse: 2.1, mase: 0.8 },
    next_month_prediction: 5,
    training_data: [...],
    validation_data: [...],
    has_chart_data: true
  }
}
```

### Forecast

```
GET /api/forecast/{municipality}/{barangay}?months=8
Response: {
  forecast: {
    forecast_start: "2024-11-01",
    forecast_end: "2025-06-01",
    predictions: [
      { date: "2024-11-01", predicted: 4 }
    ]
  }
}
```

### Model Interpretability

```
GET /api/interpretability/{municipality}/{barangay}
Response: {
  interpretability: {
    trend: { dates: [...], values: [...], description: "..." },
    seasonality: { dates: [...], values: [...], description: "..." },
    holidays: { has_holidays: true, values: [...], significant_effects: [...] },
    weather_regressors: { columns: [...], data: {...}, description: "..." },
    vaccination_regressors: { columns: [...], data: {...}, description: "..." },
    seasonal_regressors: { columns: [...], data: {...}, description: "..." },
    feature_importance: { top_3_features: [...], description: "..." },
    model_config: { ... }
  }
}
```

### Report Downloads

```
GET /api/report/csv/{municipality}/{barangay}       # CSV report
GET /api/report/pdf/{municipality}/{barangay}       # PDF report
GET /api/report/insights/{municipality}/{barangay}  # Insights PDF
```

All download endpoints return binary file blobs.

## 🎨 Customization

### Changing the API URL

1. **Development**: Update `.env` file:
   ```env
   REACT_APP_API_URL=http://your-api-url:port
   ```

2. **Production**: Set environment variable during build:
   ```powershell
   $env:REACT_APP_API_URL="https://production-api.com"; npm run build
   ```

### Modifying Forecast Horizon

In `BarangayDetails.jsx`, change the `months` parameter:

```javascript
const { forecastData, loading: forecastLoading, fetchForecast } = useForecast(
  municipality, 
  barangay, 
  12  // Change from 8 to 12 months
);
```

### Styling

Each feature has its own CSS file:
- Global styles: `src/styles/App.css`
- Layout: `src/components/Layout/Layout.css`
- Forecasting: `src/features/forecasting/styles.css`
- Insights: `src/features/insights/ModelInsights.css`
- Home: `src/features/home/Home.css`

## 🔐 Security Considerations

### Current Implementation

- **Token Storage**: Currently not using authentication tokens
- **API Calls**: Direct HTTP requests without authentication

### Recommended for Production

1. **Authentication**: Implement JWT token-based authentication
2. **Token Storage**: Use HTTP-only cookies instead of localStorage
3. **HTTPS**: Always use HTTPS in production
4. **Environment Variables**: Never commit `.env` files to version control
5. **CORS Configuration**: Configure proper CORS policies on backend

Example with authentication:

```javascript
// In api/axiosInstance.js (already supports tokens)
const token = localStorage.getItem('token');
if (token) {
  config.headers.Authorization = `Bearer ${token}`;
}
```

## 📖 Usage Guide

### For Developers

1. **Adding a New Feature**:
   - Create a new folder in `src/features/`
   - Add components, hooks, api, and styles
   - Create a routes file (e.g., `YourFeatureRoutes.jsx`)
   - Import and add route to `src/app/AppRoutes.jsx`

2. **Adding API Endpoints**:
   - Add function to appropriate `api.js` file
   - Create custom hook in `hooks.js` if needed
   - Use the hook in your component

3. **Styling**:
   - Use feature-specific CSS files
   - Follow existing naming conventions
   - Keep responsive design in mind (`@media` queries)

### For Users

1. **Navigate to Forecasting**: Click "📊 Forecasting" in header
2. **Select a Barangay**: Click on any barangay card (color-coded by risk)
3. **View Metrics**: See MAE, RMSE, MASE performance metrics
4. **Generate Forecast**: Click "🔮 Show Future Forecast" button
5. **Download Reports**: Use CSV/PDF buttons for offline analysis
6. **Check Model Insights**: Switch to "🔍 Model Insights" tab
7. **Understand Predictions**: View trend, seasonality, weather, and vaccination impacts

## 🐛 Troubleshooting

### "Cannot connect to API"

- Ensure backend server is running on http://localhost:8000
- Check `.env` file has correct `REACT_APP_API_URL`
- Verify CORS is enabled on backend

### "Module not found" errors

```powershell
rm -r node_modules
rm package-lock.json
npm install
```

### Build fails

```powershell
npm run build
```

If errors persist, check Node.js version:

```powershell
node --version   # Should be v16+
```

### Charts not displaying

- Check browser console for errors
- Verify `recharts` is installed: `npm list recharts`
- Ensure data format matches expected structure

## 📊 Data Flow

```
User Action
    ↓
React Component
    ↓
Custom Hook (hooks.js)
    ↓
API Function (api.js)
    ↓
Axios Instance (with interceptors)
    ↓
Backend API
    ↓
Response
    ↓
React State Update
    ↓
UI Re-render
```

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Follow existing code structure and naming conventions
3. Test your changes thoroughly
4. Commit with descriptive messages
5. Create a pull request

## 📝 License

[Your License Here]

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- NeuralProphet library for time series forecasting
- XGBoost for gradient boosting
- Recharts for beautiful visualizations
- FastAPI for the backend framework
- React team for the amazing frontend library

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Contact: your-email@example.com

---

**Built with ❤️ for public health decision-makers**
