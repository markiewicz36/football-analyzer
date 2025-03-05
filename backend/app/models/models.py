from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON, Table
from sqlalchemy.orm import relationship
from ..db.database import Base
import datetime

# Association table for many-to-many between Team and Competition
team_competition = Table(
    "team_competition",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id")),
    Column("competition_id", Integer, ForeignKey("competitions.id"))
)

class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    country = Column(String, index=True)
    type = Column(String)  # league or cup
    season = Column(Integer)  # e.g., 2023
    logo_url = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    fixtures = relationship("Fixture", back_populates="competition")
    teams = relationship("Team", secondary=team_competition, back_populates="competitions")

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    code = Column(String)
    country = Column(String, index=True)
    founded = Column(Integer)
    logo_url = Column(String)
    venue_name = Column(String)
    venue_capacity = Column(Integer)
    venue_city = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    home_fixtures = relationship("Fixture", foreign_keys="Fixture.home_team_id", back_populates="home_team")
    away_fixtures = relationship("Fixture", foreign_keys="Fixture.away_team_id", back_populates="away_team")
    competitions = relationship("Competition", secondary=team_competition, back_populates="teams")
    players = relationship("Player", back_populates="team")
    statistics = relationship("TeamStatistics", back_populates="team")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    firstname = Column(String)
    lastname = Column(String)
    age = Column(Integer)
    nationality = Column(String)
    height = Column(String)
    weight = Column(String)
    injured = Column(Boolean, default=False)
    photo_url = Column(String)
    team_id = Column(Integer, ForeignKey("teams.id"))
    position = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    team = relationship("Team", back_populates="players")
    statistics = relationship("PlayerStatistics", back_populates="player")

class Fixture(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, unique=True, index=True)
    referee = Column(String)
    timezone = Column(String)
    date = Column(DateTime)
    timestamp = Column(Integer)
    venue_name = Column(String)
    venue_city = Column(String)
    status = Column(String)  # NS, 1H, HT, 2H, FT, etc.
    elapsed = Column(Integer)
    competition_id = Column(Integer, ForeignKey("competitions.id"))
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    home_halftime_goals = Column(Integer)
    away_halftime_goals = Column(Integer)
    home_fulltime_goals = Column(Integer)
    away_fulltime_goals = Column(Integer)
    home_extratime_goals = Column(Integer)
    away_extratime_goals = Column(Integer)
    home_penalty_goals = Column(Integer)
    away_penalty_goals = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    competition = relationship("Competition", back_populates="fixtures")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_fixtures")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_fixtures")
    statistics = relationship("FixtureStatistics", back_populates="fixture")
    events = relationship("Event", back_populates="fixture")
    lineups = relationship("Lineup", back_populates="fixture")
    predictions = relationship("Prediction", back_populates="fixture")
    odds = relationship("Odds", back_populates="fixture")

class FixtureStatistics(Base):
    __tablename__ = "fixture_statistics"

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    shots_on_goal = Column(Integer)
    shots_off_goal = Column(Integer)
    total_shots = Column(Integer)
    blocked_shots = Column(Integer)
    shots_inside_box = Column(Integer)
    shots_outside_box = Column(Integer)
    fouls = Column(Integer)
    corner_kicks = Column(Integer)
    offsides = Column(Integer)
    ball_possession = Column(Integer)  # percentage
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    goalkeeper_saves = Column(Integer)
    total_passes = Column(Integer)
    accurate_passes = Column(Integer)
    pass_accuracy = Column(Integer)  # percentage
    expected_goals = Column(Float)  # xG
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    fixture = relationship("Fixture", back_populates="statistics")

class TeamStatistics(Base):
    __tablename__ = "team_statistics"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    competition_id = Column(Integer, ForeignKey("competitions.id"))
    season = Column(Integer)
    form = Column(String)  # last matches (e.g., WDLLW)
    played_home = Column(Integer)
    played_away = Column(Integer)
    played_total = Column(Integer)
    wins_home = Column(Integer)
    wins_away = Column(Integer)
    wins_total = Column(Integer)
    draws_home = Column(Integer)
    draws_away = Column(Integer)
    draws_total = Column(Integer)
    losses_home = Column(Integer)
    losses_away = Column(Integer)
    losses_total = Column(Integer)
    goals_for_home = Column(Integer)
    goals_for_away = Column(Integer)
    goals_for_total = Column(Integer)
    goals_against_home = Column(Integer)
    goals_against_away = Column(Integer)
    goals_against_total = Column(Integer)
    clean_sheets_home = Column(Integer)
    clean_sheets_away = Column(Integer)
    clean_sheets_total = Column(Integer)
    failed_to_score_home = Column(Integer)
    failed_to_score_away = Column(Integer)
    failed_to_score_total = Column(Integer)
    avg_goals_scored = Column(Float)
    avg_goals_conceded = Column(Float)
    avg_first_goal_scored = Column(Float)
    avg_first_goal_conceded = Column(Float)
    ppda = Column(Float)  # Passes Per Defensive Action
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    team = relationship("Team", back_populates="statistics")

class PlayerStatistics(Base):
    __tablename__ = "player_statistics"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    competition_id = Column(Integer, ForeignKey("competitions.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    season = Column(Integer)
    appearances = Column(Integer)
    minutes_played = Column(Integer)
    lineups = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    shots_total = Column(Integer)
    shots_on = Column(Integer)
    dribbles_attempts = Column(Integer)
    dribbles_success = Column(Integer)
    passes_total = Column(Integer)
    passes_accuracy = Column(Integer)
    key_passes = Column(Integer)
    tackles_total = Column(Integer)
    tackles_blocks = Column(Integer)
    tackles_interceptions = Column(Integer)
    duels_total = Column(Integer)
    duels_won = Column(Integer)
    rating = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    player = relationship("Player", back_populates="statistics")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    player_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    assist_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    time = Column(Integer)
    type = Column(String)  # Goal, Card, Subst, etc.
    detail = Column(String)  # Normal Goal, Yellow Card, etc.
    comments = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    fixture = relationship("Fixture", back_populates="events")

class Lineup(Base):
    __tablename__ = "lineups"

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    formation = Column(String)
    coach_name = Column(String)
    coach_id = Column(Integer, nullable=True)
    startxi = Column(JSON)
    substitutes = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    fixture = relationship("Fixture", back_populates="lineups")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"))
    home_win_probability = Column(Float)
    draw_probability = Column(Float)
    away_win_probability = Column(Float)
    under_15_probability = Column(Float)
    over_15_probability = Column(Float)
    under_25_probability = Column(Float)
    over_25_probability = Column(Float)
    btts_yes_probability = Column(Float)  # Both teams to score - Yes
    btts_no_probability = Column(Float)  # Both teams to score - No
    advice = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    fixture = relationship("Fixture", back_populates="predictions")

class Odds(Base):
    __tablename__ = "odds"

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"))
    bookmaker = Column(String)
    market = Column(String)  # 1X2, Over/Under, etc.
    odds_home = Column(Float, nullable=True)
    odds_draw = Column(Float, nullable=True)
    odds_away = Column(Float, nullable=True)
    odds_over_25 = Column(Float, nullable=True)
    odds_under_25 = Column(Float, nullable=True)
    odds_btts_yes = Column(Float, nullable=True)
    odds_btts_no = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    fixture = relationship("Fixture", back_populates="odds")

# Function to create all tables
def create_tables(engine):
    Base.metadata.create_all(bind=engine)