import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.models import Fixture, Team, Competition, Prediction
from ..services.football_api import football_api_client
from ..services.deepseek_api import deepseek_client
from ..services.fixtures_service import fixtures_service
from ..services.statistics_service import statistics_service

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Service for analyzing football matches using ML and AI.
    Provides methods for generating predictions, insights, and match reports.
    """

    @staticmethod
    async def analyze_fixture(fixture_id: int) -> Dict[str, Any]:
        """
        Analyze a football fixture using available statistics and AI.

        Args:
            fixture_id (int): Fixture ID

        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            # Get fixture details
            fixture_data = await fixtures_service.get_fixture_by_id(fixture_id)
            if not fixture_data:
                return {"error": f"Fixture with ID {fixture_id} not found"}

            # Get statistics
            statistics = await statistics_service.get_fixture_statistics(fixture_id)

            # Get team IDs
            home_team_id = fixture_data["teams"]["home"]["id"]
            away_team_id = fixture_data["teams"]["away"]["id"]
            league_id = fixture_data["league"]["id"]
            season = fixture_data["league"]["season"]

            # Get team performance analyses
            home_team_analysis = await statistics_service.analyze_team_performance(
                home_team_id, league_id, season
            )

            away_team_analysis = await statistics_service.analyze_team_performance(
                away_team_id, league_id, season
            )

            # Get head-to-head matches
            h2h_matches = await fixtures_service.get_head_to_head(home_team_id, away_team_id, last=10)

            # Calculate expected goals
            home_xg, away_xg = await statistics_service.calculate_fixture_xg(fixture_id)

            # Prepare data for AI analysis
            analysis_data = {
                "fixture": fixture_data,
                "statistics": statistics,
                "home_team_analysis": home_team_analysis,
                "away_team_analysis": away_team_analysis,
                "head_to_head": h2h_matches,
                "expected_goals": {
                    "home_xg": home_xg,
                    "away_xg": away_xg
                }
            }

            # Process matches by status
            if fixture_data["fixture"]["status"]["short"] in ["NS", "TBD", "PST"]:
                # Pre-match analysis
                analysis = await AnalysisService.generate_pre_match_analysis(analysis_data)
            elif fixture_data["fixture"]["status"]["short"] in ["1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT",
                                                                "LIVE"]:
                # In-play analysis
                analysis = await AnalysisService.generate_in_play_analysis(analysis_data)
            else:
                # Post-match analysis
                analysis = await AnalysisService.generate_post_match_analysis(analysis_data)

            return analysis
        except Exception as e:
            logger.error(f"Error analyzing fixture {fixture_id}: {e}")
            return {"error": str(e)}

    @staticmethod
    async def generate_pre_match_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate pre-match analysis and predictions using AI.

        Args:
            data (Dict[str, Any]): Match data including fixture details, statistics, and team analyses

        Returns:
            Dict[str, Any]: Pre-match analysis
        """
        try:
            fixture = data["fixture"]
            home_team = fixture["teams"]["home"]
            away_team = fixture["teams"]["away"]

            # Get team analyses
            home_team_analysis = data["home_team_analysis"]
            away_team_analysis = data["away_team_analysis"]
            head_to_head = data["head_to_head"]

            # Generate pre-match report using DeepSeek AI
            ai_report = await deepseek_client.generate_pre_match_report(
                fixture_data=fixture,
                team_stats={
                    "home": home_team_analysis,
                    "away": away_team_analysis
                },
                league_context=None,  # Could add league standings here
                historical_h2h=head_to_head
            )

            # Calculate match prediction
            prediction = await AnalysisService.predict_match_result(
                fixture["fixture"]["id"],
                home_team["id"],
                away_team["id"],
                home_team_analysis,
                away_team_analysis,
                head_to_head
            )

            # Compile pre-match analysis
            pre_match_analysis = {
                "fixture_id": fixture["fixture"]["id"],
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "kickoff_time": fixture["fixture"]["date"],
                "league": fixture["league"]["name"],
                "venue": fixture["fixture"]["venue"]["name"],
                "prediction": prediction,
                "home_team_stats": home_team_analysis,
                "away_team_stats": away_team_analysis,
                "head_to_head": {
                    "matches": head_to_head,
                    "summary": AnalysisService.summarize_head_to_head(head_to_head, home_team["id"], away_team["id"])
                },
                "report": ai_report["report"],
                "key_insights": AnalysisService.extract_key_insights(home_team_analysis, away_team_analysis,
                                                                     head_to_head)
            }

            return pre_match_analysis
        except Exception as e:
            logger.error(f"Error generating pre-match analysis: {e}")
            return {"error": str(e)}

    @staticmethod
    async def generate_in_play_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate in-play analysis for a match in progress.

        Args:
            data (Dict[str, Any]): Match data including fixture details, statistics, and team analyses

        Returns:
            Dict[str, Any]: In-play analysis
        """
        try:
            fixture = data["fixture"]
            home_team = fixture["teams"]["home"]
            away_team = fixture["teams"]["away"]
            statistics = data["statistics"]

            # Get current score
            current_score = {
                "home": fixture["goals"]["home"],
                "away": fixture["goals"]["away"]
            }

            # Get match events
            events = await fixtures_service.get_fixture_events(fixture["fixture"]["id"])

            # Calculate expected goals
            home_xg = data["expected_goals"]["home_xg"]
            away_xg = data["expected_goals"]["away_xg"]

            # Calculate momentum based on events and statistics
            momentum = AnalysisService.calculate_match_momentum(events, statistics,
                                                                fixture["fixture"]["status"]["elapsed"])

            # Generate in-play analysis using DeepSeek AI
            match_data = {
                "fixture": fixture,
                "statistics": statistics,
                "events": events,
                "xg": {"home": home_xg, "away": away_xg},
                "momentum": momentum
            }

            # Use AI to analyze current match state
            ai_analysis = await deepseek_client.analyze_match(
                home_team={"name": home_team["name"], "id": home_team["id"]},
                away_team={"name": away_team["name"], "id": away_team["id"]},
                match_data=match_data,
                league_data=None,
                historical_data=None
            )

            # Compile in-play analysis
            in_play_analysis = {
                "fixture_id": fixture["fixture"]["id"],
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "elapsed_time": fixture["fixture"]["status"]["elapsed"],
                "match_status": fixture["fixture"]["status"]["long"],
                "current_score": current_score,
                "expected_goals": {
                    "home": home_xg,
                    "away": away_xg
                },
                "statistics": statistics,
                "events": events,
                "momentum": momentum,
                "analysis": ai_analysis["analysis"],
                "key_observations": AnalysisService.extract_key_observations(statistics, events, current_score,
                                                                             fixture["fixture"]["status"]["elapsed"])
            }

            return in_play_analysis
        except Exception as e:
            logger.error(f"Error generating in-play analysis: {e}")
            return {"error": str(e)}

    @staticmethod
    async def generate_post_match_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate post-match analysis for a completed match.

        Args:
            data (Dict[str, Any]): Match data including fixture details, statistics, and team analyses

        Returns:
            Dict[str, Any]: Post-match analysis
        """
        try:
            fixture = data["fixture"]
            home_team = fixture["teams"]["home"]
            away_team = fixture["teams"]["away"]
            statistics = data["statistics"]

            # Get final score
            final_score = {
                "home": fixture["goals"]["home"],
                "away": fixture["goals"]["away"]
            }

            # Get match events
            events = await fixtures_service.get_fixture_events(fixture["fixture"]["id"])

            # Get player statistics
            players = await fixtures_service.get_fixture_players(fixture["fixture"]["id"])

            # Calculate expected goals
            home_xg = data["expected_goals"]["home_xg"]
            away_xg = data["expected_goals"]["away_xg"]

            # Generate post-match report using DeepSeek AI
            match_data = {
                "fixture": fixture,
                "statistics": statistics,
                "events": events,
                "players": players,
                "xg": {"home": home_xg, "away": away_xg}
            }

            # Use AI to analyze match
            ai_analysis = await deepseek_client.analyze_match(
                home_team={"name": home_team["name"], "id": home_team["id"]},
                away_team={"name": away_team["name"], "id": away_team["id"]},
                match_data=match_data,
                league_data=None,
                historical_data=None
            )

            # Compile post-match analysis
            post_match_analysis = {
                "fixture_id": fixture["fixture"]["id"],
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "final_score": final_score,
                "match_status": fixture["fixture"]["status"]["long"],
                "statistics": statistics,
                "events": events,
                "players": players,
                "expected_goals": {
                    "home": home_xg,
                    "away": away_xg
                },
                "winner": fixture["teams"]["home"]["winner"] and home_team["name"] or
                          fixture["teams"]["away"]["winner"] and away_team["name"] or
                          "Draw",
                "analysis": ai_analysis["analysis"],
                "key_highlights": AnalysisService.extract_key_highlights(statistics, events, players, final_score)
            }

            return post_match_analysis
        except Exception as e:
            logger.error(f"Error generating post-match analysis: {e}")
            return {"error": str(e)}

    @staticmethod
    async def predict_match_result(
            fixture_id: int,
            home_team_id: int,
            away_team_id: int,
            home_team_analysis: Dict[str, Any],
            away_team_analysis: Dict[str, Any],
            h2h_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Predict the result of a match using statistics and machine learning.

        Args:
            fixture_id (int): Fixture ID
            home_team_id (int): Home team ID
            away_team_id (int): Away team ID
            home_team_analysis (Dict[str, Any]): Home team analysis data
            away_team_analysis (Dict[str, Any]): Away team analysis data
            h2h_matches (List[Dict[str, Any]]): Head-to-head match history

        Returns:
            Dict[str, Any]: Match prediction
        """
        try:
            # Prepare data for prediction
            home_team = {"id": home_team_id, "name": home_team_analysis.get("team_name", "Home Team")}
            away_team = {"id": away_team_id, "name": away_team_analysis.get("team_name", "Away Team")}

            team_stats = {
                "home": home_team_analysis,
                "away": away_team_analysis
            }

            # Get recent form
            home_recent_form = []
            away_recent_form = []

            if "recent_matches" in home_team_analysis:
                home_recent_form = home_team_analysis["recent_matches"]

            if "recent_matches" in away_team_analysis:
                away_recent_form = away_team_analysis["recent_matches"]

            recent_form = {
                "home": home_recent_form,
                "away": away_recent_form
            }

            # Use DeepSeek AI to predict match result
            prediction = await deepseek_client.predict_match_result(
                fixture_id=fixture_id,
                home_team=home_team,
                away_team=away_team,
                team_stats=team_stats,
                recent_form=recent_form,
                h2h_matches=h2h_matches
            )

            return prediction
        except Exception as e:
            logger.error(f"Error predicting match result: {e}")
            return {
                "fixture_id": fixture_id,
                "error": str(e),
                "home_win_probability": 0.0,
                "draw_probability": 0.0,
                "away_win_probability": 0.0
            }

    @staticmethod
    def summarize_head_to_head(h2h_matches: List[Dict[str, Any]], team1_id: int, team2_id: int) -> Dict[str, Any]:
        """
        Summarize head-to-head matches between two teams.

        Args:
            h2h_matches (List[Dict[str, Any]]): Head-to-head match history
            team1_id (int): First team ID
            team2_id (int): Second team ID

        Returns:
            Dict[str, Any]: Head-to-head summary
        """
        team1_wins = 0
        team2_wins = 0
        draws = 0
        team1_goals = 0
        team2_goals = 0

        for match in h2h_matches:
            home_id = match["teams"]["home"]["id"]
            away_id = match["teams"]["away"]["id"]
            home_goals = match["goals"]["home"] or 0
            away_goals = match["goals"]["away"] or 0

            if home_id == team1_id:
                team1_goals += home_goals
                team2_goals += away_goals

                if home_goals > away_goals:
                    team1_wins += 1
                elif home_goals < away_goals:
                    team2_wins += 1
                else:
                    draws += 1
            else:  # home_id == team2_id
                team1_goals += away_goals
                team2_goals += home_goals

                if home_goals > away_goals:
                    team2_wins += 1
                elif home_goals < away_goals:
                    team1_wins += 1
                else:
                    draws += 1

        return {
            "matches_played": len(h2h_matches),
            "team1_wins": team1_wins,
            "team2_wins": team2_wins,
            "draws": draws,
            "team1_goals": team1_goals,
            "team2_goals": team2_goals
        }

    @staticmethod
    def extract_key_insights(
            home_team_analysis: Dict[str, Any],
            away_team_analysis: Dict[str, Any],
            h2h_matches: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract key insights for pre-match analysis.

        Args:
            home_team_analysis (Dict[str, Any]): Home team analysis data
            away_team_analysis (Dict[str, Any]): Away team analysis data
            h2h_matches (List[Dict[str, Any]]): Head-to-head match history

        Returns:
            List[str]: Key insights
        """
        insights = []

        # Form comparison
        if "form" in home_team_analysis and "form" in away_team_analysis:
            home_form = home_team_analysis["form"]
            away_form = away_team_analysis["form"]

            home_wins = home_form.count("W")
            home_draws = home_form.count("D")
            home_losses = home_form.count("L")

            away_wins = away_form.count("W")
            away_draws = away_form.count("D")
            away_losses = away_form.count("L")

            if home_wins > away_wins:
                insights.append(
                    f"{home_team_analysis.get('team_name', 'Home team')} has better recent form with {home_wins} wins in the last {len(home_form)} matches")
            elif away_wins > home_wins:
                insights.append(
                    f"{away_team_analysis.get('team_name', 'Away team')} has better recent form with {away_wins} wins in the last {len(away_form)} matches")
            else:
                insights.append(f"Both teams have similar recent form with {home_wins} wins each")

        # Goals comparison
        if "goals_for" in home_team_analysis and "goals_for" in away_team_analysis and "matches_played" in home_team_analysis and "matches_played" in away_team_analysis:
            home_goals = home_team_analysis["goals_for"]
            away_goals = away_team_analysis["goals_for"]
            home_matches = home_team_analysis["matches_played"]
            away_matches = away_team_analysis["matches_played"]

            if home_matches > 0 and away_matches > 0:
                home_avg_goals = home_goals / home_matches
                away_avg_goals = away_goals / away_matches

                if home_avg_goals > away_avg_goals:
                    insights.append(
                        f"{home_team_analysis.get('team_name', 'Home team')} scores more goals per match ({home_avg_goals:.2f}) compared to {away_team_analysis.get('team_name', 'Away team')} ({away_avg_goals:.2f})")
                elif away_avg_goals > home_avg_goals:
                    insights.append(
                        f"{away_team_analysis.get('team_name', 'Away team')} scores more goals per match ({away_avg_goals:.2f}) compared to {home_team_analysis.get('team_name', 'Home team')} ({home_avg_goals:.2f})")

        # Defense comparison
        if "goals_against" in home_team_analysis and "goals_against" in away_team_analysis and "matches_played" in home_team_analysis and "matches_played" in away_team_analysis:
            home_goals_against = home_team_analysis["goals_against"]
            away_goals_against = away_team_analysis["goals_against"]
            home_matches = home_team_analysis["matches_played"]
            away_matches = away_team_analysis["matches_played"]

            if home_matches > 0 and away_matches > 0:
                home_avg_conceded = home_goals_against / home_matches
                away_avg_conceded = away_goals_against / away_matches

                if home_avg_conceded < away_avg_conceded:
                    insights.append(
                        f"{home_team_analysis.get('team_name', 'Home team')} has a stronger defense, conceding {home_avg_conceded:.2f} goals per match")
                elif away_avg_conceded < home_avg_conceded:
                    insights.append(
                        f"{away_team_analysis.get('team_name', 'Away team')} has a stronger defense, conceding {away_avg_conceded:.2f} goals per match")

        # Clean sheets
        if "clean_sheets" in home_team_analysis and "clean_sheets" in away_team_analysis and "matches_played" in home_team_analysis and "matches_played" in away_team_analysis:
            home_clean_sheets = home_team_analysis["clean_sheets"]
            away_clean_sheets = away_team_analysis["clean_sheets"]
            home_matches = home_team_analysis["matches_played"]
            away_matches = away_team_analysis["matches_played"]

            if home_matches > 0 and away_matches > 0:
                home_cs_ratio = home_clean_sheets / home_matches
                away_cs_ratio = away_clean_sheets / away_matches

                if home_cs_ratio > 0.3:  # 30% clean sheets is significant
                    insights.append(
                        f"{home_team_analysis.get('team_name', 'Home team')} has kept clean sheets in {home_clean_sheets} out of {home_matches} matches")
                if away_cs_ratio > 0.3:
                    insights.append(
                        f"{away_team_analysis.get('team_name', 'Away team')} has kept clean sheets in {away_clean_sheets} out of {away_matches} matches")

        # H2H insights
        if h2h_matches:
            h2h_count = len(h2h_matches)
            if h2h_count > 0:
                insights.append(f"The teams have met {h2h_count} times previously")

                # Check for recent dominance
                recent_h2h = h2h_matches[:5]  # Last 5 matches
                home_team_id = home_team_analysis.get("team_id")
                away_team_id = away_team_analysis.get("team_id")

                home_wins = 0
                away_wins = 0

                for match in recent_h2h:
                    if match["teams"]["home"]["id"] == home_team_id and match["teams"]["home"]["winner"]:
                        home_wins += 1
                    elif match["teams"]["away"]["id"] == home_team_id and match["teams"]["away"]["winner"]:
                        home_wins += 1
                    elif match["teams"]["home"]["id"] == away_team_id and match["teams"]["home"]["winner"]:
                        away_wins += 1
                    elif match["teams"]["away"]["id"] == away_team_id and match["teams"]["away"]["winner"]:
                        away_wins += 1

                if home_wins >= 3 and len(recent_h2h) >= 5:
                    insights.append(
                        f"{home_team_analysis.get('team_name', 'Home team')} has won {home_wins} of the last {len(recent_h2h)} meetings")
                elif away_wins >= 3 and len(recent_h2h) >= 5:
                    insights.append(
                        f"{away_team_analysis.get('team_name', 'Away team')} has won {away_wins} of the last {len(recent_h2h)} meetings")

        return insights

    # Brakujące metody do dołączenia do klasy AnalysisService

    @staticmethod
    def extract_key_observations(
            statistics: List[Dict[str, Any]],
            events: List[Dict[str, Any]],
            current_score: Dict[str, int],
            elapsed_time: int
    ) -> List[str]:
        """
        Extract key observations for in-play match analysis.

        Args:
            statistics (List[Dict[str, Any]]): Match statistics
            events (List[Dict[str, Any]]): Match events
            current_score (Dict[str, int]): Current score
            elapsed_time (int): Elapsed match time in minutes

        Returns:
            List[str]: Key observations
        """
        observations = []

        if not statistics or len(statistics) < 2:
            return ["Insufficient statistics data available"]

        home_team_name = statistics[0]["team"]["name"]
        away_team_name = statistics[1]["team"]["name"]

        home_stats = statistics[0]["statistics"]
        away_stats = statistics[1]["statistics"]

        # Extract key statistics
        home_possession = 50
        away_possession = 50
        home_shots = 0
        away_shots = 0
        home_shots_on_target = 0
        away_shots_on_target = 0
        home_corners = 0
        away_corners = 0

        for stat in home_stats:
            if stat["type"] == "Ball Possession":
                home_possession = int(stat["value"].replace("%", "") or 50)
            elif stat["type"] == "Total Shots":
                home_shots = int(stat["value"] or 0)
            elif stat["type"] == "Shots on Goal":
                home_shots_on_target = int(stat["value"] or 0)
            elif stat["type"] == "Corner Kicks":
                home_corners = int(stat["value"] or 0)

        for stat in away_stats:
            if stat["type"] == "Ball Possession":
                away_possession = int(stat["value"].replace("%", "") or 50)
            elif stat["type"] == "Total Shots":
                away_shots = int(stat["value"] or 0)
            elif stat["type"] == "Shots on Goal":
                away_shots_on_target = int(stat["value"] or 0)
            elif stat["type"] == "Corner Kicks":
                away_corners = int(stat["value"] or 0)

        # Add observations based on statistics

        # Score
        if current_score["home"] > current_score["away"]:
            observations.append(
                f"{home_team_name} leads {current_score['home']}-{current_score['away']} after {elapsed_time} minutes")
        elif current_score["away"] > current_score["home"]:
            observations.append(
                f"{away_team_name} leads {current_score['away']}-{current_score['home']} after {elapsed_time} minutes")
        else:
            observations.append(
                f"Score is level at {current_score['home']}-{current_score['away']} after {elapsed_time} minutes")

        # Possession
        if abs(home_possession - away_possession) >= 10:  # Significant possession difference
            if home_possession > away_possession:
                observations.append(f"{home_team_name} is dominating possession ({home_possession}%)")
            else:
                observations.append(f"{away_team_name} is dominating possession ({away_possession}%)")
        else:
            observations.append(f"Possession is balanced ({home_possession}%-{away_possession}%)")

        # Shots
        if home_shots > 0 or away_shots > 0:
            if home_shots > away_shots + 5:
                observations.append(f"{home_team_name} is creating more chances ({home_shots} shots vs {away_shots})")
            elif away_shots > home_shots + 5:
                observations.append(f"{away_team_name} is creating more chances ({away_shots} shots vs {home_shots})")

        # Shots on target
        if home_shots_on_target > 0 or away_shots_on_target > 0:
            if home_shots_on_target > away_shots_on_target + 3:
                observations.append(
                    f"{home_team_name} has been more accurate with {home_shots_on_target} shots on target")
            elif away_shots_on_target > home_shots_on_target + 3:
                observations.append(
                    f"{away_team_name} has been more accurate with {away_shots_on_target} shots on target")

        # Recent goals
        recent_goals = [event for event in events if
                        event["type"] == "Goal" and event["time"]["elapsed"] > elapsed_time - 10]
        if recent_goals:
            goal = recent_goals[-1]  # Most recent goal
            team_name = goal["team"]["name"]
            time = goal["time"]["elapsed"]

            if team_name == home_team_name:
                if current_score["home"] > current_score["away"]:
                    observations.append(f"{home_team_name} took the lead with a goal in the {time}' minute")
                elif current_score["home"] == current_score["away"]:
                    observations.append(f"{home_team_name} equalized with a goal in the {time}' minute")
                else:
                    observations.append(f"{home_team_name} reduced the deficit with a goal in the {time}' minute")
            else:  # away team
                if current_score["away"] > current_score["home"]:
                    observations.append(f"{away_team_name} took the lead with a goal in the {time}' minute")
                elif current_score["away"] == current_score["home"]:
                    observations.append(f"{away_team_name} equalized with a goal in the {time}' minute")
                else:
                    observations.append(f"{away_team_name} reduced the deficit with a goal in the {time}' minute")

        # Recent cards
        recent_red_cards = [event for event in events if
                            event["type"] == "Card" and event["detail"] == "Red Card" and event["time"][
                                "elapsed"] <= elapsed_time]

        if recent_red_cards:
            for card in recent_red_cards:
                team_name = card["team"]["name"]
                player_name = card["player"]["name"]
                time = card["time"]["elapsed"]
                observations.append(f"{player_name} ({team_name}) was sent off in the {time}' minute")

        return observations

    @staticmethod
    def extract_key_highlights(
            statistics: List[Dict[str, Any]],
            events: List[Dict[str, Any]],
            players: List[Dict[str, Any]],
            final_score: Dict[str, int]
    ) -> List[str]:
        """
        Extract key highlights for post-match analysis.

        Args:
            statistics (List[Dict[str, Any]]): Match statistics
            events (List[Dict[str, Any]]): Match events
            players (List[Dict[str, Any]]): Player statistics
            final_score (Dict[str, int]): Final score

        Returns:
            List[str]: Key highlights
        """
        highlights = []

        if not statistics or len(statistics) < 2:
            return ["Insufficient statistics data available"]

        home_team_name = statistics[0]["team"]["name"]
        away_team_name = statistics[1]["team"]["name"]

        # Final result
        if final_score["home"] > final_score["away"]:
            highlights.append(
                f"{home_team_name} won {final_score['home']}-{final_score['away']} against {away_team_name}")
        elif final_score["away"] > final_score["home"]:
            highlights.append(
                f"{away_team_name} won {final_score['away']}-{final_score['home']} against {home_team_name}")
        else:
            highlights.append(f"{home_team_name} and {away_team_name} drew {final_score['home']}-{final_score['away']}")

        # Extract key statistics
        home_stats = statistics[0]["statistics"]
        away_stats = statistics[1]["statistics"]

        home_possession = 50
        away_possession = 50
        home_shots = 0
        away_shots = 0
        home_shots_on_target = 0
        away_shots_on_target = 0

        for stat in home_stats:
            if stat["type"] == "Ball Possession":
                home_possession = int(stat["value"].replace("%", "") or 50)
            elif stat["type"] == "Total Shots":
                home_shots = int(stat["value"] or 0)
            elif stat["type"] == "Shots on Goal":
                home_shots_on_target = int(stat["value"] or 0)

        for stat in away_stats:
            if stat["type"] == "Ball Possession":
                away_possession = int(stat["value"].replace("%", "") or 50)
            elif stat["type"] == "Total Shots":
                away_shots = int(stat["value"] or 0)
            elif stat["type"] == "Shots on Goal":
                away_shots_on_target = int(stat["value"] or 0)

        # Possession summary
        if abs(home_possession - away_possession) >= 10:  # Significant possession difference
            if home_possession > away_possession:
                highlights.append(f"{home_team_name} dominated possession with {home_possession}%")
            else:
                highlights.append(f"{away_team_name} dominated possession with {away_possession}%")

        # Shots summary
        if home_shots > away_shots + 5:
            highlights.append(
                f"{home_team_name} created more chances with {home_shots} shots ({home_shots_on_target} on target)")
        elif away_shots > home_shots + 5:
            highlights.append(
                f"{away_team_name} created more chances with {away_shots} shots ({away_shots_on_target} on target)")

        # Against the run of play?
        if home_shots > away_shots + 8 and final_score["away"] > final_score["home"]:
            highlights.append(f"{away_team_name} won against the run of play, despite having fewer shots")
        elif away_shots > home_shots + 8 and final_score["home"] > final_score["away"]:
            highlights.append(f"{home_team_name} won against the run of play, despite having fewer shots")

        # Goal scorers
        goals = [event for event in events if
                 event["type"] == "Goal" and event["detail"] in ["Normal Goal", "Penalty", "Own Goal"]]

        if goals:
            # Group goals by player
            scorers = {}
            for goal in goals:
                player_name = goal["player"]["name"]
                team_name = goal["team"]["name"]

                if player_name not in scorers:
                    scorers[player_name] = {"count": 0, "team": team_name}

                scorers[player_name]["count"] += 1

            # Highlight top scorers
            for player, data in scorers.items():
                if data["count"] > 1:
                    highlights.append(f"{player} ({data['team']}) scored {data['count']} goals")
                elif data["count"] == 1:
                    # Only mention single-goal scorers if there aren't too many
                    if len(scorers) <= 5:
                        highlights.append(f"{player} ({data['team']}) scored a goal")

        # Red cards
        red_cards = [event for event in events if event["type"] == "Card" and event["detail"] == "Red Card"]

        if red_cards:
            for card in red_cards:
                team_name = card["team"]["name"]
                player_name = card["player"]["name"]
                time = card["time"]["elapsed"]
                highlights.append(f"{player_name} ({team_name}) was sent off in the {time}' minute")

        # Standout player performances (if available)
        if players and len(players) > 0:
            top_rated_players = []
            for team_players in players:
                if "players" in team_players:
                    for player in team_players["players"]:
                        if "rating" in player and player["rating"]:
                            try:
                                rating = float(player["rating"])
                                if rating >= 8.0:  # Exceptional performance
                                    top_rated_players.append({
                                        "name": player["player"]["name"],
                                        "team": team_players["team"]["name"],
                                        "rating": rating
                                    })
                            except (ValueError, TypeError):
                                continue

            # Sort by rating (highest first)
            top_rated_players.sort(key=lambda x: x["rating"], reverse=True)

            # Highlight top players
            for player in top_rated_players[:2]:  # Limit to top 2 players
                highlights.append(
                    f"{player['name']} ({player['team']}) had an outstanding performance with a rating of {player['rating']}")

        return highlights

    @staticmethod
    async def analyze_betting_opportunities(fixture_id: int) -> Dict[str, Any]:
        """
        Analyze betting opportunities for a fixture.

        Args:
            fixture_id (int): Fixture ID

        Returns:
            Dict[str, Any]: Betting analysis
        """
        try:
            # Get fixture details
            fixture_data = await fixtures_service.get_fixture_by_id(fixture_id)
            if not fixture_data:
                return {"error": f"Fixture with ID {fixture_id} not found"}

            # Get odds
            odds_data = await fixtures_service.get_fixture_odds(fixture_id)

            # Get prediction
            prediction_data = await football_api_client.get_predictions(fixture=fixture_id)
            predictions = prediction_data.get("response", [{}])[0] if prediction_data.get("response") else {}

            # Get team IDs
            home_team_id = fixture_data["teams"]["home"]["id"]
            away_team_id = fixture_data["teams"]["away"]["id"]
            league_id = fixture_data["league"]["id"]
            season = fixture_data["league"]["season"]

            # Get team performance analyses
            home_team_analysis = await statistics_service.analyze_team_performance(
                home_team_id, league_id, season
            )

            away_team_analysis = await statistics_service.analyze_team_performance(
                away_team_id, league_id, season
            )

            # Generate AI-based betting analysis
            betting_analysis = await deepseek_client.analyze_betting_opportunities(
                fixture_data=fixture_data,
                odds_data=odds_data,
                team_stats={"home": home_team_analysis, "away": away_team_analysis},
                predictions=predictions
            )

            # Find value bets
            value_bets = []

            if odds_data:
                # For simple markets like 1X2
                home_win_prob = predictions.get("predictions", {}).get("percent", {}).get("home", "30")
                draw_prob = predictions.get("predictions", {}).get("percent", {}).get("draw", "30")
                away_win_prob = predictions.get("predictions", {}).get("percent", {}).get("away", "30")

                # Remove '%' and convert to float
                home_win_prob = float(home_win_prob.replace("%", "")) / 100
                draw_prob = float(draw_prob.replace("%", "")) / 100
                away_win_prob = float(away_win_prob.replace("%", "")) / 100

                for odds_group in odds_data:
                    if "bookmakers" in odds_group:
                        for bookmaker in odds_group["bookmakers"]:
                            for bet in bookmaker["bets"]:
                                if bet["name"] == "Match Winner":
                                    for value in bet["values"]:
                                        if value["value"] == "Home" and home_win_prob > 0:
                                            implied_prob = 1 / float(value["odd"])
                                            if home_win_prob > implied_prob * 1.1:  # 10% edge
                                                value_bets.append({
                                                    "market": "Match Winner",
                                                    "selection": "Home",
                                                    "team": fixture_data["teams"]["home"]["name"],
                                                    "odds": value["odd"],
                                                    "bookmaker": bookmaker["name"],
                                                    "implied_probability": round(implied_prob * 100, 2),
                                                    "estimated_probability": round(home_win_prob * 100, 2),
                                                    "edge": round((home_win_prob / implied_prob - 1) * 100, 2)
                                                })
                                        elif value["value"] == "Draw" and draw_prob > 0:
                                            implied_prob = 1 / float(value["odd"])
                                            if draw_prob > implied_prob * 1.1:  # 10% edge
                                                value_bets.append({
                                                    "market": "Match Winner",
                                                    "selection": "Draw",
                                                    "odds": value["odd"],
                                                    "bookmaker": bookmaker["name"],
                                                    "implied_probability": round(implied_prob * 100, 2),
                                                    "estimated_probability": round(draw_prob * 100, 2),
                                                    "edge": round((draw_prob / implied_prob - 1) * 100, 2)
                                                })
                                        elif value["value"] == "Away" and away_win_prob > 0:
                                            implied_prob = 1 / float(value["odd"])
                                            if away_win_prob > implied_prob * 1.1:  # 10% edge
                                                value_bets.append({
                                                    "market": "Match Winner",
                                                    "selection": "Away",
                                                    "team": fixture_data["teams"]["away"]["name"],
                                                    "odds": value["odd"],
                                                    "bookmaker": bookmaker["name"],
                                                    "implied_probability": round(implied_prob * 100, 2),
                                                    "estimated_probability": round(away_win_prob * 100, 2),
                                                    "edge": round((away_win_prob / implied_prob - 1) * 100, 2)
                                                })

            # Return compiled analysis
            return {
                "fixture_id": fixture_id,
                "home_team": fixture_data["teams"]["home"]["name"],
                "away_team": fixture_data["teams"]["away"]["name"],
                "kickoff_time": fixture_data["fixture"]["date"],
                "league": fixture_data["league"]["name"],
                "analysis": betting_analysis["analysis"],
                "value_bets": value_bets,
                "odds_data": odds_data,
                "prediction": predictions.get("predictions", {})
            }
        except Exception as e:
            logger.error(f"Error analyzing betting opportunities for fixture {fixture_id}: {e}")
            return {"error": str(e)}

    @staticmethod
    async def store_prediction_in_db(db: Session, fixture_id: int, prediction_data: Dict[str, Any]) -> Optional[
        Prediction]:
        """
        Store match prediction in the database.

        Args:
            db (Session): Database session
            fixture_id (int): Fixture ID
            prediction_data (Dict[str, Any]): Prediction data

        Returns:
            Optional[Prediction]: Stored prediction object or None if error
        """
        try:
            # Check if fixture exists in the database
            fixture = db.query(Fixture).filter(Fixture.api_id == fixture_id).first()
            if not fixture:
                logger.warning(f"Fixture with API ID {fixture_id} not found in database")
                return None

            # Check if prediction already exists for this fixture
            existing_prediction = db.query(Prediction).filter(Prediction.fixture_id == fixture.id).first()

            # Extract prediction values
            home_win_probability = prediction_data.get("home_win_probability", 0.0)
            draw_probability = prediction_data.get("draw_probability", 0.0)
            away_win_probability = prediction_data.get("away_win_probability", 0.0)

            under_15_probability = prediction_data.get("under_15_probability")
            over_15_probability = prediction_data.get("over_15_probability")
            under_25_probability = prediction_data.get("under_25_probability")
            over_25_probability = prediction_data.get("over_25_probability")

            btts_yes_probability = prediction_data.get("btts_yes_probability")
            btts_no_probability = prediction_data.get("btts_no_probability")

            advice = prediction_data.get("advice")

            if existing_prediction:
                # Update existing prediction
                existing_prediction.home_win_probability = home_win_probability
                existing_prediction.draw_probability = draw_probability
                existing_prediction.away_win_probability = away_win_probability

                if under_15_probability is not None:
                    existing_prediction.under_15_probability = under_15_probability
                if over_15_probability is not None:
                    existing_prediction.over_15_probability = over_15_probability
                if under_25_probability is not None:
                    existing_prediction.under_25_probability = under_25_probability
                if over_25_probability is not None:
                    existing_prediction.over_25_probability = over_25_probability

                if btts_yes_probability is not None:
                    existing_prediction.btts_yes_probability = btts_yes_probability
                if btts_no_probability is not None:
                    existing_prediction.btts_no_probability = btts_no_probability

                if advice:
                    existing_prediction.advice = advice

                db.commit()
                db.refresh(existing_prediction)
                return existing_prediction
            else:
                # Create new prediction
                new_prediction = Prediction(
                    fixture_id=fixture.id,
                    home_win_probability=home_win_probability,
                    draw_probability=draw_probability,
                    away_win_probability=away_win_probability,
                    under_15_probability=under_15_probability,
                    over_15_probability=over_15_probability,
                    under_25_probability=under_25_probability,
                    over_25_probability=over_25_probability,
                    btts_yes_probability=btts_yes_probability,
                    btts_no_probability=btts_no_probability,
                    advice=advice
                )

                db.add(new_prediction)
                db.commit()
                db.refresh(new_prediction)
                return new_prediction
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error storing prediction: {e}")
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing prediction in database: {e}")
            return None

    # Create a singleton instance
analysis_service = AnalysisService()