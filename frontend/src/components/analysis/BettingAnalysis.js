import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const BettingAnalysis = ({ fixtureId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const navigate = useNavigate();

  // If fixtureId is not passed as a prop, get it from URL params
  const params = useParams();
  const id = fixtureId || params.id;

  useEffect(() => {
    const fetchBettingAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await axios.get(`/api/analysis/betting/${id}`);
        setAnalysis(response.data.response);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching betting analysis:', err);
        setError(err.response?.data?.detail || 'Failed to fetch betting analysis');
        setLoading(false);
      }
    };

    if (id) {
      fetchBettingAnalysis();
    }
  }, [id]);

  // Render loading state
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading betting analysis...</p>
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
  if (!analysis) {
    return (
      <div className="no-data-container">
        <h3>No Betting Analysis Available</h3>
        <p>There is no betting analysis available for this match.</p>
        <button className="btn btn-primary" onClick={() => navigate('/fixtures')}>
          Back to Fixtures
        </button>
      </div>
    );
  }

  // Extract data for rendering
  const homeTeam = analysis.home_team || 'Home Team';
  const awayTeam = analysis.away_team || 'Away Team';
  const matchDate = analysis.kickoff_time ? new Date(analysis.kickoff_time).toLocaleString() : 'Upcoming';

  return (
    <div className="betting-analysis">
      <div className="betting-analysis-header">
        <h2>{homeTeam} vs {awayTeam}</h2>
        <p className="match-date">{matchDate}</p>
      </div>

      <div className="grid">
        {/* AI Analysis Section */}
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Betting Analysis</h3>
            </div>
            <div className="card-body">
              <div className="analysis-content">
                {/* Display analysis text with paragraphs */}
                {analysis.analysis.split('\n\n').map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Value Bets Section */}
        {analysis.value_bets && analysis.value_bets.length > 0 && (
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Value Bets</h3>
              </div>
              <div className="card-body">
                <div className="value-bets-list">
                  <table className="value-bets-table">
                    <thead>
                      <tr>
                        <th>Bet Type</th>
                        <th>Selection</th>
                        <th>Odds</th>
                        <th>Implied Probability</th>
                        <th>Estimated Probability</th>
                        <th>Edge</th>
                        <th>Bookmaker</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysis.value_bets.map((bet, index) => (
                        <tr key={index} className="value-bet-item">
                          <td>{bet.market}</td>
                          <td>{bet.selection}</td>
                          <td className="odds">{bet.odds}</td>
                          <td>{bet.implied_probability}%</td>
                          <td>{bet.estimated_probability}%</td>
                          <td className="edge">{bet.edge}%</td>
                          <td>{bet.bookmaker}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Odds Comparison Section */}
        {analysis.odds_data && analysis.odds_data.length > 0 && (
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Odds Comparison</h3>
              </div>
              <div className="card-body">
                <div className="odds-comparison">
                  {analysis.odds_data.map((oddsGroup, groupIndex) => (
                    <div key={groupIndex} className="odds-group">
                      <h4>{oddsGroup.league.name}</h4>

                      {oddsGroup.bookmakers.map((bookmaker, bookmakerIndex) => (
                        <div key={bookmakerIndex} className="bookmaker-odds">
                          <h5>{bookmaker.name}</h5>

                          <div className="bets-list">
                            {bookmaker.bets.map((bet, betIndex) => (
                              <div key={betIndex} className="bet-item">
                                <div className="bet-name">{bet.name}</div>

                                <div className="bet-values">
                                  {bet.values.map((value, valueIndex) => (
                                    <div key={valueIndex} className="bet-value">
                                      <span className="bet-value-name">{value.value}</span>
                                      <span className="bet-value-odd">{value.odd}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Prediction Comparison Section */}
        {analysis.prediction && (
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Prediction vs. Market Odds</h3>
              </div>
              <div className="card-body">
                <div className="prediction-comparison">
                  <table className="prediction-comparison-table">
                    <thead>
                      <tr>
                        <th>Outcome</th>
                        <th>Model Probability</th>
                        <th>Best Market Odds</th>
                        <th>Implied Probability</th>
                        <th>Edge</th>
                      </tr>
                    </thead>
                    <tbody>
                      {/* Home Win */}
                      <tr>
                        <td>{homeTeam} Win</td>
                        <td>{analysis.prediction.percent?.home || 'N/A'}</td>
                        <td>
                          {analysis.value_bets?.find(bet => bet.selection === 'Home')?.odds ||
                           analysis.odds_data?.[0]?.bookmakers?.[0]?.bets?.[0]?.values?.[0]?.odd || 'N/A'}
                        </td>
                        <td>
                          {analysis.value_bets?.find(bet => bet.selection === 'Home')?.implied_probability ||
                           (analysis.odds_data?.[0]?.bookmakers?.[0]?.bets?.[0]?.values?.[0]?.odd ?
                            ((1 / analysis.odds_data[0].bookmakers[0].bets[0].values[0].odd) * 100).toFixed(2) + '%' : 'N/A')}
                        </td>
                        <td>
                          {analysis.value_bets?.find(bet => bet.selection === 'Home')?.edge || 'N/A'}
                        </td>
                      </tr>

                      {/* Draw */}
                      <tr>
                        <td>Draw</td>
                        <td>{analysis.prediction.percent?.draw || 'N/A'}</td>
                        <td>
                          {analysis.value_bets?.find(bet => bet.selection === 'Draw')?.odds ||
                           analysis.odds_data?.[0]?.bookmakers?.[0]?.bets?.[0]?.values?.[1]?.odd || 'N/A'}
                        </td>
                        <td>
                          {analysis.value_bets?.find(bet => bet.selection === 'Draw')?.implied_probability ||
                           (analysis.odds_data?.[0]?.bookmakers?.[0]?.bets?.[0]?.values?.[1]?.odd ?
                            ((1 / analysis.odds_data[0].bookmakers[0].bets[0].values[1].odd) * 100).toFixed(2) + '%' : 'N/A')}
                        </td>
                        <td>
                          {analysis.value_bets?.find(bet => bet.selection === 'Draw')?.edge || 'N/A'}
                        </td>
                      </tr>

                      {/* Away Win */}
                      <tr>
                        <td>{awayTeam} Win</td>
                        <td>{analysis.prediction.percent?.away || 'N/A'}</td>
                        <td>
                          {analysis.value_bets?.find(bet => bet.selection === 'Away')?.odds ||
                           analysis.odds_data?.[0]?.bookmakers?.[0]?.bets?.[0]?.values?.[2]?.odd || 'N/A'}
                        </td>
                        <td>
                          {analysis.value_bets?.find(bet => bet.selection === 'Away')?.implied_probability ||
                           (analysis.odds_data?.[0]?.bookmakers?.[0]?.bets?.[0]?.values?.[2]?.odd ?
                            ((1 / analysis.odds_data[0].bookmakers[0].bets[0].values[2].odd) * 100).toFixed(2) + '%' : 'N/A')}
                        </td>
                        <td>
                          {analysis.value_bets?.find(bet => bet.selection === 'Away')?.edge || 'N/A'}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BettingAnalysis;