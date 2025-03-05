import React from 'react';
import { Link } from 'react-router-dom';

const LiveFixtures = ({ fixtures }) => {
  if (!fixtures || fixtures.length === 0) {
    return (
      <div className="empty-state">
        <p>No live fixtures at the moment.</p>
      </div>
    );
  }

  return (
    <div className="live-fixtures">
      {fixtures.map((fixture) => (
        <Link
          to={`/fixtures/${fixture.fixture.id}`}
          key={fixture.fixture.id}
          className="fixture-item live"
        >
          <div className="fixture-status">
            <span className="live-indicator"></span>
            <span className="fixture-minute">{fixture.fixture.status.elapsed}'</span>
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
              <span className="score-home">{fixture.goals.home}</span>
              <span className="score-separator">-</span>
              <span className="score-away">{fixture.goals.away}</span>
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

          <div className="fixture-stats">
            {/* Simplified stats for dashboard preview */}
            <div className="stat">
              <span className="stat-label">Possession</span>
              <div className="stat-bar">
                <div
                  className="stat-bar-home"
                  style={{ width: `${fixture.statistics?.[0]?.statistics?.[9]?.value?.replace('%', '') || 50}%` }}
                ></div>
                <div
                  className="stat-bar-away"
                  style={{ width: `${fixture.statistics?.[1]?.statistics?.[9]?.value?.replace('%', '') || 50}%` }}
                ></div>
              </div>
              <div className="stat-values">
                <span className="stat-value-home">{fixture.statistics?.[0]?.statistics?.[9]?.value || '50%'}</span>
                <span className="stat-value-away">{fixture.statistics?.[1]?.statistics?.[9]?.value || '50%'}</span>
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
};

export default LiveFixtures;