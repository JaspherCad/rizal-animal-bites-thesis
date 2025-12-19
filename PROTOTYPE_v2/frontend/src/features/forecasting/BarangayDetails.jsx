import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useBarangayData, useForecast, useInterpretability } from './hooks';
import { downloadCSVReport, downloadPDFReport, downloadInsightsPDF } from './api';
import BarangayChart from '../../components/charts/BarangayChart';
import ModelInsights from '../insights/ModelInsights';
import MetricsHelpBanner from './components/MetricsHelpBanner';
import RiskExplanation from './components/RiskExplanation';
import './styles.css';

function BarangayDetails() {
  const { municipality, barangay } = useParams();
  const navigate = useNavigate();
  
  const { barangayData, loading: dataLoading } = useBarangayData(municipality, barangay);
  const { forecastData, loading: forecastLoading, fetchForecast } = useForecast(municipality, barangay);
  const { interpretabilityData, loading: insightsLoading, fetchInterpretability } = useInterpretability(municipality, barangay);
  
  const [showForecast, setShowForecast] = useState(false);
  const [activeTab, setActiveTab] = useState('forecast');
  const [downloadLoading, setDownloadLoading] = useState(false);

  const handleForecastClick = async () => {
    if (!showForecast && !forecastData) {
      await fetchForecast();
    }
    setShowForecast(!showForecast);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'insights' && !interpretabilityData) {
      fetchInterpretability();
    }
  };

  const handleDownloadCSV = async () => {
    try {
      setDownloadLoading(true);
      const blob = await downloadCSVReport(municipality, barangay);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rabies_forecast_${municipality}_${barangay}_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading CSV:', error);
      alert(`Failed to download CSV report: ${error.message}`);
    } finally {
      setDownloadLoading(false);
    }
  };

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

  const calculateRiskLevel = (barangayData, forecastData) => {
    if (!barangayData || !barangayData.validation_data) return null;

    const historicalAvg = barangayData.validation_data.reduce((sum, d) => sum + d.actual, 0) / 
                          barangayData.validation_data.length;

    const forecastAvg = forecastData && forecastData.predictions 
      ? forecastData.predictions.reduce((sum, d) => sum + d.predicted, 0) / forecastData.predictions.length
      : barangayData.next_month_prediction || 0;

    const historicalMax = Math.max(...barangayData.validation_data.map(d => d.actual));

    const avgThreshold = historicalAvg * 1.2;
    const maxThreshold = historicalMax * 0.8;

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

  const riskInfo = barangayData && showForecast ? calculateRiskLevel(barangayData, forecastData) : null;

  if (dataLoading) {
    return <div className="loading">Loading barangay data...</div>;
  }

  if (!barangayData) {
    return <div className="error-message">Barangay data not found</div>;
  }

  return (
    <div className="barangay-details">
      <div className="details-header">
        <h2>{barangay}, {municipality}</h2>
        <button onClick={() => navigate('/forecasting')} className="close-btn">
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
          <MetricsHelpBanner />
          <RiskExplanation />

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
              disabled={forecastLoading}
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
                disabled={downloadLoading}
              >
                📊 Download CSV Report
              </button>
              <button 
                className="report-btn report-btn-pdf"
                onClick={handleDownloadPDF}
                disabled={downloadLoading}
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
          <div className="report-section insights-download">
            <h3>📊 Download Model Interpretability Report</h3>
            <p>Get a comprehensive PDF with all charts, decompositions, and technical explanations</p>
            <button 
              className="report-btn report-btn-pdf"
              onClick={handleDownloadInsightsPDF}
              disabled={downloadLoading || !interpretabilityData}
            >
              🔍 Download Insights PDF
            </button>
          </div>
          
          <ModelInsights interpretabilityData={interpretabilityData} loading={insightsLoading} />
        </>
      )}
    </div>
  );
}

export default BarangayDetails;
