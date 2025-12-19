/**
 * FRONTEND INTEGRATION EXAMPLE
 * React component for displaying Model Interpretability
 */

import React, { useState, useEffect } from 'react';
import { LineChart, BarChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import axios from 'axios';

const ModelInterpretability = ({ municipality, barangay }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchInterpretability();
  }, [municipality, barangay]);

  const fetchInterpretability = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/interpretability/${municipality}/${barangay}`
      );
      setData(response.data.interpretability);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch interpretability:', error);
      setLoading(false);
    }
  };

  if (loading) return <div>Loading interpretability data...</div>;
  if (!data) return <div>No interpretability data available</div>;

  // Prepare data for charts
  const trendData = data.trend.dates.map((date, i) => ({
    date,
    trend: data.trend.values[i],
    seasonality: data.seasonality.values[i]
  }));

  const featureData = data.feature_importance.features
    .slice(0, 7) // Top 7 features
    .map(f => ({
      name: f.feature,
      importance: f.percentage
    }));

  return (
    <div className="interpretability-panel">
      {/* Tab Navigation */}
      <div className="tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={activeTab === 'decomposition' ? 'active' : ''}
          onClick={() => setActiveTab('decomposition')}
        >
          📈 Trend & Seasonality
        </button>
        <button 
          className={activeTab === 'importance' ? 'active' : ''}
          onClick={() => setActiveTab('importance')}
        >
          🎯 Feature Importance
        </button>
        <button 
          className={activeTab === 'changepoints' ? 'active' : ''}
          onClick={() => setActiveTab('changepoints')}
        >
          🔄 Changepoints
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="overview-section">
            <h3>🔍 Model Interpretability Overview</h3>
            <p className="subtitle">
              Understanding how the model makes predictions for {barangay}, {municipality}
            </p>

            <div className="info-cards">
              <div className="card">
                <div className="icon">📈</div>
                <h4>Trend Analysis</h4>
                <p>{data.trend.description}</p>
                <div className="stat">
                  {data.trend.values[data.trend.values.length - 1] > 
                   data.trend.values[0] ? '↗️ Upward' : '↘️ Downward'}
                </div>
              </div>

              <div className="card">
                <div className="icon">🌊</div>
                <h4>Seasonality</h4>
                <p>{data.seasonality.description}</p>
                <div className="stat">
                  Peak Amplitude: ±{Math.max(...data.seasonality.values.map(Math.abs)).toFixed(2)}
                </div>
              </div>

              <div className="card">
                <div className="icon">🎯</div>
                <h4>Top Predictor</h4>
                <p>{data.feature_importance.description}</p>
                <div className="stat">
                  {data.feature_importance.top_3_features[0].feature} 
                  ({data.feature_importance.top_3_features[0].percentage.toFixed(1)}%)
                </div>
              </div>

              <div className="card">
                <div className="icon">🔄</div>
                <h4>Changepoints</h4>
                <p>{data.changepoints.description}</p>
                <div className="stat">
                  {data.changepoints.points.length} detected
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TREND & SEASONALITY TAB */}
        {activeTab === 'decomposition' && (
          <div className="decomposition-section">
            <h3>📈 Trend & Seasonality Decomposition</h3>
            <p className="info-text">
              The model breaks down predictions into trend (long-term pattern) 
              and seasonality (recurring patterns).
            </p>

            <div className="chart-container">
              <h4>Time Series Decomposition</h4>
              <LineChart width={800} height={400} data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="trend" 
                  stroke="#2196F3" 
                  name="Trend"
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="seasonality" 
                  stroke="#4CAF50" 
                  name="Seasonality"
                  strokeWidth={2}
                />
              </LineChart>

              <div className="insights">
                <h4>💡 Key Insights:</h4>
                <ul>
                  <li>
                    <strong>Trend Direction:</strong>{' '}
                    {data.trend.values[data.trend.values.length - 1] > 
                     data.trend.values[0] 
                      ? 'Cases are increasing over time' 
                      : 'Cases are decreasing over time'}
                  </li>
                  <li>
                    <strong>Seasonal Pattern:</strong>{' '}
                    Cases vary by ±{Math.max(...data.seasonality.values.map(Math.abs)).toFixed(1)} 
                    {' '}due to seasonal effects
                  </li>
                  <li>
                    <strong>Interpretation:</strong> The blue line shows the underlying trend 
                    while green shows recurring monthly patterns.
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* FEATURE IMPORTANCE TAB */}
        {activeTab === 'importance' && (
          <div className="importance-section">
            <h3>🎯 Feature Importance Analysis</h3>
            <p className="info-text">
              Shows which factors the XGBoost model considers most important 
              when making predictions.
            </p>

            <div className="chart-container">
              <BarChart 
                width={800} 
                height={400} 
                data={featureData}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={150} />
                <Tooltip />
                <Bar dataKey="importance" fill="#FF9800" />
              </BarChart>

              <div className="insights">
                <h4>💡 What This Means:</h4>
                <ul>
                  {data.feature_importance.top_3_features.map((feat, i) => (
                    <li key={i}>
                      <strong>{feat.feature}:</strong> {feat.percentage.toFixed(1)}% importance
                      {getFeatureExplanation(feat.feature)}
                    </li>
                  ))}
                </ul>
                
                <div className="explanation-box">
                  <h5>📚 Feature Definitions:</h5>
                  <ul>
                    <li><strong>np_prediction:</strong> NeuralProphet's baseline forecast</li>
                    <li><strong>lag_12:</strong> Cases from 12 months ago (yearly pattern)</li>
                    <li><strong>rolling_mean_3:</strong> Average of last 3 months</li>
                    <li><strong>lag_1:</strong> Previous month's cases</li>
                    <li><strong>Month:</strong> Current month number</li>
                    <li><strong>month_sin/cos:</strong> Cyclical encoding of seasons</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* CHANGEPOINTS TAB */}
        {activeTab === 'changepoints' && (
          <div className="changepoints-section">
            <h3>🔄 Significant Changepoints</h3>
            <p className="info-text">
              Dates where the trend significantly changed direction, 
              possibly due to outbreaks or interventions.
            </p>

            {data.changepoints.points.length > 0 ? (
              <>
                <div className="changepoints-list">
                  {data.changepoints.points.map((cp, i) => (
                    <div key={i} className="changepoint-item">
                      <div className="date">{cp.date}</div>
                      <div className="value">Value: {cp.value.toFixed(2)}</div>
                      <div className="badge">Significant Change Detected</div>
                    </div>
                  ))}
                </div>

                <div className="insights">
                  <h4>💡 Analysis:</h4>
                  <ul>
                    <li>
                      <strong>{data.changepoints.points.length} changepoints detected</strong> 
                      {' '}in the historical data
                    </li>
                    <li>
                      These dates may correspond to:
                      <ul>
                        <li>Start of outbreak periods</li>
                        <li>Implementation of intervention programs</li>
                        <li>Seasonal shifts or environmental changes</li>
                        <li>Changes in data collection methods</li>
                      </ul>
                    </li>
                    <li>
                      Cross-reference these dates with local events to validate patterns
                    </li>
                  </ul>
                </div>
              </>
            ) : (
              <div className="no-data">
                <p>No significant changepoints detected in the data.</p>
                <p>This suggests a stable trend with gradual changes.</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Model Configuration Footer */}
      <div className="model-config">
        <h4>⚙️ Model Configuration</h4>
        <div className="config-grid">
          {Object.entries(data.model_config).map(([key, value]) => (
            <div key={key} className="config-item">
              <span className="key">{formatConfigKey(key)}:</span>
              <span className="value">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Helper functions
const getFeatureExplanation = (feature) => {
  const explanations = {
    'np_prediction': ' - The base forecast from NeuralProphet',
    'lag_12': ' - Strong yearly seasonality indicator',
    'rolling_mean_3': ' - Recent trend matters most',
    'lag_1': ' - Previous month heavily influences next month',
    'Month': ' - Month of the year affects predictions',
    'month_sin': ' - Seasonal cycle encoding',
    'month_cos': ' - Seasonal cycle encoding'
  };
  return explanations[feature] || '';
};

const formatConfigKey = (key) => {
  return key.replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase());
};

// CSS styles (add to your stylesheet)
const styles = `
.interpretability-panel {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.tabs button.active {
  border-bottom: 3px solid #2196F3;
  font-weight: bold;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.card {
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  text-align: center;
}

.card .icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.card .stat {
  font-size: 24px;
  font-weight: bold;
  color: #2196F3;
  margin-top: 10px;
}

.chart-container {
  margin: 20px 0;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.insights {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-left: 4px solid #4CAF50;
}

.explanation-box {
  margin-top: 15px;
  padding: 15px;
  background: #E3F2FD;
  border-radius: 4px;
}

.changepoints-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 20px 0;
}

.changepoint-item {
  padding: 15px;
  background: #FFF3E0;
  border-left: 4px solid #FF9800;
  border-radius: 4px;
}

.model-config {
  margin-top: 30px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.config-item {
  padding: 10px;
  background: white;
  border-radius: 4px;
}

.config-item .key {
  font-weight: bold;
  color: #666;
}

.config-item .value {
  margin-left: 10px;
  color: #2196F3;
}
`;

export default ModelInterpretability;
