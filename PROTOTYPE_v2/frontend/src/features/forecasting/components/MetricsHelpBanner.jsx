import React from 'react';

function MetricsHelpBanner() {
  return (
    <div className="metrics-help-banner">
      <span className="help-icon">💡</span>
      <div className="help-content">
        <h3>Understanding Model Metrics</h3>
        <p>These numbers tell you how accurate our predictions are. Lower is better for all metrics!</p>
        <ul className="metrics-legend">
          <li>
            <strong>MAE (Mean Absolute Error)</strong>
            {' '}Average prediction error. If MAE = 1.5, predictions are off by ~1-2 cases. <span className="good-value">Under 2 is excellent!</span>
          </li>
          <li>
            <strong>RMSE (Root Mean Squared Error)</strong>
            {' '}Similar to MAE but penalizes big errors more. <span className="good-value">Close to MAE is good!</span>
          </li>
          <li>
            <strong>MASE (Mean Absolute Scaled Error)</strong>
            {' '}Compares to simple baseline. <span className="good-value">Under 1 means better than basic forecast!</span>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default MetricsHelpBanner;
