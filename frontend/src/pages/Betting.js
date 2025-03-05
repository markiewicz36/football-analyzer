import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { format } from 'date-fns';

const Betting = () => {
  const [todayFixtures, setTodayFixtures] = useState([]);
  const [valueBets, setValueBets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get today's date in YYYY-MM-DD format
        const today = format(new Date(), 'yyyy-MM-dd');

        // Fetch today's fixtures
        const fixturesResponse = await axios.get('/api/fixtures', {
          params: { date: today }
        });

        // Fetch value bets
        const valueBetsResponse = await axios.get('/api/analysis/value-bets', {
          params: { date: today, min_edge: 0.05, max_results: 5 }
        });

        setTodayFixtures(fixturesResponse.data.response || []);
        setValueBets(valueBetsResponse.data.response || []);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching betting data:', err);
        setError(err.response?.data?.detail || 'Failed to fetch data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter fixtures with available odds
  const fixturesWithOdds = todayFixtures.filter(fixture =>
    fixture.fixture.status.short === 'NS' &&
    fixture.odds &&
    fixture.odds.length > 0
  );

  // Render loading state
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading betting data...</p>
      </div>
    );
  }

  return (
    <div className="betting-page">
      <div className="page-header">
        <h1>Betting Center</h1>
        <p>Find value bets and compare odds across matches</p>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <div className="grid">
        {/* Value Bets Section */}
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Today's Value Bets</h2>
              <Link to="/betting/value-bets" className="btn btn-sm btn-outline-primary">
                See All Value Bets
              </Link>
            </div>
            <div className="card-body">
              {valueBets.length === 0 ? (
                <div className="no-data-message">
                  <p>No value bets found for today. Check back later or adjust your criteria.</p>
                </div>
              ) : (
                <div className="value-bets-grid">
                  {valueBets.map((bet, index) => (
                    <div key={index} className="value-bet-card">
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
                        <div className="value-bet-time">
                          {new Date(bet.match_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </div>
                      </div>

                      <div className="value-bet-teams">
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
                      </div>

                      <div className="value-bet-details">
                        <div className="bet-type">{bet.market} - {bet.selection}</div>
                        <div className="bet-bookmaker">{bet.bookmaker}</div>
                        <div className="bet-odds">{bet.odds.toFixed(2)}</div>
                        <div className="bet-edge">Edge: {bet.edge}%</div>
                      </div>

                      <div className="value-bet-actions">
                        <Link to={`/fixtures/${bet.fixture_id}/analysis`} className="btn btn-sm btn-primary">
                          Analysis
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="value-bets-cta">
                <Link to="/betting/value-bets" className="btn btn-primary">
                  View All Value Bets
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Fixtures with Odds Section */}
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Today's Matches with Odds</h2>
              <Link to="/fixtures" className="btn btn-sm btn-outline-primary">
                See All Fixtures
              </Link>
            </div>
            <div className="card-body">
              {fixturesWithOdds.length === 0 ? (
                <div className="no-data-message">
                  <p>No fixtures with odds found for today.</p>
                </div>
              ) : (
                <div className="fixtures-with-odds">
                  {fixturesWithOdds.slice(0, 10).map((fixture) => (
                    <div key={fixture.fixture.id} className="fixture-odds-item">
                      <div className="fixture-odds-header">
                        <div className="fixture-league">
                          <img
                            src={fixture.league.logo}
                            alt={fixture.league.name}
                            className="league-logo"
                            onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-logo.png'}}
                          />
                          <span>{fixture.league.name}</span>
                        </div>
                        <div className="fixture-time">
                          {new Date(fixture.fixture.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </div>
                      </div>

                      <div className="fixture-teams">
                        <div className="team home">
                          <img
                            src={fixture.teams.home.logo}
                            alt={fixture.teams.home.name}
                            className="team-logo"
                            onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-team.png'}}
                          />
                          <span className="team-name">{fixture.teams.home.name}</span>
                        </div>
                        <span className="vs">vs</span>
                        <div className="team away">
                          <img
                            src={fixture.teams.away.logo}
                            alt={fixture.teams.away.name}
                            className="team-logo"
                            onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-team.png'}}
                          />
                          <span className="team-name">{fixture.teams.away.name}</span>
                        </div>
                      </div>

                      {fixture.odds && fixture.odds.length > 0 && fixture.odds[0].bookmakers && fixture.odds[0].bookmakers.length > 0 && (
                        <div className="fixture-odds">
                          <div className="odds-grid">
                            <div className="odd home">
                              <div className="odd-label">1</div>
                              <div className="odd-value">
                                {fixture.odds[0].bookmakers[0].bets[0].values.find(v => v.value === 'Home')?.odd || '-'}
                              </div>
                            </div>
                            <div className="odd draw">
                              <div className="odd-label">X</div>
                              <div className="odd-value">
                                {fixture.odds[0].bookmakers[0].bets[0].values.find(v => v.value === 'Draw')?.odd || '-'}
                              </div>
                            </div>
                            <div className="odd away">
                              <div className="odd-label">2</div>
                              <div className="odd-value">
                                {fixture.odds[0].bookmakers[0].bets[0].values.find(v => v.value === 'Away')?.odd || '-'}
                              </div>
                            </div>
                          </div>

                          <div className="odd-bookmaker">
                            {fixture.odds[0].bookmakers[0].name}
                          </div>
                        </div>
                      )}

                      <div className="fixture-actions">
                        <Link to={`/fixtures/${fixture.fixture.id}/analysis`} className="btn btn-sm btn-primary">
                          Analysis
                        </Link>
                        <Link to={`/fixtures/${fixture.fixture.id}`} className="btn btn-sm btn-outline-primary">
                          Details
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Betting;