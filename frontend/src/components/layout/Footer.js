import React from 'react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <p>© {currentYear} Football Analyzer - All rights reserved</p>
    </footer>
  );
};

export default Footer;