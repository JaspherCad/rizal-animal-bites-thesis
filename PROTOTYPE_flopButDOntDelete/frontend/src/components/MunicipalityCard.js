import React, { useState } from 'react';
import './MunicipalityCard.css';
import MunicipalityDetails from './MunicipalityDetails';

function MunicipalityCard({ data, isSelected }) {
  const [showDetails, setShowDetails] = useState(false);
  
  const getTotalAlerts = () => {
    return data.high_alerts + data.medium_alerts + data.low_alerts;
  };

  const getAlertColor = () => {
    if (data.high_alerts > 0) return 'red';
    if (data.medium_alerts > 0) return 'yellow';
    if (data.low_alerts > 0) return 'green';
    return 'gray';
  };

  const totalAlerts = getTotalAlerts();
  const alertColor = getAlertColor();

  return (
    <>
      <div 
        className={`municipality-card ${isSelected ? 'selected' : ''} alert-${alertColor}`}
      >
      <div className="card-header">
        <h3>{data.municipality}</h3>
        {totalAlerts > 0 && (
          <span className={`alert-count ${alertColor}`}>
            {totalAlerts} {totalAlerts === 1 ? 'alert' : 'alerts'}
          </span>
        )}
      </div>

      <div className="card-body">
        <div className="stat-row">
          <div className="stat-item">
            <span className="stat-icon">📍</span>
            <div className="stat-content">
              <div className="stat-number">{data.total_barangays}</div>
              <div className="stat-label">Barangays</div>
            </div>
          </div>
          
          <div className="stat-item">
            <span className="stat-icon">📊</span>
            <div className="stat-content">
              <div className="stat-number">{data.total_predicted_cases}</div>
              <div className="stat-label">Predicted Cases</div>
            </div>
          </div>
        </div>

        <div className="stat-row">
          <div className="stat-item">
            <span className="stat-icon">🎯</span>
            <div className="stat-content">
              <div className="stat-number">±{data.avg_mae}</div>
              <div className="stat-label">Avg MAE</div>
            </div>
          </div>
        </div>

        {totalAlerts > 0 && (
          <div className="alert-breakdown">
            <div className="breakdown-title">Alert Breakdown:</div>
            <div className="breakdown-items">
              {data.high_alerts > 0 && (
                <span className="breakdown-badge high">
                  🔴 {data.high_alerts} High
                </span>
              )}
              {data.medium_alerts > 0 && (
                <span className="breakdown-badge medium">
                  🟡 {data.medium_alerts} Medium
                </span>
              )}
              {data.low_alerts > 0 && (
                <span className="breakdown-badge low">
                  🟢 {data.low_alerts} Low
                </span>
              )}
            </div>
          </div>
        )}
      </div>

        <div className="card-footer">
          <button 
            className="view-details-btn"
            onClick={() => setShowDetails(true)}
          >
            📊 View Barangay Charts
          </button>
        </div>
      </div>

      {showDetails && (
        <MunicipalityDetails 
          municipality={data.municipality}
          onClose={() => setShowDetails(false)}
        />
      )}
    </>
  );
}

export default MunicipalityCard;
