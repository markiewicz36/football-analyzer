import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-logo">
        <span>Football Analyzer</span>
      </Link>
      <div className="navbar-menu">
        <Link to="/settings" className="navbar-item">
          <i className="fas fa-cog"></i>
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;