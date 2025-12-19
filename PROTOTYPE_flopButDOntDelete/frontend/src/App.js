import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import { rabiesAPI } from './services/api';

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    // Check API connection on mount
    const checkConnection = async () => {
      try {
        const status = await rabiesAPI.healthCheck();
        setSystemStatus(status);
        setLoading(false);
      } catch (err) {
        setError('Failed to connect to API server. Please ensure backend is running on port 8000.');
        setLoading(false);
      }
    };

    checkConnection();
  }, []);

  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner"></div>
        <p>Connecting to Rabies Alert System...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-error">
        <div className="error-card">
          <h2>⚠️ Connection Error</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🦠 Rabies Alert System</h1>
          <p>AI-Powered Forecasting for Rizal Province</p>
        </div>
        <div className="header-status">
          <span className="status-indicator active"></span>
          <span>{systemStatus?.total_barangays || 0} Barangays Monitored</span>
        </div>
      </header>
      
      <main className="app-main">
        <Dashboard />
      </main>

      <footer className="app-footer">
        <p>Hybrid NeuralProphet + XGBoost Model | Version {systemStatus?.version || '1.0.0'}</p>
      </footer>
    </div>
  );
}

export default App;
