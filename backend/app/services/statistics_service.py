import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.models import Fixture, FixtureStatistics, Team
from ..services.football_api import football_api_client
from ..services.fixtures_service import fixtures_service
from ..utils.utils import calculate_xg_from_shots, calculate_ppda

logger = logging.getLogger(__name__)


class StatisticsService:
    """
    Service for managing football match statistics.
    Provides methods for fetching, processing, and storing statistics data.
    """

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
            return await fixtures_service.get_fixture_statistics(fixture_id)
        except Exception as e:
            logger.error(f"Error in StatisticsService.get_fixture_statistics: {e}")
            return []

    @staticmethod
    async def get_team_match_statistics(team_id: int, last: int = 5) -> List[Dict[str, Any]]:
        """
        Get statistics for the last N matches of a team.

        Args:
            team_id (int): Team ID
            last (int): Number of past fixtures to analyze

        Returns:
            List[Dict[str, Any]]: List of match statistics for the team
        """
        try:
            # Get the last matches of the team
            team_fixtures = await fixtures_service.get_fixtures_by_team(team_id, last=last, next=0)
            past_fixtures = team_fixtures.get("past", [])

            # Get statistics for each match
            match_statistics = []
            for fixture in past_fixtures:
                fixture_id = fixture["fixture"]["id"]
                fixture_stats = await StatisticsService.get_fixture_statistics(fixture_id)

                # Find the team's statistics in the fixture
                team_stats = None
                for stats in fixture_stats:
                    if stats["team"]["id"] == team_id:
                        team_stats = stats
                        break

                if team_stats:
                    match_statistics.append({
                        "fixture_id": fixture_id,
                        "fixture_date": fixture["fixture"]["date"],
                        "home": fixture["teams"]["home"]["id"] == team_id,
                        "opponent": fixture["teams"]["away" if fixture["teams"]["home"]["id"] == team_id else "home"][
                            "name"],
                        "result": "W" if ((fixture["teams"]["home"]["id"] == team_id and fixture["teams"]["home"][
                            "winner"]) or
                                          (fixture["teams"]["away"]["id"] == team_id and fixture["teams"]["away"][
                                              "winner"]))
                        else "L" if ((fixture["teams"]["home"]["id"] == team_id and fixture["teams"]["away"][
                            "winner"]) or
                                     (fixture["teams"]["away"]["id"] == team_id and fixture["teams"]["home"]["winner"]))
                        else "D",
                        "score": f"{fixture['goals']['home']}-{fixture['goals']['away']}",
                        "statistics": team_stats["statistics"]
                    })

            return match_statistics
        except Exception as e:
            logger.error(f"Error in StatisticsService.get_team_match_statistics: {e}")
            return []

    @staticmethod
    async def get_team_aggregate_statistics(team_id: int, league_id: int, season: int) -> Dict[str, Any]:
        """
        Get aggregate statistics for a team in a specific league and season.

        Args:
            team_id (int): Team ID
            league_id (int): League ID
            season (int): Season (e.g., 2023)

        Returns:
            Dict[str, Any]: Aggregated team statistics
        """
        try:
            response = await football_api_client.get_team_statistics(
                league=league_id, season=season, team=team_id
            )

            return response.get("response", {})
        except Exception as e:
            logger.error(f"Error in StatisticsService.get_team_aggregate_statistics: {e}")
            return {}

    @staticmethod
    async def calculate_fixture_xg(fixture_id: int) -> Tuple[float, float]:
        """
        Calculate Expected Goals (xG) for both teams in a fixture.

        Args:
            fixture_id (int): Fixture ID

        Returns:
            Tuple[float, float]: (home_xg, away_xg)
        """
        try:
            # Get fixture statistics
            statistics = await StatisticsService.get_fixture_statistics(fixture_id)

            # Get fixture data to identify home/away teams
            fixture_data = await fixtures_service.get_fixture_by_id(fixture_id)
            if not fixture_data:
                return (0.0, 0.0)

            home_team_id = fixture_data["teams"]["home"]["id"]
            away_team_id = fixture_data["teams"]["away"]["id"]

            # Calculate xG for home team
            home_xg = 0.0
            away_xg = 0.0

            for team_stats in statistics:
                team_id = team_stats["team"]["id"]

                # Approximate xG based on available statistics
                # This is a simplified model; in a real system, you'd use shot location data
                shots_total = 0
                shots_on_goal = 0
                shots_inside_box = 0

                for stat in team_stats["statistics"]:
                    if stat["type"] == "Total Shots":
                        shots_total = int(stat["value"] or 0)
                    elif stat["type"] == "Shots on Goal":
                        shots_on_goal = int(stat["value"] or 0)
                    elif stat["type"] == "Shots insidebox":
                        shots_inside_box = int(stat["value"] or 0)

                # Simple xG model:
                # - Shots inside box: 0.1 xG per shot
                # - Shots on goal: 0.07 xG per shot
                # - Other shots: 0.02 xG per shot
                shots_outside_box = shots_total - shots_inside_box

                team_xg = (
                        (shots_inside_box * 0.1) +
                        (shots_on_goal * 0.07) +
                        (shots_outside_box * 0.02)
                )

                if team_id == home_team_id:
                    home_xg = team_xg
                elif team_id == away_team_id:
                    away_xg = team_xg

            return (home_xg, away_xg)
        except Exception as e:
            logger.error(f"Error in StatisticsService.calculate_fixture_xg: {e}")
            return (0.0, 0.0)

    @staticmethod
    def store_fixture_statistics(db: Session, fixture_id: int, statistics_data: List[Dict[str, Any]]) -> bool:
        """
        Store fixture statistics in the database.

        Args:
            db (Session): Database session
            fixture_id (int): Fixture ID
            statistics_data (List[Dict[str, Any]]): Statistics data from the API

        Returns:
            bool: Success status
        """
        try:
            # Check if fixture exists in the database
            fixture = db.query(Fixture).filter(Fixture.api_id == fixture_id).first()
            if not fixture:
                logger.warning(f"Fixture with API ID {fixture_id} not found in database")
                return False

            # Process each team's statistics
            for team_stats in statistics_data:
                team_id = team_stats["team"]["id"]

                # Get team from database
                team = db.query(Team).filter(Team.api_id == team_id).first()
                if not team:
                    logger.warning(f"Team with API ID {team_id} not found in database")
                    continue

                # Check if statistics already exist for this fixture and team
                existing_stats = db.query(FixtureStatistics).filter(
                    FixtureStatistics.fixture_id == fixture.id,
                    FixtureStatistics.team_id == team.id
                ).first()

                # Extract statistics values
                shots_on_goal = 0
                shots_off_goal = 0
                total_shots = 0
                blocked_shots = 0
                shots_inside_box = 0
                shots_outside_box = 0
                fouls = 0
                corner_kicks = 0
                offsides = 0
                ball_possession = 0
                yellow_cards = 0
                red_cards = 0
                goalkeeper_saves = 0
                total_passes = 0
                accurate_passes = 0
                pass_accuracy = 0

                for stat in team_stats.get("statistics", []):
                    stat_type = stat.get("type")
                    stat_value = stat.get("value")

                    if stat_value is None or stat_value == "":
                        continue

                    if stat_type == "Shots on Goal":
                        shots_on_goal = int(stat_value)
                    elif stat_type == "Shots off Goal":
                        shots_off_goal = int(stat_value)
                    elif stat_type == "Total Shots":
                        total_shots = int(stat_value)
                    elif stat_type == "Blocked Shots":
                        blocked_shots = int(stat_value)
                    elif stat_type == "Shots insidebox":
                        shots_inside_box = int(stat_value)
                    elif stat_type == "Shots outsidebox":
                        shots_outside_box = int(stat_value)
                    elif stat_type == "Fouls":
                        fouls = int(stat_value)
                    elif stat_type == "Corner Kicks":
                        corner_kicks = int(stat_value)
                    elif stat_type == "Offsides":
                        offsides = int(stat_value)
                    elif stat_type == "Ball Possession":
                        ball_possession = int(stat_value.replace("%", ""))
                    elif stat_type == "Yellow Cards":
                        yellow_cards = int(stat_value)
                    elif stat_type == "Red Cards":
                        red_cards = int(stat_value)
                    elif stat_type == "Goalkeeper Saves":
                        goalkeeper_saves = int(stat_value)
                    elif stat_type == "Total passes":
                        total_passes = int(stat_value)
                    elif stat_type == "Passes accurate":
                        accurate_passes = int(stat_value)
                    elif stat_type == "Passes %":
                        pass_accuracy = int(stat_value.replace("%", ""))

                # Calculate expected goals
                # In a real application, you would use a more sophisticated model
                expected_goals = shots_on_goal * 0.3 + shots_inside_box * 0.1 + shots_outside_box * 0.02

                if existing_stats:
                    # Update existing statistics
                    existing_stats.shots_on_goal = shots_on_goal
                    existing_stats.shots_off_goal = shots_off_goal
                    existing_stats.total_shots = total_shots
                    existing_stats.blocked_shots = blocked_shots
                    existing_stats.shots_inside_box = shots_inside_box
                    existing_stats.shots_outside_box = shots_outside_box
                    existing_stats.fouls = fouls
                    existing_stats.corner_kicks = corner_kicks
                    existing_stats.offsides = offsides
                    existing_stats.ball_possession = ball_possession
                    existing_stats.yellow_cards = yellow_cards
                    existing_stats.red_cards = red_cards
                    existing_stats.goalkeeper_saves = goalkeeper_saves
                    existing_stats.total_passes = total_passes
                    existing_stats.accurate_passes = accurate_passes
                    existing_stats.pass_accuracy = pass_accuracy
                    existing_stats.expected_goals = expected_goals
                else:
                    # Create new statistics
                    new_stats = FixtureStatistics(
                        fixture_id=fixture.id,
                        team_id=team.id,
                        shots_on_goal=shots_on_goal,
                        shots_off_goal=shots_off_goal,
                        total_shots=total_shots,
                        blocked_shots=blocked_shots,
                        shots_inside_box=shots_inside_box,
                        shots_outside_box=shots_outside_box,
                        fouls=fouls,
                        corner_kicks=corner_kicks,
                        offsides=offsides,
                        ball_possession=ball_possession,
                        yellow_cards=yellow_cards,
                        red_cards=red_cards,
                        goalkeeper_saves=goalkeeper_saves,
                        total_passes=total_passes,
                        accurate_passes=accurate_passes,
                        pass_accuracy=pass_accuracy,
                        expected_goals=expected_goals
                    )
                    db.add(new_stats)

            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error storing fixture statistics: {e}")
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing fixture statistics: {e}")
            return False

    @staticmethod
    async def sync_fixture_statistics(db: Session, fixture_id: int) -> Dict[str, Any]:
        """
        Sync statistics for a specific fixture from the API to the database.

        Args:
            db (Session): Database session
            fixture_id (int): Fixture ID

        Returns:
            Dict[str, Any]: Summary of the sync operation
        """
        try:
            # Get statistics from API
            statistics = await StatisticsService.get_fixture_statistics(fixture_id)

            if not statistics:
                return {
                    "fixture_id": fixture_id,
                    "success": False,
                    "message": "No statistics found for fixture"
                }

            # Store statistics in database
            success = StatisticsService.store_fixture_statistics(db, fixture_id, statistics)

            return {
                "fixture_id": fixture_id,
                "success": success,
                "statistics_count": len(statistics),
                "message": "Statistics synced successfully" if success else "Failed to sync statistics"
            }
        except Exception as e:
            logger.error(f"Error syncing fixture statistics: {e}")
            return {
                "fixture_id": fixture_id,
                "success": False,
                "message": f"Error: {str(e)}"
            }

    @staticmethod
    async def analyze_team_performance(team_id: int, league_id: int, season: int) -> Dict[str, Any]:
        """
        Analyze the performance of a team in a specific league and season.

        Args:
            team_id (int): Team ID
            league_id (int): League ID
            season (int): Season (e.g., 2023)

        Returns:
            Dict[str, Any]: Team performance analysis
        """
        try:
            # Get aggregate statistics
            aggregate_stats = await StatisticsService.get_team_aggregate_statistics(
                team_id, league_id, season
            )

            # Get recent match statistics
            match_stats = await StatisticsService.get_team_match_statistics(team_id, last=10)

            # Calculate performance metrics
            avg_possession = 0
            avg_shots = 0
            avg_shots_on_target = 0
            avg_passes = 0
            avg_pass_accuracy = 0
            avg_corners = 0

            for match in match_stats:
                for stat in match.get("statistics", []):
                    stat_type = stat.get("type")
                    stat_value = stat.get("value")

                    if stat_value is None or stat_value == "":
                        continue

                    if stat_type == "Ball Possession":
                        avg_possession += int(stat_value.replace("%", ""))
                    elif stat_type == "Total Shots":
                        avg_shots += int(stat_value)
                    elif stat_type == "Shots on Goal":
                        avg_shots_on_target += int(stat_value)
                    elif stat_type == "Total passes":
                        avg_passes += int(stat_value)
                    elif stat_type == "Passes %":
                        avg_pass_accuracy += int(stat_value.replace("%", ""))
                    elif stat_type == "Corner Kicks":
                        avg_corners += int(stat_value)

            match_count = len(match_stats)
            if match_count > 0:
                avg_possession /= match_count
                avg_shots /= match_count
                avg_shots_on_target /= match_count
                avg_passes /= match_count
                avg_pass_accuracy /= match_count
                avg_corners /= match_count

            # Extract key team information
            team_info = {
                "team_id": team_id,
                "team_name": aggregate_stats.get("team", {}).get("name", "Unknown"),
                "league_id": league_id,
                "league_name": aggregate_stats.get("league", {}).get("name", "Unknown"),
                "season": season,
                "form": aggregate_stats.get("form", ""),
                "matches_played": aggregate_stats.get("fixtures", {}).get("played", {}).get("total", 0),
                "wins": aggregate_stats.get("fixtures", {}).get("wins", {}).get("total", 0),
                "draws": aggregate_stats.get("fixtures", {}).get("draws", {}).get("total", 0),
                "losses": aggregate_stats.get("fixtures", {}).get("losses", {}).get("total", 0),
                "goals_for": aggregate_stats.get("goals", {}).get("for", {}).get("total", {}).get("total", 0),
                "goals_against": aggregate_stats.get("goals", {}).get("against", {}).get("total", {}).get("total", 0),
                "clean_sheets": aggregate_stats.get("clean_sheet", {}).get("total", 0),
                "failed_to_score": aggregate_stats.get("failed_to_score", {}).get("total", 0),
                "recent_matches": match_stats,
                "average_stats": {
                    "possession": round(avg_possession, 2),
                    "shots": round(avg_shots, 2),
                    "shots_on_target": round(avg_shots_on_target, 2),
                    "passes": round(avg_passes, 2),
                    "pass_accuracy": round(avg_pass_accuracy, 2),
                    "corners": round(avg_corners, 2)
                }
            }

            return team_info
        except Exception as e:
            logger.error(f"Error analyzing team performance: {e}")
            return {
                "team_id": team_id,
                "error": str(e)
            }

    @staticmethod
    async def compare_teams(team1_id: int, team2_id: int, league_id: int, season: int) -> Dict[str, Any]:
        """
        Compare the performance of two teams in a specific league and season.

        Args:
            team1_id (int): First team ID
            team2_id (int): Second team ID
            league_id (int): League ID
            season (int): Season (e.g., 2023)

        Returns:
            Dict[str, Any]: Team comparison analysis
        """
        try:
            # Get team analyses
            team1_analysis = await StatisticsService.analyze_team_performance(
                team1_id, league_id, season
            )

            team2_analysis = await StatisticsService.analyze_team_performance(
                team2_id, league_id, season
            )

            # Get head-to-head matches
            h2h_matches = await fixtures_service.get_head_to_head(team1_id, team2_id, last=10)

            # Analyze head-to-head results
            team1_wins = 0
            team2_wins = 0
            draws = 0

            for match in h2h_matches:
                home_id = match["teams"]["home"]["id"]
                away_id = match["teams"]["away"]["id"]
                home_winner = match["teams"]["home"]["winner"]
                away_winner = match["teams"]["away"]["winner"]

                if home_winner:
                    if home_id == team1_id:
                        team1_wins += 1
                    else:
                        team2_wins += 1
                elif away_winner:
                    if away_id == team1_id:
                        team1_wins += 1
                    else:
                        team2_wins += 1
                else:
                    draws += 1

            return {
                "team1": team1_analysis,
                "team2": team2_analysis,
                "head_to_head": {
                    "matches": h2h_matches,
                    "summary": {
                        "team1_wins": team1_wins,
                        "team2_wins": team2_wins,
                        "draws": draws
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error comparing teams: {e}")
            return {
                "team1_id": team1_id,
                "team2_id": team2_id,
                "error": str(e)
            }


# Create a singleton instance
statistics_service = StatisticsService()