import logging
import math
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def poisson_probability(mean: float, k: int) -> float:
    """
    Calculate Poisson probability.

    Args:
        mean (float): Mean/lambda value
        k (int): Number of occurrences

    Returns:
        float: Probability
    """
    return (math.exp(-mean) * mean ** k) / math.factorial(k)


def calculate_match_probabilities(home_strength: float, away_strength: float) -> Dict[str, float]:
    """
    Calculate match outcome probabilities using Poisson distribution.

    Args:
        home_strength (float): Home team attacking strength
        away_strength (float): Away team attacking strength

    Returns:
        Dict[str, float]: Probabilities for home win, draw, and away win
    """
    home_win_prob = 0.0
    draw_prob = 0.0
    away_win_prob = 0.0

    # Typically consider scores up to 0-0, 0-1, ..., 7-7
    for i in range(8):  # home goals
        for j in range(8):  # away goals
            p = poisson_probability(home_strength, i) * poisson_probability(away_strength, j)
            if i > j:
                home_win_prob += p
            elif i == j:
                draw_prob += p
            else:
                away_win_prob += p

    return {
        "home_win": home_win_prob,
        "draw": draw_prob,
        "away_win": away_win_prob
    }


def calculate_value_bet(actual_odds: float, calculated_probability: float) -> Dict[str, Any]:
    """
    Calculate if a bet has value.

    Args:
        actual_odds (float): Bookmaker odds
        calculated_probability (float): Our calculated probability

    Returns:
        Dict[str, Any]: Value bet information
    """
    if calculated_probability <= 0:
        return {"value": False, "ev": 0, "ratio": 0}

    # Convert decimal odds to implied probability
    implied_probability = 1 / actual_odds

    # Calculate expected value
    expected_value = (actual_odds * calculated_probability) - 1

    # Calculate value ratio (>1 means value bet)
    value_ratio = calculated_probability / implied_probability

    return {
        "value": value_ratio > 1.05,  # 5% threshold for value
        "ev": expected_value,
        "ratio": value_ratio,
        "actual_odds": actual_odds,
        "implied_probability": implied_probability,
        "calculated_probability": calculated_probability
    }


def calculate_elo_ratings(team1_elo: float, team2_elo: float, team1_score: int, team2_score: int,
                          k_factor: float = 40) -> Tuple[float, float]:
    """
    Calculate updated Elo ratings after a match.

    Args:
        team1_elo (float): Team 1's current Elo rating
        team2_elo (float): Team 2's current Elo rating
        team1_score (int): Team 1's score
        team2_score (int): Team 2's score
        k_factor (float): K-factor controlling rating changes

    Returns:
        Tuple[float, float]: Updated Elo ratings for team1 and team2
    """
    # Calculate expected outcome
    expected_team1 = 1 / (1 + 10 ** ((team2_elo - team1_elo) / 400))
    expected_team2 = 1 - expected_team1

    # Determine actual outcome
    if team1_score > team2_score:
        actual_team1 = 1
        actual_team2 = 0
    elif team1_score < team2_score:
        actual_team1 = 0
        actual_team2 = 1
    else:
        actual_team1 = 0.5
        actual_team2 = 0.5

    # Calculate new ratings
    new_team1_elo = team1_elo + k_factor * (actual_team1 - expected_team1)
    new_team2_elo = team2_elo + k_factor * (actual_team2 - expected_team2)

    return new_team1_elo, new_team2_elo


def calculate_xg_from_shots(shots_data: List[Dict[str, Any]]) -> float:
    """
    Calculate expected goals (xG) from shot data.

    Args:
        shots_data (List[Dict[str, Any]]): List of shots with position and info

    Returns:
        float: Expected goals value
    """
    # This is a simplified model
    total_xg = 0.0

    for shot in shots_data:
        # Start with base probability
        shot_xg = 0.01

        # Adjust based on distance
        if "distance" in shot:
            distance = shot["distance"]
            if distance < 6:
                shot_xg = 0.3
            elif distance < 12:
                shot_xg = 0.1
            elif distance < 18:
                shot_xg = 0.05
            else:
                shot_xg = 0.02

        # Adjust based on angle
        if "angle" in shot:
            angle = shot["angle"]  # 0-90 degrees
            angle_factor = angle / 90.0  # 0-1
            shot_xg *= angle_factor

        # Adjust for header
        if shot.get("header", False):
            shot_xg *= 0.7

        # Adjust for body part
        if "body_part" in shot:
            if shot["body_part"] == "left_foot":
                shot_xg *= 0.9
            elif shot["body_part"] == "right_foot":
                shot_xg *= 1.0
            elif shot["body_part"] == "head":
                shot_xg *= 0.7
            else:
                shot_xg *= 0.6

        total_xg += shot_xg

    return total_xg


