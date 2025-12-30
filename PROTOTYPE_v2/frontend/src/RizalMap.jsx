import React, { useState } from 'react';
import './RizalMap.css';

function RizalMap({ municipalities, onMunicipalityClick }) {
  const [hoveredMun, setHoveredMun] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  // Get municipality data by name
  const getMunData = (munName) => {
    return municipalities.find(m => m.municipality === munName) || {};
  };

  // Get risk level for municipality
  const getMunRiskLevel = (munName) => {
    const munData = getMunData(munName);
    if (!munData.risk_summary) return 'unknown';
    
    const { HIGH = 0, MEDIUM = 0, LOW = 0 } = munData.risk_summary;
    const total = HIGH + MEDIUM + LOW;
    
    if (total === 0) return 'unknown';
    
    // Determine overall risk
    const highPct = (HIGH / total) * 100;
    const mediumPct = (MEDIUM / total) * 100;
    
    if (highPct > 50) return 'high';
    if (highPct + mediumPct > 60) return 'medium';
    return 'low';
  };

  // Get total predicted cases for municipality
  const getMunTotalCases = (munName) => {
    const munData = getMunData(munName);
    if (!munData.barangays) return 0;
    return munData.barangays.reduce((sum, b) => sum + (b.predicted_next || 0), 0);
  };

  // Handle mouse move for tooltip
  const handleMouseMove = (e, munName) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setTooltipPos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
    setHoveredMun(munName);
  };

  const handleMouseLeave = () => {
    setHoveredMun(null);
  };

  const handleClick = (munName) => {
    onMunicipalityClick(munName);
  };

  // Simplified SVG paths for Rizal municipalities (approximation)
  const municipalityPaths = {
    'CITY OF ANTIPOLO': {
      // Large area (eastern part)
      path: 'M 450,150 L 700,150 L 700,450 L 500,500 L 450,350 Z',
      label: { x: 575, y: 320 }
    },
    'CAINTA': {
      // Northwest area
      path: 'M 200,180 L 400,160 L 450,280 L 350,320 L 200,300 Z',
      label: { x: 320, y: 240 }
    },
    'ANGONO': {
      // Southwest area
      path: 'M 180,320 L 350,330 L 380,450 L 250,480 L 180,420 Z',
      label: { x: 280, y: 390 }
    },
    'TAYTAY': {
      // Central area
      path: 'M 380,290 L 480,270 L 500,380 L 420,420 L 380,360 Z',
      label: { x: 435, y: 340 }
    }
  };

  return (
    <div className="rizal-map-wrapper">
      <div className="map-header">
        <h2>🗺️ Rizal Province Interactive Map</h2>
        <p className="map-subtitle">Click on a municipality to view barangay forecasts</p>
      </div>

      <div className="map-container">
        <svg viewBox="0 0 900 650" className="rizal-svg-map">
          {/* Background */}
          <rect x="0" y="0" width="900" height="650" fill="#f0f4f8" />
          
          {/* Province border */}
          <path 
            d="M 180,180 L 700,150 L 700,500 L 250,510 L 180,420 Z" 
            fill="none" 
            stroke="#1976d2" 
            strokeWidth="3"
            strokeDasharray="5,5"
            opacity="0.3"
          />

          {/* Draw each municipality */}
          {Object.entries(municipalityPaths).map(([munName, munData]) => {
            const riskLevel = getMunRiskLevel(munName);
            const totalCases = getMunTotalCases(munName);
            const data = getMunData(munName);
            
            return (
              <g key={munName}>
                {/* Municipality area */}
                <path
                  d={munData.path}
                  className={`municipality-area risk-${riskLevel} ${hoveredMun === munName ? 'hovered' : ''}`}
                  onClick={() => handleClick(munName)}
                  onMouseMove={(e) => handleMouseMove(e, munName)}
                  onMouseLeave={handleMouseLeave}
                  style={{ cursor: 'pointer' }}
                />
                
                {/* Municipality label */}
                <text
                  x={munData.label.x}
                  y={munData.label.y}
                  className="municipality-label"
                  textAnchor="middle"
                  pointerEvents="none"
                >
                  {munName.replace('CITY OF ', '')}
                </text>
                
                {/* Cases count */}
                <text
                  x={munData.label.x}
                  y={munData.label.y + 25}
                  className="municipality-cases"
                  textAnchor="middle"
                  pointerEvents="none"
                >
                  {totalCases.toFixed(0)} cases
                </text>
                
                {/* Barangay count */}
                <text
                  x={munData.label.x}
                  y={munData.label.y + 45}
                  className="municipality-barangays"
                  textAnchor="middle"
                  pointerEvents="none"
                >
                  {data.total_barangays || 0} barangays
                </text>
              </g>
            );
          })}

          {/* Tooltip */}
          {hoveredMun && (
            <g className="map-tooltip" transform={`translate(${tooltipPos.x}, ${tooltipPos.y})`}>
              <rect
                x="10"
                y="-40"
                width="200"
                height="80"
                fill="rgba(0, 0, 0, 0.9)"
                stroke="#fff"
                strokeWidth="2"
                rx="5"
              />
              <text x="20" y="-20" fill="#fff" fontSize="14" fontWeight="bold">
                {hoveredMun}
              </text>
              <text x="20" y="0" fill="#ffd700" fontSize="12">
                {getMunRiskLevel(hoveredMun).toUpperCase()} RISK
              </text>
              <text x="20" y="20" fill="#fff" fontSize="12">
                Total: {getMunTotalCases(hoveredMun).toFixed(0)} cases
              </text>
            </g>
          )}
        </svg>
      </div>

      {/* Map Legend */}
      <div className="map-legend">
        <h4>Risk Level Legend</h4>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color risk-high"></div>
            <span>🔴 HIGH RISK</span>
          </div>
          <div className="legend-item">
            <div className="legend-color risk-medium"></div>
            <span>🟡 MEDIUM RISK</span>
          </div>
          <div className="legend-item">
            <div className="legend-color risk-low"></div>
            <span>🟢 LOW RISK</span>
          </div>
        </div>
      </div>

      {/* Map Instructions */}
      <div className="map-instructions">
        <p>💡 <strong>Tip:</strong> Hover over municipalities to see details. Click to view barangay-level forecasts.</p>
      </div>
    </div>
  );
}

export default RizalMap;
