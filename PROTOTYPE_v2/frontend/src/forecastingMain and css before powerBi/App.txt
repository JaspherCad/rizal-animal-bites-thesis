import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import BarangayChart from './BarangayChart';
import ModelInsights from './ModelInsights';

const API_URL = 'http://localhost:8000';

function App() {
  const [municipalities, setMunicipalities] = useState([]);
  const [selectedMun, setSelectedMun] = useState(null);
  const [selectedBarangay, setSelectedBarangay] = useState(null);
  const [barangayData, setBarangayData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [showForecast, setShowForecast] = useState(false);
  const [interpretabilityData, setInterpretabilityData] = useState(null);
  const [activeTab, setActiveTab] = useState('forecast');
  const [loading, setLoading] = useState(true);

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

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'insights' && !interpretabilityData) {
      fetchInterpretability();
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
                
                <ModelInsights interpretabilityData={interpretabilityData} />
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
