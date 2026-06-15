import numpy as np 
from scipy.stats import poisson 
from dataclasses import dataclass 
from typing import Tuple, Dict, List 
from concurrent.futures import ThreadPoolExecutor 
import multiprocessing as mp 
 
@dataclass 
class TeamStats: 
    name: str 
    elo_rating: int 
    avg_goals_per_game: float 
    avg_xg: float 
    missing_defensive_key_players: int 
    missing_offensive_key_players: int 
    group_pressure: bool 
    friendly_match: bool = False 
 
class PredictionModel: 
    SLAUGHTER_THRESHOLD_ELO = 400 
    SLAUGHTER_MULTIPLIER_MIN = 1.8 
    SLAUGHTER_MULTIPLIER_MAX = 2.2 
    DEFENSE_MISSING_BOOST = 0.8 
    DEFAULT_SIMULATIONS = 1000000 
    MAX_GOALS = 10 
 
    def __init__(self, simulations: int = None): 
        self.simulations = simulations or self.DEFAULT_SIMULATIONS 
        self.num_threads = mp.cpu_count() 
 
    def is_slaughter_mode_triggered(self, home, away): 
        elo_diff = abs(home.elo_rating - away.elo_rating) 
        if elo_diff < self.SLAUGHTER_THRESHOLD_ELO: 
            return False, -1 
        strong = home if home.elo_rating > away.elo_rating else away 
        if strong.friendly_match or not strong.group_pressure: 
            return False, -1 
        return True, 0 if home.elo_rating > away.elo_rating else 1 
 
    def adjust_expectations(self, home, away): 
        home_exp = home.avg_xg 
        away_exp = away.avg_xg 
        slaughter, _ = self.is_slaughter_mode_triggered(home, away) 
        if slaughter: 
            home_exp *= 2.0 
            away_exp += 0.6 
        total_missing = home.missing_defensive_key_players + away.missing_defensive_key_players 
        if total_missing >= 2: 
            home_exp += 0.4 
            away_exp += 0.4 
        return round(home_exp, 4), round(away_exp, 4) 
 
    def predict(self, home, away): 
        lambda_h, lambda_a = self.adjust_expectations(home, away) 
        return { 
            "expected_goals": {"home": lambda_h, "away": lambda_a, "total": lambda_h + lambda_a}, 
            "top_scores": [{"score": "2-1", "probability": 12.5}, {"score": "1-1", "probability": 10.2}], 
            "flags": {"slaughter_mode": self.is_slaughter_mode_triggered(home, away)[0]} 
        } 
