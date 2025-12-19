import React, { useState, useEffect } from 'react';
import './BarangayChart.css';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { rabiesAPI } from '../services/api';

function BarangayChart({ municipality, barangay }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBarangayData();
  }, [municipality, barangay]);

  const fetchBarangayData = async () => {
    try {
      setLoading(true);
      const response = await rabiesAPI.getBarangayDetails(municipality, barangay);
      setData(response.barangay);
      setLoading(false);
    } catch (err) {
      setError('Failed to load barangay data');
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="chart-loading">Loading chart...</div>;
  }

  if (error) {
    return <div className="chart-error">{error}</div>;
  }

  if (!data) {
    return null;
  }

  // Combine training and validation data for the chart
  const chartData = [
    ...data.training_data.map(d => ({
      ...d,
      type: 'Training'
    })),
    ...data.validation_data.map(d => ({
      ...d,
      type: 'Validation'
    }))
  ];

  return (
    <div className="barangay-chart">
      <div className="chart-header">
        <h3>{barangay}, {municipality}</h3>
        <div className="chart-metrics">
          <span className="metric">MAE: {data.metrics.mae}</span>
          <span className="metric">RMSE: {data.metrics.rmse}</span>
          <span className="metric">R²: {data.metrics.r2}</span>
          <span className="metric improvement">↑ {data.metrics.improvement}% Improvement</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ecf0f1" />
          <XAxis 
            dataKey="date" 
            stroke="#7f8c8d"
            style={{ fontSize: '0.75rem' }}
          />
          <YAxis 
            stroke="#7f8c8d"
            style={{ fontSize: '0.75rem' }}
            label={{ value: 'Cases', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'white', 
              border: '2px solid #3498db',
              borderRadius: '8px',
              padding: '10px'
            }}
          />
          <Legend 
            wrapperStyle={{ paddingTop: '10px' }}
          />
          <Line 
            type="monotone" 
            dataKey="actual" 
            stroke="#e74c3c" 
            strokeWidth={2}
            dot={{ fill: '#e74c3c', r: 3 }}
            name="Actual Cases"
          />
          <Line 
            type="monotone" 
            dataKey="predicted" 
            stroke="#3498db" 
            strokeWidth={2}
            dot={{ fill: '#3498db', r: 3 }}
            name="Predicted Cases"
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-color actual"></span>
          <span>Actual Cases</span>
        </div>
        <div className="legend-item">
          <span className="legend-color predicted"></span>
          <span>Predicted Cases</span>
        </div>
        <div className="legend-note">
          Training data used to build the model | Validation data used to test accuracy
        </div>
      </div>
    </div>
  );
}

export default BarangayChart;
