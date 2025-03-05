import React from 'react';
import { Link } from 'react-router-dom';

// Mock data for value bets (until real API integration)
const mockValueBets = [
  {
    id: 1,
    fixture_id: 1234567,
    league: { id: 39, name: 'Premier League', logo: 'https://media.api-sports.io/football/leagues/39.png' },
    teams: {
      home: { id: 33, name: 'Manchester United', logo: 'https://media.api-sports.io/football/teams/33.png' },
      away: { id: 34, name: 'Newcastle', logo: 'https://media.api-sports.io/football/teams/34.png' }
    },
    bet_type: 'Home Win',
    odds: 2.1,
    value_ratio: 1.23,
    expected_value: 0.23,
    match_date: '2025-03-07T15:00:00+00:00'
  },
  {
    id: 2,
    fixture_id: 1234568,
    league: { id: 140, name: 'La Liga', logo: 'https://media.api-sports.io/football/leagues/140.png' },
    teams: {
      home: { id: 529, name: 'Barcelona', logo: 'https://media.api-sports.io/football/teams/529.png' },
      away: { id: 530, name: 'Atletico Madrid', logo: 'https://media.api-sports.io/football/teams/530.png' }
    },
    bet_type: 'Under 2.5 Goals',
    odds: 2.5,
    value_ratio: 1.32,
    expected_value: 0.32,
    match_date: '2025-03-07T19:45:00+00:00'
  },
  {
    id: 3,
    fixture_id: 1234569,
    league: { id: 78, name: 'Bundesliga', logo: 'https://media.api-sports.io/football/leagues/78.png' },
    teams: {
      home: { id: 157, name: 'Bayern Munich', logo: 'https://media.api-sports.io/football/teams/157.png' },
      away: { id: 159, name: 'Hertha Berlin', logo: 'https://media.api-sports.io/football/teams/159.png' }
    },
    bet_type: 'Away Win',
    odds: 7.5,
    value_ratio: 1.15,
    expected_value: 0.15,
    match_date: '2025-03-08T14:30:00+00:00'
  }
];

const ValueBets = ({ bets = [] }) => {
  // Use the provided bets, or fallback to mock data if empty
  const displayBets = bets.length > 0 ? bets : mockValueBets;

  if (displayBets.length === 0) {
    return (
      <div className="empty-state">
        <p>No value bets found at the moment.</p>
      </div>
    );
  }

  return (
    <div className="value-bets">
      <ul className="value-bet-list">
        {displayBets.map((bet) => (
          <li key={bet.id} className="value-bet-item">
            <Link to={`/fixtures/${bet.fixture_id}`} className="value-bet-link">
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
                <div className="bet-type">{bet.bet_type}</div>
                <div className="bet-odds">
                  <span className="odds-value">{bet.odds.toFixed(2)}</span>
                  <span className="value-ratio">(Value: {bet.value_ratio.toFixed(2)}x)</span>
                </div>
              </div>
              <div className="value-bet-ev">
                <div className="ev-label">Expected Value:</div>
                <div className="ev-value">{(bet.expected_value * 100).toFixed(1)}%</div>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ValueBets;