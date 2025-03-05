from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import Field

from ..db.database import get_db
from ..services.analysis_service import analysis_service
from ..services.fixtures_service import fixtures_service
from ..services.football_api import football_api_client
from ..services.deepseek_api import deepseek_client
from ..models import models
from . import schemas

# Create router
router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}},
)


@router.get("/match/{fixture_id}", response_model=schemas.MatchAnalysisResponse)
async def analyze_match(
        fixture_id: int = Path(..., description="Fixture ID"),
        db: Session = Depends(get_db)
):
    """
    Analyze a football match using AI and statistical models.
    Provides comprehensive analysis including team form, key statistics, tactical insights, and predictions.
    """
    try:
        analysis = await analysis_service.analyze_fixture(fixture_id)
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        return {"response": analysis}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing match {fixture_id}: {str(e)}")


@router.get("/pre-match/{fixture_id}", response_model=schemas.PreMatchAnalysisResponse)
async def get_pre_match_analysis(
        fixture_id: int = Path(..., description="Fixture ID"),
        db: Session = Depends(get_db)
):
    """
    Get pre-match analysis for a specific fixture.
    Includes team form analysis, key statistical comparisons, historical context, and match predictions.
    """
    try:
        # Get fixture details first
        fixture_data = await fixtures_service.get_fixture_by_id(fixture_id)
        if not fixture_data:
            raise HTTPException(status_code=404, detail=f"Fixture with ID {fixture_id} not found")

        # Only allow pre-match analysis for fixtures that haven't started yet
        if fixture_data["fixture"]["status"]["short"] not in ["NS", "TBD", "PST"]:
            raise HTTPException(status_code=400,
                                detail="Pre-match analysis is only available for fixtures that haven't started yet")

        # Get required data for analysis
        home_team_id = fixture_data["teams"]["home"]["id"]
        away_team_id = fixture_data["teams"]["away"]["id"]
        league_id = fixture_data["league"]["id"]
        season = fixture_data["league"]["season"]

        # Get team analyses
        home_team_analysis = await analysis_service.analyze_team_performance(home_team_id, league_id, season)
        away_team_analysis = await analysis_service.analyze_team_performance(away_team_id, league_id, season)

        # Get head-to-head matches
        h2h_matches = await fixtures_service.get_head_to_head(home_team_id, away_team_id, last=10)

        # Build data for pre-match analysis
        analysis_data = {
            "fixture": fixture_data,
            "home_team_analysis": home_team_analysis,
            "away_team_analysis": away_team_analysis,
            "head_to_head": h2h_matches,
            "expected_goals": {
                "home_xg": None,
                "away_xg": None
            }
        }

        # Generate analysis
        analysis = await analysis_service.generate_pre_match_analysis(analysis_data)

        return {"response": analysis}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error generating pre-match analysis for fixture {fixture_id}: {str(e)}")


@router.get("/in-play/{fixture_id}", response_model=schemas.InPlayAnalysisResponse)
async def get_in_play_analysis(
        fixture_id: int = Path(..., description="Fixture ID"),
        db: Session = Depends(get_db)
):
    """
    Get in-play analysis for a fixture currently in progress.
    Includes match momentum, live statistics, key observations, and tactical insights.
    """
    try:
        # Get fixture details first
        fixture_data = await fixtures_service.get_fixture_by_id(fixture_id)
        if not fixture_data:
            raise HTTPException(status_code=404, detail=f"Fixture with ID {fixture_id} not found")

        # Only allow in-play analysis for fixtures that are currently live
        if fixture_data["fixture"]["status"]["short"] not in ["1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT", "LIVE"]:
            raise HTTPException(status_code=400,
                                detail="In-play analysis is only available for fixtures currently in progress")

        # Get required data for analysis
        home_team_id = fixture_data["teams"]["home"]["id"]
        away_team_id = fixture_data["teams"]["away"]["id"]
        league_id = fixture_data["league"]["id"]
        season = fixture_data["league"]["season"]

        # Get team analyses
        home_team_analysis = await analysis_service.analyze_team_performance(home_team_id, league_id, season)
        away_team_analysis = await analysis_service.analyze_team_performance(away_team_id, league_id, season)

        # Get match statistics
        statistics = await fixtures_service.get_fixture_statistics(fixture_id)

        # Get match events
        events = await fixtures_service.get_fixture_events(fixture_id)

        # Calculate expected goals
        home_xg, away_xg = await analysis_service.calculate_fixture_xg(fixture_id)

        # Build data for in-play analysis
        analysis_data = {
            "fixture": fixture_data,
            "home_team_analysis": home_team_analysis,
            "away_team_analysis": away_team_analysis,
            "statistics": statistics,
            "events": events,
            "expected_goals": {
                "home_xg": home_xg,
                "away_xg": away_xg
            }
        }

        # Generate analysis
        analysis = await analysis_service.generate_in_play_analysis(analysis_data)

        return {"response": analysis}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error generating in-play analysis for fixture {fixture_id}: {str(e)}")


