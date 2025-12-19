import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MunicipalityList from './MunicipalityList';
import BarangayDetails from './BarangayDetails';

/**
 * Nested routes for the forecasting feature
 * Base path: /forecasting
 */
function ForecastingRoutes() {
  return (
    <Routes>
      {/* List all municipalities and barangays */}
      <Route index element={<MunicipalityList />} />
      
      {/* Individual barangay details with forecast and insights */}
      <Route path=":municipality/:barangay" element={<BarangayDetails />} />
    </Routes>
  );
}

export default ForecastingRoutes;
