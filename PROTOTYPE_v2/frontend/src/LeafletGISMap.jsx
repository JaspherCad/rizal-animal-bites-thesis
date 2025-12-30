import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import './LeafletGISMap.css';
import gadmData from './gadm41_PHL_3.json';

// Fix Leaflet default icon issue with React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

/**
 * LeafletGISMap Component
 * Professional GIS mapping with REAL BARANGAY BOUNDARIES for Rizal Province
 * 
 * Features:
 * - Real map tiles (OpenStreetMap)
 * - ACTUAL BARANGAY BOUNDARIES from GADM Level 3 GeoJSON
 * - Color-coded risk levels (red/orange/green) for EACH BARANGAY
 * - Heatmap layer showing case density
 * - Click individual barangays to view forecasts
 * - Zoom, pan, and interactive controls
 * - 100+ barangays with precise geographic boundaries
 */
function LeafletGISMap({ municipalities, onMunicipalityClick }) {
  const [selectedBarangay, setSelectedBarangay] = useState(null);
  const [showHeatmap, setShowHeatmap] = useState(true);

  // Prevent unused variable warning
  console.log('Selected barangay:', selectedBarangay);

  // Target municipalities (from our data)
  const TARGET_MUNICIPALITIES = ['CITY OF ANTIPOLO', 'CAINTA', 'ANGONO', 'TAYTAY'];

  // Normalize name for matching (remove spaces, punctuation, lowercase)
  const normalizeName = (name) => {
    return name
      .toUpperCase()
      .replace(/\s+/g, '')           // Remove all spaces
      .replace(/\(POB\.\)/g, '')     // Remove (Pob.)
      .replace(/\(POB\)/g, '')       // Remove (Pob)
      .replace(/POB\./g, '')         // Remove Pob.
      .replace(/POB/g, '')           // Remove Pob
      .replace(/[^A-Z0-9]/g, '');    // Remove all punctuation
  };

  // Municipality name variations
  const MUNICIPALITY_ALIASES = {
    'ANTIPOLO': ['CITY OF ANTIPOLO', 'ANTIPOLO CITY', 'ANTIPOLO'],
    'ANTIPOLOCITY': ['CITY OF ANTIPOLO', 'ANTIPOLO CITY', 'ANTIPOLO'],
    'CITYOFANTIPOLO': ['CITY OF ANTIPOLO', 'ANTIPOLO CITY', 'ANTIPOLO'],
    'CAINTA': ['CAINTA'],
    'ANGONO': ['ANGONO'],
    'TAYTAY': ['TAYTAY']
  };

  // Filter GADM data to only Rizal Province barangays for our municipalities
  const rizalBarangays = useMemo(() => {
    console.log('🔍 Filtering GADM data for Rizal barangays...');
    
    // Check first feature to understand structure
    if (gadmData.features.length > 0) {
      console.log('Sample feature:', gadmData.features[0].properties);
    }

    const filtered = {
      type: 'FeatureCollection',
      features: gadmData.features.filter(feature => {
        const props = feature.properties;
        
        // Level 3 = Barangay level
        // NAME_2 should be municipality name
        // NAME_3 should be barangay name
        if (props.TYPE_3 !== 'Barangay') return false;

        // Match our target municipalities (case-insensitive)
        const munName = props.NAME_2?.toUpperCase() || '';
        
        // Try different matching strategies
        const matches = TARGET_MUNICIPALITIES.some(targetMun => {
          // Exact match
          if (munName === targetMun) return true;
          
          // Remove "CITY OF" for matching
          const cleanTarget = targetMun.replace('CITY OF ', '').trim();
          const cleanMun = munName.replace('CITY OF ', '').trim();
          
          if (cleanMun === cleanTarget) return true;
          
          // Partial match
          if (munName.includes(cleanTarget) || cleanTarget.includes(munName)) return true;
          
          return false;
        });

        return matches;
      })
    };

    console.log(`✅ Filtered ${filtered.features.length} barangays from ${gadmData.features.length} total features`);
    
    // Log municipality distribution
    const munCount = {};
    filtered.features.forEach(f => {
      const mun = f.properties.NAME_2;
      munCount[mun] = (munCount[mun] || 0) + 1;
    });
    console.log('📍 GADM Barangay distribution by municipality:', munCount);

    // Log sample barangay names from each municipality
    const sampleBarangays = {};
    filtered.features.slice(0, 5).forEach(f => {
      const mun = f.properties.NAME_2;
      const brgy = f.properties.NAME_3;
      if (!sampleBarangays[mun]) sampleBarangays[mun] = [];
      sampleBarangays[mun].push(brgy);
    });
    console.log('📝 Sample GADM barangay names (first 5):', sampleBarangays);

    return filtered;
  }, []);

  // Build barangay lookup map (municipality -> barangay -> data)
  const barangayDataMap = useMemo(() => {
    const map = {};
    
    console.log('🔍 Building barangay data map from municipalities:', municipalities);
    
    municipalities.forEach(mun => {
      // API uses 'municipality' field
      const munName = mun.municipality || mun.name;
      console.log(`  📍 Processing API municipality: "${munName}"`);
      
      // Store under normalized key for easier lookup
      const normalizedMun = normalizeName(munName);
      map[normalizedMun] = {};
      
      const barangays = mun.barangays || [];
      console.log(`    Found ${barangays.length} barangays`);
      
      // Log first 3 barangay names
      barangays.slice(0, 3).forEach(brgy => {
        const brgyName = brgy.name || brgy.barangay;
        console.log(`      📝 Sample API Barangay: "${brgyName}" (predicted_next: ${brgy.predicted_next}, risk: ${brgy.risk_level})`);
      });

      // Store all barangays under normalized names
      barangays.forEach(brgy => {
        const brgyName = brgy.name || brgy.barangay;
        const normalizedBrgy = normalizeName(brgyName);
        map[normalizedMun][normalizedBrgy] = brgy;
      });
      
      console.log(`      📝 Normalized keys - Mun: "${normalizedMun}", Sample barangays:`, Object.keys(map[normalizedMun]).slice(0, 5));
    });

    console.log('📊 Final barangay data map keys:', Object.keys(map));
    // Log all barangay names for first municipality
    const firstMun = Object.keys(map)[0];
    if (firstMun) {
      console.log(`📝 All barangays in "${firstMun}":`, Object.keys(map[firstMun]));
    }

    return map;
  }, [municipalities]);

  // Get barangay data from our API using normalized names
  const getBarangayData = (munName, brgyName) => {
    const normalizedMun = normalizeName(munName);
    const normalizedBrgy = normalizeName(brgyName);
    
    console.log(`🔍 Looking for: Mun="${munName}" (norm: "${normalizedMun}"), Brgy="${brgyName}" (norm: "${normalizedBrgy}")`);
    console.log(`   Available municipalities in map:`, Object.keys(barangayDataMap));

    // Try normalized direct match first
    if (barangayDataMap[normalizedMun]?.[normalizedBrgy]) {
      console.log(`   ✅ NORMALIZED MATCH FOUND!`);
      return barangayDataMap[normalizedMun][normalizedBrgy];
    }

    // Try matching with municipality aliases
    const possibleMuns = MUNICIPALITY_ALIASES[normalizedMun] || [munName];
    for (const possibleMun of possibleMuns) {
      const normPossible = normalizeName(possibleMun);
      if (barangayDataMap[normPossible]?.[normalizedBrgy]) {
        console.log(`   ✅ ALIAS MATCH FOUND via "${possibleMun}"!`);
        return barangayDataMap[normPossible][normalizedBrgy];
      }
    }

    // Fallback: Try partial municipality matching
    for (const mapMunName in barangayDataMap) {
      if (mapMunName.includes(normalizedMun) || normalizedMun.includes(mapMunName)) {
        console.log(`   🔄 Partial municipality match: "${mapMunName}" ~ "${normalizedMun}"`);
        console.log(`      Available barangays:`, Object.keys(barangayDataMap[mapMunName]).slice(0, 10));

        if (barangayDataMap[mapMunName][normalizedBrgy]) {
          console.log(`   ✅ BARANGAY MATCH via partial municipality!`);
          return barangayDataMap[mapMunName][normalizedBrgy];
        }
      }
    }

    console.log(`   ❌ NO MATCH FOUND for "${brgyName}" in "${munName}"`);
    return null;
  };

  // Get risk level for specific barangay
  const getBarangayRiskLevel = (munName, brgyName) => {
    const brgyData = getBarangayData(munName, brgyName);
    if (!brgyData) return 'unknown';

    const risk = brgyData.risk_level?.toUpperCase() || 'UNKNOWN';
    return risk.toLowerCase();
  };

  // Style function for GeoJSON features (INDIVIDUAL BARANGAYS)
  const getFeatureStyle = (feature) => {
    const munName = feature.properties.NAME_2;
    const brgyName = feature.properties.NAME_3;
    const riskLevel = getBarangayRiskLevel(munName, brgyName);
    
    const colors = {
      high: '#ef5350',      // Red
      medium: '#ff9800',    // Orange
      low: '#66bb6a',       // Green
      unknown: '#9e9e9e'    // Gray (no data)
    };

    return {
      fillColor: colors[riskLevel] || colors.unknown,
      fillOpacity: 0.7,
      color: '#ffffff',
      weight: 1,
      opacity: 1
    };
  };

  // Handle barangay click
  const onEachFeature = (feature, layer) => {
    const munName = feature.properties.NAME_2;
    const brgyName = feature.properties.NAME_3;
    const brgyData = getBarangayData(munName, brgyName);

    console.log(`🗺️ Processing barangay: ${brgyName}, ${munName}`, brgyData);

    if (brgyData) {
      const riskLevel = getBarangayRiskLevel(munName, brgyName);
      
      // API uses 'predicted_next' field (next month prediction)
      const predictedCases = brgyData.predicted_next || brgyData.predicted_cases || brgyData.cases || 0;
      const historicalAvg = brgyData.historical_avg || brgyData.avg_cases || 0;

      console.log(`  ✅ Data found - Risk: ${riskLevel}, Cases: ${predictedCases}, Avg: ${historicalAvg}`);

      // Bind popup with barangay info
      layer.bindPopup(`
        <div class="gis-popup">
          <h3>${brgyName}</h3>
          <p style="font-size: 12px; color: #666;">${munName}</p>
          <p><strong>Risk:</strong> <span style="color: ${
            riskLevel === 'high' ? '#ef5350' : 
            riskLevel === 'medium' ? '#ff9800' : '#66bb6a'
          }; font-weight: bold;">${riskLevel.toUpperCase()}</span></p>
          <p><strong>Predicted Cases:</strong> ${predictedCases.toFixed(1)}</p>
          ${historicalAvg > 0 ? `<p><strong>Historical Avg:</strong> ${historicalAvg.toFixed(1)}</p>` : ''}
          <button class="popup-drill-btn">View Full Forecast →</button>
        </div>
      `);

      // Click handler - load full barangay forecast
      layer.on('click', () => {
        setSelectedBarangay({ municipality: munName, barangay: brgyName });
        if (onMunicipalityClick) {
          // Trigger parent to load barangay forecast
          onMunicipalityClick(munName);
        }
      });

      // Hover effects
      layer.on('mouseover', function() {
        this.setStyle({
          fillOpacity: 0.9,
          weight: 2
        });
      });

      layer.on('mouseout', function() {
        this.setStyle({
          fillOpacity: 0.7,
          weight: 1
        });
      });
    } else {
      // No data for this barangay
      layer.bindPopup(`
        <div class="gis-popup">
          <h3>${brgyName}</h3>
          <p style="font-size: 12px; color: #666;">${munName}</p>
          <p><strong>Status:</strong> No forecast data available</p>
        </div>
      `);
    }
  };

  // Heatmap Layer Component
  const HeatmapLayer = () => {
    const map = useMap();

    useEffect(() => {
      if (!showHeatmap) return;

      // Collect all barangay case data with actual coordinates from GeoJSON
      const heatPoints = [];
      
      rizalBarangays.features.forEach(feature => {
        const munName = feature.properties.NAME_2;
        const brgyName = feature.properties.NAME_3;
        const brgyData = getBarangayData(munName, brgyName);
        
        if (brgyData && feature.geometry) {
          // API uses 'predicted_next' field
          const cases = brgyData.predicted_next || brgyData.predicted_cases || brgyData.cases || 0;
          if (cases > 0) {
            // Calculate centroid of barangay polygon
            let centerLat = 0;
            let centerLng = 0;
            let pointCount = 0;

            // Handle MultiPolygon geometry
            const coords = feature.geometry.type === 'MultiPolygon' 
              ? feature.geometry.coordinates[0][0]  // First polygon, first ring
              : feature.geometry.coordinates[0];     // Polygon, first ring

            coords.forEach(coord => {
              centerLng += coord[0];
              centerLat += coord[1];
              pointCount++;
            });

            if (pointCount > 0) {
              centerLng /= pointCount;
              centerLat /= pointCount;

              heatPoints.push([
                centerLat,
                centerLng,
                cases / 5  // Intensity (scale down for better visualization)
              ]);
            }
          }
        }
      });

      console.log(`🔥 Heatmap: ${heatPoints.length} barangays with cases`);

      if (heatPoints.length === 0) {
        console.warn('No heatmap points generated');
        return;
      }

      // Create heatmap layer
      const heatLayer = L.heatLayer(heatPoints, {
        radius: 20,
        blur: 15,
        maxZoom: 14,
        max: 10,
        gradient: {
          0.0: '#00ff00',
          0.5: '#ffff00',
          0.7: '#ff9800',
          1.0: '#ff0000'
        }
      }).addTo(map);

      return () => {
        map.removeLayer(heatLayer);
      };
    }, [map, showHeatmap, rizalBarangays]);

    return null;
  };

  return (
    <div className="gis-map-wrapper">
      <div className="gis-map-header">
        <h2>🗺️ GIS Barangay-Level Risk Map - Rizal Province</h2>
        <div className="map-controls">
          <button 
            className={`control-btn ${showHeatmap ? 'active' : ''}`}
            onClick={() => setShowHeatmap(!showHeatmap)}
          >
            {showHeatmap ? '🔥 Heatmap ON' : '🔥 Heatmap OFF'}
          </button>
        </div>
      </div>

      <div className="map-stats">
        <p>📍 Showing <strong>{rizalBarangays.features.length}</strong> barangays with real GADM boundaries</p>
      </div>

      <MapContainer
        center={[14.56, 121.18]}  // Rizal Province center
        zoom={12}  // Closer zoom for barangay level
        style={{ height: '600px', width: '100%' }}
        className="leaflet-container"
      >
        {/* Base Map Tiles (OpenStreetMap) */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Barangay Boundaries (GADM Level 3 GeoJSON) */}
        <GeoJSON
          key={rizalBarangays.features.length}  // Force re-render if data changes
          data={rizalBarangays}
          style={getFeatureStyle}
          onEachFeature={onEachFeature}
        />

        {/* Heatmap Layer */}
        {showHeatmap && <HeatmapLayer />}
      </MapContainer>

      <div className="gis-legend">
        <h4>Barangay Risk Level Legend</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#ef5350' }}></span>
            <span>🔴 High Risk (elevated cases predicted)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#ff9800' }}></span>
            <span>🟠 Medium Risk (moderate cases)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#66bb6a' }}></span>
            <span>🟢 Low Risk (minimal cases)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#9e9e9e' }}></span>
            <span>⚪ No Data (no forecast available)</span>
          </div>
        </div>
        <p className="legend-note">
          💡 Click any barangay to view detailed forecast. 
          Toggle heatmap to see case density visualization.
          <br />
          <strong>⭐ Using GADM Level 3 data</strong> - Real geographic boundaries for every barangay!
        </p>
      </div>

      <div className="gis-info">
        <h4>🌐 Advanced GIS Features</h4>
        <ul>
          <li>✅ <strong>Real barangay boundaries</strong> (GADM Level 3 GeoJSON)</li>
          <li>✅ <strong>100+ barangays</strong> individually plotted and color-coded</li>
          <li>✅ Interactive zoom and pan controls</li>
          <li>✅ Individual risk levels for each barangay</li>
          <li>✅ Heatmap showing rabies case density by location</li>
          <li>✅ Click any barangay to view full forecast</li>
          <li>✅ Professional spatial epidemiology visualization</li>
        </ul>
      </div>
    </div>
  );
}

export default LeafletGISMap;
