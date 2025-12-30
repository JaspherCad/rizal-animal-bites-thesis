import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Layout.css';

function AppHeader({ isOpen, onClose }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    onClose();
    navigate('/login');
  };

  return (
    <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
      <div className="sidebar-header">
        <h2>🐕 Menu</h2>
        <button className="sidebar-close" onClick={onClose}>
          ✕
        </button>
      </div>

      <div className="sidebar-content">
        <h3 className="sidebar-title">Animal Bite Forecasting</h3>
        <p className="sidebar-subtitle">NeuralProphet + XGBoost Hybrid Model</p>
      </div>

      <nav className="sidebar-nav">
        <Link to="/" className="sidebar-link" onClick={onClose}>
          <span className="link-icon">🏠</span>
          <span>Home</span>
        </Link>

        <Link to="/forecasting" className="sidebar-link" onClick={onClose}>
          <span className="link-icon">📊</span>
          <span>Forecasting</span>
        </Link>

        <button className="sidebar-link sidebar-logout" onClick={handleLogout}>
          <span className="link-icon">🚪</span>
          <span>Logout</span>
        </button>
      </nav>

      <div className="sidebar-footer">
        <p>© 2024 AI & ML Powered</p>
      </div>
    </aside>
  );
}

export default AppHeader;
