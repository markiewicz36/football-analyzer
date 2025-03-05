from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..db.database import get_db
from ..services.statistics_service import statistics_service
from ..models import models
from . import schemas

# Create router
router = APIRouter(
    prefix="/statistics",
    tags=["statistics"],
    responses={404: {"description": "Not found"}},
)


@router.get("/fixture/{fixture_id}", response_model=schemas.FixtureStatisticsResponse)
async def get_fixture_statistics(
        fixture_id: int = Path(..., description="Fixture ID"),
        db: Session = Depends(get_db)
):
    """
    Get statistics for a specific fixture.
    """
    try:
        statistics = await statistics_service.get_fixture_statistics(fixture_id)
        return {"response": statistics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics for fixture {fixture_id}: {str(e)}")


@router.get("/team/{team_id}/matches", response_model=schemas.TeamMatchStatisticsResponse)
async def get_team_match_statistics(
        team_id: int = Path(..., description="Team ID"),
        last: int = Query(5, ge=1, le=20, description="Number of matches to analyze"),
        db: Session = Depends(get_db)
):
    """
    Get statistics for recent matches of a team.
    """
    try:
        statistics = await statistics_service.get_team_match_statistics(team_id, last)
        return {"response": statistics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching match statistics for team {team_id}: {str(e)}")


@router.get("/team/{team_id}/aggregate", response_model=schemas.TeamAggregateStatisticsResponse)
async def get_team_aggregate_statistics(
        team_id: int = Path(..., description="Team ID"),
        league_id: int = Query(..., description="League ID"),
        season: int = Query(..., description="Season (e.g., 2023)"),
        db: Session = Depends(get_db)
):
    """
    Get aggregate statistics for a team in a specific league and season.
    """
    try:
        statistics = await statistics_service.get_team_aggregate_statistics(team_id, league_id, season)
        return {"response": statistics}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching aggregate statistics for team {team_id} in league {league_id}, season {season}: {str(e)}"
        )


@router.get("/fixture/{fixture_id}/xg", response_model=schemas.FixtureXGResponse)
async def get_fixture_xg(
        fixture_id: int = Path(..., description="Fixture ID"),
        db: Session = Depends(get_db)
):
    """
    Get calculated Expected Goals (xG) for a fixture.
    """
    try:
        home_xg, away_xg = await statistics_service.calculate_fixture_xg(fixture_id)
        return {
            "response": {
                "fixture_id": fixture_id,
                "home_xg": home_xg,
                "away_xg": away_xg
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating xG for fixture {fixture_id}: {str(e)}")


@router.post("/fixture/{fixture_id}/sync", response_model=schemas.SyncResponse)
async def sync_fixture_statistics(
        fixture_id: int = Path(..., description="Fixture ID"),
        background_tasks: BackgroundTasks = None,
        db: Session = Depends(get_db)
):
    """
    Sync statistics for a specific fixture from the API to the database.
    """
    try:
        # If background_tasks is provided, run the sync in the background
        if background_tasks:
            background_tasks.add_task(statistics_service.sync_fixture_statistics, db, fixture_id)
            return {
                "message": f"Sync of statistics for fixture {fixture_id} started in the background",
                "status": "pending",
                "type": "fixture_statistics",
                "parameters": {"fixture_id": fixture_id}
            }

        # Otherwise, run the sync immediately
        result = await statistics_service.sync_fixture_statistics(db, fixture_id)
        return {
            "message": f"Sync of statistics for fixture {fixture_id} completed",
            "status": "completed",
            "type": "fixture_statistics",
            "parameters": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing statistics for fixture {fixture_id}: {str(e)}")


@router.get("/team/{team_id}/analysis", response_model=schemas.TeamAnalysisResponse)
async def analyze_team_performance(
        team_id: int = Path(..., description="Team ID"),
        league_id: int = Query(..., description="League ID"),
        season: int = Query(..., description="Season (e.g., 2023)"),
        db: Session = Depends(get_db)
):
    """
    Analyze the performance of a team in a specific league and season.
    """
    try:
        analysis = await statistics_service.analyze_team_performance(team_id, league_id, season)
        return {"response": analysis}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing team {team_id} performance in league {league_id}, season {season}: {str(e)}"
        )


@router.get("/compare/{team1_id}/{team2_id}", response_model=schemas.TeamComparisonResponse)
async def compare_teams(
        team1_id: int = Path(..., description="First team ID"),
        team2_id: int = Path(..., description="Second team ID"),
        league_id: int = Query(..., description="League ID"),
        season: int = Query(..., description="Season (e.g., 2023)"),
        db: Session = Depends(get_db)
):
    """
    Compare the performance of two teams in a specific league and season.
    """
    try:
        comparison = await statistics_service.compare_teams(team1_id, team2_id, league_id, season)
        return {"response": comparison}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing teams {team1_id} and {team2_id} in league {league_id}, season {season}: {str(e)}"
        )