import multiprocessing as mp
from dataclasses import dataclass, field
from typing import Dict

from scipy.stats import poisson

from factor_definitions import FACTOR_DEFINITIONS, FACTOR_BY_KEY
from quantification import first_six_category_scores


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
    recent_form_points: float = 7.5
    recent_xg_diff: float = 0.0
    shots_on_target_per_game: float = 4.0
    possession_pct: float = 50.0
    pressing_intensity: float = 50.0
    set_piece_strength: float = 50.0
    counter_attack_strength: float = 50.0
    goalkeeper_form: float = 50.0
    rest_days: int = 5
    travel_distance_km: float = 0.0
    home_advantage: float = 0.0
    crowd_support: float = 50.0
    morale: float = 50.0
    coach_tactical_rating: float = 50.0
    squad_depth: float = 50.0
    fatigue_index: float = 0.0
    live_goals: int = 0
    factors: Dict[str, float] = field(default_factory=dict)


class PredictionModel:
    SLAUGHTER_THRESHOLD_ELO = 400
    DEFAULT_SIMULATIONS = 1000000
    MAX_GOALS = 10
    MIN_EXPECTED_GOALS = 0.05
    FACTOR_GOAL_SCALE = 0.018
    TEMPO_GOAL_SCALE = 0.012

    def __init__(self, simulations: int = None):
        self.simulations = simulations or self.DEFAULT_SIMULATIONS
        self.num_threads = mp.cpu_count()

    @staticmethod
    def _clamp(value, low, high):
        return max(low, min(high, value))

    @staticmethod
    def _safe_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _factor_value(self, factors, key):
        definition = FACTOR_BY_KEY[key]
        return self._safe_float(factors.get(key), definition.neutral)

    def _normalized_factor(self, factors, key):
        definition = FACTOR_BY_KEY[key]
        value = self._factor_value(factors, key)
        if definition.scale == 0:
            return 0.0
        normalized = (value - definition.neutral) / definition.scale
        return self._clamp(normalized * definition.direction, -2.0, 2.0)

    def _build_legacy_factors(self, team):
        return {
            "elo_rating": team.elo_rating,
            "goals_per_game": team.avg_goals_per_game,
            "expected_goals": team.avg_xg,
            "defensive_core_absent": team.missing_defensive_key_players,
            "possession_rate": team.possession_pct,
            "high_press_intensity": team.pressing_intensity,
            "set_piece_goal_rate": team.set_piece_strength,
            "counter_attack_goal_rate": team.counter_attack_strength,
            "goalkeeper_save_rate": team.goalkeeper_form,
            "last5_form_points": team.recent_form_points,
            "team_morale": team.morale,
            "travel_fatigue": team.travel_distance_km,
            "home_fan_support": team.crowd_support,
            "rest_days_advantage": team.rest_days,
        }

    def _merged_factors(self, team):
        merged = self._build_legacy_factors(team)
        merged.update(team.factors or {})
        return merged

    def is_slaughter_mode_triggered(self, home, away):
        elo_diff = abs(home.elo_rating - away.elo_rating)
        if elo_diff < self.SLAUGHTER_THRESHOLD_ELO:
            return False, -1
        strong = home if home.elo_rating > away.elo_rating else away
        if strong.friendly_match or not strong.group_pressure:
            return False, -1
        return True, 0 if home.elo_rating > away.elo_rating else 1

    def _empty_contributions(self):
        return {
            "attack": 0.0,
            "defense": 0.0,
            "control": 0.0,
            "strength": 0.0,
            "form": 0.0,
            "player": 0.0,
            "motivation": 0.0,
            "h2h": 0.0,
            "set_piece": 0.0,
            "market": 0.0,
            "stamina": 0.0,
            "discipline": 0.0,
            "depth": 0.0,
        }

    def _team_contributions(self, team, opponent):
        factors = self._merged_factors(team)
        opponent_factors = self._merged_factors(opponent)
        contributions = self._empty_contributions()
        by_category = {}
        active = 0

        for definition in FACTOR_DEFINITIONS:
            if definition.scope != "team":
                continue
            own = self._normalized_factor(factors, definition.key)
            other = self._normalized_factor(opponent_factors, definition.key)
            advantage = own - other
            weighted = advantage * definition.weight
            if definition.key in factors or definition.key in opponent_factors:
                active += 1
            by_category[definition.category] = (
                by_category.get(definition.category, 0.0) + weighted
            )

            effect = definition.effect
            if effect in contributions:
                contributions[effect] += weighted
            elif effect == "tempo":
                contributions["attack"] += weighted * 0.5
            else:
                contributions["strength"] += weighted

        return contributions, by_category, active

    def _quantified_team_contributions(self, team, opponent):
        factors = self._merged_factors(team)
        opponent_factors = self._merged_factors(opponent)
        own_scores = first_six_category_scores(factors, opponent_factors)
        opponent_scores = first_six_category_scores(opponent_factors, factors)

        q_strength = own_scores["q_strength"] - opponent_scores["q_strength"]
        q_attack = own_scores["q_attack"] - opponent_scores["q_defense"]
        q_defense = own_scores["q_defense"] - opponent_scores["q_attack"]
        q_midfield = own_scores["q_midfield"] - opponent_scores["q_midfield"]
        q_form = own_scores["q_form"] - opponent_scores["q_form"]
        q_player = own_scores["q_player"] - opponent_scores["q_player"]
        q_team = own_scores["q_team"] - opponent_scores["q_team"]

        contributions = self._empty_contributions()
        contributions["strength"] = q_strength * 18
        contributions["attack"] = (q_attack * 18) + (q_team * 8)
        contributions["defense"] = q_defense * 18
        contributions["control"] = q_midfield * 14
        contributions["form"] = q_form * 12
        contributions["player"] = q_player * 10
        contributions["set_piece"] = (
            own_scores.get("market_value_ratio_score", 0.5)
            - opponent_scores.get("market_value_ratio_score", 0.5)
        ) * 3
        contributions["stamina"] = (
            own_scores.get("fatigue_available_score", 0.5)
            - opponent_scores.get("fatigue_available_score", 0.5)
        ) * 4

        by_category = {
            "strength": q_strength * 100,
            "attack": q_attack * 100,
            "defense": q_defense * 100,
            "midfield": q_midfield * 100,
            "form": q_form * 100,
            "player": q_player * 100,
            "team_composite": q_team * 100,
        }
        return contributions, by_category, own_scores

    def _match_contributions(self, match_context):
        contributions = {
            "tempo": 0.0,
            "cards": 0.0,
            "weather": 0.0,
            "chaos": 0.0,
            "uncertainty": 0.0,
        }
        by_category = {}
        active = 0
        for definition in FACTOR_DEFINITIONS:
            if definition.scope != "match":
                continue
            value = self._normalized_factor(match_context, definition.key)
            weighted = value * definition.weight
            if definition.key in match_context:
                active += 1
            by_category[definition.category] = (
                by_category.get(definition.category, 0.0) + weighted
            )
            contributions[definition.effect] = contributions.get(definition.effect, 0.0) + weighted
        return contributions, by_category, active

    def _apply_team_contributions(self, base_xg, own, opponent):
        attack_score = (
            own["attack"]
            + own["control"] * 0.55
            + own["strength"] * 0.45
            + own["form"] * 0.5
            + own["player"] * 0.45
            + own["motivation"] * 0.4
            + own["h2h"] * 0.35
            + own["set_piece"] * 0.35
            + own["market"] * 0.35
            + own["stamina"] * 0.25
            + own["depth"] * 0.2
        )
        defensive_resistance = (
            opponent["defense"] * 0.7
            + opponent["control"] * 0.25
            + opponent["discipline"] * 0.25
            + opponent["stamina"] * 0.2
        )
        return base_xg + (attack_score - defensive_resistance) * self.FACTOR_GOAL_SCALE

    def adjust_expectations(self, home, away, match_context=None):
        match_context = match_context or {}
        home_exp = home.avg_xg
        away_exp = away.avg_xg

        slaughter, _ = self.is_slaughter_mode_triggered(home, away)
        if slaughter:
            if home.elo_rating > away.elo_rating:
                home_exp *= 1.75
            else:
                away_exp *= 1.75

        home_generic, _, home_active = self._team_contributions(home, away)
        away_generic, _, away_active = self._team_contributions(away, home)
        home_contrib, home_categories, home_quant = self._quantified_team_contributions(
            home, away
        )
        away_contrib, away_categories, away_quant = self._quantified_team_contributions(
            away, home
        )
        match_contrib, match_categories, match_active = self._match_contributions(match_context)

        for key in home_contrib:
            home_contrib[key] += home_generic.get(key, 0.0) * 0.25
            away_contrib[key] += away_generic.get(key, 0.0) * 0.25

        home_exp = self._apply_team_contributions(home_exp, home_contrib, away_contrib)
        away_exp = self._apply_team_contributions(away_exp, away_contrib, home_contrib)

        tempo_delta = (
            match_contrib.get("tempo", 0.0)
            + match_contrib.get("chaos", 0.0) * 0.8
            - abs(match_contrib.get("weather", 0.0)) * 0.45
            - abs(match_contrib.get("uncertainty", 0.0)) * 0.2
        ) * self.TEMPO_GOAL_SCALE
        card_delta = match_contrib.get("cards", 0.0) * 0.004

        total_before = max(home_exp + away_exp, self.MIN_EXPECTED_GOALS)
        home_share = home_exp / total_before
        home_exp += (tempo_delta + card_delta) * home_share
        away_exp += (tempo_delta + card_delta) * (1 - home_share)

        market_goal_expectation = match_context.get("market_goal_expectation")
        if market_goal_expectation is None:
            market_goal_expectation = match_context.get("over_under_goal_expectation")
        if market_goal_expectation is not None:
            current_total = max(home_exp + away_exp, self.MIN_EXPECTED_GOALS)
            blend_total = (
                current_total * 0.75
                + self._safe_float(market_goal_expectation, current_total) * 0.25
            )
            scale = blend_total / current_total
            home_exp *= scale
            away_exp *= scale

        metadata = {
            "active_factor_count": home_active + away_active + match_active,
            "implemented_factor_count": len(FACTOR_DEFINITIONS),
            "home_category_score": {k: round(v, 4) for k, v in home_categories.items()},
            "away_category_score": {k: round(v, 4) for k, v in away_categories.items()},
            "match_category_score": {k: round(v, 4) for k, v in match_categories.items()},
            "home_quantified": {k: round(v, 4) for k, v in home_quant.items()},
            "away_quantified": {k: round(v, 4) for k, v in away_quant.items()},
        }
        return (
            round(max(home_exp, self.MIN_EXPECTED_GOALS), 4),
            round(max(away_exp, self.MIN_EXPECTED_GOALS), 4),
            metadata,
        )

    def _score_distribution(self, lambda_h, lambda_a, home_live_goals=0, away_live_goals=0):
        home_remaining_max = max(self.MAX_GOALS - home_live_goals, 0)
        away_remaining_max = max(self.MAX_GOALS - away_live_goals, 0)
        scores = []
        for home_remaining in range(home_remaining_max + 1):
            for away_remaining in range(away_remaining_max + 1):
                probability = poisson.pmf(home_remaining, lambda_h) * poisson.pmf(
                    away_remaining, lambda_a
                )
                scores.append(
                    {
                        "score": (
                            f"{home_live_goals + home_remaining}-"
                            f"{away_live_goals + away_remaining}"
                        ),
                        "probability": round(probability * 100, 2),
                    }
                )
        return sorted(scores, key=lambda item: item["probability"], reverse=True)[:5]

    def _live_adjusted_lambdas(self, lambda_h, lambda_a, match_context):
        match_minute = match_context.get("match_minute")
        if match_minute is None:
            return lambda_h, lambda_a
        remaining_share = self._clamp(
            (95.0 - self._safe_float(match_minute)) / 95.0, 0.0, 1.0
        )
        score_gap = abs(
            self._safe_float(match_context.get("home_live_goals"), 0.0)
            - self._safe_float(match_context.get("away_live_goals"), 0.0)
        )
        game_state_slowdown = 1.0 - min(score_gap, 4) * 0.08
        return (
            lambda_h * remaining_share * game_state_slowdown,
            lambda_a * remaining_share * game_state_slowdown,
        )

    def predict(self, home, away, match_context=None):
        match_context = match_context or {}
        lambda_h, lambda_a, factor_metadata = self.adjust_expectations(home, away, match_context)
        live_lambda_h, live_lambda_a = self._live_adjusted_lambdas(
            lambda_h, lambda_a, match_context
        )
        home_live_goals = int(match_context.get("home_live_goals", home.live_goals) or 0)
        away_live_goals = int(match_context.get("away_live_goals", away.live_goals) or 0)
        geopolitical_pressure = max(
            self._safe_float(match_context.get("political_tension"), 0.0),
            self._safe_float(match_context.get("diplomatic_friction"), 0.0),
            self._safe_float(match_context.get("historic_rivalry"), 0.0),
        )
        return {
            "expected_goals": {
                "home": round(home_live_goals + live_lambda_h, 4),
                "away": round(away_live_goals + live_lambda_a, 4),
                "total": round(
                    home_live_goals + away_live_goals + live_lambda_h + live_lambda_a,
                    4,
                ),
                "pre_match_home": lambda_h,
                "pre_match_away": lambda_a,
                "remaining_home": round(live_lambda_h, 4),
                "remaining_away": round(live_lambda_a, 4),
            },
            "top_scores": self._score_distribution(
                live_lambda_h, live_lambda_a, home_live_goals, away_live_goals
            ),
            "factor_model": factor_metadata,
            "flags": {
                "slaughter_mode": self.is_slaughter_mode_triggered(home, away)[0],
                "live_data_applied": match_context.get("match_minute") is not None
                or home_live_goals > 0
                or away_live_goals > 0,
                "geopolitical_pressure": geopolitical_pressure >= 70.0,
            },
        }
