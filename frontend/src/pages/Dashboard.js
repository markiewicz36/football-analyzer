import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

// Components
import LiveFixtures from '../components/dashboard/LiveFixtures';
import UpcomingFixtures from '../components/dashboard/UpcomingFixtures';
import RecentResults from '../components/dashboard/RecentResults';
import TopLeagues from '../components/dashboard/TopLeagues';
import ValueBets from '../components/dashboard/ValueBets';

const Dashboard = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [liveFixtures, setLiveFixtures] = useState([]);
  const [upcomingFixtures, setUpcomingFixtures] = useState([]);
  const [recentResults, setRecentResults] = useState([]);
  const [valueBets, setValueBets] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);

        // Fetch live fixtures
        const liveResponse = await axios.get('/api/fixtures', {
          params: { live: 'all' }
        });
        setLiveFixtures(liveResponse.data.response || []);

        // Fetch upcoming fixtures (next 3 days)
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];
        const upcomingResponse = await axios.get('/api/fixtures', {
          params: { date: formattedDate }
        });
        setUpcomingFixtures(upcomingResponse.data.response || []);

        // Fetch recent results (last 3 days)
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const formattedYesterday = yesterday.toISOString().split('T')[0];
        const recentResponse = await axios.get('/api/fixtures', {
          params: { date: formattedYesterday, status: 'FT' }
        });
        setRecentResults(recentResponse.data.response || []);

        // Fetch value bets
        // Note: In a real app, this endpoint would return actual value bets
        // For now, we'll just use a mock endpoint
        const valueBetsResponse = await axios.get('/api/betting', {
          params: { type: 'value' }
        }).catch(() => ({ data: { response: [] } }));
        setValueBets(valueBetsResponse.data.response || []);

        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to fetch dashboard data. Please try again later.');
        setIsLoading(false);
      }
      );
};

export default Dashboard;

    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-message">{error}</p>
        <button className="btn btn-primary" onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome to Football Analyzer - Your sports data analysis hub</p>
      </div>

      <div className="dashboard-cards">
        <div className="stat-card">
          <div className="stat-card-title">Live Matches</div>
          <div className="stat-card-value">{liveFixtures.length}</div>
          <Link to="/fixtures?live=true" className="btn btn-outline-primary">
            View All
          </Link>
        </div>

        <div className="stat-card">
          <div className="stat-card-title">Today's Matches</div>
          <div className="stat-card-value">{upcomingFixtures.length}</div>
          <Link to="/fixtures" className="btn btn-outline-primary">
            View All
          </Link>
        </div>

        <div className="stat-card">
          <div className="stat-card-title">Value Bets</div>
          <div className="stat-card-value">{valueBets.length}</div>
          <Link to="/betting" className="btn btn-outline-primary">
            View All
          </Link>
        </div>

        <div className="stat-card">
          <div className="stat-card-title">AI Predictions</div>
          <div className="stat-card-value">24</div> {/* Mock data */}
          <Link to="/predictions" className="btn btn-outline-primary">
            View All
          </Link>
        </div>
      </div>

      <div className="grid">
        <div className="col-8 col-md-12">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Live Fixtures</h2>
              <Link to="/fixtures?live=true" className="btn btn-sm btn-outline-primary">
                View All
              </Link>
            </div>
            <div className="card-body">
              <LiveFixtures fixtures={liveFixtures} />
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Upcoming Fixtures</h2>
              <Link to="/fixtures" className="btn btn-sm btn-outline-primary">
                View All
              </Link>
            </div>
            <div className="card-body">
              <UpcomingFixtures fixtures={upcomingFixtures} />
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Recent Results</h2>
              <Link to="/fixtures?status=FT" className="btn btn-sm btn-outline-primary">
                View All
              </Link>
            </div>
            <div className="card-body">
              <RecentResults fixtures={recentResults} />
            </div>
          </div>
        </div>

        <div className="col-4 col-md-12">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Value Bets</h2>
              <Link to="/betting" className="btn btn-sm btn-outline-primary">
                View All
              </Link>
            </div>
            <div className="card-body">
              <ValueBets bets={valueBets} />
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Top Leagues</h2>
              <Link to="/leagues" className="btn btn-sm btn-outline-primary">
                View All
              </Link>
            </div>
            <div className="card-body">
              <TopLeagues />
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Ask AI Assistant</h2>
              <Link to="/ai-chat" className="btn btn-sm btn-outline-primary">
                Full Chat
              </Link>
            </div>
            <div className="card-body">
              <div className="ai-assistant-preview">
                <p>Ask our AI assistant about teams, matches, or betting advice.</p>
                <Link to="/ai-chat" className="btn btn-primary">
                  Chat with AI
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};