def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def num(values, key, default=0.0):
    try:
        return float(values.get(key, default))
    except (TypeError, ValueError):
        return default


def ratio(numerator, denominator, default=0.0):
    denominator = float(denominator or 0.0)
    if denominator == 0:
        return default
    return float(numerator) / denominator


def norm(value, low, high, inverse=False):
    if high == low:
        return 0.5
    score = (value - low) / (high - low)
    score = clamp(score)
    return 1.0 - score if inverse else score


def norm_pct(value, inverse=False):
    return norm(value, 0.0, 100.0, inverse=inverse)


def strength_score(team, opponent):
    elo_diff = clamp((num(team, "elo_rating", 1800) - num(opponent, "elo_rating", 1800) + 500) / 1000)
    fifa_rank = norm(num(team, "fifa_ranking", 100), 1, 200, inverse=True)
    value_ratio = clamp(ratio(num(team, "squad_market_value", 450), num(opponent, "squad_market_value", 450), 1), 0.2, 5)
    value_score = norm(value_ratio, 0.2, 5)
    star_score = norm(num(team, "star_player_count", 2), 0, 8)
    age_score = 1.0 - clamp(abs(num(team, "average_age", 27) - 27) / 8)
    height_score = norm(num(team, "average_height", 181), 170, 192)
    continent_score = norm_pct(num(team, "continental_coefficient", 50))
    youth_score = norm_pct(num(team, "youth_development_index", 50))
    return {
        "q_strength": (
            elo_diff * 0.35
            + fifa_rank * 0.20
            + value_score * 0.14
            + star_score * 0.09
            + age_score * 0.05
            + height_score * 0.04
            + continent_score * 0.08
            + youth_score * 0.05
        ),
        "elo_diff_score": elo_diff,
        "fifa_rank_score": fifa_rank,
        "market_value_ratio_score": value_score,
    }


def attack_score(team):
    xg = norm(num(team, "expected_goals", 1.4), 0, 3)
    goals = norm(num(team, "goals_per_game", 1.4), 0, 3)
    conversion = norm(num(team, "shot_conversion_rate", 12), 0, 30)
    shot_quality = norm(
        num(team, "shot_quality_score", ratio(num(team, "expected_goals", 1.4), num(team, "shots_per_game", 12), 0.12)),
        0.05,
        0.25,
    )
    big_chances = norm(num(team, "big_chance_creation", num(team, "chances_created_per_game", 1.2)), 0, 3)
    box_entries = norm(num(team, "penalty_area_entries", 12), 5, 25)
    press = norm(num(team, "pressing_intensity", num(team, "high_press_intensity", 40)), 20, 60)
    fast_break = norm(num(team, "fast_break_efficiency", num(team, "counter_attack_goal_rate", 15) / 100), 0, 0.5)
    shot_on_target = norm(num(team, "shot_on_target_rate", 35), 15, 55)
    set_piece = norm(num(team, "set_piece_goal_rate", 25), 0, 55)
    key_passes = norm(num(team, "key_passes_per_game", 9), 0, 18)
    dribbles = norm(num(team, "dribbles_per_game", 8), 0, 18)
    return {
        "q_attack": (
            xg * 0.22
            + goals * 0.17
            + conversion * 0.12
            + shot_quality * 0.08
            + big_chances * 0.12
            + box_entries * 0.08
            + press * 0.08
            + fast_break * 0.05
            + shot_on_target * 0.03
            + set_piece * 0.02
            + key_passes * 0.02
            + dribbles * 0.01
        ),
        "shot_quality_score": shot_quality,
        "big_chance_creation_score": big_chances,
        "penalty_area_entries_score": box_entries,
    }


def defense_score(team):
    xga = norm(num(team, "expected_goals_against", 1.2), 0, 3, inverse=True)
    conceded = norm(num(team, "goals_conceded_per_game", 1.2), 0, 3, inverse=True)
    clean_sheet = norm_pct(num(team, "clean_sheet_rate", 30))
    duel = norm(num(team, "defensive_duel_rate", num(team, "tackle_success_rate", 60) / 100), 0.5, 0.85)
    aerial = norm(num(team, "aerial_duel_rate", 0.55), 0.4, 0.75)
    interception = norm(num(team, "interception_efficiency", ratio(num(team, "interceptions_per_game", 10), 350, 0.03)), 0.01, 0.05)
    line = norm(num(team, "defensive_line_cohesion", 0.85), 0.7, 0.98)
    save = norm_pct(num(team, "goalkeeper_save_rate", 70))
    absent_loss = norm(num(team, "defensive_core_absent", 0) * 0.12, 0, 0.36, inverse=True)
    fouls = norm(num(team, "fouls_per_game", 12), 5, 22, inverse=True)
    return {
        "q_defense": (
            xga * 0.22
            + clean_sheet * 0.17
            + duel * 0.16
            + interception * 0.12
            + line * 0.09
            + aerial * 0.09
            + save * 0.07
            + conceded * 0.04
            + absent_loss * 0.03
            + fouls * 0.01
        ),
        "defensive_duel_score": duel,
        "interception_efficiency_score": interception,
        "defensive_core_available_score": absent_loss,
    }


