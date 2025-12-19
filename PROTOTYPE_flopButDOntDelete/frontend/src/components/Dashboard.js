import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import AlertList from './AlertList';
import MunicipalityCard from './MunicipalityCard';
import { rabiesAPI } from '../services/api';

function Dashboard() {
  const [alerts, setAlerts] = useState([]);
  const [municipalities, setMunicipalities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMunicipality, setSelectedMunicipality] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    fetchData();
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchData, 300000);
    return () => clearInterval(interval);
  }, [selectedMunicipality]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [alertsData, municipalitiesData] = await Promise.all([
        rabiesAPI.getAlerts(selectedMunicipality),
        rabiesAPI.getMunicipalities()
      ]);
      
      setAlerts(alertsData.alerts || []);
      setMunicipalities(municipalitiesData.municipalities || []);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAlertSummary = () => {
    const high = alerts.filter(a => a.alert_level === 'HIGH').length;
    const medium = alerts.filter(a => a.alert_level === 'MEDIUM').length;
    const low = alerts.filter(a => a.alert_level === 'LOW').length;
    return { high, medium, low, total: alerts.length };
  };

  const summary = getAlertSummary();

  return (
    <div className="dashboard">
      {/* Alert Summary Banner */}
      <div className="alert-summary">
        <div className="summary-card total">
          <div className="summary-number">{summary.total}</div>
          <div className="summary-label">Total Alerts</div>
        </div>
        <div className="summary-card high">
          <div className="summary-number">{summary.high}</div>
          <div className="summary-label">🔴 High Priority</div>
        </div>
        <div className="summary-card medium">
          <div className="summary-number">{summary.medium}</div>
          <div className="summary-label">🟡 Medium Priority</div>
        </div>
        <div className="summary-card low">
          <div className="summary-number">{summary.low}</div>
          <div className="summary-label">🟢 Low Priority</div>
        </div>
      </div>

      {/* Municipality Filter */}
      <div className="filter-bar">
        <label>Filter by Municipality:</label>
        <select 
          value={selectedMunicipality || ''} 
          onChange={(e) => setSelectedMunicipality(e.target.value || null)}
        >
          <option value="">All Municipalities</option>
          {municipalities.map(mun => (
            <option key={mun.municipality} value={mun.municipality}>
              {mun.municipality}
            </option>
          ))}
        </select>
        <button onClick={fetchData} className="refresh-btn">
          🔄 Refresh
        </button>
        <span className="last-update">
          Last updated: {lastUpdate.toLocaleTimeString()}
        </span>
      </div>

      {/* Municipality Cards */}
      <div className="municipalities-section">
        <h2>Municipality Overview</h2>
        <div className="municipality-grid">
          {loading ? (
            <div className="loading">Loading...</div>
          ) : (
            municipalities.map(mun => (
              <MunicipalityCard 
                key={mun.municipality} 
                data={mun}
                isSelected={false}
              />
            ))
          )}
        </div>
      </div>

      {/* Alerts List */}
      <div className="alerts-section">
        <h2>Active Alerts</h2>
        {loading ? (
          <div className="loading">Loading alerts...</div>
        ) : alerts.length === 0 ? (
          <div className="no-alerts">
            <p>✅ No active alerts. All barangays within normal thresholds.</p>
          </div>
        ) : (
          <AlertList alerts={alerts} />
        )}
      </div>
    </div>
  );
}

export default Dashboard;
