import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMunicipalities } from './hooks';
import './styles.css';

function MunicipalityList() {
  const navigate = useNavigate();
  const { municipalities, loading, error } = useMunicipalities();

  const handleBarangayClick = (municipality, barangay) => {
    navigate(`/forecasting/${municipality}/${barangay}`);
  };

  if (loading) {
    return <div className="loading">Loading municipalities...</div>;
  }

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  return (
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
  );
}

export default MunicipalityList;