@router.get("/post-match/{fixture_id}", response_model=schemas.PostMatchAnalysisResponse)
async def get_post_match_analysis(
        fixture_id: int = Path(..., description="Fixture ID"),
        db: Session = Depends(get_db)
):
    """
    Get post-match analysis for a completed fixture.
    Includes comprehensive performance analysis, key statistics, tactical breakdowns, and standout player performances.
    """
    try:
        # Get fixture details first
        fixture_data = await fixtures_service.get_fixture_by_id(fixture_id)
        if not fixture_data:
            raise HTTPException(status_code=404, detail=f"Fixture with ID {fixture_id} not found")

        # Only allow post-match analysis for fixtures that have been completed
        if fixture_data["fixture"]["status"]["short"] not in ["FT", "AET", "PEN", "AWD", "WO"]:
            raise HTTPException(status_code=400, detail="Post-match analysis is only available for completed fixtures")

        # Get required data for analysis
        home_team_id = fixture_data["teams"]["home"]["id"]
        away_team_id = fixture_data["teams"]["away"]["id"]
        league_id = fixture_data["league"]["id"]
        season = fixture_data["league"]["season"]

        # Get team analyses
        home_team_analysis = await analysis_service.analyze_team_performance(home_team_id, league_id, season)
        away_team_analysis = await analysis_service.analyze_team_performance(away_team_id, league_id, season)

        # Get match statistics
        statistics = await fixtures_service.get_fixture_statistics(fixture_id)

        # Get match events
        events = await fixtures_service.get_fixture_events(fixture_id)

        # Get player statistics
        players = await fixtures_service.get_fixture_players(fixture_id)

        # Calculate expected goals
        home_xg, away_xg = await analysis_service.calculate_fixture_xg(fixture_id)

        # Build data for post-match analysis
        analysis_data = {
            "fixture": fixture_data,
            "home_team_analysis": home_team_analysis,
            "away_team_analysis": away_team_analysis,
            "statistics": statistics,
            "events": events,
            "players": players,
            "expected_goals": {
                "home_xg": home_xg,
                "away_xg": away_xg
            }
        }

        # Generate analysis
        analysis = await analysis_service.generate_post_match_analysis(analysis_data)

        return {"response": analysis}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error generating post-match analysis for fixture {fixture_id}: {str(e)}")


@router.get("/predict/{fixture_id}", response_model=schemas.PredictionResponse)
async def predict_match(
        fixture_id: int = Path(..., description="Fixture ID"),
        db: Session = Depends(get_db)
):
    """
    Predict the outcome of a match using AI and statistical models.
    Returns probabilities for match outcomes, expected goals, and other key predictions.
    """
    try:
        # Get fixture details first
        fixture_data = await fixtures_service.get_fixture_by_id(fixture_id)
        if not fixture_data:
            raise HTTPException(status_code=404, detail=f"Fixture with ID {fixture_id} not found")

        # Get team information
        home_team_id = fixture_data["teams"]["home"]["id"]
        away_team_id = fixture_data["teams"]["away"]["id"]
        league_id = fixture_data["league"]["id"]
        season = fixture_data["league"]["season"]

        # Get team analyses
        home_team_analysis = await analysis_service.analyze_team_performance(home_team_id, league_id, season)
        away_team_analysis = await analysis_service.analyze_team_performance(away_team_id, league_id, season)

        # Get head-to-head matches
        h2h_matches = await fixtures_service.get_head_to_head(home_team_id, away_team_id, last=10)

        # Generate prediction
        prediction = await analysis_service.predict_match_result(
            fixture_id,
            home_team_id,
            away_team_id,
            home_team_analysis,
            away_team_analysis,
            h2h_matches
        )

        # Store prediction in database
        await analysis_service.store_prediction_in_db(db, fixture_id, prediction)

        return prediction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting match {fixture_id}: {str(e)}")


