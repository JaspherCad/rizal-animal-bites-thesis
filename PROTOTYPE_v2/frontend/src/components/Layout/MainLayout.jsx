import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import AppHeader from './AppHeader';
import './Layout.css';

function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const closeSidebar = () => setSidebarOpen(false);

  return (
    <div className="app-layout">
      {/* Top bar with menu button */}
      <div className="top-bar">
        <button className="menu-toggle" onClick={toggleSidebar}>
          ☰
        </button>
        <h1 className="top-bar-title">🐕 Animal Bite Forecasting</h1>
      </div>

      {/* Sidebar Navigation */}
      <AppHeader isOpen={sidebarOpen} onClose={closeSidebar} />

      {/* Overlay */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={closeSidebar}></div>}

      <main className="main-content">
        <Outlet />
      </main>

      <footer className="app-footer">
        <p>© 2024 Animal Bite Incident Forecasting System | Powered by AI & Machine Learning</p>
      </footer>
    </div>
  );
}

export default MainLayout;
