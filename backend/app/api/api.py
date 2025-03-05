from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..db.database import get_db
from ..services.football_api import football_api_client
from ..services.deepseek_api import deepseek_client
from . import schemas
from ..models import models

# Create API router
api_router = APIRouter()


# Health check endpoint
@api_router.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}


# Football data endpoints

@api_router.get("/competitions", response_model=schemas.CompetitionsResponse, tags=["competitions"])
async def get_competitions(
        id: Optional[int] = None,
        name: Optional[str] = None,
        country: Optional[str] = None,
        season: Optional[int] = None,
        team: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """
    Get list of competitions (leagues and cups).
    """
    try:
        response = await football_api_client.get_leagues(
            id=id, name=name, country=country, season=season, team=team
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/seasons", response_model=schemas.SeasonsResponse, tags=["competitions"])
async def get_seasons():
    """
    Get available seasons.
    """
    try:
        response = await football_api_client.get_seasons()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/teams", response_model=schemas.TeamsResponse, tags=["teams"])
async def get_teams(
        id: Optional[int] = None,
        name: Optional[str] = None,
        league: Optional[int] = None,
        season: Optional[int] = None,
        country: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """
    Get teams information.
    """
    try:
        response = await football_api_client.get_teams(
            id=id, name=name, league=league, season=season, country=country
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/teams/{team_id}/statistics", response_model=schemas.TeamStatisticsResponse, tags=["teams"])
async def get_team_statistics(
        team_id: int,
        league_id: int,
        season: int,
        db: Session = Depends(get_db)
):
    """
    Get team statistics for a specific league and season.
    """
    try:
        response = await football_api_client.get_team_statistics(
            league=league_id, season=season, team=team_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/fixtures", response_model=schemas.FixturesResponse, tags=["fixtures"])
async def get_fixtures(
        id: Optional[int] = None,
        date: Optional[str] = None,
        league: Optional[int] = None,
        season: Optional[int] = None,
        team: Optional[int] = None,
        live: Optional[str] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """
    Get fixtures information.
    """
    try:
        response = await football_api_client.get_fixtures(
            id=id, date=date, league=league, season=season, team=team, live=live, status=status
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/fixtures/{fixture_id}/statistics", response_model=schemas.FixtureStatisticsResponse,
                tags=["fixtures"])
async def get_fixture_statistics(
        fixture_id: int,
        team: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """
    Get statistics for a specific fixture.
    """
    try:
        response = await football_api_client.get_fixture_statistics(
            fixture=fixture_id, team=team
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/fixtures/{fixture_id}/events", response_model=schemas.FixtureEventsResponse, tags=["fixtures"])
async def get_fixture_events(
        fixture_id: int,
        db: Session = Depends(get_db)
):
    """
    Get events for a specific fixture.
    """
    try:
        response = await football_api_client.get_fixture_events(
            fixture=fixture_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/fixtures/{fixture_id}/lineups", response_model=schemas.FixtureLineupsResponse, tags=["fixtures"])
async def get_fixture_lineups(
        fixture_id: int,
        db: Session = Depends(get_db)
):
    """
    Get lineups for a specific fixture.
    """
    try:
        response = await football_api_client.get_fixture_lineups(
            fixture=fixture_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/fixtures/{fixture_id}/players", response_model=schemas.FixturePlayersResponse, tags=["fixtures"])
async def get_fixture_players(
        fixture_id: int,
        db: Session = Depends(get_db)
):
    """
    Get player statistics for a specific fixture.
    """
    try:
        response = await football_api_client.get_fixture_players(
            fixture=fixture_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/fixtures/headtohead/{team1}/{team2}", response_model=schemas.HeadToHeadResponse, tags=["fixtures"])
async def get_head_to_head(
        team1: int,
        team2: int,
        last: Optional[int] = 10,
        db: Session = Depends(get_db)
):
    """
    Get head to head matches between two teams.
    """
    try:
        response = await football_api_client.get_fixtures(
            h2h=f"{team1}-{team2}",
            last=last
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/standings", response_model=schemas.StandingsResponse, tags=["standings"])
async def get_standings(
        league: int,
        season: int,
        team: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """
    Get standings for a specific league and season.
    """
    try:
        response = await football_api_client.get_standings(
            league=league, season=season, team=team
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/predictions/{fixture_id}", response_model=schemas.PredictionsResponse, tags=["predictions"])
async def get_predictions(
        fixture_id: int,
        db: Session = Depends(get_db)
):
    """
    Get predictions for a specific fixture.
    """
    try:
        response = await football_api_client.get_predictions(
            fixture=fixture_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/odds", response_model=schemas.OddsResponse, tags=["odds"])
async def get_odds(
        fixture: Optional[int] = None,
        league: Optional[int] = None,
        season: Optional[int] = None,
        date: Optional[str] = None,
        bookmaker: Optional[int] = None,
        bet: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """
    Get odds for fixtures.
    """
    try:
        response = await football_api_client.get_odds(
            fixture=fixture, league=league, season=season, date=date, bookmaker=bookmaker, bet=bet
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/odds/live", response_model=schemas.OddsLiveResponse, tags=["odds"])
async def get_odds_live(
        fixture: Optional[int] = None,
        league: Optional[int] = None,
        bet: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """
    Get live odds for fixtures in progress.
    """
    try:
        response = await football_api_client.get_odds_live(
            fixture=fixture, league=league, bet=bet
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# AI Analysis endpoints

@api_router.post("/analysis/match", response_model=schemas.MatchAnalysisResponse, tags=["analysis"])
async def analyze_match(
        data: schemas.MatchAnalysisRequest,
        db: Session = Depends(get_db)
):
    """
    Analyze a match using DeepSeek AI.
    """
    try:
        # Fetch additional data if needed
        fixture_data = await football_api_client.get_fixtures(id=data.fixture_id)

        if not fixture_data.get("response"):
            raise HTTPException(status_code=404, detail="Fixture not found")

        fixture = fixture_data["response"][0]

        # Get team information
        home_team_id = fixture["teams"]["home"]["id"]
        away_team_id = fixture["teams"]["away"]["id"]

        # Get team statistics
        home_team_stats = await football_api_client.get_team_statistics(
            league=data.league_id,
            season=data.season,
            team=home_team_id
        )

        away_team_stats = await football_api_client.get_team_statistics(
            league=data.league_id,
            season=data.season,
            team=away_team_id
        )

        # Get standings
        standings = await football_api_client.get_standings(
            league=data.league_id,
            season=data.season
        )

        # Get head to head
        h2h = await football_api_client.get_fixtures(
            h2h=f"{home_team_id}-{away_team_id}",
            last=10
        )

        # Use DeepSeek to analyze the match
        analysis = await deepseek_client.analyze_match(
            home_team=home_team_stats["response"],
            away_team=away_team_stats["response"],
            match_data=fixture,
            league_data=standings["response"][0] if standings.get("response") else None,
            historical_data=h2h["response"] if h2h.get("response") else None
        )

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/analysis/pre-match-report", response_model=schemas.PreMatchReportResponse, tags=["analysis"])
async def generate_pre_match_report(
        data: schemas.PreMatchReportRequest,
        db: Session = Depends(get_db)
):
    """
    Generate a pre-match report using DeepSeek AI.
    """
    try:
        # Fetch fixture data
        fixture_data = await football_api_client.get_fixtures(id=data.fixture_id)

        if not fixture_data.get("response"):
            raise HTTPException(status_code=404, detail="Fixture not found")

        fixture = fixture_data["response"][0]

        # Get team information
        home_team_id = fixture["teams"]["home"]["id"]
        away_team_id = fixture["teams"]["away"]["id"]
        league_id = fixture["league"]["id"]
        season = fixture["league"]["season"]

        # Get team statistics
        home_team_stats = await football_api_client.get_team_statistics(
            league=league_id,
            season=season,
            team=home_team_id
        )

        away_team_stats = await football_api_client.get_team_statistics(
            league=league_id,
            season=season,
            team=away_team_id
        )

        # Get standings
        standings = await football_api_client.get_standings(
            league=league_id,
            season=season
        )

        # Get head to head
        h2h = await football_api_client.get_fixtures(
            h2h=f"{home_team_id}-{away_team_id}",
            last=10
        )

        # Combine team stats
        team_stats = {
            "home": home_team_stats["response"],
            "away": away_team_stats["response"]
        }

        # Use DeepSeek to generate pre-match report
        report = await deepseek_client.generate_pre_match_report(
            fixture_data=fixture,
            team_stats=team_stats,
            league_context=standings["response"][0] if standings.get("response") else None,
            historical_h2h=h2h["response"] if h2h.get("response") else None
        )

        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/analysis/prediction", response_model=schemas.PredictionResponse, tags=["analysis"])
async def predict_match(
        data: schemas.PredictionRequest,
        db: Session = Depends(get_db)
):
    """
    Predict match result using DeepSeek AI.
    """
    try:
        # Fetch fixture data
        fixture_data = await football_api_client.get_fixtures(id=data.fixture_id)

        if not fixture_data.get("response"):
            raise HTTPException(status_code=404, detail="Fixture not found")

        fixture = fixture_data["response"][0]

        # Get team information
        home_team_id = fixture["teams"]["home"]["id"]
        away_team_id = fixture["teams"]["away"]["id"]
        home_team_name = fixture["teams"]["home"]["name"]
        away_team_name = fixture["teams"]["away"]["name"]
        league_id = fixture["league"]["id"]
        season = fixture["league"]["season"]

        # Get team statistics
        home_team_stats = await football_api_client.get_team_statistics(
            league=league_id,
            season=season,
            team=home_team_id
        )

        away_team_stats = await football_api_client.get_team_statistics(
            league=league_id,
            season=season,
            team=away_team_id
        )

        # Get recent form (last 5 matches)
        home_team_form = await football_api_client.get_fixtures(
            team=home_team_id,
            last=5
        )

        away_team_form = await football_api_client.get_fixtures(
            team=away_team_id,
            last=5
        )

        # Get head to head
        h2h = await football_api_client.get_fixtures(
            h2h=f"{home_team_id}-{away_team_id}",
            last=10
        )

        # Prepare data for prediction
        home_team = {"id": home_team_id, "name": home_team_name}
        away_team = {"id": away_team_id, "name": away_team_name}

        team_stats = {
            "home": home_team_stats["response"],
            "away": away_team_stats["response"]
        }

        recent_form = {
            "home": home_team_form["response"] if home_team_form.get("response") else [],
            "away": away_team_form["response"] if away_team_form.get("response") else []
        }

        h2h_matches = h2h["response"] if h2h.get("response") else []

        # Use DeepSeek to predict match result
        prediction = await deepseek_client.predict_match_result(
            fixture_id=data.fixture_id,
            home_team=home_team,
            away_team=away_team,
            team_stats=team_stats,
            recent_form=recent_form,
            h2h_matches=h2h_matches
        )

        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/analysis/betting", response_model=schemas.BettingAnalysisResponse, tags=["analysis"])
async def analyze_betting_opportunities(
        data: schemas.BettingAnalysisRequest,
        db: Session = Depends(get_db)
):
    """
    Analyze betting opportunities for a match using DeepSeek AI.
    """
    try:
        # Fetch fixture data
        fixture_data = await football_api_client.get_fixtures(id=data.fixture_id)

        if not fixture_data.get("response"):
            raise HTTPException(status_code=404, detail="Fixture not found")

        fixture = fixture_data["response"][0]

        # Get odds data
        odds_data = await football_api_client.get_odds(fixture=data.fixture_id)

        # Get team information
        home_team_id = fixture["teams"]["home"]["id"]
        away_team_id = fixture["teams"]["away"]["id"]
        league_id = fixture["league"]["id"]
        season = fixture["league"]["season"]

        # Get team statistics
        home_team_stats = await football_api_client.get_team_statistics(
            league=league_id,
            season=season,
            team=home_team_id
        )

        away_team_stats = await football_api_client.get_team_statistics(
            league=league_id,
            season=season,
            team=away_team_id
        )

        # Get predictions from API
        api_predictions = await football_api_client.get_predictions(fixture=data.fixture_id)

        # Combine team stats
        team_stats = {
            "home": home_team_stats["response"],
            "away": away_team_stats["response"]
        }

        # Use DeepSeek to analyze betting opportunities
        analysis = await deepseek_client.analyze_betting_opportunities(
            fixture_data=fixture,
            odds_data=odds_data["response"] if odds_data.get("response") else None,
            team_stats=team_stats,
            predictions=api_predictions["response"][0] if api_predictions.get("response") else None
        )

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/ai/chat", response_model=schemas.ChatResponse, tags=["ai"])
async def chat_with_ai(
        data: schemas.ChatRequest,
        db: Session = Depends(get_db)
):
    """
    Chat with the football AI assistant.
    """
    try:
        # Prepare optional context data if provided
        context = None
        if data.context_type and data.context_id:
            if data.context_type == "fixture":
                fixture_data = await football_api_client.get_fixtures(id=data.context_id)
                if fixture_data.get("response"):
                    context = fixture_data["response"][0]
            elif data.context_type == "team":
                team_data = await football_api_client.get_teams(id=data.context_id)
                if team_data.get("response"):
                    context = team_data["response"][0]
            elif data.context_type == "league":
                league_data = await football_api_client.get_leagues(id=data.context_id)
                if league_data.get("response"):
                    context = league_data["response"][0]

        # Use DeepSeek for AI chat
        response = await deepseek_client.chat_with_ai(
            query=data.query,
            context=context
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/data/sync", response_model=schemas.SyncResponse, tags=["data"])
async def sync_data(
        data: schemas.SyncRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    """
    Sync data from Football API to local database.
    """
    # This would be implemented to handle background data synchronization
    # For now, we'll return a placeholder response
    return {
        "message": "Data sync initiated",
        "status": "pending",
        "sync_id": "123456",
        "type": data.type,
        "parameters": data.parameters
    }