import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Chart } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  RadarController,
  RadialLinearScale,
  ArcElement,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  RadarController,
  RadialLinearScale,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const MatchAnalysis = ({ fixtureId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [analysisType, setAnalysisType] = useState('pre-match'); // 'pre-match', 'in-play', 'post-match'
  const navigate = useNavigate();

  // If fixtureId is not passed as a prop, get it from URL params
  const params = useParams();
  const id = fixtureId || params.id;

  useEffect(() => {
    const fetchMatchAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);

        // Determine API endpoint based on analysis type
        let endpoint = `/api/analysis/match/${id}`;
        if (analysisType === 'pre-match') {
          endpoint = `/api/analysis/pre-match/${id}`;
        } else if (analysisType === 'in-play') {
          endpoint = `/api/analysis/in-play/${id}`;
        } else if (analysisType === 'post-match') {
          endpoint = `/api/analysis/post-match/${id}`;
        }

        const response = await axios.get(endpoint);
        setAnalysis(response.data.response);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching match analysis:', err);
        setError(err.response?.data?.detail || 'Failed to fetch match analysis');
        setLoading(false);
      }
    };

    if (id) {
      fetchMatchAnalysis();
    }
  }, [id, analysisType]);

  // Handle analysis type change
  const handleAnalysisTypeChange = (type) => {
    setAnalysisType(type);
  };

  // Render loading state
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading match analysis...</p>
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
        <h3>No Analysis Available</h3>
        <p>There is no analysis available for this match.</p>
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
    <div className="match-analysis">
      <div className="match-analysis-header">
        <h2>{homeTeam} vs {awayTeam}</h2>
        <p className="match-date">{matchDate}</p>

        <div className="analysis-type-selector">
          <button
            className={`btn ${analysisType === 'pre-match' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => handleAnalysisTypeChange('pre-match')}
          >
            Pre-Match
          </button>
          <button
            className={`btn ${analysisType === 'in-play' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => handleAnalysisTypeChange('in-play')}
          >
            In-Play
          </button>
          <button
            className={`btn ${analysisType === 'post-match' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => handleAnalysisTypeChange('post-match')}
          >
            Post-Match
          </button>
        </div>
      </div>

      <div className="grid">
        {/* Team Comparison Section */}
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Team Comparison</h3>
            </div>
            <div className="card-body">
              <div className="team-comparison">
                <div className="team-comparison-item">
                  <div className="team-comparison-label">Form</div>
                  <div className="team-comparison-values">
                    <div className="team-comparison-home">
                      {analysis.home_team_stats?.form || 'N/A'}
                    </div>
                    <div className="team-comparison-away">
                      {analysis.away_team_stats?.form || 'N/A'}
                    </div>
                  </div>
                </div>

                <div className="team-comparison-item">
                  <div className="team-comparison-label">Goals Per Match</div>
                  <div className="team-comparison-values">
                    <div className="team-comparison-home">
                      {analysis.home_team_stats?.average_goals_scored?.toFixed(2) || 'N/A'}
                    </div>
                    <div className="team-comparison-away">
                      {analysis.away_team_stats?.average_goals_scored?.toFixed(2) || 'N/A'}
                    </div>
                  </div>
                </div>

                <div className="team-comparison-item">
                  <div className="team-comparison-label">Goals Conceded Per Match</div>
                  <div className="team-comparison-values">
                    <div className="team-comparison-home">
                      {analysis.home_team_stats?.average_goals_conceded?.toFixed(2) || 'N/A'}
                    </div>
                    <div className="team-comparison-away">
                      {analysis.away_team_stats?.average_goals_conceded?.toFixed(2) || 'N/A'}
                    </div>
                  </div>
                </div>

                <div className="team-comparison-item">
                  <div className="team-comparison-label">Clean Sheets</div>
                  <div className="team-comparison-values">
                    <div className="team-comparison-home">
                      {analysis.home_team_stats?.clean_sheets || 'N/A'}
                    </div>
                    <div className="team-comparison-away">
                      {analysis.away_team_stats?.clean_sheets || 'N/A'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Prediction Section */}
        {analysis.prediction && (
          <div className="col-6 col-md-12">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Match Prediction</h3>
              </div>
              <div className="card-body">
                <div className="prediction-probabilities">
                  <div className="probability-item">
                    <div className="probability-label">Home Win</div>
                    <div className="probability-bar">
                      <div
                        className="probability-fill home-win"
                        style={{ width: `${analysis.prediction.home_win_probability * 100}%` }}
                      ></div>
                    </div>
                    <div className="probability-value">
                      {(analysis.prediction.home_win_probability * 100).toFixed(1)}%
                    </div>
                  </div>

                  <div className="probability-item">
                    <div className="probability-label">Draw</div>
                    <div className="probability-bar">
                      <div
                        className="probability-fill draw"
                        style={{ width: `${analysis.prediction.draw_probability * 100}%` }}
                      ></div>
                    </div>
                    <div className="probability-value">
                      {(analysis.prediction.draw_probability * 100).toFixed(1)}%
                    </div>
                  </div>

                  <div className="probability-item">
                    <div className="probability-label">Away Win</div>
                    <div className="probability-bar">
                      <div
                        className="probability-fill away-win"
                        style={{ width: `${analysis.prediction.away_win_probability * 100}%` }}
                      ></div>
                    </div>
                    <div className="probability-value">
                      {(analysis.prediction.away_win_probability * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                {analysis.prediction.most_likely_score && (
                  <div className="likely-score">
                    <div className="likely-score-label">Most Likely Score:</div>
                    <div className="likely-score-value">{analysis.prediction.most_likely_score}</div>
                  </div>
                )}

                {analysis.prediction.expected_goals_home && analysis.prediction.expected_goals_away && (
                  <div className="expected-goals">
                    <div className="expected-goals-label">Expected Goals:</div>
                    <div className="expected-goals-value">
                      {homeTeam}: {analysis.prediction.expected_goals_home.toFixed(2)} |
                      {awayTeam}: {analysis.prediction.expected_goals_away.toFixed(2)}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Key Insights Section */}
        {analysis.key_insights && (
          <div className="col-6 col-md-12">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Key Insights</h3>
              </div>
              <div className="card-body">
                <ul className="insights-list">
                  {analysis.key_insights.map((insight, index) => (
                    <li key={index} className="insight-item">{insight}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Analysis Report Section */}
        {analysis.report && (
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Analysis Report</h3>
              </div>
              <div className="card-body">
                <div className="analysis-report">
                  {/* Split report by line breaks and create paragraphs */}
                  {analysis.report.split('\n\n').map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Head to Head Section */}
        {analysis.head_to_head && (
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Head to Head</h3>
              </div>
              <div className="card-body">
                <div className="h2h-summary">
                  <div className="h2h-stat">
                    <div className="h2h-label">Matches</div>
                    <div className="h2h-value">{analysis.head_to_head.summary.matches_played}</div>
                  </div>
                  <div className="h2h-stat">
                    <div className="h2h-label">{homeTeam} Wins</div>
                    <div className="h2h-value">{analysis.head_to_head.summary.team1_wins}</div>
                  </div>
                  <div className="h2h-stat">
                    <div className="h2h-label">Draws</div>
                    <div className="h2h-value">{analysis.head_to_head.summary.draws}</div>
                  </div>
                  <div className="h2h-stat">
                    <div className="h2h-label">{awayTeam} Wins</div>
                    <div className="h2h-value">{analysis.head_to_head.summary.team2_wins}</div>
                  </div>
                </div>

                {analysis.head_to_head.matches && analysis.head_to_head.matches.length > 0 && (
                  <div className="h2h-matches">
                    <h4>Recent Matches</h4>
                    <div className="h2h-matches-list">
                      {analysis.head_to_head.matches.slice(0, 5).map((match, index) => (
                        <div key={index} className="h2h-match-item">
                          <div className="h2h-match-date">
                            {new Date(match.fixture.date).toLocaleDateString()}
                          </div>
                          <div className="h2h-match-teams">
                            <span className={match.teams.home.winner ? 'winner' : ''}>
                              {match.teams.home.name}
                            </span>
                            <span className="h2h-match-score">
                              {match.goals.home} - {match.goals.away}
                            </span>
                            <span className={match.teams.away.winner ? 'winner' : ''}>
                              {match.teams.away.name}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MatchAnalysis;