import React from 'react';

function RiskExplanation() {
  return (
    <div className="risk-explanation">
      <h3>🚦 Risk Level Guide</h3>
      <ul>
        <li>
          <strong>🔴 HIGH RISK (Red):</strong>
          {' '}Predicted cases are very high - <span className="action-needed">immediate action needed!</span> Increase vaccination campaigns, conduct awareness programs, and prepare resources.
        </li>
        <li>
          <strong>🟡 MEDIUM RISK (Orange):</strong>
          {' '}Cases above normal - <span className="action-needed">monitor closely.</span> Consider targeted interventions in affected areas.
        </li>
        <li>
          <strong>🟢 LOW RISK (Green):</strong>
          {' '}Cases within expected range - maintain current prevention measures and stay vigilant.
        </li>
      </ul>
    </div>
  );
}

export default RiskExplanation;
