import time
from typing import Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from data_sources import DATA_SOURCES, FACTOR_TO_SOURCES, TECH_STACK
from factor_definitions import (
    CATEGORY_WEIGHTS,
    FACTOR_DEFINITIONS,
    MATCH_FACTOR_KEYS,
    TEAM_FACTOR_KEYS,
)
from prediction_model import PredictionModel, TeamStats

app = FastAPI(title="World Cup Prediction API")
model = PredictionModel()


class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    home_elo: int
    away_elo: int
    home_avg_xg: float = 1.2
    away_avg_xg: float = 1.0
    home_missing_defense: int = 0
    away_missing_defense: int = 0
    home_missing_offense: int = 0
    away_missing_offense: int = 0
    group_pressure: bool = False
    friendly_match: bool = False
    match_minute: Optional[float] = Field(None, ge=0, le=130)
    home_live_goals: int = Field(0, ge=0, le=20)
    away_live_goals: int = Field(0, ge=0, le=20)
    market_goal_expectation: Optional[float] = Field(None, ge=0, le=10)

    # New 100-factor interface. Team factors are sent separately for each side.
    home_factors: Dict[str, float] = Field(default_factory=dict)
    away_factors: Dict[str, float] = Field(default_factory=dict)
    match_factors: Dict[str, float] = Field(default_factory=dict)

    # Backward-compatible aliases from the previous API version.
    home_recent_form_points: float = Field(7.5, ge=0, le=15)
    away_recent_form_points: float = Field(7.5, ge=0, le=15)
    home_recent_xg_diff: float = 0.0
    away_recent_xg_diff: float = 0.0
    home_shots_on_target: float = 4.0
    away_shots_on_target: float = 4.0
    home_possession_pct: float = Field(50.0, ge=0, le=100)
    away_possession_pct: float = Field(50.0, ge=0, le=100)
    home_pressing_intensity: float = Field(50.0, ge=0, le=100)
    away_pressing_intensity: float = Field(50.0, ge=0, le=100)
    home_set_piece_strength: float = Field(50.0, ge=0, le=100)
    away_set_piece_strength: float = Field(50.0, ge=0, le=100)
    home_counter_attack_strength: float = Field(50.0, ge=0, le=100)
    away_counter_attack_strength: float = Field(50.0, ge=0, le=100)
    home_goalkeeper_form: float = Field(50.0, ge=0, le=100)
    away_goalkeeper_form: float = Field(50.0, ge=0, le=100)
    home_rest_days: int = Field(5, ge=0, le=30)
    away_rest_days: int = Field(5, ge=0, le=30)
    home_travel_distance_km: float = Field(0.0, ge=0)
    away_travel_distance_km: float = Field(0.0, ge=0)
    home_advantage: float = Field(0.0, ge=0, le=1)
    home_crowd_support: float = Field(50.0, ge=0, le=100)
    away_crowd_support: float = Field(50.0, ge=0, le=100)
    home_morale: float = Field(50.0, ge=0, le=100)
    away_morale: float = Field(50.0, ge=0, le=100)
    home_coach_tactical_rating: float = Field(50.0, ge=0, le=100)
    away_coach_tactical_rating: float = Field(50.0, ge=0, le=100)
    home_squad_depth: float = Field(50.0, ge=0, le=100)
    away_squad_depth: float = Field(50.0, ge=0, le=100)
    home_fatigue_index: float = Field(0.0, ge=0, le=1)
    away_fatigue_index: float = Field(0.0, ge=0, le=1)
    referee_strictness: float = Field(50.0, ge=0, le=100)
    referee_penalty_rate: float = Field(0.25, ge=0, le=2)
    referee_cards_per_match: float = Field(4.0, ge=0, le=12)
    political_tension: float = Field(0.0, ge=0, le=100)
    diplomatic_friction: float = Field(0.0, ge=0, le=100)
    rivalry_index: float = Field(0.0, ge=0, le=100)
    weather_heat_c: float = Field(22.0, ge=-20, le=50)
    humidity_pct: float = Field(50.0, ge=0, le=100)
    wind_kmh: float = Field(8.0, ge=0, le=120)
    altitude_m: float = Field(0.0, ge=0, le=5000)
    pitch_quality: float = Field(70.0, ge=0, le=100)


def request_factor_count():
    return len(FACTOR_DEFINITIONS)


def _filtered_factors(values, allowed_keys):
    return {key: float(value) for key, value in values.items() if key in allowed_keys}


def _team_factors(req, side):
    prefix = f"{side}_"
    factors = {
        key: float(value)
        for key, value in getattr(req, f"{side}_factors").items()
        if isinstance(value, (int, float))
    }
    factors.update(
        {
            "elo_rating": getattr(req, f"{prefix}elo"),
            "expected_goals": getattr(req, f"{prefix}avg_xg"),
            "defensive_core_absent": getattr(req, f"{prefix}missing_defense"),
            "last5_form_points": getattr(req, f"{prefix}recent_form_points"),
            "possession_rate": getattr(req, f"{prefix}possession_pct"),
            "high_press_intensity": getattr(req, f"{prefix}pressing_intensity"),
            "set_piece_goal_rate": getattr(req, f"{prefix}set_piece_strength"),
            "counter_attack_goal_rate": getattr(req, f"{prefix}counter_attack_strength"),
            "goalkeeper_save_rate": getattr(req, f"{prefix}goalkeeper_form"),
            "rest_days_advantage": getattr(req, f"{prefix}rest_days"),
            "travel_fatigue": getattr(req, f"{prefix}travel_distance_km"),
            "home_fan_support": getattr(req, f"{prefix}crowd_support"),
            "team_morale": getattr(req, f"{prefix}morale"),
            "stamina_reserve": 100 - getattr(req, f"{prefix}fatigue_index") * 100,
        }
    )
    if side == "home":
        factors["home_fan_support"] = max(
            factors["home_fan_support"], req.home_advantage * 100
        )
    return factors


