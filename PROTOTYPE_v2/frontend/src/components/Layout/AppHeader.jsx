import React from 'react';
import { Link } from 'react-router-dom';
import './Layout.css';

function AppHeader() {
  return (
    <header className="app-header">
      <div className="header-content">
        <h1>🐕 ANIMAL BITE INCIDENT Forecasting Dashboard</h1>
        <p className="subtitle">NeuralProphet + XGBoost Hybrid Model</p>
      </div>
      <nav className="header-nav">
        <Link to="/" className="nav-link">🏠 Home</Link>
        <Link to="/forecasting" className="nav-link">📊 Forecasting</Link>
      </nav>
    </header>
  );
}

export default AppHeader;
