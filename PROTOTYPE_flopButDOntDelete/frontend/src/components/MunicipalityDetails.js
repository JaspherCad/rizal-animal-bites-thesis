import React, { useState, useEffect } from 'react';
import './MunicipalityDetails.css';
import BarangayChart from './BarangayChart';
import { rabiesAPI } from '../services/api';

function MunicipalityDetails({ municipality, onClose }) {
  const [barangays, setBarangays] = useState([]);
  const [selectedBarangay, setSelectedBarangay] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMunicipalityData();
  }, [municipality]);

  const fetchMunicipalityData = async () => {
    try {
      setLoading(true);
      const response = await rabiesAPI.getAlerts(municipality);
      
      // Get unique barangays from alerts (we'll show all barangays with alerts)
      const barangayList = response.alerts.map(alert => ({
        name: alert.barangay,
        predicted: alert.predicted_cases,
        alertLevel: alert.alert_level
      }));
      
      setBarangays(barangayList);
      if (barangayList.length > 0) {
        setSelectedBarangay(barangayList[0].name);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching municipality data:', error);
      setLoading(false);
    }
  };

  const getAlertBadgeClass = (level) => {
    const classes = {
      'HIGH': 'badge-high',
      'MEDIUM': 'badge-medium',
      'LOW': 'badge-low'
    };
    return classes[level] || 'badge-normal';
  };

  return (
    <div className="municipality-details-overlay" onClick={onClose}>
      <div className="municipality-details" onClick={(e) => e.stopPropagation()}>
        <div className="details-header">
          <h2>📍 {municipality}</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {loading ? (
          <div className="details-loading">Loading barangay data...</div>
        ) : barangays.length === 0 ? (
          <div className="no-data">
            <p>✅ No alerts for this municipality. All barangays within normal thresholds.</p>
          </div>
        ) : (
          <>
            <div className="barangay-selector">
              <label>Select Barangay:</label>
              <div className="barangay-buttons">
                {barangays.map((brgy, index) => (
                  <button
                    key={index}
                    className={`barangay-btn ${selectedBarangay === brgy.name ? 'active' : ''} ${getAlertBadgeClass(brgy.alertLevel)}`}
                    onClick={() => setSelectedBarangay(brgy.name)}
                  >
                    <span className="brgy-name">{brgy.name}</span>
                    <span className="brgy-cases">{brgy.predicted.toFixed(1)} cases</span>
                  </button>
                ))}
              </div>
            </div>

            {selectedBarangay && (
              <BarangayChart 
                municipality={municipality} 
                barangay={selectedBarangay}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default MunicipalityDetails;
