import React from 'react';
import './Home.css';

function Home() {
  return (
    <div className="home-page">
      <div className="welcome-card">
        <h2>🏠 Welcome to the Rabies Forecasting Dashboard</h2>
        <p className="intro-text">
          This advanced forecasting system uses a hybrid <strong>NeuralProphet + XGBoost</strong> model 
          to predict animal bite incidents across municipalities in Rizal Province, Philippines.
        </p>
      </div>

      <div className="features-grid">
        <div className="feature-card">
          <span className="feature-icon">📊</span>
          <h3>Accurate Forecasting</h3>
          <p>8-month ahead predictions with municipality-specific models trained on historical data from 2020-2024</p>
        </div>

        <div className="feature-card">
          <span className="feature-icon">🚦</span>
          <h3>Risk Assessment</h3>
          <p>Automatic risk level classification (High/Medium/Low) to prioritize intervention efforts</p>
        </div>

        <div className="feature-card">
          <span className="feature-icon">🔍</span>
          <h3>Model Interpretability</h3>
          <p>Understand predictions through trend, seasonality, holiday effects, weather, and vaccination impact analysis</p>
        </div>

        <div className="feature-card">
          <span className="feature-icon">📑</span>
          <h3>Comprehensive Reports</h3>
          <p>Download CSV and PDF reports for stakeholders, decision-makers, and public health officials</p>
        </div>

        <div className="feature-card">
          <span className="feature-icon">🌤️</span>
          <h3>Weather Integration</h3>
          <p>Incorporates temperature, humidity, and precipitation patterns that influence rabies transmission</p>
        </div>

        <div className="feature-card">
          <span className="feature-icon">💉</span>
          <h3>Vaccination Tracking</h3>
          <p>Measures the impact of mass vaccination campaigns on rabies case reduction</p>
        </div>
      </div>

      <div className="getting-started">
        <h3>🚀 Getting Started</h3>
        <ol>
          <li>Click on <strong>Forecasting</strong> in the navigation menu</li>
          <li>Browse municipalities and their barangays (color-coded by risk level)</li>
          <li>Click on any barangay to view detailed predictions and metrics</li>
          <li>Switch between <strong>Forecast</strong> and <strong>Model Insights</strong> tabs</li>
          <li>Download reports for offline analysis and sharing</li>
        </ol>
      </div>

      <div className="tech-stack">
        <h3>⚙️ Technology Stack</h3>
        <div className="tech-badges">
          <span className="tech-badge">NeuralProphet</span>
          <span className="tech-badge">XGBoost</span>
          <span className="tech-badge">React</span>
          <span className="tech-badge">FastAPI</span>
          <span className="tech-badge">Python</span>
          <span className="tech-badge">Recharts</span>
        </div>
      </div>

      <div className="data-info">
        <h3>📈 Data Coverage</h3>
        <div className="info-grid">
          <div className="info-item">
            <strong>Time Period:</strong> January 2020 - October 2024
          </div>
          <div className="info-item">
            <strong>Municipalities:</strong> ANTIPOLO, CAINTA, TAYTAY, ANGONO
          </div>
          <div className="info-item">
            <strong>Total Barangays:</strong> 40+
          </div>
          <div className="info-item">
            <strong>Forecast Horizon:</strong> 8 months ahead
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
