import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const TopLeagues = () => {
  const [topLeagues, setTopLeagues] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Define our top leagues (could come from API or settings in a full implementation)
  const popularLeagueIds = [39, 140, 61, 78, 135]; // Premier League, La Liga, Ligue 1, Bundesliga, Serie A

  useEffect(() => {
    const fetchTopLeagues = async () => {
      try {
        setIsLoading(true);

        // Get current season
        const currentYear = new Date().getFullYear();
        const season = new Date().getMonth() >= 7 ? currentYear : currentYear - 1;

        // Fetch leagues data
        const leaguesPromises = popularLeagueIds.map(leagueId =>
          axios.get('/api/leagues', { params: { id: leagueId, season: season } })
        );

        const responses = await Promise.all(leaguesPromises);

        // Combine and format results
        const leagues = responses
          .map(response => response.data?.response?.[0] || null)
          .filter(league => league !== null);

        setTopLeagues(leagues);
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching top leagues:', err);
        setError('Failed to fetch leagues');
        setIsLoading(false);
      }
    };

    fetchTopLeagues();
  }, []);

  if (isLoading) {
    return <div className="loading">Loading top leagues...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (topLeagues.length === 0) {
    return <div className="empty-state">No leagues found</div>;
  }

  return (
    <div className="top-leagues">
      <ul className="league-list">
        {topLeagues.map((league) => (
          <li key={league.league.id} className="league-item">
            <Link to={`/leagues/${league.league.id}`} className="league-link">
              <img
                src={league.league.logo}
                alt={league.league.name}
                className="league-logo"
                onError={(e) => {e.target.onerror = null; e.target.src = '/placeholder-logo.png'}}
              />
              <div className="league-info">
                <span className="league-name">{league.league.name}</span>
                <span className="league-country">{league.country.name}</span>
              </div>
              <div className="league-action">
                <i className="fas fa-chevron-right"></i>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TopLeagues;