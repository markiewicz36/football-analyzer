import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

// Components
import MatchAnalysis from '../components/analysis/MatchAnalysis';
import BettingAnalysis from '../components/analysis/BettingAnalysis';

const FixtureAnalysis = () => {
  const [activeTab, setActiveTab] = useState('match'); // 'match', 'betting'
  const [fixture, setFixture] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { id } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchFixtureData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await axios.get(`/api/fixtures/${id}`);
        setFixture(response.data.response);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching fixture:', err);
        setError(err.response?.data?.detail || 'Failed to fetch fixture data');
        setLoading(false);
      }
    };

    if (id) {
      fetchFixtureData();
    }
  }, [id]);

  // Handle tab change
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  // Render loading state
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading fixture data...</p>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="error-container">
        <h3>Error</h3>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={() => navigate('/fixtures')}>
          Back to Fixtures
        </button>
      </div>
    );
  }

  // Render no data state
  if (!fixture) {
    return (
      <div className="no-data-container">
        <h3>Fixture Not Found</h3>
        <p>The fixture you are looking for does not exist or could not be loaded.</p>
        <button className="btn btn-primary" onClick={() => navigate('/fixtures')}>
          Back to Fixtures
        </button>
      </div>
    );
  }

  // Extract fixture data
  const { fixture: fixtureData, league, teams, goals } = fixture;
  const homeTeam = teams.home.name;
  const awayTeam = teams.away.name;
  const matchDate = new Date(fixtureData.date).toLocaleString();
  const matchStatus = fixtureData.status.long;
  const leagueName = league.name;
  const leagueCountry = league.country;
  const homeGoals = goals.home;
  const awayGoals = goals.away;
  const matchVenue = fixtureData.venue.name;
  const matchReferee = fixtureData.referee;

  return (
    <div className="fixture-analysis-page">
      <div className="fixture-header">
        <div className="fixture-meta">
          <Link to={`/leagues/${league.id}`} className="league-link">
            <img
              src={league.logo}
              alt={league.name}
              className="league-logo"
              onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-logo.png'}}
            />
            <span>{leagueName} ({leagueCountry})</span>
          </Link>
          <span className="fixture-date">{matchDate}</span>
          <span className="fixture-status">{matchStatus}</span>
        </div>

        <div className="fixture-teams">
          <div className="team home">
            <Link to={`/teams/${teams.home.id}`} className="team-link">
              <img
                src={teams.home.logo}
                alt={teams.home.name}
                className="team-logo"
                onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-team.png'}}
              />
              <span className="team-name">{homeTeam}</span>
            </Link>
          </div>

          <div className="fixture-score">
            {fixtureData.status.short === 'NS' ? (
              <span className="fixture-time">
                {new Date(fixtureData.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            ) : (
              <>
                <span className="score-home">{homeGoals !== null ? homeGoals : '-'}</span>
                <span className="score-separator">:</span>
                <span className="score-away">{awayGoals !== null ? awayGoals : '-'}</span>
              </>
            )}
          </div>

          <div className="team away">
            <Link to={`/teams/${teams.away.id}`} className="team-link">
              <img
                src={teams.away.logo}
                alt={teams.away.name}
                className="team-logo"
                onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-team.png'}}
              />
              <span className="team-name">{awayTeam}</span>
            </Link>
          </div>
        </div>

        <div className="fixture-details">
          {matchVenue && (
            <div className="fixture-venue">
              <i className="fas fa-map-marker-alt"></i>
              <span>{matchVenue}</span>
            </div>
          )}

          {matchReferee && (
            <div className="fixture-referee">
              <i className="fas fa-whistle"></i>
              <span>Referee: {matchReferee}</span>
            </div>
          )}
        </div>
      </div>

      <div className="analysis-tabs">
        <div className="tabs-header">
          <button
            className={`tab-button ${activeTab === 'match' ? 'active' : ''}`}
            onClick={() => handleTabChange('match')}
          >
            Match Analysis
          </button>
          <button
            className={`tab-button ${activeTab === 'betting' ? 'active' : ''}`}
            onClick={() => handleTabChange('betting')}
          >
            Betting Analysis
          </button>
          <Link to={`/fixtures/${id}`} className="tab-button">
            Match Details
          </Link>
        </div>

        <div className="tabs-content">
          {activeTab === 'match' && (
            <MatchAnalysis fixtureId={id} />
          )}

          {activeTab === 'betting' && (
            <BettingAnalysis fixtureId={id} />
          )}
        </div>
      </div>
    </div>
  );
};

export default FixtureAnalysis;