def _match_factors(req):
    factors = {
        key: float(value)
        for key, value in req.match_factors.items()
        if isinstance(value, (int, float))
    }
    factors.update(
        {
            "referee_yellow_cards_per_game": req.referee_cards_per_match,
            "referee_penalties_per_game": req.referee_penalty_rate,
            "historic_rivalry": max(
                req.rivalry_index, req.political_tension, req.diplomatic_friction
            ),
            "temperature_c": req.weather_heat_c,
            "humidity_pct": req.humidity_pct,
            "wind_speed_kmh": req.wind_kmh,
            "altitude_m": req.altitude_m,
            "pitch_quality": req.pitch_quality,
            "match_minute": req.match_minute,
            "home_live_goals": req.home_live_goals,
            "away_live_goals": req.away_live_goals,
        }
    )
    if req.market_goal_expectation is not None:
        factors["market_goal_expectation"] = req.market_goal_expectation
        factors["over_under_goal_expectation"] = req.market_goal_expectation
    return factors


@app.get("/")
async def root():
    return {
        "service": "World Cup Prediction API",
        "version": "4.0",
        "implemented_factors": request_factor_count(),
    }


@app.get("/factors")
async def factors():
    return {
        "factor_count": request_factor_count(),
        "category_weights": CATEGORY_WEIGHTS,
        "team_factor_keys": TEAM_FACTOR_KEYS,
        "match_factor_keys": MATCH_FACTOR_KEYS,
        "factors": [factor.__dict__ for factor in FACTOR_DEFINITIONS],
    }


@app.get("/data-sources")
async def data_sources():
    return {
        "source_count": len(DATA_SOURCES),
        "tech_stack": TECH_STACK,
        "factor_to_sources": FACTOR_TO_SOURCES,
        "sources": [source.__dict__ for source in DATA_SOURCES],
    }


@app.get("/data-sources/{factor_key}")
async def data_sources_for_factor(factor_key: str):
    source_keys = FACTOR_TO_SOURCES.get(factor_key, [])
    return {
        "factor_key": factor_key,
        "sources": [
            source.__dict__ for source in DATA_SOURCES if source.key in source_keys
        ],
    }


@app.post("/predict")
async def predict(req: PredictRequest):
    start = time.time()
    home = TeamStats(
        name=req.home_team,
        elo_rating=req.home_elo,
        avg_goals_per_game=req.home_avg_xg * 0.9,
        avg_xg=req.home_avg_xg,
        missing_defensive_key_players=req.home_missing_defense,
        missing_offensive_key_players=req.home_missing_offense,
        group_pressure=req.group_pressure,
        friendly_match=req.friendly_match,
        recent_form_points=req.home_recent_form_points,
        recent_xg_diff=req.home_recent_xg_diff,
        shots_on_target_per_game=req.home_shots_on_target,
        possession_pct=req.home_possession_pct,
        pressing_intensity=req.home_pressing_intensity,
        set_piece_strength=req.home_set_piece_strength,
        counter_attack_strength=req.home_counter_attack_strength,
        goalkeeper_form=req.home_goalkeeper_form,
        rest_days=req.home_rest_days,
        travel_distance_km=req.home_travel_distance_km,
        home_advantage=req.home_advantage,
        crowd_support=req.home_crowd_support,
        morale=req.home_morale,
        coach_tactical_rating=req.home_coach_tactical_rating,
        squad_depth=req.home_squad_depth,
        fatigue_index=req.home_fatigue_index,
        live_goals=req.home_live_goals,
        factors=_team_factors(req, "home"),
    )
    away = TeamStats(
        name=req.away_team,
        elo_rating=req.away_elo,
        avg_goals_per_game=req.away_avg_xg * 0.9,
        avg_xg=req.away_avg_xg,
        missing_defensive_key_players=req.away_missing_defense,
        missing_offensive_key_players=req.away_missing_offense,
        group_pressure=req.group_pressure,
        friendly_match=req.friendly_match,
        recent_form_points=req.away_recent_form_points,
        recent_xg_diff=req.away_recent_xg_diff,
        shots_on_target_per_game=req.away_shots_on_target,
        possession_pct=req.away_possession_pct,
        pressing_intensity=req.away_pressing_intensity,
        set_piece_strength=req.away_set_piece_strength,
        counter_attack_strength=req.away_counter_attack_strength,
        goalkeeper_form=req.away_goalkeeper_form,
        rest_days=req.away_rest_days,
        travel_distance_km=req.away_travel_distance_km,
        crowd_support=req.away_crowd_support,
        morale=req.away_morale,
        coach_tactical_rating=req.away_coach_tactical_rating,
        squad_depth=req.away_squad_depth,
        fatigue_index=req.away_fatigue_index,
        live_goals=req.away_live_goals,
        factors=_team_factors(req, "away"),
    )
    result = model.predict(home, away, _match_factors(req))
    result["factor_count"] = request_factor_count()
    result["time_ms"] = round((time.time() - start) * 1000, 2)
    return result
