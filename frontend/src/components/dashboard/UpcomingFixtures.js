import React from 'react';
import { Link } from 'react-router-dom';

const UpcomingFixtures = ({ fixtures }) => {
  if (!fixtures || fixtures.length === 0) {
    return (
      <div className="empty-state">
        <p>No upcoming fixtures found.</p>
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

  // Sort fixtures by time within each date group
  Object.keys(groupedFixtures).forEach(date => {
    groupedFixtures[date].sort((a, b) => {
      return new Date(a.fixture.date) - new Date(b.fixture.date);
    });
  });

  return (
    <div className="upcoming-fixtures">
      {Object.entries(groupedFixtures).map(([date, dateFixtures]) => (
        <div key={date} className="fixture-group">
          <h3 className="fixture-date">{date}</h3>
          <div className="fixture-list">
            {dateFixtures.slice(0, 5).map((fixture) => (
              <Link
                to={`/fixtures/${fixture.fixture.id}`}
                key={fixture.fixture.id}
                className="fixture-item upcoming"
              >
                <div className="fixture-time">
                  {new Date(fixture.fixture.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>

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
                  <div className="team home">
                    <img
                      src={fixture.teams.home.logo}
                      alt={fixture.teams.home.name}
                      className="team-logo"
                      onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-team.png'}}
                    />
                    <span className="team-name">{fixture.teams.home.name}</span>
                  </div>

                  <div className="fixture-score">
                    <span className="score-vs">vs</span>
                  </div>

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

                {fixture.odds && fixture.odds.length > 0 && (
                  <div className="fixture-odds">
                    <div className="odd">
                      <span className="odd-value">{fixture.odds[0]?.bookmakers[0]?.bets[0]?.values[0]?.odd || '-'}</span>
                      <span className="odd-type">1</span>
                    </div>
                    <div className="odd">
                      <span className="odd-value">{fixture.odds[0]?.bookmakers[0]?.bets[0]?.values[1]?.odd || '-'}</span>
                      <span className="odd-type">X</span>
                    </div>
                    <div className="odd">
                      <span className="odd-value">{fixture.odds[0]?.bookmakers[0]?.bets[0]?.values[2]?.odd || '-'}</span>
                      <span className="odd-type">2</span>
                    </div>
                  </div>
                )}
              </Link>
            ))}

            {dateFixtures.length > 5 && (
              <Link to="/fixtures" className="more-fixtures">
                View {dateFixtures.length - 5} more fixtures for this date
              </Link>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default UpcomingFixtures;