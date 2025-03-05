from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..db.database import get_db
from ..services.fixtures_service import fixtures_service
from ..models import models
from . import schemas

# Create router
router = APIRouter(
    prefix="/fixtures",
    tags=["fixtures"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=schemas.FixturesResponse)
async def get_fixtures(
    id: Optional[int] = None,
    date: Optional[str] = None,
    league: Optional[int] = None,
    season: Optional[int] = None,
    team: Optional[int] = None,
    live: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get fixtures with various filters.
    
    - **id**: Filter by fixture ID
    - **date**: Filter by date (YYYY-MM-DD)
    - **league**: Filter by league ID
    - **season**: Filter by season (e.g., 2023)
    - **team**: Filter by team ID
    - **live**: Get live fixtures ('all' or specific league IDs)
    - **status**: Filter by fixture status (e.g., 'NS', 'FT', '1H', etc.)
    - **from_date**: Filter from date (YYYY-MM-DD)
    - **to_date**: Filter to date (YYYY-MM-DD)
    - **limit**: Limit the number of results
    """
    try:
        # Handle live fixtures
        if live:
            fixtures = await fixtures_service.get_live_fixtures()
            return {"response": fixtures[:limit]}
        
        # Handle date range
        if from_date and to_date:
            fixtures_by_date = await fixtures_service.get_fixtures_in_date_range(from_date, to_date)
            
            # Flatten the dictionary of fixtures by date
            all_fixtures = []
            for date_fixtures in fixtures_by_date.values():
                all_fixtures.extend(date_fixtures)
            
            return {"response": all_fixtures[:limit]}
        
        # Handle single fixture
        if id:
            fixture = await fixtures_service.get_fixture_by_id(id)
            return {"response": [fixture] if fixture else []}
        
        # Handle fixtures by date
        if date:
            fixtures = await fixtures_service.get_fixtures_by_date(date)
            
            # Apply additional filters if needed
            if status:
                fixtures = [f for f in fixtures if f["fixture"]["status"]["short"] == status]
            
            return {"response": fixtures[:limit]}
        
        # Handle fixtures by league and season
        if league and season:
            fixtures = await fixtures_service.get_fixtures_by_league_season(league, season)
            return {"response": fixtures[:limit]}
        
        # Handle fixtures by team
        if team:
            team_fixtures = await fixtures_service.get_fixtures_by_team(team)
            
            # Combine past and upcoming fixtures
            all_fixtures = team_fixtures["past"] + team_fixtures["upcoming"]
            return {"response": all_fixtures[:limit]}
        
        # Default: get fixtures for today
        today = datetime.now().strftime("%Y-%m-%d")
        fixtures = await fixtures_service.get_fixtures_by_date(today)
        return {"response": fixtures[:limit]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fixtures: {str(e)}")

@router.get("/live", response_model=schemas.FixturesResponse)
async def get_live_fixtures(db: Session = Depends(get_db)):
    """
    Get currently live fixtures.
    """
    try:
        fixtures = await fixtures_service.get_live_fixtures()
        return {"response": fixtures}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching live fixtures: {str(e)}")

@router.get("/date/{date}", response_model=schemas.FixturesResponse)
async def get_fixtures_by_date(
    date: str = Path(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get fixtures for a specific date.
    """
    try:
        fixtures = await fixtures_service.get_fixtures_by_date(date)
        return {"response": fixtures}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fixtures for date {date}: {str(e)}")

@router.get("/upcoming", response_model=schemas.FixturesResponse)
async def get_upcoming_fixtures(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Get fixtures for the upcoming days.
    """
    try:
        fixtures = await fixtures_service.get_upcoming_fixtures(days)
        return {"response": fixtures}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching upcoming fixtures: {str(e)}")

@router.get("/league/{league_id}/season/{season}", response_model=schemas.FixturesResponse)
async def get_fixtures_by_league_season(
    league_id: int = Path(..., description="League ID"),
    season: int = Path(..., description="Season (e.g., 2023)"),
    db: Session = Depends(get_db)
):
    """
    Get fixtures for a specific league and season.
    """
    try:
        fixtures = await fixtures_service.get_fixtures_by_league_season(league_id, season)
        return {"response": fixtures}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fixtures for league {league_id}, season {season}: {str(e)}")

@router.get("/team/{team_id}", response_model=schemas.TeamFixturesResponse)
async def get_fixtures_by_team(
    team_id: int = Path(..., description="Team ID"),
    last: int = Query(10, ge=1, le=50),
    next: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get past and upcoming fixtures for a specific team.
    """
    try:
        fixtures = await fixtures_service.get_fixtures_by_team(team_id, last, next)
        return {
            "response": {
                "past": fixtures["past"],
                "upcoming": fixtures["upcoming"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fixtures for team {team_id}: {str(e)}")

@router.get("/{fixture_id}", response_model=schemas.FixtureResponse)
async def get_fixture_by_id(
    fixture_id: int = Path(..., description="Fixture ID"),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific fixture.
    """
    try:
        fixture = await fixtures_service.get_fixture_by_id(fixture_id)
        if not fixture:
            raise HTTPException(status_code=404, detail=f"Fixture with ID {fixture_id} not found")
        return {"response": fixture}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fixture {fixture_id}: {str(e)}")

@router.get("/{fixture_id}/statistics", response_model=schemas.FixtureStatisticsResponse)
async def get_fixture_statistics(
    fixture_id: int = Path(..., description="Fixture ID"),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific fixture.
    """
    try:
        statistics = await fixtures_service.get_fixture_statistics(fixture_id)
        return {"response": statistics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics for fixture {fixture_id}: {str(e)}")

@router.get("/{fixture_id}/events", response_model=schemas.FixtureEventsResponse)
async def get_fixture_events(
    fixture_id: int = Path(..., description="Fixture ID"),
    db: Session = Depends(get_db)
):
    """
    Get events for a specific fixture.
    """
    try:
        events = await fixtures_service.get_fixture_events(fixture_id)
        return {"response": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events for fixture {fixture_id}: {str(e)}")

@router.get("/{fixture_id}/lineups", response_model=schemas.FixtureLineupsResponse)
async def get_fixture_lineups(
    fixture_id: int = Path(..., description="Fixture ID"),
    db: Session = Depends(get_db)
):
    """
    Get lineups for a specific fixture.
    """
    try:
        lineups = await fixtures_service.get_fixture_lineups(fixture_id)
        return {"response": lineups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lineups for fixture {fixture_id}: {str(e)}")

@router.get("/{fixture_id}/players", response_model=schemas.FixturePlayersResponse)
async def get_fixture_players(
    fixture_id: int = Path(..., description="Fixture ID"),
    db: Session = Depends(get_db)
):
    """
    Get player statistics for a specific fixture.
    """
    try:
        players = await fixtures_service.get_fixture_players(fixture_id)
        return {"response": players}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching player statistics for fixture {fixture_id}: {str(e)}")

@router.get("/{fixture_id}/odds", response_model=schemas.OddsResponse)
async def get_fixture_odds(
    fixture_id: int = Path(..., description="Fixture ID"),
    db: Session = Depends(get_db)
):
    """
    Get odds for a specific fixture.
    """
    try:
        odds = await fixtures_service.get_fixture_odds(fixture_id)
        return {"response": odds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching odds for fixture {fixture_id}: {str(e)}")

@router.get("/h2h/{team1_id}/{team2_id}", response_model=schemas.FixturesResponse)
async def get_head_to_head(
    team1_id: int = Path(..., description="First team ID"),
    team2_id: int = Path(..., description="Second team ID"),
    last: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get head-to-head fixtures between two teams.
    """
    try:
        fixtures = await fixtures_service.get_head_to_head(team1_id, team2_id, last)
        return {"response": fixtures}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching head-to-head fixtures for teams {team1_id} and {team2_id}: {str(e)}")

@router.post("/sync/date/{date}", response_model=schemas.SyncResponse)
async def sync_fixtures_by_date(
    date: str = Path(..., description="Date in YYYY-MM-DD format"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Sync fixtures for a specific date from the API to the database.
    """
    try:
        # If background_tasks is provided, run the sync in the background
        if background_tasks:
            background_tasks.add_task(fixtures_service.sync_fixtures_by_date, db, date)
            return {
                "message": f"Sync of fixtures for date {date} started in the background",
                "status": "pending",
                "type": "fixtures_by_date",
                "parameters": {"date": date}
            }
        
        # Otherwise, run the sync immediately
        result = await fixtures_service.sync_fixtures_by_date(db, date)
        return {
            "message": f"Sync of fixtures for date {date} completed",
            "status": "completed",
            "type": "fixtures_by_date",
            "parameters": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing fixtures for date {date}: {str(e)}")

@router.post("/sync/league/{league_id}/season/{season}", response_model=schemas.SyncResponse)
async def sync_fixtures_by_league_season(
    league_id: int = Path(..., description="League ID"),
    season: int = Path(..., description="Season (e.g., 2023)"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Sync fixtures for a specific league and season from the API to the database.
    """
    try:
        # If background_tasks is provided, run the sync in the background
        if background_tasks:
            background_tasks.add_task(fixtures_service.sync_fixtures_by_league_season, db, league_id, season)
            return {
                "message": f"Sync of fixtures for league {league_id}, season {season} started in the background",
                "status": "pending",
                "type": "fixtures_by_league_season",
                "parameters": {"league_id": league_id, "season": season}
            }
        
        # Otherwise, run the sync immediately
        result = await fixtures_service.sync_fixtures_by_league_season(db, league_id, season)
        return {
            "message": f"Sync of fixtures for league {league_id}, season {season} completed",
            "status": "completed",
            "type": "fixtures_by_league_season",
            "parameters": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing fixtures for league {league_id}, season {season}: {str(e)}")