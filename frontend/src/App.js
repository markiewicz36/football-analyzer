import React from 'react';
import { Routes, Route } from 'react-router-dom';
import './App.css';

// Layout Components
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import Footer from './components/layout/Footer';

// Page Components
import Dashboard from './pages/Dashboard';
import Fixtures from './pages/Fixtures';
import FixtureDetails from './pages/FixtureDetails';
import FixtureAnalysis from './pages/FixtureAnalysis';
import Teams from './pages/Teams';
import TeamDetails from './pages/TeamDetails';
import Leagues from './pages/Leagues';
import LeagueDetails from './pages/LeagueDetails';
import Predictions from './pages/Predictions';
import Statistics from './pages/Statistics';
import Betting from './pages/Betting';
import ValueBets from './pages/ValueBets';
import AiChat from './pages/AiChat';
import Settings from './pages/Settings';

function App() {
  return (
    <div className="app">
      <Navbar />
      <div className="main-container">
        <Sidebar />
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/fixtures" element={<Fixtures />} />
            <Route path="/fixtures/:id" element={<FixtureDetails />} />
            <Route path="/fixtures/:id/analysis" element={<FixtureAnalysis />} />
            <Route path="/teams" element={<Teams />} />
            <Route path="/teams/:id" element={<TeamDetails />} />
            <Route path="/leagues" element={<Leagues />} />
            <Route path="/leagues/:id" element={<LeagueDetails />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/statistics" element={<Statistics />} />
            <Route path="/betting" element={<Betting />} />
            <Route path="/betting/value-bets" element={<ValueBets />} />
            <Route path="/ai-chat" element={<AiChat />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
      <Footer />
    </div>
  );
}

export default App;