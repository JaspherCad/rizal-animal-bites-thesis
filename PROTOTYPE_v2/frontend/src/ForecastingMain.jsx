import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import BarangayChart from './BarangayChart';
import ModelInsights from './ModelInsights';
import RizalMap from './RizalMap';
import LeafletGISMap from './LeafletGISMap';

const API_URL = 'http://localhost:8000';

function ForecastingMain() {
  const [municipalities, setMunicipalities] = useState([]);
  const [selectedMun, setSelectedMun] = useState(null);
  const [selectedBarangay, setSelectedBarangay] = useState(null);
  const [barangayData, setBarangayData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [showForecast, setShowForecast] = useState(false);
  const [interpretabilityData, setInterpretabilityData] = useState(null);
  const [weatherInsights, setWeatherInsights] = useState(null);
  const [activeTab, setActiveTab] = useState('forecast');
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('gis'); // 'gis', 'svg', or 'list'

  useEffect(() => {
    fetchMunicipalities();
  }, []);

  const fetchMunicipalities = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/municipalities`);
      setMunicipalities(response.data.municipalities);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching municipalities:', error);
      setLoading(false);
    }
  };

  const handleBarangayClick = async (municipality, barangay) => {
    setLoading(true);
    setShowForecast(false);
    setForecastData(null);
    setInterpretabilityData(null);
    setActiveTab('forecast');
    try {
      const response = await axios.get(
        `${API_URL}/api/barangay/${municipality}/${barangay}`
      );
      setBarangayData(response.data.barangay);
      setSelectedBarangay(barangay);
      setSelectedMun(municipality);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching barangay data:', error);
      setLoading(false);
    }
  };

  const handleMunicipalityClickFromMap = (municipalityName) => {
    // Find the municipality in the list and scroll to it
    const munData = municipalities.find(m => m.municipality === municipalityName);
    if (munData && munData.barangays.length > 0) {
      // Automatically select the first barangay with highest predicted cases
      const topBarangay = munData.barangays[0]; // Already sorted by predicted_next in API
      handleBarangayClick(municipalityName, topBarangay.name);
      
      // Scroll to barangay details
      setTimeout(() => {
        const detailsSection = document.querySelector('.barangay-details');
        if (detailsSection) {
          detailsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    }
  };

  const handleForecastClick = async () => {
    if (!selectedMun || !selectedBarangay) return;
    
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_URL}/api/forecast/${selectedMun}/${selectedBarangay}?months=8`
      );
      setForecastData(response.data.forecast);
      setShowForecast(true);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching forecast:', error);
      setLoading(false);
    }
  };

  const fetchInterpretability = async () => {
    if (!selectedMun || !selectedBarangay) return;
    
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_URL}/api/interpretability/${selectedMun}/${selectedBarangay}`
      );
      setInterpretabilityData(response.data.interpretability);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching interpretability:', error);
      setLoading(false);
    }
  };

  const fetchWeatherInsights = async () => {
    if (!selectedMun || !selectedBarangay) return;
    
    try {
      const response = await axios.get(
        `${API_URL}/api/weather-insights/${selectedMun}/${selectedBarangay}`
      );
      setWeatherInsights(response.data);
    } catch (error) {
      console.error('Error fetching weather insights:', error);
      setWeatherInsights(null);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'insights') {
      if (!interpretabilityData) {
        fetchInterpretability();
      }
      if (!weatherInsights) {
        fetchWeatherInsights();
      }
    }
  };

  // Download CSV report
  const handleDownloadCSV = async () => {
    if (!selectedMun || !selectedBarangay) return;
    
    try {
      // Encode URL components properly
      const encodedMun = encodeURIComponent(selectedMun);
      const encodedBarangay = encodeURIComponent(selectedBarangay);
      
      const response = await fetch(
        `${API_URL}/api/report/csv/${encodedMun}/${encodedBarangay}`
      );
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to generate CSV report: ${errorText}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rabies_forecast_${selectedMun}_${selectedBarangay}_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading CSV:', error);
      alert(`Failed to download CSV report: ${error.message}`);
    }
  };

  // Download PDF report
  const handleDownloadPDF = async () => {
    if (!selectedMun || !selectedBarangay) return;
    
    try {
      // Encode URL components properly
      const encodedMun = encodeURIComponent(selectedMun);
      const encodedBarangay = encodeURIComponent(selectedBarangay);
      
      const response = await fetch(
        `${API_URL}/api/report/pdf/${encodedMun}/${encodedBarangay}`
      );
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to generate PDF report: ${errorText}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rabies_forecast_${selectedMun}_${selectedBarangay}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert(`Failed to download PDF report: ${error.message}`);
    }
  };

  // Download Model Insights PDF
  const handleDownloadInsightsPDF = async () => {
    if (!selectedMun || !selectedBarangay) return;
    
    try {
      const encodedMun = encodeURIComponent(selectedMun);
      const encodedBarangay = encodeURIComponent(selectedBarangay);
      
      const response = await fetch(
        `${API_URL}/api/report/insights-pdf/${encodedMun}/${encodedBarangay}`
      );
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to generate Insights PDF: ${errorText}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rabies_model_insights_${selectedMun}_${selectedBarangay}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading Insights PDF:', error);
      alert(`Failed to download Insights PDF: ${error.message}`);
    }
  };

  // Calculate risk level based on historical and forecast data
  const calculateRiskLevel = (barangayData, forecastData) => {
    if (!barangayData || !barangayData.validation_data) return null;

    // Get historical average from validation data
    const historicalAvg = barangayData.validation_data.reduce((sum, d) => sum + d.actual, 0) / 
                          barangayData.validation_data.length;

    // Get forecast average if available
    const forecastAvg = forecastData && forecastData.predictions 
      ? forecastData.predictions.reduce((sum, d) => sum + d.predicted, 0) / forecastData.predictions.length
      : barangayData.next_month_prediction || 0;

    // Get max value from validation
    const historicalMax = Math.max(...barangayData.validation_data.map(d => d.actual));

    // Risk thresholds
    const avgThreshold = historicalAvg * 1.2; // 20% above average
    const maxThreshold = historicalMax * 0.8;  // 80% of historical max

    // Determine risk level
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

  const riskInfo = barangayData && (showForecast ? calculateRiskLevel(barangayData, forecastData) : null);

  if (loading && municipalities.length === 0) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="App">
      <header className="header">
        <h1>ANIMAL BITE INCIDENT Forecasting Dashboard</h1>
        <p>NeuralProphet + XGBoost Hybrid Model</p>
      </header>

      <div className="container">
        {/* View Mode Toggle */}
        {!loading && municipalities.length > 0 && (
          <div className="view-mode-toggle">
            <button 
              className={`toggle-btn ${viewMode === 'gis' ? 'active' : ''}`}
              onClick={() => setViewMode('gis')}
            >
              🌐 GIS Map
            </button>
            <button 
              className={`toggle-btn ${viewMode === 'svg' ? 'active' : ''}`}
              onClick={() => setViewMode('svg')}
            >
              🗺️ Simple Map
            </button>
            <button 
              className={`toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              📋 List View
            </button>
          </div>
        )}

        {/* GIS Map View (Leaflet with Real Boundaries) */}
        {!loading && municipalities.length > 0 && viewMode === 'gis' && (
          <LeafletGISMap 
            municipalities={municipalities} 
            onMunicipalityClick={handleMunicipalityClickFromMap}
          />
        )}

        {/* Interactive SVG Rizal Province Map */}
        {!loading && municipalities.length > 0 && viewMode === 'svg' && (
          <RizalMap 
            municipalities={municipalities} 
            onMunicipalityClick={handleMunicipalityClickFromMap}
          />
        )}

        {/* Municipality List View */}
        {viewMode === 'list' && (
          <div className="municipalities-grid">
          {municipalities.map((mun) => (
            <div key={mun.municipality} className="municipality-card">
              <h2>{mun.municipality}</h2>
              <p className="stats">
                <strong>{mun.total_barangays}</strong> Barangays | 
                <strong> MAE: {mun.avg_mae}</strong>
              </p>
              
              {/* Risk Summary */}
              {mun.risk_summary && (
                <div className="risk-summary">
                  <span className="risk-badge risk-high">🔴 {mun.risk_summary.HIGH || 0}</span>
                  <span className="risk-badge risk-medium">🟡 {mun.risk_summary.MEDIUM || 0}</span>
                  <span className="risk-badge risk-low">🟢 {mun.risk_summary.LOW || 0}</span>
                </div>
              )}
              
              <div className="barangay-list">
                {mun.barangays.map((brgy) => (
                  <div
                    key={brgy.name}
                    className={`barangay-item risk-${brgy.risk_level?.toLowerCase() || 'unknown'}`}
                    onClick={() => handleBarangayClick(mun.municipality, brgy.name)}
                  >
                    <div className="barangay-info">
                      <span className="risk-indicator">{brgy.risk_icon || '⚪'}</span>
                      <span className="barangay-name">{brgy.name}</span>
                    </div>
                    <span className="predicted-cases">
                      {brgy.predicted_next} cases
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        )}

        {barangayData && (
          <div className="barangay-details">
            <div className="details-header">
              <h2>{selectedBarangay}, {selectedMun}</h2>
              <button onClick={() => setBarangayData(null)} className="close-btn">
                ✕
              </button>
            </div>

            {/* Tab System */}
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

            {/* Forecast Tab Content */}
            {activeTab === 'forecast' && (
              <>
                {/* Metrics Help Banner */}
                <div className="metrics-help-banner">
                  <span className="help-icon">💡</span>
                  <div className="help-content">
                    <h3>Understanding Model Metrics</h3>
                    <p>These numbers tell you how accurate our predictions are. Lower is better for all metrics!</p>
                    <ul className="metrics-legend">
                      <li>
                        <strong>MAE (Mean Absolute Error)</strong>
                        Average prediction error. If MAE = 1.5, predictions are off by ~1-2 cases. <span className="good-value">Under 2 is excellent!</span>
                      </li>
                      <li>
                        <strong>RMSE (Root Mean Squared Error)</strong>
                        Similar to MAE but penalizes big errors more. <span className="good-value">Close to MAE is good!</span>
                      </li>
                      
                      <li>
                        <strong>MASE (Mean Absolute Scaled Error)</strong>
                        Compares to simple baseline. <span className="good-value">Under 1 means better than basic forecast!</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Risk Level Explanation */}
                <div className="risk-explanation">
                  <h3>🚦 Risk Level Guide</h3>
                  <ul>
                    <li>
                      <strong>🔴 HIGH RISK (Red):</strong>
                      Predicted cases are very high - <span className="action-needed">immediate action needed!</span> Increase vaccination campaigns, conduct awareness programs, and prepare resources.
                    </li>
                    <li>
                      <strong>🟡 MEDIUM RISK (Orange):</strong>
                      Cases above normal - <span className="action-needed">monitor closely.</span> Consider targeted interventions in affected areas.
                    </li>
                    <li>
                      <strong>🟢 LOW RISK (Green):</strong>
                      Cases within expected range - maintain current prevention measures and stay vigilant.
                    </li>
                  </ul>
                </div>

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

                {barangayData.next_month_prediction && (
                  <div className="next-prediction">
                    <strong>Next Month Prediction:</strong> {barangayData.next_month_prediction} cases
                  </div>
                )}

                <div className="forecast-button-container">
                  <button 
                    className="forecast-btn" 
                    onClick={handleForecastClick}
                    disabled={loading}
                  >
                    🔮 {showForecast ? 'Hide' : 'Show'} Future Forecast (8 Months)
                  </button>
                </div>

                {/* Report Download Section */}
                <div className="report-section">
                  <h3>📑 Download Reports</h3>
                  <p>Generate comprehensive forecast reports for stakeholders and decision-makers</p>
                  <div className="report-buttons">
                    <button 
                      className="report-btn report-btn-csv"
                      onClick={handleDownloadCSV}
                      disabled={loading}
                    >
                      📊 Download CSV Report
                    </button>
                    <button 
                      className="report-btn report-btn-pdf"
                      onClick={handleDownloadPDF}
                      disabled={loading}
                    >
                      📄 Download PDF Report
                    </button>
                  </div>
                </div>

                {/* Risk Alert */}
                {showForecast && riskInfo && (
                  <div className={`risk-alert risk-${riskInfo.level.toLowerCase()}`}>
                    <div className="risk-header">
                      <span className="risk-icon">{riskInfo.icon}</span>
                      <span className="risk-level">{riskInfo.level} RISK ALERT</span>
                    </div>
                    <p className="risk-message">{riskInfo.message}</p>
                  </div>
                )}

                {showForecast && forecastData && (
                  <div className="forecast-section">
                    <h3>📈 Future Forecast</h3>
                    <p className="forecast-info">
                      Predictions from <strong>{forecastData.forecast_start}</strong> to <strong>{forecastData.forecast_end}</strong>
                    </p>
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

                {barangayData.has_chart_data ? (
                  <BarangayChart
                    trainingData={barangayData.training_data}
                    validationData={barangayData.validation_data}
                    forecastData={showForecast && forecastData ? forecastData.predictions : null}
                  />
                ) : (
                  <div className="no-chart-data">
                    <h3>📊 Chart Data Not Available</h3>
                    <p>Historical training/validation data was not saved with this model.</p>
                    <p>To enable charts, re-train models and save with historical predictions.</p>
                  </div>
                )}
              </>
            )}

            {/* Model Insights Tab Content */}
            {activeTab === 'insights' && (
              <>
                {/* Download Insights PDF Button */}
                <div className="report-section insights-download">
                  <h3>📊 Download Model Interpretability Report</h3>
                  <p>Get a comprehensive PDF with all charts, decompositions, and technical explanations</p>
                  <button 
                    className="report-btn report-btn-pdf"
                    onClick={handleDownloadInsightsPDF}
                    disabled={loading || !interpretabilityData}
                  >
                    🔍 Download Insights PDF
                  </button>
                </div>

                {/* Weather-FPM Interpretability Timeline */}
                {interpretabilityData && interpretabilityData.weather_timeline && interpretabilityData.weather_timeline.months && (
                  <div className="weather-fpm-timeline-section">
                    <div className="timeline-header">
                      <h3>📅 Weather-Driven Interpretability Timeline</h3>
                      <p className="timeline-subtitle">
                        Understanding model performance through <strong>weather patterns</strong> (FPM Analysis)
                      </p>
                      <p className="timeline-explanation">
                        Each month shows how weather conditions influenced prediction accuracy. 
                        FPM reveals whether the model <em>underpredicted</em> (weather was riskier than expected) 
                        or <em>overpredicted</em> (weather was more favorable than expected).
                      </p>
                    </div>

                    <div className="timeline-months-grid">
                      {interpretabilityData.weather_timeline.months.map((month, idx) => (
                        <div key={idx} className={`timeline-month-card fpm-risk-${month.fpm_risk.toLowerCase()}`}>
                          <div className="month-header">
                            <h4>{month.date_display}</h4>
                            <span className={`fpm-risk-badge risk-${month.fpm_risk.toLowerCase()}`}>
                              {month.fpm_risk === 'HIGH' ? '🔴' : month.fpm_risk === 'LOW' ? '🟢' : '🟡'} 
                              {month.fpm_risk} RISK
                            </span>
                          </div>

                          <div className="month-cases-comparison">
                            <div className="cases-row">
                              <span className="label">Actual Cases:</span>
                              <span className="value actual">{month.actual_cases}</span>
                            </div>
                            <div className="cases-row">
                              <span className="label">Predicted Cases:</span>
                              <span className="value predicted">{month.predicted_cases}</span>
                            </div>
                            <div className={`cases-row error ${month.error > 0 ? 'overpredicted' : 'underpredicted'}`}>
                              <span className="label">Error:</span>
                              <span className="value">
                                {month.error > 0 ? '+' : ''}{month.error} ({month.error > 0 ? '+' : ''}{month.error_pct}%)
                              </span>
                            </div>
                          </div>

                          <div className="month-weather-summary">
                            <h5>🌤️ Weather Conditions:</h5>
                            <div className="weather-tags">
                              <span className="weather-tag">💧 {month.weather_categories.humidity} ({month.weather.humidity}%)</span>
                              <span className="weather-tag">💨 {month.weather_categories.wind} ({month.weather.wind_speed} km/h)</span>
                              <span className="weather-tag">🌧️ {month.weather_categories.precipitation} ({month.weather.precipitation}mm)</span>
                              <span className="weather-tag">🌡️ {month.weather_categories.temperature} ({month.weather.temperature}°C)</span>
                            </div>
                          </div>

                          <div className="fpm-interpretation">
                            <h5>🔍 FPM Interpretation:</h5>
                            <p>{month.interpretation}</p>
                            <div className="fpm-stats">
                              <span>Confidence: {(month.fpm_confidence * 100).toFixed(1)}%</span>
                              <span>Lift: {month.fpm_lift}×</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="timeline-summary">
                      <h4>💡 Key Insights:</h4>
                      <ul>
                        <li>🔴 <strong>HIGH RISK weather</strong> → Model tends to underpredict (actual cases often exceed forecast)</li>
                        <li>🟢 <strong>LOW RISK weather</strong> → Model tends to overpredict (favorable weather reduces cases)</li>
                        <li>🟡 <strong>MEDIUM RISK weather</strong> → Predictions generally accurate (weather impact minimal)</li>
                        <li>📊 FPM helps explain <em>why</em> model errors occur - often weather-driven!</li>
                      </ul>
                    </div>
                  </div>
                )}

                {/* Weather-Rabies Pattern Insights (FPM) */}
                {weatherInsights && weatherInsights.insights && weatherInsights.insights.available && (
                  <div className="weather-insights-section">
                    <div className="insights-header">
                      <h3>🌤️ Weather-Rabies Pattern Analysis (FPM)</h3>
                      <p className="insights-subtitle">
                        Independent analysis using Frequent Pattern Mining. Shows weather associations 
                        <strong> without affecting forecast accuracy.</strong>
                      </p>
                      <p className="weather-data-warning">
                        ⚠️ <strong>Note:</strong> {weatherInsights.note}
                        <br/><strong>📊 MONTHLY Assessment:</strong> Weather values are MONTHLY TOTALS/AVERAGES (Precip & Sunshine = totals | Temp & Humidity = averages | Wind = max). Risk assessment is for the ENTIRE MONTH, not daily.
                      </p>
                    </div>

                    {/* Risk Level Card */}
                    <div className={`weather-risk-card risk-${weatherInsights.insights.risk_level?.toLowerCase()}`}>
                      <div className="weather-risk-header">
                        <span className="weather-risk-icon">
                          {weatherInsights.insights.risk_level === 'HIGH' ? '🔴' : 
                           weatherInsights.insights.risk_level === 'MEDIUM' ? '🟡' : '🟢'}
                        </span>
                        <div className="weather-risk-info">
                          <h4>{weatherInsights.insights.risk_level} MONTHLY WEATHER RISK</h4>
                          <p>Confidence: {(weatherInsights.insights.confidence * 100).toFixed(1)}%</p>
                          <p style={{ fontSize: '11px', opacity: 0.8, marginTop: '4px' }}>⏱️ Risk for entire month</p>
                        </div>
                      </div>

                      {/* Why This Risk Level? */}
                      <div className="risk-explanation-box">
                        <h5>🤔 Why This Risk Level?</h5>
                        <p>{weatherInsights.insights.why_this_risk}</p>
                      </div>

                      {/* Risk Factors - Detailed List */}
                      <div className="risk-factors-section">
                        <h5>📋 Key Risk Factors Identified:</h5>
                        <ul className="risk-factors-list">
                          {weatherInsights.insights.risk_factors.map((factor, idx) => (
                            <li key={idx}>{factor}</li>
                          ))}
                        </ul>
                      </div>

                      {/* Current Weather Conditions */}
                      <div className="weather-conditions">
                        <h5>📊 Monthly Weather Conditions Analyzed:</h5>
                        <div className="conditions-grid">
                          <div className="condition-item">
                            <span className="condition-icon">🌡️</span>
                            <div className="condition-details">
                              <span className="condition-label">Temperature (monthly avg)</span>
                              <span className="condition-value">
                                {weatherInsights.weather_data.tmean_c}°C
                              </span>
                              <span className="condition-category">
                                {weatherInsights.insights.weather_conditions.temperature}
                              </span>
                            </div>
                          </div>

                          <div className="condition-item">
                            <span className="condition-icon">💧</span>
                            <div className="condition-details">
                              <span className="condition-label">Humidity (monthly avg)</span>
                              <span className="condition-value">
                                {weatherInsights.weather_data.rh_pct}%
                              </span>
                              <span className="condition-category">
                                {weatherInsights.insights.weather_conditions.humidity}
                              </span>
                            </div>
                          </div>

                          <div className="condition-item">
                            <span className="condition-icon">🌧️</span>
                            <div className="condition-details">
                              <span className="condition-label">Rainfall (monthly total)</span>
                              <span className="condition-value">
                                {weatherInsights.weather_data.precip_mm}mm
                              </span>
                              <span className="condition-category">
                                {weatherInsights.insights.weather_conditions.precipitation}
                              </span>
                            </div>
                          </div>

                          <div className="condition-item">
                            <span className="condition-icon">💨</span>
                            <div className="condition-details">
                              <span className="condition-label">Wind Speed (monthly max)</span>
                              <span className="condition-value">
                                {weatherInsights.weather_data.wind_speed_10m_max_kmh} km/h
                              </span>
                              <span className="condition-category">
                                {weatherInsights.insights.weather_conditions.wind}
                              </span>
                            </div>
                          </div>

                          <div className="condition-item">
                            <span className="condition-icon">☀️</span>
                            <div className="condition-details">
                              <span className="condition-label">Sunshine (monthly total)</span>
                              <span className="condition-value">
                                {weatherInsights.weather_data.sunshine_hours}h
                              </span>
                              <span className="condition-category">
                                {weatherInsights.insights.weather_conditions.sunshine}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* FPM Rule Thresholds */}
                      <div className="fpm-rules-section">
                        <h5>📐 FPM Pattern Thresholds (What Makes Risk High/Low?):</h5>
                        <div className="rules-comparison">
                          <div className="rule-box high-risk-rule">
                            <h6>🔴 HIGH RISK Pattern:</h6>
                            <ul>
                              <li><strong>Humidity:</strong> {weatherInsights.insights.rule_explanations.high_risk_threshold.humidity}</li>
                              <li><strong>Wind:</strong> {weatherInsights.insights.rule_explanations.high_risk_threshold.wind}</li>
                              <li><strong>Rainfall:</strong> {weatherInsights.insights.rule_explanations.high_risk_threshold.rainfall}</li>
                              <li><strong>Temperature:</strong> {weatherInsights.insights.rule_explanations.high_risk_threshold.temperature}</li>
                            </ul>
                            <p className="pattern-formula">{weatherInsights.insights.rule_explanations.high_risk_threshold.pattern}</p>
                          </div>

                          <div className="rule-box low-risk-rule">
                            <h6>🟢 LOW RISK Pattern:</h6>
                            <ul>
                              <li><strong>Humidity:</strong> {weatherInsights.insights.rule_explanations.low_risk_threshold.humidity}</li>
                              <li><strong>Wind:</strong> {weatherInsights.insights.rule_explanations.low_risk_threshold.wind}</li>
                              <li><strong>Rainfall:</strong> {weatherInsights.insights.rule_explanations.low_risk_threshold.rainfall}</li>
                              <li><strong>Temperature:</strong> {weatherInsights.insights.rule_explanations.low_risk_threshold.temperature}</li>
                            </ul>
                            <p className="pattern-formula">{weatherInsights.insights.rule_explanations.low_risk_threshold.pattern}</p>
                          </div>
                        </div>
                      </div>

                      {/* Why Weather Matters */}
                      <div className="why-weather-matters">
                        <h5>🔬 Why Do These Weather Factors Matter?</h5>
                        <ul className="science-list">
                          {weatherInsights.insights.rule_explanations.why_weather_matters.map((reason, idx) => (
                            <li key={idx}>{reason}</li>
                          ))}
                        </ul>
                      </div>

                      {/* Matched Pattern */}
                      {weatherInsights.insights.matched_pattern && (
                        <div className="matched-pattern">
                          <h5>🎯 Matched Pattern:</h5>
                          <div className="pattern-details">
                            <p className="pattern-conditions">
                              <strong>Conditions:</strong> {weatherInsights.insights.matched_pattern.conditions}
                            </p>
                            <div className="pattern-metrics">
                              <span className="pattern-metric">
                                <strong>Confidence:</strong> {(weatherInsights.insights.matched_pattern.confidence * 100).toFixed(1)}%
                              </span>
                              <span className="pattern-metric">
                                <strong>Lift:</strong> {weatherInsights.insights.matched_pattern.lift}× stronger
                              </span>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Recommendations */}
                      <div className="weather-recommendations">
                        <h5>💡 Actionable Recommendations:</h5>
                        <ul className="recommendations-list">
                          {weatherInsights.insights.recommendations.map((rec, idx) => (
                            <li key={idx} className="recommendation-item">
                              <span className="recommendation-bullet">✓</span>
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Model Info */}
                      <div className="fpm-model-info">
                        <p className="info-note">
                          📚 Analysis based on <strong>{weatherInsights.insights.model_info.total_rules}</strong> weather-rabies association rules 
                          from <strong>{weatherInsights.insights.model_info.data_source}</strong> across <strong>{weatherInsights.insights.model_info.barangays_analyzed}</strong>
                          <br/>
                          ({weatherInsights.insights.model_info.high_risk_rules} high-risk patterns, {weatherInsights.insights.model_info.low_risk_rules} low-risk patterns detected)
                        </p>
                      </div>
                    </div>

                    {/* Explanation Box */}
                    <div className="fpm-explanation">
                      <h5>ℹ️ Why Separate Weather Analysis?</h5>
                      <p>
                        Weather data was <strong>not included as regressors</strong> in the main forecasting model 
                        because it reduced prediction accuracy. However, understanding weather-rabies associations 
                        is still valuable for risk assessment and planning.
                      </p>
                      <p>
                        This <strong>Frequent Pattern Mining (FPM)</strong> analysis runs independently, revealing 
                        weather patterns associated with rabies outbreaks without compromising forecast quality.
                      </p>
                      <p className="fpm-method-note">
                        <strong>📖 Method:</strong> FPM discovered {weatherInsights.insights.model_info.total_rules} association rules 
                        by analyzing which weather combinations frequently appeared with high/low rabies cases. 
                        These rules show <em>correlation, not causation</em> - but are useful for risk assessment.
                      </p>
                    </div>
                  </div>
                )}
                
                <ModelInsights interpretabilityData={interpretabilityData} />
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ForecastingMain;
