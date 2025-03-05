from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# Base response model
class BaseResponse(BaseModel):
    get: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    results: Optional[int] = None
    paging: Optional[Dict[str, int]] = None
    response: Any = None

# Football API response models
class CompetitionsResponse(BaseResponse):
    """Response model for competitions endpoint."""
    pass

class SeasonsResponse(BaseResponse):
    """Response model for seasons endpoint."""
    pass

class TeamsResponse(BaseResponse):
    """Response model for teams endpoint."""
    pass

class TeamStatisticsResponse(BaseResponse):
    """Response model for team statistics endpoint."""
    pass

class FixturesResponse(BaseResponse):
    """Response model for fixtures endpoint."""
    pass

class TeamFixturesResponse(BaseModel):
    """Response model for team fixtures endpoint."""
    response: Dict[str, List[Dict[str, Any]]]

class FixtureResponse(BaseResponse):
    """Response model for single fixture endpoint."""
    pass

class FixtureStatisticsResponse(BaseResponse):
    """Response model for fixture statistics endpoint."""
    pass

class FixtureEventsResponse(BaseResponse):
    """Response model for fixture events endpoint."""
    pass

class FixtureLineupsResponse(BaseResponse):
    """Response model for fixture lineups endpoint."""
    pass

class FixturePlayersResponse(BaseResponse):
    """Response model for fixture players endpoint."""
    pass

class HeadToHeadResponse(BaseResponse):
    """Response model for head to head endpoint."""
    pass

class StandingsResponse(BaseResponse):
    """Response model for standings endpoint."""
    pass

class PredictionsResponse(BaseResponse):
    """Response model for predictions endpoint."""
    pass

class OddsResponse(BaseResponse):
    """Response model for odds endpoint."""
    pass

class OddsLiveResponse(BaseResponse):
    """Response model for live odds endpoint."""
    pass

class SyncResponse(BaseModel):
    """Response model for sync operations."""
    message: str
    status: str
    type: str
    parameters: Dict[str, Any]

# Request models
class SyncRequest(BaseModel):
    type: str  # "leagues", "teams", "fixtures", "odds", etc.
    parameters: Dict[str, Any] = Field(default_factory=dict)

# Request models for AI Analysis
class MatchAnalysisRequest(BaseModel):
    fixture_id: int
    league_id: int
    season: int

class MatchAnalysisResponse(BaseModel):
    analysis: str
    match_id: str
    home_team: str
    away_team: str

class PreMatchReportRequest(BaseModel):
    fixture_id: int

class PreMatchReportResponse(BaseModel):
    report: str
    fixture_id: str
    home_team: str
    away_team: str

class PredictionRequest(BaseModel):
    fixture_id: int

class PredictionResponse(BaseModel):
    fixture_id: int
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    under_25_probability: Optional[float] = None
    over_25_probability: Optional[float] = None
    btts_yes_probability: Optional[float] = None
    btts_no_probability: Optional[float] = None
    most_likely_score: Optional[str] = None
    expected_goals_home: Optional[float] = None
    expected_goals_away: Optional[float] = None
    advice: Optional[str] = None
    error: Optional[str] = None
    raw_output: Optional[str] = None

class BettingAnalysisRequest(BaseModel):
    fixture_id: int

class BettingAnalysisResponse(BaseModel):
    analysis: str
    fixture_id: str
    home_team: str
    away_team: str

class ChatRequest(BaseModel):
    query: str
    context_type: Optional[str] = None  # "fixture", "team", "league"
    context_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    query: str

# Database models
class CompetitionCreate(BaseModel):
    api_id: int
    name: str
    country: str
    type: str
    season: int
    logo_url: Optional[str] = None

class CompetitionResponse(BaseModel):
    id: int
    api_id: int
    name: str
    country: str
    type: str
    season: int
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TeamCreate(BaseModel):
    api_id: int
    name: str
    code: Optional[str] = None
    country: str
    founded: Optional[int] = None
    logo_url: Optional[str] = None
    venue_name: Optional[str] = None
    venue_capacity: Optional[int] = None
    venue_city: Optional[str] = None

