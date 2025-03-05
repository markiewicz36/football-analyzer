import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <ul className="sidebar-menu">
        <li className="sidebar-item">
          <NavLink to="/" className={({ isActive }) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <i className="fas fa-tachometer-alt sidebar-icon"></i>
            <span>Dashboard</span>
          </NavLink>
        </li>
        <li className="sidebar-item">
          <NavLink to="/fixtures" className={({ isActive }) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <i className="fas fa-futbol sidebar-icon"></i>
            <span>Fixtures</span>
          </NavLink>
        </li>
        <li className="sidebar-item">
          <NavLink to="/teams" className={({ isActive }) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <i className="fas fa-users sidebar-icon"></i>
            <span>Teams</span>
          </NavLink>
        </li>
        <li className="sidebar-item">
          <NavLink to="/leagues" className={({ isActive }) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <i className="fas fa-trophy sidebar-icon"></i>
            <span>Leagues</span>
          </NavLink>
        </li>
        <li className="sidebar-item">
          <NavLink to="/predictions" className={({ isActive }) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <i className="fas fa-chart-line sidebar-icon"></i>
            <span>Predictions</span>
          </NavLink>
        </li>
        <li className="sidebar-item">
          <NavLink to="/statistics" className={({ isActive }) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <i className="fas fa-chart-bar sidebar-icon"></i>
            <span>Statistics</span>
          </NavLink>
        </li>
        <li className="sidebar-item">
          <NavLink to="/betting" className={({ isActive }) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <i className="fas fa-money-bill-wave sidebar-icon"></i>
            <span>Betting</span>
          </NavLink>
          <ul className="sidebar-submenu">
            <li className="sidebar-subitem">
              <NavLink to="/betting/value-bets" className={({ isActive }) => isActive ? "sidebar-sublink active" : "sidebar-sublink"}>
                <i className="fas fa-percentage sidebar-icon"></i>
                <span>Value Bets</span>
              </NavLink>
            </li>
          </ul>
        </li>
        <li className="sidebar-item">
          <NavLink to="/ai-chat" className={({ isActive }) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <i className="fas fa-robot sidebar-icon"></i>
            <span>AI Chat</span>
          </NavLink>
        </li>
      </ul>
    </aside>
  );
};

export default Sidebar;