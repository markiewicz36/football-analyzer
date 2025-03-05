import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.models import Fixture, Competition, Team, FixtureStatistics, Event, Lineup, Prediction, Odds
from ..services.football_api import football_api_client
from ..utils.utils import parse_fixtures_by_date, parse_fixtures_by_league

logger = logging.getLogger(__name__)

class FixturesService:
    """
    Service for managing fixtures (matches) data.
    Provides methods for fetching, processing, and storing fixtures data.
    """

    @staticmethod
    async def get_live_fixtures() -> List[Dict[str, Any]]:
        """
        Get currently live fixtures from the Football API.

        Returns:
            List[Dict[str, Any]]: List of live fixtures
        """
        try:
            response = await football_api_client.get_fixtures(live="all")
            return response.get("response", [])
        except Exception as e:
            logger.error(f"Error fetching live fixtures: {e}")
            return []

    @staticmethod
    async def get_fixtures_by_date(date: str) -> List[Dict[str, Any]]:
        """
        Get fixtures for a specific date from the Football API.

        Args:
            date (str): Date in format YYYY-MM-DD

        Returns:
            List[Dict[str, Any]]: List of fixtures for the specified date
        """
        try:
            response = await football_api_client.get_fixtures(date=date)
            return response.get("response", [])
        except Exception as e:
            logger.error(f"Error fetching fixtures for date {date}: {e}")
            return []

    @staticmethod
    async def get_fixtures_by_league_season(league_id: int, season: int) -> List[Dict[str, Any]]:
        """
        Get fixtures for a specific league and season from the Football API.

        Args:
            league_id (int): League ID
            season (int): Season (e.g., 2023)

        Returns:
            List[Dict[str, Any]]: List of fixtures for the specified league and season
        """
        try:
            response = await football_api_client.get_fixtures(league=league_id, season=season)
            return response.get("response", [])
        except Exception as e:
            logger.error(f"Error fetching fixtures for league {league_id}, season {season}: {e}")
            return []

    @staticmethod
    async def get_fixtures_by_team(team_id: int, last: int = 10, next: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get past and upcoming fixtures for a specific team from the Football API.

        Args:
            team_id (int): Team ID
            last (int): Number of past fixtures to fetch
            next (int): Number of upcoming fixtures to fetch

        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary with "past" and "upcoming" fixtures
        """
        try:
            # Get past fixtures
            past_response = await football_api_client.get_fixtures(team=team_id, last=last)

            # Get upcoming fixtures
            next_response = await football_api_client.get_fixtures(team=team_id, next=next)

            return {
                "past": past_response.get("response", []),
                "upcoming": next_response.get("response", [])
            }
        except Exception as e:
            logger.error(f"Error fetching fixtures for team {team_id}: {e}")
            return {"past": [], "upcoming": []}

    @staticmethod
    async def get_fixture_by_id(fixture_id: int) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific fixture from the Football API.

        Args:
            fixture_id (int): Fixture ID

        Returns:
            Optional[Dict[str, Any]]: Fixture details or None if not found
        """
        try:
            response = await football_api_client.get_fixtures(id=fixture_id)
            fixtures = response.get("response", [])
            return fixtures[0] if fixtures else None
        except Exception as e:
            logger.error(f"Error fetching fixture {fixture_id}: {e}")
            return None

    @staticmethod
    async def get_fixture_statistics(fixture_id: int) -> List[Dict[str, Any]]:
        """
        Get statistics for a specific fixture from the Football API.

        Args:
            fixture_id (int): Fixture ID

        Returns:
            List[Dict[str, Any]]: List of team statistics for the fixture
        """
        try:
            response = await football_api_client.get_fixture_statistics(fixture=fixture_id)
            return response.get("response", [])
        except Exception as e:
            logger.error(f"Error fetching statistics for fixture {fixture_id}: {e}")
            return []

    @staticmethod
    async def get_fixture_events(fixture_id: int) -> List[Dict[str, Any]]:
        """
        Get events for a specific fixture from the Football API.

        Args:
            fixture_id (int): Fixture ID

        Returns:
            List[Dict[str, Any]]: List of events for the fixture
        """
        try:
            response = await football_api_client.get_fixture_events(fixture=fixture_id)
            return response.get("response", [])
        except Exception as e:
            logger.error(f"Error fetching events for fixture {fixture_id}: {e}")
            return []

    @staticmethod
    async def get_fixture_lineups(fixture_id: int) -> List[Dict[str, Any]]:
        """
        Get lineups for a specific fixture from the Football API.

        Args:
            fixture_id (int): Fixture ID

        Returns:
            List[Dict[str, Any]]: List of lineups for the fixture
        """
        try:
            response = await football_api_client.get_fixture_lineups(fixture=fixture_id)
            return response.get("response", [])
        except Exception as e:
            logger.error(f"Error fetching lineups for fixture {fixture_id}: {e}")
            return []

    @staticmethod
    async def get_fixture_players(fixture_id: int) -> List[Dict[str, Any]]:
        """
        Get player statistics for a specific fixture from the Football API.

        Args:
            fixture_id (int): Fixture ID

        Returns:
            List[Dict[str, Any]]: List of player statistics for the fixture
        """
        try:
            response = await football_api_client.get_fixture_players(fixture=fixture_id)
            return response.get("response", [])
        except Exception as e:
            logger.error(f"Error fetching player statistics for fixture {fixture_id}: {e}")
            return []

    @staticmethod
    async def get_fixture_odds(fixture_id: int) -> List[Dict[str, Any]]:
        """
        Get odds for a specific fixture from the Football API.

        Args:
            fixture_id (int): Fixture ID

        Returns:
            List[Dict[str, Any]]: List of odds for the fixture
        """
        try:
            response = await football_api_client.get_odds(fixture=fixture_id)
            return response.get("response", [])
        except Exception as e:
            logger.error(f"Error fetching odds for fixture {fixture_id}: {e}")
            return []

    @staticmethod
    async def get_fixtures_in_date_range(from_date: str, to_date: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get fixtures in a specific date range from the Football API.

        Args:
            from_date (str): Start date in format YYYY-MM-DD
            to_date (str): End date in format YYYY-MM-DD

        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary with fixtures grouped by date
        """
        try:
            response = await football_api_client.get_fixtures(from_date=from_date, to=to_date)
            fixtures = response.get("response", [])
            return parse_fixtures_by_date(fixtures)
        except Exception as e:
            logger.error(f"Error fetching fixtures for date range {from_date} to {to_date}: {e}")
            return {}

    @staticmethod
    async def get_head_to_head(team1_id: int, team2_id: int, last: int = 10) -> List[Dict[str, Any]]:
        """
        Get head-to-head fixtures between two teams from the Football API.

        Args:
            team1_id (int): First team ID
            team2_id (int): Second team ID
            last (int): Number of past fixtures to fetch

        Returns:
            List[Dict[str, Any]]: List of head-to-head fixtures
        """
        try:
            h2h = f"{team1_id}-{team2_id}"
            response = await football_api_client.get_fixtures(h2h=h2h, last=last)
            return response.get("response", [])
        except Exception as e:
            logger.error(f"Error fetching head-to-head fixtures for teams {team1_id} and {team2_id}: {e}")
            return []

    @staticmethod
    def store_fixture_in_db(db: Session, fixture_data: Dict[str, Any]) -> Optional[Fixture]:
        """
        Store fixture data in the database.

        Args:
            db (Session): Database session
            fixture_data (Dict[str, Any]): Fixture data from the API

        Returns:
            Optional[Fixture]: Stored fixture object or None if error
        """
        try:
            # Extract basic fixture data
            fixture_api_id = fixture_data["fixture"]["id"]

            # Check if fixture already exists
            existing_fixture = db.query(Fixture).filter(Fixture.api_id == fixture_api_id).first()
            if existing_fixture:
                # Update existing fixture
                existing_fixture.status = fixture_data["fixture"]["status"]["short"]
                existing_fixture.elapsed = fixture_data["fixture"]["status"]["elapsed"]
                existing_fixture.referee = fixture_data["fixture"]["referee"]
                existing_fixture.home_goals = fixture_data["goals"]["home"]
                existing_fixture.away_goals = fixture_data["goals"]["away"]

                db.commit()
                db.refresh(existing_fixture)
                return existing_fixture

            # Get or create competition
            competition_api_id = fixture_data["league"]["id"]
            competition = db.query(Competition).filter(Competition.api_id == competition_api_id).first()
            if not competition:
                competition = Competition(
                    api_id=competition_api_id,
                    name=fixture_data["league"]["name"],
                    country=fixture_data["league"]["country"],
                    type=fixture_data["league"]["type"],
                    season=fixture_data["league"]["season"],
                    logo_url=fixture_data["league"]["logo"]
                )
                db.add(competition)
                db.flush()

            # Get or create home team
            home_team_api_id = fixture_data["teams"]["home"]["id"]
            home_team = db.query(Team).filter(Team.api_id == home_team_api_id).first()
            if not home_team:
                home_team = Team(
                    api_id=home_team_api_id,
                    name=fixture_data["teams"]["home"]["name"],
                    logo_url=fixture_data["teams"]["home"]["logo"],
                    country=fixture_data["league"]["country"]  # Default to league country
                )
                db.add(home_team)
                db.flush()

            # Get or create away team
            away_team_api_id = fixture_data["teams"]["away"]["id"]
            away_team = db.query(Team).filter(Team.api_id == away_team_api_id).first()
            if not away_team:
                away_team = Team(
                    api_id=away_team_api_id,
                    name=fixture_data["teams"]["away"]["name"],
                    logo_url=fixture_data["teams"]["away"]["logo"],
                    country=fixture_data["league"]["country"]  # Default to league country
                )
                db.add(away_team)
                db.flush()

            # Create fixture
            fixture_date = datetime.fromisoformat(fixture_data["fixture"]["date"].replace("Z", "+00:00"))
            fixture = Fixture(
                api_id=fixture_api_id,
                referee=fixture_data["fixture"]["referee"],
                timezone=fixture_data["fixture"]["timezone"],
                date=fixture_date,
                timestamp=fixture_data["fixture"]["timestamp"],
                venue_name=fixture_data["fixture"]["venue"]["name"],
                venue_city=fixture_data["fixture"]["venue"]["city"],
                status=fixture_data["fixture"]["status"]["short"],
                elapsed=fixture_data["fixture"]["status"]["elapsed"],
                competition_id=competition.id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                home_goals=fixture_data["goals"]["home"],
                away_goals=fixture_data["goals"]["away"],
                # Score details if available
                home_halftime_goals=fixture_data.get("score", {}).get("halftime", {}).get("home"),
                away_halftime_goals=fixture_data.get("score", {}).get("halftime", {}).get("away"),
                home_fulltime_goals=fixture_data.get("score", {}).get("fulltime", {}).get("home"),
                away_fulltime_goals=fixture_data.get("score", {}).get("fulltime", {}).get("away"),
                home_extratime_goals=fixture_data.get("score", {}).get("extratime", {}).get("home"),
                away_extratime_goals=fixture_data.get("score", {}).get("extratime", {}).get("away"),
                home_penalty_goals=fixture_data.get("score", {}).get("penalty", {}).get("home"),
                away_penalty_goals=fixture_data.get("score", {}).get("penalty", {}).get("away")
            )

            db.add(fixture)
            db.commit()
            db.refresh(fixture)
            return fixture

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error storing fixture: {e}")
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing fixture in database: {e}")
            return None

    @staticmethod
    async def sync_fixtures_by_date(db: Session, date: str) -> Dict[str, Any]:
        """
        Sync fixtures for a specific date from the API to the database.

        Args:
            db (Session): Database session
            date (str): Date in format YYYY-MM-DD

        Returns:
            Dict[str, Any]: Summary of the sync operation
        """
        try:
            fixtures = await FixturesService.get_fixtures_by_date(date)

            total = len(fixtures)
            stored = 0
            failed = 0

            for fixture_data in fixtures:
                fixture = FixturesService.store_fixture_in_db(db, fixture_data)
                if fixture:
                    stored += 1
                else:
                    failed += 1

            return {
                "date": date,
                "total_fixtures": total,
                "stored_fixtures": stored,
                "failed_fixtures": failed
            }

        except Exception as e:
            logger.error(f"Error syncing fixtures for date {date}: {e}")
            return {
                "date": date,
                "error": str(e),
                "total_fixtures": 0,
                "stored_fixtures": 0,
                "failed_fixtures": 0
            }

    @staticmethod
    async def sync_fixtures_by_league_season(db: Session, league_id: int, season: int) -> Dict[str, Any]:
        """
        Sync fixtures for a specific league and season from the API to the database.

        Args:
            db (Session): Database session
            league_id (int): League ID
            season (int): Season (e.g., 2023)

        Returns:
            Dict[str, Any]: Summary of the sync operation
        """
        try:
            fixtures = await FixturesService.get_fixtures_by_league_season(league_id, season)

            total = len(fixtures)
            stored = 0
            failed = 0

            for fixture_data in fixtures:
                fixture = FixturesService.store_fixture_in_db(db, fixture_data)
                if fixture:
                    stored += 1
                else:
                    failed += 1

            return {
                "league_id": league_id,
                "season": season,
                "total_fixtures": total,
                "stored_fixtures": stored,
                "failed_fixtures": failed
            }

        except Exception as e:
            logger.error(f"Error syncing fixtures for league {league_id}, season {season}: {e}")
            return {
                "league_id": league_id,
                "season": season,
                "error": str(e),
                "total_fixtures": 0,
                "stored_fixtures": 0,
                "failed_fixtures": 0
            }

    @staticmethod
    async def get_upcoming_fixtures(days: int = 7) -> List[Dict[str, Any]]:
        """
        Get fixtures for the upcoming days.

        Args:
            days (int): Number of days to look ahead

        Returns:
            List[Dict[str, Any]]: List of upcoming fixtures
        """
        try:
            today = datetime.now().date()
            dates = []

            # Generate dates for the upcoming days
            for i in range(days):
                date = today + timedelta(days=i)
                dates.append(date.strftime("%Y-%m-%d"))

            # Get fixtures for each date
            fixtures = []
            for date in dates:
                date_fixtures = await FixturesService.get_fixtures_by_date(date)
                fixtures.extend(date_fixtures)

            return fixtures
        except Exception as e:
            logger.error(f"Error fetching upcoming fixtures: {e}")
            return []

# Create a singleton instance
fixtures_service = FixturesService()