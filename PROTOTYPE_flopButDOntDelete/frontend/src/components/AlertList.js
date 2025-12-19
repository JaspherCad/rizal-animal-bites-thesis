import React, { useState } from 'react';
import './AlertList.css';

function AlertList({ alerts }) {
  const [sortBy, setSortBy] = useState('alert_level');
  const [sortOrder, setSortOrder] = useState('asc');
  const [filterLevel, setFilterLevel] = useState('all');

  // Filter alerts
  const filteredAlerts = alerts.filter(alert => {
    if (filterLevel === 'all') return true;
    return alert.alert_level === filterLevel;
  });

  // Sort alerts
  const sortedAlerts = [...filteredAlerts].sort((a, b) => {
    let compareA, compareB;

    switch (sortBy) {
      case 'alert_level':
        const levelOrder = { 'HIGH': 0, 'MEDIUM': 1, 'LOW': 2 };
        compareA = levelOrder[a.alert_level];
        compareB = levelOrder[b.alert_level];
        break;
      case 'predicted_cases':
        compareA = a.predicted_cases;
        compareB = b.predicted_cases;
        break;
      case 'municipality':
        compareA = a.municipality;
        compareB = b.municipality;
        break;
      case 'barangay':
        compareA = a.barangay;
        compareB = b.barangay;
        break;
      default:
        return 0;
    }

    if (compareA < compareB) return sortOrder === 'asc' ? -1 : 1;
    if (compareA > compareB) return sortOrder === 'asc' ? 1 : -1;
    return 0;
  });

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const getAlertBadge = (level) => {
    const badges = {
      'HIGH': { emoji: '🔴', class: 'badge-high', text: 'HIGH' },
      'MEDIUM': { emoji: '🟡', class: 'badge-medium', text: 'MEDIUM' },
      'LOW': { emoji: '🟢', class: 'badge-low', text: 'LOW' }
    };
    return badges[level] || { emoji: '⚪', class: 'badge-normal', text: 'NORMAL' };
  };

  return (
    <div className="alert-list">
      {/* Controls */}
      <div className="alert-controls">
        <div className="filter-group">
          <label>Filter by Level:</label>
          <select value={filterLevel} onChange={(e) => setFilterLevel(e.target.value)}>
            <option value="all">All Levels</option>
            <option value="HIGH">🔴 High</option>
            <option value="MEDIUM">🟡 Medium</option>
            <option value="LOW">🟢 Low</option>
          </select>
        </div>
        <div className="sort-group">
          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="alert_level">Alert Level</option>
            <option value="predicted_cases">Predicted Cases</option>
            <option value="municipality">Municipality</option>
            <option value="barangay">Barangay</option>
          </select>
          <button 
            className="sort-toggle"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          >
            {sortOrder === 'asc' ? '⬆️' : '⬇️'}
          </button>
        </div>
        <div className="result-count">
          Showing {sortedAlerts.length} of {alerts.length} alerts
        </div>
      </div>

      {/* Alert Cards */}
      <div className="alert-cards">
        {sortedAlerts.map((alert, index) => {
          const badge = getAlertBadge(alert.alert_level);
          
          return (
            <div key={index} className={`alert-card ${badge.class}`}>
              <div className="alert-header">
                <div className="alert-badge">
                  <span className="badge-emoji">{badge.emoji}</span>
                  <span className="badge-text">{badge.text}</span>
                </div>
                <div className="alert-location">
                  <strong>{alert.barangay}</strong>
                  <span className="municipality-tag">{alert.municipality}</span>
                </div>
              </div>

              <div className="alert-body">
                <div className="alert-message">
                  {alert.message}
                </div>
                
                <div className="alert-stats">
                  <div className="stat">
                    <span className="stat-label">Forecast Date:</span>
                    <span className="stat-value">{alert.forecast_date}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Predicted:</span>
                    <span className="stat-value highlight">{alert.predicted_cases} cases</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Historical Avg:</span>
                    <span className="stat-value">{alert.historical_avg} cases</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Model MAE:</span>
                    <span className="stat-value">±{alert.model_mae}</span>
                  </div>
                </div>

                {alert.seasonal_alert !== 'No surge' && (
                  <div className="seasonal-warning">
                    <strong>{alert.seasonal_alert}</strong>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {sortedAlerts.length === 0 && (
        <div className="no-results">
          <p>No alerts match your filters</p>
        </div>
      )}
    </div>
  );
}

export default AlertList;
