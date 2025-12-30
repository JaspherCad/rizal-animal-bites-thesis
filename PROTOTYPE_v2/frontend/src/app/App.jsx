import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '../components/Layout/MainLayout';
import ProtectedRoute from '../components/ProtectedRoute';
import Login from '../features/auth/Login';
import Home from '../features/home/Home';
import MunicipalityList from '../features/forecasting/MunicipalityList';
import ForecastingMain from '../ForecastingMain'
import BarangayDetails from '../features/forecasting/BarangayDetails';
import { useAuth } from '../context/AuthContext';

/**
 * Root App component with all routes in one place
 * Simple nested routing structure with MainLayout as parent
 * Public routes: /, /login
 * Protected routes: /forecasting
 */
function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public Login Route */}
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/" replace /> : <Login />
      } />






      {/* Routes with MainLayout */}
      <Route path="/" element={<MainLayout />}>
        {/* Public Home Route */}
        <Route index element={<Home />} />
        
        {/* Protected Forecasting Routes */}
        <Route path="forecasting" element={<ProtectedRoute />}>
          <Route index element={<ForecastingMain />} />
        </Route>
        
        {/* 404 Not Found */}
        <Route path="*" element={<NotFound />} />
      </Route>
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

export default App;
