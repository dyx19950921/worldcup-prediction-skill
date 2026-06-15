from dataclasses import dataclass


@dataclass(frozen=True)
class FactorDefinition:
    id: int
    key: str
    label: str
    category: str
    weight: float
    scope: str
    effect: str
    neutral: float
    scale: float
    direction: float = 1.0


FACTOR_ROWS = [
    (1, "elo_rating", "ELO rating", "strength", 8, "team", "strength", 1800, 350, 1),
    (2, "fifa_ranking", "FIFA ranking", "strength", 5, "team", "strength", 30, 80, -1),
    (3, "squad_market_value", "Squad market value", "strength", 3, "team", "strength", 450, 700, 1),
    (4, "star_player_count", "Star player count", "strength", 2, "team", "attack", 2, 5, 1),
    (5, "average_age", "Average age", "strength", 1, "team", "strength", 27, 4, -0.4),
    (6, "average_height", "Average height", "strength", 1, "team", "set_piece", 181, 8, 1),
    (7, "continental_coefficient", "Continental coefficient", "strength", 2, "team", "strength", 50, 30, 1),
    (8, "youth_development_index", "Youth development index", "strength", 1, "team", "strength", 50, 30, 1),
    (9, "goals_per_game", "Goals per game", "attack", 5, "team", "attack", 1.4, 1.2, 1),
    (10, "expected_goals", "Expected goals", "attack", 5, "team", "attack", 1.4, 1.2, 1),
    (11, "shot_conversion_rate", "Shot conversion rate", "attack", 3, "team", "attack", 12, 10, 1),
    (12, "shot_on_target_rate", "Shot on target rate", "attack", 2, "team", "attack", 35, 18, 1),
    (13, "set_piece_goal_rate", "Set piece goal rate", "attack", 2, "team", "set_piece", 25, 20, 1),
    (14, "counter_attack_goal_rate", "Counter attack goal rate", "attack", 2, "team", "attack", 15, 15, 1),
    (15, "header_goal_rate", "Header goal rate", "attack", 1, "team", "set_piece", 18, 15, 1),
    (16, "long_shot_goal_rate", "Long shot goal rate", "attack", 1, "team", "attack", 12, 12, 1),
    (17, "penalty_goal_rate", "Penalty goal rate", "attack", 1, "team", "attack", 75, 25, 1),
    (18, "shots_per_game", "Shots per game", "attack", 2, "team", "attack", 12, 7, 1),
    (19, "key_passes_per_game", "Key passes per game", "attack", 2, "team", "attack", 9, 6, 1),
    (20, "dribbles_per_game", "Dribbles per game", "attack", 1, "team", "attack", 8, 6, 1),
    (21, "goals_conceded_per_game", "Goals conceded per game", "defense", 4, "team", "defense", 1.2, 1.0, -1),
    (22, "expected_goals_against", "Expected goals against", "defense", 3, "team", "defense", 1.2, 1.0, -1),
    (23, "clean_sheet_rate", "Clean sheet rate", "defense", 2, "team", "defense", 30, 25, 1),
    (24, "tackle_success_rate", "Tackle success rate", "defense", 2, "team", "defense", 60, 25, 1),
    (25, "interceptions_per_game", "Interceptions per game", "defense", 1, "team", "defense", 10, 8, 1),
    (26, "clearances_per_game", "Clearances per game", "defense", 1, "team", "defense", 18, 12, 1),
    (27, "blocks_per_game", "Blocks per game", "defense", 1, "team", "defense", 3, 3, 1),
    (28, "fouls_per_game", "Fouls per game", "defense", 1, "team", "discipline", 12, 8, -1),
    (29, "defensive_core_absent", "Defensive core absent", "defense", 3, "team", "defense", 0, 2, -1),
    (30, "goalkeeper_save_rate", "Goalkeeper save rate", "defense", 2, "team", "defense", 70, 20, 1),
    (31, "possession_rate", "Possession rate", "midfield", 2, "team", "control", 50, 25, 1),
    (32, "pass_success_rate", "Pass success rate", "midfield", 2, "team", "control", 82, 12, 1),
    (33, "final_third_pass_success_rate", "Final-third pass success rate", "midfield", 1, "team", "control", 70, 15, 1),
    (34, "midfield_key_passes", "Midfield key passes", "midfield", 2, "team", "control", 9, 6, 1),
    (35, "chances_created_per_game", "Chances created per game", "midfield", 2, "team", "control", 10, 7, 1),
    (36, "midfield_core_absent", "Midfield core absent", "midfield", 2, "team", "control", 0, 2, -1),
    (37, "transition_speed", "Transition speed", "midfield", 1, "team", "attack", 50, 30, 1),
    (38, "high_press_intensity", "High press intensity", "midfield", 1, "team", "control", 50, 30, 1),
    (39, "last5_form_points", "Last 5 form points", "form", 3, "team", "form", 7.5, 7.5, 1),
    (40, "last5_handicap_win_rate", "Last 5 handicap win rate", "form", 1, "team", "form", 50, 35, 1),
    (41, "last5_over_rate", "Last 5 over rate", "form", 1, "team", "tempo", 50, 35, 1),
    (42, "consecutive_scoring_matches", "Consecutive scoring matches", "form", 2, "team", "attack", 3, 5, 1),
    (43, "consecutive_conceding_matches", "Consecutive conceding matches", "form", 1, "team", "defense", 2, 5, -1),
    (44, "core_forward_rating", "Core forward rating", "form", 3, "team", "attack", 6.8, 1.4, 1),
    (45, "core_midfielder_rating", "Core midfielder rating", "form", 2, "team", "control", 6.8, 1.4, 1),
    (46, "core_defender_rating", "Core defender rating", "form", 2, "team", "defense", 6.8, 1.4, 1),
    (47, "goalkeeper_rating", "Goalkeeper rating", "form", 1, "team", "defense", 6.8, 1.4, 1),
    (48, "team_morale", "Team morale", "form", 1, "team", "form", 50, 30, 1),
    (49, "top_scorer_form", "Top scorer form", "player", 3, "team", "attack", 50, 30, 1),
    (50, "assist_leader_form", "Assist leader form", "player", 2, "team", "attack", 50, 30, 1),
    (51, "captain_absent", "Captain absent", "player", 2, "team", "form", 0, 1, -1),
    (52, "goalkeeper_absent", "Goalkeeper absent", "player", 2, "team", "defense", 0, 1, -1),
    (53, "yellow_card_suspensions", "Yellow-card suspensions", "player", 2, "team", "depth", 0, 3, -1),
    (54, "red_card_suspensions", "Red-card suspensions", "player", 2, "team", "depth", 0, 2, -1),
    (55, "key_player_returned", "Key player returned", "player", 1, "team", "form", 0, 2, 1),
    (56, "age_structure", "Age structure", "player", 1, "team", "depth", 50, 30, 1),
    (57, "tournament_experience", "Tournament experience", "player", 2, "team", "strength", 20, 35, 1),
    (58, "penalty_taker_ability", "Penalty taker ability", "player", 1, "team", "attack", 75, 25, 1),
    (59, "set_piece_taker_ability", "Set piece taker ability", "player", 1, "team", "set_piece", 50, 30, 1),
    (60, "stamina_reserve", "Stamina reserve", "player", 1, "team", "stamina", 50, 30, 1),
    (61, "group_qualification_pressure", "Group qualification pressure", "motivation", 3, "team", "motivation", 50, 40, 1),
    (62, "goal_difference_need", "Goal-difference need", "motivation", 2, "team", "attack", 0, 3, 1),
    (63, "opponent_eliminated", "Opponent eliminated", "motivation", 2, "team", "motivation", 0, 1, 1),
    (64, "already_qualified", "Already qualified", "motivation", -2, "team", "motivation", 0, 1, 1),
    (65, "knockout_match", "Knockout match", "motivation", 2, "match", "tempo", 0, 1, 1),
    (66, "historic_rivalry", "Historic rivalry", "motivation", 1, "match", "tempo", 0, 100, 1),
    (67, "revenge_motivation", "Revenge motivation", "motivation", 1, "team", "motivation", 0, 1, 1),
    (68, "rest_days_advantage", "Rest days advantage", "motivation", 1, "team", "stamina", 0, 4, 1),
    (69, "travel_fatigue", "Travel fatigue", "motivation", 1, "team", "stamina", 0, 9000, -1),
    (70, "home_fan_support", "Home fan support", "motivation", 1, "team", "motivation", 50, 50, 1),
    (71, "h2h_total_win_rate", "H2H total win rate", "h2h", 2, "team", "h2h", 50, 35, 1),
    (72, "h2h_last3_points", "H2H last 3 points", "h2h", 2, "team", "h2h", 4.5, 4.5, 1),
    (73, "h2h_home_record", "H2H home record", "h2h", 1, "team", "h2h", 50, 35, 1),
    (74, "h2h_biggest_win_margin", "H2H biggest win margin", "h2h", 1, "team", "h2h", 0, 4, 1),
    (75, "h2h_goals_per_game", "H2H goals per game", "h2h", 1, "match", "tempo", 2.5, 2, 1),
    (76, "h2h_psychological_edge", "H2H psychological edge", "h2h", 1, "team", "h2h", 0, 5, 1),
    (77, "tactical_matchup_advantage", "Tactical matchup advantage", "h2h", 1, "team", "h2h", 0, 100, 1),
    (78, "coach_h2h_win_rate", "Coach H2H win rate", "h2h", 1, "team", "h2h", 50, 35, 1),
    (79, "referee_yellow_cards_per_game", "Referee yellows per game", "environment", 2, "match", "cards", 4, 3, 1),
    (80, "referee_red_cards_per_game", "Referee reds per game", "environment", 1, "match", "cards", 0.2, 0.4, 1),
    (81, "referee_penalties_per_game", "Referee penalties per game", "environment", 1, "match", "tempo", 0.25, 0.4, 1),
    (82, "temperature_c", "Temperature C", "environment", 1, "match", "weather", 22, 18, -1),
    (83, "humidity_pct", "Humidity pct", "environment", 1, "match", "weather", 55, 40, -1),
    (84, "rainfall_mm", "Rainfall mm", "environment", 1, "match", "weather", 0, 20, -1),
    (85, "wind_speed_kmh", "Wind speed kmh", "environment", 0.5, "match", "weather", 8, 35, -1),
    (86, "altitude_m", "Altitude m", "environment", 1, "match", "weather", 300, 2200, -1),
    (87, "pitch_quality", "Pitch quality", "environment", 0.5, "match", "tempo", 70, 30, 1),
    (88, "var_intervention_rate", "VAR intervention rate", "environment", 1, "match", "tempo", 0.35, 0.5, 1),
    (89, "win_draw_loss_odds_probability", "WDL odds probability", "market", 2, "team", "market", 50, 35, 1),
    (90, "handicap_odds_confidence", "Handicap odds confidence", "market", 2, "team", "market", 50, 35, 1),
    (91, "over_under_goal_expectation", "Over-under goal expectation", "market", 1, "match", "tempo", 2.5, 2, 1),
    (92, "odds_trend", "Odds trend", "market", 2, "team", "market", 0, 100, 1),
    (93, "kelly_index", "Kelly index", "market", 1, "team", "market", 1, 0.4, -1),
    (94, "betfair_volume_share", "Betfair volume share", "market", 1, "team", "market", 50, 35, 1),
    (95, "odds_dispersion", "Odds dispersion", "market", 1, "match", "uncertainty", 0, 1, -1),
    (96, "late_odds_movement", "Late odds movement", "market", 1, "team", "market", 0, 100, 1),
    (97, "red_card_probability", "Red card probability", "special", 1, "match", "cards", 0.15, 0.4, 1),
    (98, "penalty_probability", "Penalty probability", "special", 1, "match", "tempo", 0.25, 0.4, 1),
    (99, "own_goal_probability", "Own goal probability", "special", 0.5, "match", "chaos", 0.03, 0.08, 1),
    (100, "stoppage_time_goal_probability", "Stoppage-time goal probability", "special", 0.5, "match", "tempo", 0.18, 0.25, 1),
]

FACTOR_DEFINITIONS = [FactorDefinition(*row) for row in FACTOR_ROWS]
FACTOR_BY_KEY = {factor.key: factor for factor in FACTOR_DEFINITIONS}
TEAM_FACTOR_KEYS = [factor.key for factor in FACTOR_DEFINITIONS if factor.scope == "team"]
MATCH_FACTOR_KEYS = [factor.key for factor in FACTOR_DEFINITIONS if factor.scope == "match"]
CATEGORY_WEIGHTS = {}
for factor in FACTOR_DEFINITIONS:
    CATEGORY_WEIGHTS[factor.category] = CATEGORY_WEIGHTS.get(factor.category, 0.0) + factor.weight
