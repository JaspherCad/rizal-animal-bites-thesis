import React from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './ModelInsights.css';

function ModelInsights({ interpretabilityData }) {
  if (!interpretabilityData) {
    return (
      <div className="model-insights">
        <div className="loading-message">
          Loading model insights...
        </div>
      </div>
    );
  }

  const { 
    trend, 
    seasonality, 
    holidays, 
    weather_regressors,      // 🆕 NEW
    vaccination_regressors,  // 🆕 NEW
    seasonal_regressors,     // 🆕 NEW
    feature_importance, 
    model_config 
  } = interpretabilityData;

  // Prepare data for trend, seasonality, and holidays charts
  const trendSeasonalityData = trend.dates.map((date, index) => ({
    date,
    trend: trend.values[index],
    seasonality: seasonality.values[index],
    holidays: holidays ? holidays.values[index] : 0
  }));

  // 🆕 Prepare weather regressor data
  const weatherData = weather_regressors && weather_regressors.columns && weather_regressors.columns.length > 0
    ? trend.dates.map((date, index) => {
        const dataPoint = { date };
        weather_regressors.columns.forEach(col => {
          dataPoint[col] = weather_regressors.data[col] ? weather_regressors.data[col][index] : 0;
        });
        return dataPoint;
      })
    : [];

  // 🆕 Prepare vaccination regressor data
  const vaccinationData = vaccination_regressors && vaccination_regressors.columns && vaccination_regressors.columns.length > 0
    ? trend.dates.map((date, index) => {
        const dataPoint = { date };
        vaccination_regressors.columns.forEach(col => {
          dataPoint[col] = vaccination_regressors.data[col] ? vaccination_regressors.data[col][index] : 0;
        });
        return dataPoint;
      })
    : [];

  // 🆕 Prepare seasonal regressor data
  const seasonalData = seasonal_regressors && seasonal_regressors.columns && seasonal_regressors.columns.length > 0
    ? trend.dates.map((date, index) => {
        const dataPoint = { date };
        seasonal_regressors.columns.forEach(col => {
          dataPoint[col] = seasonal_regressors.data[col] ? seasonal_regressors.data[col][index] : 0;
        });
        return dataPoint;
      })
    : [];

  // 🆕 Helper function to format regressor names
  const formatRegressorName = (name) => {
    const nameMap = {
      'tmean_c': 'Temperature (°C)',
      'rh_pct': 'Humidity (%)',
      'precip_mm': 'Precipitation (mm)',
      'pct_hot_days': 'Hot Days (%)',
      'pct_rainy_days': 'Rainy Days (%)',
      'pct_humid_days': 'Humid Days (%)',
      'vax_campaign_active': 'Vaccination Campaign Active',
      'vax_campaign_2023': 'Vaccination 2023 (Jan-Mar)',
      'vax_campaign_2024': 'Vaccination 2024 (Mar-Apr)',
      'may_peak': 'May Peak',
      'low_season': 'Low Season',
      'spring_ramp': 'Spring Ramp',
      'january_holiday': 'January Holiday',
      'post_may_decline': 'Post-May Decline',
      'high_season': 'High Season',
      'july_dip': 'July Dip',
      'august_rise': 'August Rise',
      'post_april_2024': 'Post-April 2024'
    };
    return nameMap[name] || name;
  };

  // 🆕 Color palette for regressors
  const weatherColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'];
  const vaccinationColors = ['#9B59B6', '#E74C3C', '#3498DB'];
  const seasonalColors = ['#E67E22', '#16A085', '#D35400', '#27AE60', '#8E44AD'];

  // Prepare data for feature importance chart (top 7 features)
  const featureImportanceData = feature_importance.top_3_features
    .slice(0, 7)
    .map(f => ({
      feature: f.feature,
      percentage: f.percentage
    }));

  // Custom tooltip for trend/seasonality
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label"><strong>{label}</strong></p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="model-insights">
      
      {/* Header Section */}
      <div className="insights-header">
        <h3>🔍 Model Interpretability</h3>
        <p className="subtitle">Understanding how the model makes predictions</p>
      </div>

      {/* Trend & Seasonality Chart */}
      <div className="insight-section">
        <div className="section-header">
          <h4>📈 Trend, Seasonality & Holiday Decomposition</h4>
          <p className="section-description">
            <strong>Trend:</strong> {trend.description}<br/>
            <strong>Seasonality:</strong> {seasonality.description}<br/>
            {holidays && holidays.has_holidays && (
              <><strong>Holidays:</strong> {holidays.description}</>
            )}
          </p>
        </div>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={trendSeasonalityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 11 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Line 
              type="monotone" 
              dataKey="trend" 
              stroke="#2196F3" 
              strokeWidth={2}
              dot={false}
              name="Trend"
            />
            <Line 
              type="monotone" 
              dataKey="seasonality" 
              stroke="#4CAF50" 
              strokeWidth={2}
              dot={false}
              name="Seasonality"
            />
            {holidays && holidays.has_holidays && (
              <Line 
                type="monotone" 
                dataKey="holidays" 
                stroke="#FF5722" 
                strokeWidth={2}
                dot={false}
                name="Holiday Effects"
                strokeDasharray="5 5"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
        
        {/* Holiday Effects Summary */}
        {holidays && holidays.has_holidays && holidays.significant_effects && holidays.significant_effects.length > 0 && (
          <div className="holiday-summary">
            <h5>🎉 Significant Holiday Effects Detected:</h5>
            <div className="holiday-effects-grid">
              {holidays.significant_effects.slice(0, 10).map((effect, idx) => (
                <div key={idx} className={`holiday-effect-item ${effect.impact.toLowerCase()}`}>
                  <span className="holiday-date">{effect.date}</span>
                  <span className="holiday-name">{effect.holiday}</span>
                  <span className="holiday-impact">
                    {effect.impact === 'Positive' ? '📈' : '📉'} {Math.abs(effect.effect).toFixed(1)} cases
                  </span>
                </div>
              ))}
            </div>
            <p className="holiday-note">
              <strong>Note:</strong> Holidays include Philippine public holidays (New Year, Holy Week, Christmas, Independence Day, etc.)
            </p>
          </div>
        )}
      </div>

      {/* 🆕 Weather Regressors Section */}
      {weatherData.length > 0 && (
        <div className="insight-section">
          <div className="section-header">
            <h4>🌤️ Weather Factors Impact</h4>
            <p className="section-description">
              <strong>{weather_regressors.description}</strong><br/>
              Shows how temperature, humidity, precipitation, and weather patterns affect rabies cases.
            </p>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={weatherData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 11 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} label={{ value: 'Impact on Cases', angle: -90, position: 'insideLeft' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              {weather_regressors.columns.map((col, idx) => (
                <Line 
                  key={col}
                  type="monotone" 
                  dataKey={col} 
                  stroke={weatherColors[idx % weatherColors.length]} 
                  strokeWidth={2}
                  dot={false}
                  name={formatRegressorName(col)}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
          <div className="regressor-note">
            <p><strong>💡 Interpretation:</strong> Positive values indicate weather conditions that increase rabies cases, negative values indicate conditions that decrease cases.</p>
          </div>
        </div>
      )}

      {/* 🆕 Vaccination Regressors Section */}
      {vaccinationData.length > 0 && (
        <div className="insight-section">
          <div className="section-header">
            <h4>💉 Vaccination Campaign Impact</h4>
            <p className="section-description">
              <strong>{vaccination_regressors.description}</strong><br/>
              Shows the effect of mass vaccination drives on rabies case reduction.
            </p>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={vaccinationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 11 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} label={{ value: 'Impact on Cases', angle: -90, position: 'insideLeft' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              {vaccination_regressors.columns.map((col, idx) => (
                <Line 
                  key={col}
                  type="monotone" 
                  dataKey={col} 
                  stroke={vaccinationColors[idx % vaccinationColors.length]} 
                  strokeWidth={2}
                  dot={false}
                  name={formatRegressorName(col)}
                  strokeDasharray="5 5"
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
          <div className="regressor-note">
            <p><strong>💡 Interpretation:</strong> Negative values indicate vaccination campaigns successfully reduced rabies cases during those periods.</p>
            <p><strong>📅 Campaigns:</strong> 2023 (Jan-Mar): ~35,000 animals vaccinated | 2024 (Mar-Apr): ~35,000 animals vaccinated</p>
          </div>
        </div>
      )}

      {/* 🆕 Seasonal Regressors Section */}
      {seasonalData.length > 0 && (
        <div className="insight-section">
          <div className="section-header">
            <h4>📅 Custom Seasonal Patterns</h4>
            <p className="section-description">
              <strong>{seasonal_regressors.description}</strong><br/>
              Municipality-specific seasonal features that capture unique local patterns.
            </p>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={seasonalData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 11 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} label={{ value: 'Impact on Cases', angle: -90, position: 'insideLeft' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              {seasonal_regressors.columns.map((col, idx) => (
                <Line 
                  key={col}
                  type="monotone" 
                  dataKey={col} 
                  stroke={seasonalColors[idx % seasonalColors.length]} 
                  strokeWidth={2}
                  dot={false}
                  name={formatRegressorName(col)}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
          <div className="regressor-note">
            <p><strong>💡 Interpretation:</strong> These are custom binary features (0 or 1) that activate during specific months to capture local seasonal patterns.</p>
          </div>
        </div>
      )}

      {/* Feature Importance Chart */}
      <div className="insight-section">
        <div className="section-header">
          <h4>🎯 Feature Importance</h4>
          <p className="section-description">
            {feature_importance.description}
          </p>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart 
            data={featureImportanceData} 
            layout="vertical"
            margin={{ left: 100 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" tick={{ fontSize: 12 }} />
            <YAxis 
              dataKey="feature" 
              type="category" 
              tick={{ fontSize: 12 }}
              width={95}
            />
            <Tooltip 
              formatter={(value) => `${value.toFixed(2)}%`}
              labelStyle={{ color: '#000' }}
            />
            <Bar 
              dataKey="percentage" 
              fill="#FF9800" 
              name="Importance (%)"
            />
          </BarChart>
        </ResponsiveContainer>
        
        {/* Feature Importance Legend */}
        <div className="feature-legend">
          <h5>📝 Feature Definitions:</h5>
          <ul>
            <li><strong>np_prediction:</strong> NeuralProphet baseline forecast</li>
            <li><strong>lag_1, lag_2, lag_12:</strong> Cases from 1, 2, and 12 months ago</li>
            <li><strong>rolling_mean_3:</strong> 3-month moving average</li>
            <li><strong>rolling_std_3:</strong> 3-month standard deviation (volatility)</li>
            <li><strong>rate_of_change_1:</strong> Month-over-month growth rate</li>
            <li><strong>month_sin/cos:</strong> Cyclical month encoding</li>
          </ul>
        </div>
      </div>

      {/* Model Configuration */}
      <div className="insight-section">
        <div className="section-header">
          <h4>⚙️ Model Configuration</h4>
          <p className="section-description">Technical parameters of the hybrid model</p>
        </div>
        <div className="config-grid">
          <div className="config-card">
            <div className="config-label">NeuralProphet Changepoint Range</div>
            <div className="config-value">{model_config.neuralprophet_changepoint_prior_scale}</div>
          </div>
          <div className="config-card">
            <div className="config-label">XGBoost Trees</div>
            <div className="config-value">{model_config.xgboost_n_estimators}</div>
          </div>
          <div className="config-card">
            <div className="config-label">XGBoost Max Depth</div>
            <div className="config-value">{model_config.xgboost_max_depth}</div>
          </div>
        </div>
      </div>

      {/* Insights Summary */}
      <div className="insights-summary">
        <h5>💡 What This Means:</h5>
        <div className="summary-cards">
          <div className="summary-card">
            <span className="summary-icon">📈</span>
            <div className="summary-content">
              <strong>Trend Analysis</strong>
              <p>The blue line shows the long-term direction of cases, independent of seasonal and holiday effects.</p>
            </div>
          </div>
          <div className="summary-card">
            <span className="summary-icon">🌊</span>
            <div className="summary-content">
              <strong>Seasonal Patterns</strong>
              <p>The green line reveals recurring yearly patterns - which months typically have higher cases.</p>
            </div>
          </div>
          {holidays && holidays.has_holidays && (
            <div className="summary-card">
              <span className="summary-icon">🎉</span>
              <div className="summary-content">
                <strong>Holiday Effects</strong>
                <p>The red dashed line shows how Philippine holidays impact rabies case reporting and behavior.</p>
              </div>
            </div>
          )}
          {weatherData.length > 0 && (
            <div className="summary-card">
              <span className="summary-icon">🌤️</span>
              <div className="summary-content">
                <strong>Weather Factors</strong>
                <p>Temperature, humidity, and precipitation patterns influence animal behavior and rabies transmission.</p>
              </div>
            </div>
          )}
          {vaccinationData.length > 0 && (
            <div className="summary-card">
              <span className="summary-icon">💉</span>
              <div className="summary-content">
                <strong>Vaccination Impact</strong>
                <p>Mass vaccination campaigns show measurable reduction in rabies cases during and after implementation.</p>
              </div>
            </div>
          )}
          {seasonalData.length > 0 && (
            <div className="summary-card">
              <span className="summary-icon">📅</span>
              <div className="summary-content">
                <strong>Local Patterns</strong>
                <p>Custom seasonal features capture unique rabies patterns specific to this municipality.</p>
              </div>
            </div>
          )}
          <div className="summary-card">
            <span className="summary-icon">🎯</span>
            <div className="summary-content">
              <strong>Key Factors</strong>
              <p>The bar chart shows which factors the model weighs most heavily when making predictions.</p>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

export default ModelInsights;
