import React from 'react';
import { Link } from 'react-router-dom';

const RecentResults = ({ fixtures }) => {
  if (!fixtures || fixtures.length === 0) {
    return (
      <div className="empty-state">
        <p>No recent results found.</p>
      </div>
    );
  }

  // Group fixtures by date
  const groupedFixtures = fixtures.reduce((acc, fixture) => {
    const date = new Date(fixture.fixture.date).toLocaleDateString();
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(fixture);
    return acc;
  }, {});

  return (
    <div className="recent-results">
      {Object.entries(groupedFixtures).map(([date, dateFixtures]) => (
        <div key={date} className="fixture-group">
          <h3 className="fixture-date">{date}</h3>
          <div className="fixture-list">
            {dateFixtures.slice(0, 5).map((fixture) => (
              <Link
                to={`/fixtures/${fixture.fixture.id}`}
                key={fixture.fixture.id}
                className="fixture-item result"
              >
                <div className="fixture-league">
                  <img
                    src={fixture.league.logo}
                    alt={fixture.league.name}
                    className="league-logo"
                    onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-logo.png'}}
                  />
                  <span className="league-name">{fixture.league.name}</span>
                </div>

                <div className="fixture-teams">
                  <div className={`team home ${fixture.teams.home.winner ? 'winner' : ''}`}>
                    <img
                      src={fixture.teams.home.logo}
                      alt={fixture.teams.home.name}
                      className="team-logo"
                      onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-team.png'}}
                    />
                    <span className="team-name">{fixture.teams.home.name}</span>
                  </div>

                  <div className="fixture-score">
                    <span className="score-home">{fixture.goals.home}</span>
                    <span className="score-separator">-</span>
                    <span className="score-away">{fixture.goals.away}</span>
                  </div>

                  <div className={`team away ${fixture.teams.away.winner ? 'winner' : ''}`}>
                    <img
                      src={fixture.teams.away.logo}
                      alt={fixture.teams.away.name}
                      className="team-logo"
                      onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-team.png'}}
                    />
                    <span className="team-name">{fixture.teams.away.name}</span>
                  </div>
                </div>

                <div className="fixture-stats-preview">
                  <div className="stat-preview">
                    <span>xG: {fixture.score?.home_xg?.toFixed(2) || '-'} - {fixture.score?.away_xg?.toFixed(2) || '-'}</span>
                  </div>
                </div>
              </Link>
            ))}

            {dateFixtures.length > 5 && (
              <Link to={`/fixtures?date=${date}&status=FT`} className="more-fixtures">
                View {dateFixtures.length - 5} more results for this date
              </Link>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default RecentResults;