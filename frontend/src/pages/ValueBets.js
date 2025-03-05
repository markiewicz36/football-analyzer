import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { format } from 'date-fns';

const ValueBets = () => {
  const [valueBets, setValueBets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({
    league: '',
    date: format(new Date(), 'yyyy-MM-dd'),
    minEdge: 0.05
  });

  useEffect(() => {
    const fetchValueBets = async () => {
      try {
        setLoading(true);
        setError(null);

        // Build query parameters
        const params = {
          min_edge: filter.minEdge,
          max_results: 20
        };

        if (filter.league) {
          params.league_id = filter.league;
        }

        if (filter.date) {
          params.date = filter.date;
        }

        const response = await axios.get('/api/analysis/value-bets', { params });
        setValueBets(response.data.response);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching value bets:', err);
        setError(err.response?.data?.detail || 'Failed to fetch value bets');
        setLoading(false);
      }
    };

    fetchValueBets();
  }, [filter]);

  // Handle filter changes
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilter(prevFilter => ({
      ...prevFilter,
      [name]: value
    }));
  };

  // Render loading state
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading value bets...</p>
      </div>
    );
  }

  return (
    <div className="value-bets-page">
      <div className="page-header">
        <h1>Value Bets</h1>
        <p>Discover betting opportunities with positive expected value</p>
      </div>

      <div className="filters-container card">
        <div className="card-header">
          <h3 className="card-title">Filters</h3>
        </div>
        <div className="card-body">
          <div className="filters-form">
            <div className="form-group">
              <label htmlFor="date">Date</label>
              <input
                type="date"
                id="date"
                name="date"
                className="form-control"
                value={filter.date}
                onChange={handleFilterChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="league">League</label>
              <select
                id="league"
                name="league"
                className="form-control"
                value={filter.league}
                onChange={handleFilterChange}
              >
                <option value="">All Leagues</option>
                <option value="39">Premier League</option>
                <option value="140">La Liga</option>
                <option value="61">Ligue 1</option>
                <option value="78">Bundesliga</option>
                <option value="135">Serie A</option>
                {/* Add more leagues as needed */}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="minEdge">Minimum Edge (%)</label>
              <select
                id="minEdge"
                name="minEdge"
                className="form-control"
                value={filter.minEdge}
                onChange={handleFilterChange}
              >
                <option value="0.01">1%</option>
                <option value="0.03">3%</option>
                <option value="0.05">5%</option>
                <option value="0.08">8%</option>
                <option value="0.1">10%</option>
                <option value="0.15">15%</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <div className="value-bets-list">
        {valueBets.length === 0 ? (
          <div className="no-bets-message card">
            <div className="card-body">
              <p>No value bets found matching your criteria. Try adjusting your filters.</p>
            </div>
          </div>
        ) : (
          valueBets.map((bet, index) => (
            <div key={index} className="value-bet-card card">
              <div className="card-header">
                <div className="value-bet-header">
                  <div className="value-bet-league">
                    <img
                      src={bet.league.logo}
                      alt={bet.league.name}
                      className="league-logo"
                      onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-logo.png'}}
                    />
                    <span>{bet.league.name}</span>
                  </div>
                  <div className="value-bet-date">
                    {new Date(bet.match_date).toLocaleDateString()} {new Date(bet.match_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </div>
                </div>
              </div>
              <div className="card-body">
                <div className="value-bet-teams">
                  <Link to={`/fixtures/${bet.fixture_id}`} className="teams-link">
                    <div className="team home">
                      <img
                        src={bet.teams.home.logo}
                        alt={bet.teams.home.name}
                        className="team-logo"
                        onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-team.png'}}
                      />
                      <span className="team-name">{bet.teams.home.name}</span>
                    </div>
                    <span className="vs">vs</span>
                    <div className="team away">
                      <img
                        src={bet.teams.away.logo}
                        alt={bet.teams.away.name}
                        className="team-logo"
                        onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-team.png'}}
                      />
                      <span className="team-name">{bet.teams.away.name}</span>
                    </div>
                  </Link>
                </div>

                <div className="value-bet-details">
                  <div className="bet-info">
                    <div className="bet-type">{bet.market} - {bet.selection}</div>
                    <div className="bookmaker">{bet.bookmaker}</div>
                  </div>

                  <div className="odds-info">
                    <div className="odds">
                      <span className="odds-label">Odds:</span>
                      <span className="odds-value">{bet.odds.toFixed(2)}</span>
                    </div>

                    <div className="probabilities">
                      <div className="implied">
                        <span className="prob-label">Implied:</span>
                        <span className="prob-value">{bet.implied_probability}%</span>
                      </div>
                      <div className="estimated">
                        <span className="prob-label">Model:</span>
                        <span className="prob-value">{bet.estimated_probability}%</span>
                      </div>
                    </div>
                  </div>

                  <div className="edge-container">
                    <span className="edge-label">Edge:</span>
                    <span className="edge-value">{bet.edge}%</span>
                    <div className="edge-bar">
                      <div
                        className="edge-fill"
                        style={{ width: `${Math.min(bet.edge, 30)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="value-bet-actions">
                  <Link to={`/fixtures/${bet.fixture_id}/analysis`} className="btn btn-primary">
                    Full Analysis
                  </Link>
                  <Link to={`/fixtures/${bet.fixture_id}`} className="btn btn-outline-primary">
                    Match Details
                  </Link>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ValueBets;