class TeamResponse(BaseModel):
    id: int
    api_id: int
    name: str
    code: Optional[str] = None
    country: str
    founded: Optional[int] = None
    logo_url: Optional[str] = None
    venue_name: Optional[str] = None
    venue_capacity: Optional[int] = None
    venue_city: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FixtureCreate(BaseModel):
    api_id: int
    referee: Optional[str] = None
    timezone: str
    date: datetime
    timestamp: int
    venue_name: Optional[str] = None
    venue_city: Optional[str] = None
    status: str
    elapsed: Optional[int] = None
    competition_id: int
    home_team_id: int
    away_team_id: int
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None
    home_halftime_goals: Optional[int] = None
    away_halftime_goals: Optional[int] = None
    home_fulltime_goals: Optional[int] = None
    away_fulltime_goals: Optional[int] = None
    home_extratime_goals: Optional[int] = None
    away_extratime_goals: Optional[int] = None
    home_penalty_goals: Optional[int] = None
    away_penalty_goals: Optional[int] = None

class FixtureDBResponse(BaseModel):
    id: int
    api_id: int
    referee: Optional[str] = None
    timezone: str
    date: datetime
    timestamp: int
    venue_name: Optional[str] = None
    venue_city: Optional[str] = None
    status: str
    elapsed: Optional[int] = None
    competition_id: int
    home_team_id: int
    away_team_id: int
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None
    home_halftime_goals: Optional[int] = None
    away_halftime_goals: Optional[int] = None
    home_fulltime_goals: Optional[int] = None
    away_fulltime_goals: Optional[int] = None
    home_extratime_goals: Optional[int] = None
    away_extratime_goals: Optional[int] = None
    home_penalty_goals: Optional[int] = None
    away_penalty_goals: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FixtureStatisticsCreate(BaseModel):
    fixture_id: int
    team_id: int
    shots_on_goal: Optional[int] = None
    shots_off_goal: Optional[int] = None
    total_shots: Optional[int] = None
    blocked_shots: Optional[int] = None
    shots_inside_box: Optional[int] = None
    shots_outside_box: Optional[int] = None
    fouls: Optional[int] = None
    corner_kicks: Optional[int] = None
    offsides: Optional[int] = None
    ball_possession: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    goalkeeper_saves: Optional[int] = None
    total_passes: Optional[int] = None
    accurate_passes: Optional[int] = None
    pass_accuracy: Optional[int] = None
    expected_goals: Optional[float] = None

class FixtureStatisticsDBResponse(BaseModel):
    id: int
    fixture_id: int
    team_id: int
    shots_on_goal: Optional[int] = None
    shots_off_goal: Optional[int] = None
    total_shots: Optional[int] = None
    blocked_shots: Optional[int] = None
    shots_inside_box: Optional[int] = None
    shots_outside_box: Optional[int] = None
    fouls: Optional[int] = None
    corner_kicks: Optional[int] = None
    offsides: Optional[int] = None
    ball_possession: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    goalkeeper_saves: Optional[int] = None
    total_passes: Optional[int] = None
    accurate_passes: Optional[int] = None
    pass_accuracy: Optional[int] = None
    expected_goals: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EventCreate(BaseModel):
    fixture_id: int
    team_id: int
    player_id: Optional[int] = None
    assist_id: Optional[int] = None
    time: int
    type: str
    detail: str
    comments: Optional[str] = None

class EventDBResponse(BaseModel):
    id: int
    fixture_id: int
    team_id: int
    player_id: Optional[int] = None
    assist_id: Optional[int] = None
    time: int
    type: str
    detail: str
    comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PredictionCreate(BaseModel):
    fixture_id: int
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    under_15_probability: Optional[float] = None
    over_15_probability: Optional[float] = None
    under_25_probability: Optional[float] = None
    over_25_probability: Optional[float] = None
    btts_yes_probability: Optional[float] = None
    btts_no_probability: Optional[float] = None
    advice: Optional[str] = None

class PredictionDBResponse(BaseModel):
    id: int
    fixture_id: int
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    under_15_probability: Optional[float] = None
    over_15_probability: Optional[float] = None
    under_25_probability: Optional[float] = None
    over_25_probability: Optional[float] = None
    btts_yes_probability: Optional[float] = None
    btts_no_probability: Optional[float] = None
    advice: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class OddsCreate(BaseModel):
    fixture_id: int
    bookmaker: str
    market: str
    odds_home: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away: Optional[float] = None
    odds_over_25: Optional[float] = None
    odds_under_25: Optional[float] = None
    odds_btts_yes: Optional[float] = None
    odds_btts_no: Optional[float] = None

class OddsDBResponse(BaseModel):
    id: int
    fixture_id: int
    bookmaker: str
    market: str
    odds_home: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away: Optional[float] = None
    odds_over_25: Optional[float] = None
    odds_under_25: Optional[float] = None
    odds_btts_yes: Optional[float] = None
    odds_btts_no: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True