@router.get("/betting/{fixture_id}", response_model=schemas.BettingAnalysisResponse)
async def analyze_betting_opportunities(
        fixture_id: int = Path(..., description="Fixture ID"),
        db: Session = Depends(get_db)
):
    """
    Analyze betting opportunities for a specific fixture.
    Identifies potential value bets by comparing model predictions with bookmaker odds.
    """
    try:
        betting_analysis = await analysis_service.analyze_betting_opportunities(fixture_id)
        if "error" in betting_analysis:
            raise HTTPException(status_code=500, detail=betting_analysis["error"])
        return {"response": betting_analysis}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error analyzing betting opportunities for fixture {fixture_id}: {str(e)}")


@router.get("/value-bets", response_model=schemas.ValueBetsResponse)
async def get_value_bets(
        league_id: Optional[int] = Query(None, description="Filter by league ID"),
        date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
        min_edge: float = Query(0.05, description="Minimum edge percentage (as decimal, e.g., 0.05 for 5%)"),
        max_results: int = Query(10, description="Maximum number of results to return"),
        db: Session = Depends(get_db)
):
    """
    Get list of value betting opportunities across multiple fixtures.
    Value bets are identified when the model's probability differs significantly from bookmaker implied odds.
    """
    try:
        # Get fixtures based on filters
        fixtures = []
        if league_id:
            # Get current season
            league_data = await football_api_client.get_leagues(id=league_id)
            if league_data.get("response"):
                season = league_data["response"][0]["seasons"][0]["year"]
                fixtures_data = await football_api_client.get_fixtures(league=league_id, season=season)
                fixtures.extend(fixtures_data.get("response", []))
        elif date:
            fixtures_data = await football_api_client.get_fixtures(date=date)
            fixtures.extend(fixtures_data.get("response", []))
        else:
            # Default to today's fixtures
            today = datetime.now().strftime("%Y-%m-%d")
            fixtures_data = await football_api_client.get_fixtures(date=today)
            fixtures.extend(fixtures_data.get("response", []))

        # Filter to only include upcoming fixtures
        upcoming_fixtures = [
            fixture for fixture in fixtures
            if fixture["fixture"]["status"]["short"] in ["NS", "TBD", "PST"]
        ]

        # Limit to a reasonable number for processing
        fixtures_to_analyze = upcoming_fixtures[:min(50, len(upcoming_fixtures))]

        value_bets = []
        for fixture in fixtures_to_analyze:
            fixture_id = fixture["fixture"]["id"]
            try:
                # Analyze betting opportunities for this fixture
                betting_analysis = await analysis_service.analyze_betting_opportunities(fixture_id)

                # Add value bets that meet the criteria
                if "value_bets" in betting_analysis:
                    for bet in betting_analysis["value_bets"]:
                        if bet.get("edge", 0) >= min_edge * 100:  # Convert min_edge to percentage
                            value_bets.append({
                                **bet,
                                "fixture_id": fixture_id,
                                "league": fixture["league"],
                                "teams": fixture["teams"],
                                "match_date": fixture["fixture"]["date"]
                            })
            except Exception as e:
                # Continue with other fixtures even if one fails
                print(f"Error analyzing fixture {fixture_id}: {str(e)}")
                continue

        # Sort by edge (highest first) and limit results
        value_bets.sort(key=lambda x: x.get("edge", 0), reverse=True)
        value_bets = value_bets[:max_results]

        return {"response": value_bets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching value bets: {str(e)}")


@router.post("/report", response_model=schemas.AnalysisReportResponse)
async def generate_analysis_report(
        request: schemas.AnalysisReportRequest = Body(...),
        db: Session = Depends(get_db)
):
    """
    Generate a comprehensive analysis report for a match using DeepSeek AI.
    The report can include pre-match analysis, in-play analysis, or post-match analysis based on the request.
    """
    try:
        # Get fixture details
        fixture_data = await fixtures_service.get_fixture_by_id(request.fixture_id)
        if not fixture_data:
            raise HTTPException(status_code=404, detail=f"Fixture with ID {request.fixture_id} not found")

        # Get team information
        home_team_id = fixture_data["teams"]["home"]["id"]
        away_team_id = fixture_data["teams"]["away"]["id"]
        league_id = fixture_data["league"]["id"]
        season = fixture_data["league"]["season"]

        # Gather data needed for the report
        data = {
            "fixture": fixture_data,
            "report_type": request.report_type
        }

        # Add additional data based on report type
        if request.report_type in ["pre-match", "comprehensive"]:
            # Get team analyses
            home_team_analysis = await analysis_service.analyze_team_performance(home_team_id, league_id, season)
            away_team_analysis = await analysis_service.analyze_team_performance(away_team_id, league_id, season)

            # Get head-to-head matches
            h2h_matches = await fixtures_service.get_head_to_head(home_team_id, away_team_id, last=10)

            data["home_team_analysis"] = home_team_analysis
            data["away_team_analysis"] = away_team_analysis
            data["head_to_head"] = h2h_matches

        if request.report_type in ["in-play", "post-match", "comprehensive"]:
            # Get match statistics
            statistics = await fixtures_service.get_fixture_statistics(request.fixture_id)

            # Get match events
            events = await fixtures_service.get_fixture_events(request.fixture_id)

            # Calculate expected goals
            home_xg, away_xg = await analysis_service.calculate_fixture_xg(request.fixture_id)

            data["statistics"] = statistics
            data["events"] = events
            data["expected_goals"] = {
                "home_xg": home_xg,
                "away_xg": away_xg
            }

        if request.report_type in ["post-match", "comprehensive"]:
            # Get player statistics
            players = await fixtures_service.get_fixture_players(request.fixture_id)
            data["players"] = players

        # Generate the AI analysis
        analysis_prompt = f"""
        Generate a comprehensive {request.report_type} analysis report for the match between {fixture_data['teams']['home']['name']} and {fixture_data['teams']['away']['name']}.

        Match Information:
        - Competition: {fixture_data['league']['name']} {season}
        - Date: {fixture_data['fixture']['date']}
        - Status: {fixture_data['fixture']['status']['long']}

        {request.additional_instructions or ""}

        Include the following sections in your analysis:
        1. Match Overview
        2. Team Analysis
        3. Key Statistics
        4. Tactical Breakdown
        5. Key Performers
        6. Conclusion and Insights
        """

        # Call DeepSeek API to generate the report
        ai_response = await deepseek_client.chat_with_ai(
            query=analysis_prompt,
            context=data
        )

        return {
            "response": {
                "report": ai_response["response"],
                "fixture_id": request.fixture_id,
                "home_team": fixture_data["teams"]["home"]["name"],
                "away_team": fixture_data["teams"]["away"]["name"],
                "report_type": request.report_type
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis report: {str(e)}")


@router.get("/team/{team_id}/form", response_model=schemas.TeamFormAnalysisResponse)
async def analyze_team_form(
        team_id: int = Path(..., description="Team ID"),
        league_id: Optional[int] = Query(None, description="League ID"),
        season: Optional[int] = Query(None, description="Season (e.g., 2023)"),
        last_matches: int = Query(10, description="Number of last matches to analyze"),
        db: Session = Depends(get_db)
):
    """
    Analyze the current form of a specific team.
    Includes performance metrics, trends, and insights based on recent matches.
    """
    try:
        # If league_id and season are not provided, get the current league and season for the team
        if not league_id or not season:
            # Get team information to determine primary league
            team_data = await football_api_client.get_teams(id=team_id)
            if not team_data.get("response"):
                raise HTTPException(status_code=404, detail=f"Team with ID {team_id} not found")

            # Get current season
            current_year = datetime.now().year
            current_month = datetime.now().month

            # If current month is between January and July, use the previous year as season
            season = current_year if current_month > 7 else current_year - 1

            # Find the main league for this team in this season
            team_leagues = await football_api_client.get_leagues(team=team_id, season=season)
            if not team_leagues.get("response"):
                raise HTTPException(status_code=404, detail=f"No leagues found for team {team_id} in season {season}")

            # Use the first league (typically the main league)
            league_id = team_leagues["response"][0]["league"]["id"]

        # Get team performance analysis
        team_analysis = await analysis_service.analyze_team_performance(team_id, league_id, season)

        # Get recent matches
        team_fixtures = await fixtures_service.get_fixtures_by_team(team_id, last=last_matches)
        recent_matches = team_fixtures.get("past", [])

        # Get team statistics for matches
        match_stats = await analysis_service.get_team_match_statistics(team_id, last_matches)

        # Calculate form metrics
        form_string = ""
        points_trend = []
        goals_scored_trend = []
        goals_conceded_trend = []
        xg_trend = []
        possession_trend = []

        for match in recent_matches:
            # Create form string (W, D, L)
            result = ""
            if match["teams"]["home"]["id"] == team_id:
                result = "W" if match["teams"]["home"]["winner"] else "L" if match["teams"]["away"]["winner"] else "D"
            else:
                result = "W" if match["teams"]["away"]["winner"] else "L" if match["teams"]["home"]["winner"] else "D"

            form_string += result

            # Calculate points from result
            points = 3 if result == "W" else 1 if result == "D" else 0
            points_trend.append(points)

            # Goals scored and conceded
            if match["teams"]["home"]["id"] == team_id:
                goals_scored_trend.append(match["goals"]["home"] or 0)
                goals_conceded_trend.append(match["goals"]["away"] or 0)
            else:
                goals_scored_trend.append(match["goals"]["away"] or 0)
                goals_conceded_trend.append(match["goals"]["home"] or 0)

            # XG and possession will be added if available in match_stats

        # Prepare response
        team_form_analysis = {
            "team_id": team_id,
            "team_name": team_analysis.get("team_name", "Unknown"),
            "league_id": league_id,
            "league_name": team_analysis.get("league_name", "Unknown"),
            "season": season,
            "form_string": form_string,
            "points_last_5": sum(points_trend[:5]),
            "points_trend": points_trend,
            "goals_scored_trend": goals_scored_trend,
            "goals_conceded_trend": goals_conceded_trend,
            "recent_matches": recent_matches[:5],  # Include full match data for last 5 matches
            "match_stats": match_stats,
            "team_analysis": team_analysis
        }

        return {"response": team_form_analysis}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing team form: {str(e)}")


@router.get("/compare/{team1_id}/{team2_id}", response_model=schemas.TeamComparisonResponse)
async def compare_teams(
        team1_id: int = Path(..., description="First team ID"),
        team2_id: int = Path(..., description="Second team ID"),
        league_id: Optional[int] = Query(None, description="League ID"),
        season: Optional[int] = Query(None, description="Season (e.g., 2023)"),
        db: Session = Depends(get_db)
):
    """
    Compare two teams based on performance metrics and head-to-head record.
    Provides detailed statistics comparison and analysis of team strengths and weaknesses.
    """
    try:
        # If league_id and season are not provided, get the current league and season
        if not league_id or not season:
            # Get current season
            current_year = datetime.now().year
            current_month = datetime.now().month

            # If current month is between January and July, use the previous year as season
            season = current_year if current_month > 7 else current_year - 1

            # Find common leagues for both teams
            team1_leagues = await football_api_client.get_leagues(team=team1_id, season=season)
            team2_leagues = await football_api_client.get_leagues(team=team2_id, season=season)

            if not team1_leagues.get("response") or not team2_leagues.get("response"):
                raise HTTPException(status_code=404, detail=f"No leagues found for both teams in season {season}")

            # Find a common league
            team1_league_ids = [league["league"]["id"] for league in team1_leagues["response"]]
            team2_league_ids = [league["league"]["id"] for league in team2_leagues["response"]]

            common_leagues = set(team1_league_ids).intersection(set(team2_league_ids))
            if not common_leagues:
                raise HTTPException(status_code=404,
                                    detail=f"No common leagues found for both teams in season {season}")

            # Use the first common league
            league_id = list(common_leagues)[0]

        # Get team comparison
        team_comparison = await analysis_service.compare_teams(team1_id, team2_id, league_id, season)

        return {"response": team_comparison}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing teams: {str(e)}")