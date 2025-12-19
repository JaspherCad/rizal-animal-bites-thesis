import React from 'react';
import AppHeader from './AppHeader';
import './Layout.css';

function MainLayout({ children }) {
  return (
    <div className="app-layout">
      <AppHeader />
      <main className="main-content">
        {children}
      </main>
      <footer className="app-footer">
        <p>© 2024 Animal Bite Incident Forecasting System | Powered by AI & Machine Learning</p>
      </footer>
    </div>
  );
}

export default MainLayout;
