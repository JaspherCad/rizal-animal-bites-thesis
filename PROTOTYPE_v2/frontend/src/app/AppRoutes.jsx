import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Home from '../features/home/Home';
import ForecastingRoutes from '../features/forecasting/ForecastingRoutes';

/**
 * Main application routes
 * All routes are defined here with their respective components
 */
function AppRoutes() {
  return (
    <Routes>
      {/* Home page */}
      <Route path="/" element={<Home />} />
      
      {/* Forecasting feature with nested routes */}
      <Route path="/forecasting/*" element={<ForecastingRoutes />} />
      
      {/* Catch-all route for 404 Not Found */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

/**
 * Simple 404 Not Found component
 */
function NotFound() {
  return (
    <div style={{ 
      textAlign: 'center', 
      padding: '4rem',
      maxWidth: '600px',
      margin: '0 auto'
    }}>
      <h1 style={{ fontSize: '4rem', color: '#667eea' }}>404</h1>
      <h2>Page Not Found</h2>
      <p>The page you're looking for doesn't exist.</p>
      <a 
        href="/" 
        style={{
          display: 'inline-block',
          marginTop: '2rem',
          padding: '0.75rem 1.5rem',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '8px',
          fontWeight: '600'
        }}
      >
        Go Back Home
      </a>
    </div>
  );
}

export default AppRoutes;
