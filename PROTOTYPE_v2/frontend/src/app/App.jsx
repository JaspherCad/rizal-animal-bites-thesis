import React from 'react';
import MainLayout from '../components/Layout/MainLayout';
import AppRoutes from './AppRoutes';

/**
 * Root App component
 * Provides layout wrapper and routing
 */
function App() {
  return (
    <MainLayout>
      <AppRoutes />
    </MainLayout>
  );
}

export default App;