def parse_fixtures_by_date(fixtures_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group fixtures by date.

    Args:
        fixtures_data (List[Dict[str, Any]]): List of fixtures

    Returns:
        Dict[str, List[Dict[str, Any]]]: Fixtures grouped by date
    """
    result = {}

    for fixture in fixtures_data:
        if "fixture" in fixture and "date" in fixture["fixture"]:
            date_str = fixture["fixture"]["date"].split("T")[0]  # Get yyyy-mm-dd part

            if date_str not in result:
                result[date_str] = []

            result[date_str].append(fixture)

    return result


def parse_fixtures_by_league(fixtures_data: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    Group fixtures by league ID.

    Args:
        fixtures_data (List[Dict[str, Any]]): List of fixtures

    Returns:
        Dict[int, Dict[str, Any]]: Fixtures grouped by league ID
    """
    result = {}

    for fixture in fixtures_data:
        if "league" in fixture and "id" in fixture["league"]:
            league_id = fixture["league"]["id"]

            if league_id not in result:
                result[league_id] = {
                    "league": fixture["league"],
                    "fixtures": []
                }

            result[league_id]["fixtures"].append(fixture)

    return result


def calculate_team_form(recent_fixtures: List[Dict[str, Any]], team_id: int) -> str:
    """
    Calculate team form string (e.g., "WDLWW") based on recent fixtures.

    Args:
        recent_fixtures (List[Dict[str, Any]]): List of recent fixtures
        team_id (int): ID of the team

    Returns:
        str: Form string (W=win, D=draw, L=loss)
    """
    form = ""

    # Process fixtures in chronological order (oldest first)
    sorted_fixtures = sorted(recent_fixtures, key=lambda x: x["fixture"]["timestamp"])

    for fixture in sorted_fixtures:
        if fixture["teams"]["home"]["id"] == team_id:
            # Team played at home
            if fixture["teams"]["home"]["winner"]:
                form += "W"
            elif fixture["teams"]["away"]["winner"]:
                form += "L"
            else:
                form += "D"
        elif fixture["teams"]["away"]["id"] == team_id:
            # Team played away
            if fixture["teams"]["away"]["winner"]:
                form += "W"
            elif fixture["teams"]["home"]["winner"]:
                form += "L"
            else:
                form += "D"

    return form


def calculate_ppda(passes: int, defensive_actions: int) -> float:
    """
    Calculate PPDA (Passes Per Defensive Action) - lower is better.

    Args:
        passes (int): Number of passes by opponent
        defensive_actions (int): Number of defensive actions (tackles + interceptions)

    Returns:
        float: PPDA value
    """
    if defensive_actions == 0:
        return float('inf')

    return passes / defensive_actions


def get_upcoming_fixtures(fixtures_data: List[Dict[str, Any]], days: int = 7) -> List[Dict[str, Any]]:
    """
    Get fixtures scheduled for the upcoming days.

    Args:
        fixtures_data (List[Dict[str, Any]]): List of fixtures
        days (int): Number of days to look ahead

    Returns:
        List[Dict[str, Any]]: List of upcoming fixtures
    """
    now = datetime.now()
    end_date = now + timedelta(days=days)

    upcoming = []

    for fixture in fixtures_data:
        if "fixture" in fixture and "date" in fixture["fixture"]:
            fixture_date = datetime.fromisoformat(fixture["fixture"]["date"].replace("Z", "+00:00"))

            if now <= fixture_date <= end_date:
                upcoming.append(fixture)

    return upcoming


def identify_value_bets(odds_data: List[Dict[str, Any]], prediction_data: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Identify value bets by comparing bookmaker odds to our calculated probabilities.

    Args:
        odds_data (List[Dict[str, Any]]): Bookmaker odds
        prediction_data (Dict[str, float]): Our calculated probabilities

    Returns:
        List[Dict[str, Any]]: List of potential value bets
    """
    value_bets = []

    for market in odds_data:
        # Handle 1X2 market
        if market["name"] == "Match Winner" or market["name"] == "1X2":
            for bookmaker in market["bookmakers"]:
                for bet in bookmaker["bets"]:
                    # Home win
                    if bet["value"] == "Home" and prediction_data.get("home_win_probability"):
                        value_info = calculate_value_bet(
                            float(bet["odd"]),
                            prediction_data["home_win_probability"]
                        )
                        if value_info["value"]:
                            value_bets.append({
                                "market": market["name"],
                                "bookmaker": bookmaker["name"],
                                "bet": "Home Win",
                                "odds": bet["odd"],
                                "value_ratio": value_info["ratio"],
                                "expected_value": value_info["ev"]
                            })

                    # Draw
                    elif bet["value"] == "Draw" and prediction_data.get("draw_probability"):
                        value_info = calculate_value_bet(
                            float(bet["odd"]),
                            prediction_data["draw_probability"]
                        )
                        if value_info["value"]:
                            value_bets.append({
                                "market": market["name"],
                                "bookmaker": bookmaker["name"],
                                "bet": "Draw",
                                "odds": bet["odd"],
                                "value_ratio": value_info["ratio"],
                                "expected_value": value_info["ev"]
                            })

                    # Away win
                    elif bet["value"] == "Away" and prediction_data.get("away_win_probability"):
                        value_info = calculate_value_bet(
                            float(bet["odd"]),
                            prediction_data["away_win_probability"]
                        )
                        if value_info["value"]:
                            value_bets.append({
                                "market": market["name"],
                                "bookmaker": bookmaker["name"],
                                "bet": "Away Win",
                                "odds": bet["odd"],
                                "value_ratio": value_info["ratio"],
                                "expected_value": value_info["ev"]
                            })

        # Handle Over/Under 2.5 market
        elif market["name"] == "Over/Under" or "goals" in market["name"].lower():
            for bookmaker in market["bookmakers"]:
                for bet in bookmaker["bets"]:
                    # Over 2.5
                    if bet["value"] == "Over 2.5" and prediction_data.get("over_25_probability"):
                        value_info = calculate_value_bet(
                            float(bet["odd"]),
                            prediction_data["over_25_probability"]
                        )
                        if value_info["value"]:
                            value_bets.append({
                                "market": market["name"],
                                "bookmaker": bookmaker["name"],
                                "bet": "Over 2.5 Goals",
                                "odds": bet["odd"],
                                "value_ratio": value_info["ratio"],
                                "expected_value": value_info["ev"]
                            })

                    # Under 2.5
                    elif bet["value"] == "Under 2.5" and prediction_data.get("under_25_probability"):
                        value_info = calculate_value_bet(
                            float(bet["odd"]),
                            prediction_data["under_25_probability"]
                        )
                        if value_info["value"]:
                            value_bets.append({
                                "market": market["name"],
                                "bookmaker": bookmaker["name"],
                                "bet": "Under 2.5 Goals",
                                "odds": bet["odd"],
                                "value_ratio": value_info["ratio"],
                                "expected_value": value_info["ev"]
                            })

    # Sort by expected value, descending
    value_bets.sort(key=lambda x: x["expected_value"], reverse=True)

    return value_bets


def parse_live_data(live_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and normalize live match data.

    Args:
        live_data (Dict[str, Any]): Raw live match data

    Returns:
        Dict[str, Any]: Normalized live data with key metrics
    """
    result = {
        "match_id": live_data.get("fixture", {}).get("id"),
        "status": live_data.get("fixture", {}).get("status", {}).get("short"),
        "elapsed": live_data.get("fixture", {}).get("status", {}).get("elapsed"),
        "home_team": live_data.get("teams", {}).get("home", {}).get("name"),
        "away_team": live_data.get("teams", {}).get("away", {}).get("name"),
        "score": {
            "home": live_data.get("goals", {}).get("home"),
            "away": live_data.get("goals", {}).get("away")
        },
        "statistics": {},
        "events": []
    }

    # Parse statistics if available
    if "statistics" in live_data:
        for team_stats in live_data["statistics"]:
            team_name = team_stats.get("team", {}).get("name")
            result["statistics"][team_name] = {}

            for stat in team_stats.get("statistics", []):
                stat_name = stat.get("type")
                stat_value = stat.get("value")

                if stat_name and stat_value is not None:
                    result["statistics"][team_name][stat_name] = stat_value

    # Parse events if available
    if "events" in live_data:
        for event in live_data["events"]:
            result["events"].append({
                "time": event.get("time", {}).get("elapsed"),
                "team": event.get("team", {}).get("name"),
                "type": event.get("type"),
                "detail": event.get("detail"),
                "player": event.get("player", {}).get("name")
            })

    return result