def midfield_score(team):
    possession = norm_pct(num(team, "possession_rate", 50))
    pass_success = norm(num(team, "pass_success_rate", 82), 65, 92)
    final_third = norm(num(team, "final_third_pass_success_rate", 70), 50, 85)
    key_passes = norm(num(team, "midfield_key_passes", num(team, "key_passes_per_game", 9)), 0, 18)
    chances = norm(num(team, "chances_created_per_game", 10), 0, 22)
    core_available = norm(num(team, "midfield_core_absent", 0), 0, 2, inverse=True)
    transition = norm(num(team, "transition_speed", 50), 0, 100)
    high_press = norm(num(team, "high_press_intensity", 50), 0, 100)
    return {
        "q_midfield": (
            possession * 0.15
            + pass_success * 0.18
            + final_third * 0.10
            + key_passes * 0.15
            + chances * 0.16
            + core_available * 0.12
            + transition * 0.07
            + high_press * 0.07
        ),
        "pass_control_score": pass_success,
        "chance_creation_score": chances,
    }


def form_score(team):
    last5 = norm(num(team, "last5_form_points", 7.5), 0, 15)
    handicap = norm_pct(num(team, "last5_handicap_win_rate", 50))
    over = norm_pct(num(team, "last5_over_rate", 50))
    scoring = norm(num(team, "consecutive_scoring_matches", 3), 0, 8)
    conceding = norm(num(team, "consecutive_conceding_matches", 2), 0, 8, inverse=True)
    forward = norm(num(team, "core_forward_rating", 6.8), 5.5, 8.5)
    midfielder = norm(num(team, "core_midfielder_rating", 6.8), 5.5, 8.5)
    defender = norm(num(team, "core_defender_rating", 6.8), 5.5, 8.5)
    goalkeeper = norm(num(team, "goalkeeper_rating", 6.8), 5.5, 8.5)
    morale = norm_pct(num(team, "team_morale", 50))
    return {
        "q_form": (
            last5 * 0.18
            + handicap * 0.06
            + over * 0.04
            + scoring * 0.10
            + conceding * 0.06
            + forward * 0.18
            + midfielder * 0.13
            + defender * 0.12
            + goalkeeper * 0.06
            + morale * 0.07
        ),
        "core_forward_state_index": (num(team, "core_forward_rating", 6.8) - 6) * 0.2,
        "morale_score": morale,
    }


def player_score(team):
    scorer = norm_pct(num(team, "top_scorer_form", 50))
    assist = norm_pct(num(team, "assist_leader_form", 50))
    captain = norm(num(team, "captain_absent", 0), 0, 1, inverse=True)
    goalkeeper = norm(num(team, "goalkeeper_absent", 0), 0, 1, inverse=True)
    yellow = norm(num(team, "yellow_card_suspensions", 0), 0, 3, inverse=True)
    red = norm(num(team, "red_card_suspensions", 0), 0, 2, inverse=True)
    returned = norm(num(team, "key_player_returned", 0), 0, 2)
    age_structure = norm_pct(num(team, "age_structure", 50))
    experience = norm(num(team, "tournament_experience", 20), 0, 80)
    penalty = norm_pct(num(team, "penalty_taker_ability", 75))
    set_piece = norm_pct(num(team, "set_piece_taker_ability", 50))
    stamina = norm_pct(num(team, "stamina_reserve", 50))
    goal_involvement = norm(num(team, "goal_involvement_index", 0.45), 0, 1.5)
    key_impact = norm(num(team, "key_player_impact", 0.0), -0.5, 1.0)
    fatigue = norm(num(team, "fatigue_index", 0.5), 0, 1.2, inverse=True)
    return {
        "q_player": (
            scorer * 0.14
            + assist * 0.09
            + captain * 0.08
            + goalkeeper * 0.08
            + yellow * 0.06
            + red * 0.06
            + returned * 0.04
            + age_structure * 0.04
            + experience * 0.08
            + penalty * 0.04
            + set_piece * 0.04
            + stamina * 0.08
            + goal_involvement * 0.08
            + key_impact * 0.06
            + fatigue * 0.03
        ),
        "goal_involvement_score": goal_involvement,
        "key_player_impact_score": key_impact,
        "fatigue_available_score": fatigue,
    }


def first_six_category_scores(team, opponent):
    scores = {}
    scores.update(strength_score(team, opponent))
    scores.update(attack_score(team))
    scores.update(defense_score(team))
    scores.update(midfield_score(team))
    scores.update(form_score(team))
    scores.update(player_score(team))
    scores["q_team"] = (
        scores["q_strength"] * 0.18
        + scores["q_attack"] * 0.24
        + scores["q_defense"] * 0.22
        + scores["q_midfield"] * 0.14
        + scores["q_form"] * 0.12
        + scores["q_player"] * 0.10
    )
    return scores
