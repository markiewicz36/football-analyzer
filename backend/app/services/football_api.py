import os
import json
import httpx
import logging
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# API configuration
FOOTBALL_API_BASE_URL = os.getenv("FOOTBALL_API_BASE_URL", "https://v3.football.api-sports.io")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")

# Headers for API requests
headers = {
    "x-rapidapi-key": FOOTBALL_API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}


class FootballAPIClient:
    """
    Client for interacting with the Football API.
    """

    def __init__(self, base_url=FOOTBALL_API_BASE_URL, api_key=FOOTBALL_API_KEY):
        self.base_url = base_url
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

    async def close(self):
        """Close the HTTP client session."""
        await self.client.aclose()

    async def _make_request(self, endpoint, params=None):
        """
        Make a request to the Football API.

        Args:
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters

        Returns:
            dict: API response
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if "errors" in data and data["errors"]:
                logger.error(f"API Error: {data['errors']}")
                raise HTTPException(status_code=400, detail=f"API Error: {data['errors']}")

            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    # Countries endpoints
    async def get_countries(self, name=None, code=None, search=None):
        """Get list of countries."""
        params = {}
        if name:
            params["name"] = name
        if code:
            params["code"] = code
        if search:
            params["search"] = search

        return await self._make_request("countries", params)

    # Leagues endpoints
    async def get_leagues(self, id=None, name=None, country=None, code=None, season=None, team=None, type=None,
                          current=None, search=None, last=None):
        """Get leagues information."""
        params = {}
        if id:
            params["id"] = id
        if name:
            params["name"] = name
        if country:
            params["country"] = country
        if code:
            params["code"] = code
        if season:
            params["season"] = season
        if team:
            params["team"] = team
        if type:
            params["type"] = type
        if current:
            params["current"] = current
        if search:
            params["search"] = search
        if last:
            params["last"] = last

        return await self._make_request("leagues", params)

    async def get_seasons(self):
        """Get available seasons."""
        return await self._make_request("leagues/seasons")

    # Teams endpoints
    async def get_teams(self, id=None, name=None, league=None, season=None, country=None, code=None, venue=None,
                        search=None):
        """Get teams information."""
        params = {}
        if id:
            params["id"] = id
        if name:
            params["name"] = name
        if league:
            params["league"] = league
        if season:
            params["season"] = season
        if country:
            params["country"] = country
        if code:
            params["code"] = code
        if venue:
            params["venue"] = venue
        if search:
            params["search"] = search

        return await self._make_request("teams", params)

    async def get_team_statistics(self, league, season, team, date=None):
        """Get team statistics."""
        params = {
            "league": league,
            "season": season,
            "team": team
        }
        if date:
            params["date"] = date

        return await self._make_request("teams/statistics", params)

    # Fixtures endpoints
    async def get_fixtures(self, id=None, ids=None, live=None, date=None, league=None, season=None, team=None,
                           last=None, next=None, from_date=None, to=None, round=None, status=None, timezone=None):
        """Get fixtures information."""
        params = {}
        if id:
            params["id"] = id
        if ids:
            params["ids"] = ids
        if live:
            params["live"] = live
        if date:
            params["date"] = date
        if league:
            params["league"] = league
        if season:
            params["season"] = season
        if team:
            params["team"] = team
        if last:
            params["last"] = last
        if next:
            params["next"] = next
        if from_date:
            params["from"] = from_date
        if to:
            params["to"] = to
        if round:
            params["round"] = round
        if status:
            params["status"] = status
        if timezone:
            params["timezone"] = timezone

        return await self._make_request("fixtures", params)

    async def get_fixture_statistics(self, fixture, team=None):
        """Get fixture statistics."""
        params = {
            "fixture": fixture
        }
        if team:
            params["team"] = team

        return await self._make_request("fixtures/statistics", params)

    async def get_fixture_events(self, fixture, team=None, player=None, type=None):
        """Get fixture events."""
        params = {
            "fixture": fixture
        }
        if team:
            params["team"] = team
        if player:
            params["player"] = player
        if type:
            params["type"] = type

        return await self._make_request("fixtures/events", params)

    async def get_fixture_lineups(self, fixture, team=None, player=None, type=None):
        """Get fixture lineups."""
        params = {
            "fixture": fixture
        }
        if team:
            params["team"] = team
        if player:
            params["player"] = player
        if type:
            params["type"] = type

        return await self._make_request("fixtures/lineups", params)

    async def get_fixture_players(self, fixture, team=None):
        """Get fixture players statistics."""
        params = {
            "fixture": fixture
        }
        if team:
            params["team"] = team

        return await self._make_request("fixtures/players", params)

    # Standings endpoints
    async def get_standings(self, league, season, team=None):
        """Get standings for a league or team."""
        params = {
            "league": league,
            "season": season
        }
        if team:
            params["team"] = team

        return await self._make_request("standings", params)

    # Players endpoints
    async def get_players(self, id=None, team=None, league=None, season=None, search=None, page=None):
        """Get players information."""
        params = {}
        if id:
            params["id"] = id
        if team:
            params["team"] = team
        if league:
            params["league"] = league
        if season:
            params["season"] = season
        if search and (league or team):
            params["search"] = search
        if page:
            params["page"] = page

        return await self._make_request("players", params)

    async def get_player_seasons(self, player=None):
        """Get player seasons."""
        params = {}
        if player:
            params["player"] = player

        return await self._make_request("players/seasons", params)

    async def get_squads(self, team=None, player=None):
        """Get team squads."""
        params = {}
        if team:
            params["team"] = team
        if player:
            params["player"] = player

        return await self._make_request("players/squads", params)

    # Predictions endpoints
    async def get_predictions(self, fixture):
        """Get predictions for a fixture."""
        params = {
            "fixture": fixture
        }

        return await self._make_request("predictions", params)

    # Odds endpoints
    async def get_odds(self, fixture=None, league=None, season=None, date=None, timezone=None, page=None,
                       bookmaker=None, bet=None):
        """Get odds information."""
        params = {}
        if fixture:
            params["fixture"] = fixture
        if league:
            params["league"] = league
        if season:
            params["season"] = season
        if date:
            params["date"] = date
        if timezone:
            params["timezone"] = timezone
        if page:
            params["page"] = page
        if bookmaker:
            params["bookmaker"] = bookmaker
        if bet:
            params["bet"] = bet

        return await self._make_request("odds", params)

    async def get_odds_live(self, fixture=None, league=None, bet=None):
        """Get live odds for fixtures in progress."""
        params = {}
        if fixture:
            params["fixture"] = fixture
        if league:
            params["league"] = league
        if bet:
            params["bet"] = bet

        return await self._make_request("odds/live", params)

    # Injuries endpoints
    async def get_injuries(self, league=None, season=None, fixture=None, team=None, player=None, date=None):
        """Get injuries information."""
        params = {}
        if league and season:
            params["league"] = league
            params["season"] = season
        if fixture:
            params["fixture"] = fixture
        if team and season:
            params["team"] = team
            params["season"] = season
        if player and season:
            params["player"] = player
            params["season"] = season
        if date:
            params["date"] = date

        return await self._make_request("injuries", params)


# Create a singleton instance
football_api_client = FootballAPIClient()