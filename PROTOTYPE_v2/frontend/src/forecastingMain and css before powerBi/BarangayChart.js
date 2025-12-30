import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

function BarangayChart({ trainingData, validationData, forecastData }) {
  // Combine training, validation, and forecast data
  const allData = [
    ...trainingData.map(d => ({ ...d, type: 'Training' })),
    ...validationData.map(d => ({ ...d, type: 'Validation' }))
  ];

  // Add forecast data if provided
  if (forecastData && forecastData.length > 0) {
    const forecastPoints = forecastData.map(d => ({
      date: d.date,
      predicted: d.predicted,
      type: 'Forecast',
      forecast: d.predicted  // Separate field for forecast line
    }));
    allData.push(...forecastPoints);
  }

  // Find the split points
  const splitDate = trainingData.length > 0 
    ? trainingData[trainingData.length - 1].date 
    : null;
  
  const forecastStartDate = validationData.length > 0
    ? validationData[validationData.length - 1].date
    : null;

  return (
    <div className="chart-container">
      <h3>Model Performance & Future Forecast</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={allData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis label={{ value: 'Cases', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          
          {/* Vertical line showing train/val split */}
          {splitDate && (
            <ReferenceLine 
              x={splitDate} 
              stroke="orange" 
              strokeDasharray="3 3"
              label="Train/Val Split"
            />
          )}

          {/* Vertical line showing validation/forecast split */}
          {forecastStartDate && forecastData && forecastData.length > 0 && (
            <ReferenceLine 
              x={forecastStartDate} 
              stroke="#9c27b0" 
              strokeDasharray="5 5"
              strokeWidth={2}
              label="Forecast Start"
            />
          )}
          
          {/* Actual values line */}
          <Line 
            type="monotone" 
            dataKey="actual" 
            stroke="#000000" 
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Actual"
            connectNulls={false}
          />
          
          {/* Historical predictions (training + validation) */}
          <Line 
            type="monotone" 
            dataKey="predicted" 
            stroke="#2196F3" 
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 3 }}
            name="Predicted (Historical)"
            connectNulls={true}
          />

          {/* Future forecast predictions */}
          {forecastData && forecastData.length > 0 && (
            <Line 
              type="monotone" 
              dataKey="forecast" 
              stroke="#f50057" 
              strokeWidth={3}
              strokeDasharray="8 4"
              dot={{ r: 4, fill: '#f50057' }}
              name="Future Forecast"
              connectNulls={true}
            />
          )}
        </LineChart>
      </ResponsiveContainer>

      <div className="chart-legend">
        <p><strong>Black Line:</strong> Actual cases</p>
        <p><strong>Blue Dashed:</strong> Historical predictions (NeuralProphet + XGBoost)</p>
        {forecastData && forecastData.length > 0 && (
          <p><strong>Red Dashed:</strong> Future forecast (8 months ahead - safer approach)</p>
        )}
        <p><strong>Orange Line:</strong> Training/Validation split</p>
        {forecastData && forecastData.length > 0 && (
          <p><strong>Purple Line:</strong> Historical/Forecast split</p>
        )}
      </div>
    </div>
  );
}

export default BarangayChart;
