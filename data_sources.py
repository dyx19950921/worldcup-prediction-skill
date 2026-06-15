from dataclasses import dataclass


@dataclass(frozen=True)
class DataSource:
    key: str
    name: str
    kind: str
    access: str
    update_frequency: str
    library_or_method: str
    env_var: str
    factor_keys: tuple[str, ...]
    notes: str


DATA_SOURCES = [
    DataSource(
        key="understat",
        name="Understat",
        kind="xg_xa",
        access="free_unofficial",
        update_frequency="daily",
        library_or_method="understatapi or underdata",
        env_var="",
        factor_keys=(
            "expected_goals",
            "expected_goals_against",
            "shot_quality_score",
            "big_chance_creation",
            "key_player_impact",
        ),
        notes="Use for xG, xGA, shot quality, and player/team xG impact where coverage exists.",
    ),
    DataSource(
        key="soccerdata_whoscored",
        name="soccerdata WhoScored",
        kind="player_ratings",
        access="free_scrape",
        update_frequency="matchday",
        library_or_method="soccerdata",
        env_var="",
        factor_keys=(
            "core_forward_rating",
            "core_midfielder_rating",
            "core_defender_rating",
            "goalkeeper_rating",
            "top_scorer_form",
            "assist_leader_form",
            "goal_involvement_index",
            "form_trend_slope",
            "set_piece_taker_ability",
            "stamina_reserve",
            "disciplinary_risk",
        ),
        notes="Use for ratings, player form, cards, minutes, assists, and individual contribution metrics.",
    ),
    DataSource(
        key="soccerdata_fbref",
        name="soccerdata FBref",
        kind="team_stats",
        access="free_scrape",
        update_frequency="daily",
        library_or_method="soccerdata",
        env_var="",
        factor_keys=(
            "goals_per_game",
            "goals_conceded_per_game",
            "possession_rate",
            "pass_success_rate",
            "final_third_pass_success_rate",
            "shots_per_game",
            "shot_on_target_rate",
            "key_passes_per_game",
            "dribbles_per_game",
            "tackle_success_rate",
            "interceptions_per_game",
            "clearances_per_game",
            "blocks_per_game",
            "fouls_per_game",
            "defensive_duel_rate",
            "aerial_duel_rate",
            "pressing_intensity",
            "high_press_intensity",
            "penalty_area_entries",
        ),
        notes="Use as the main free source for team possession, passing, shooting, and defensive action rates.",
    ),
    DataSource(
        key="soccerdata_clubelo",
        name="soccerdata Club Elo",
        kind="elo",
        access="free",
        update_frequency="daily",
        library_or_method="soccerdata",
        env_var="",
        factor_keys=("elo_rating",),
        notes="Best suited for club teams; national-team Elo may need eloratings.net or another national-team feed.",
    ),
    DataSource(
        key="football_data_org",
        name="Football-Data.org",
        kind="fixtures_results",
        access="free_api_key",
        update_frequency="daily",
        library_or_method="requests",
        env_var="FOOTBALL_DATA_API_KEY",
        factor_keys=(
            "last5_form_points",
            "last5_handicap_win_rate",
            "last5_over_rate",
            "consecutive_scoring_matches",
            "consecutive_conceding_matches",
            "clean_sheet_rate",
            "h2h_total_win_rate",
            "h2h_last3_points",
            "h2h_home_record",
            "h2h_biggest_win_margin",
            "h2h_goals_per_game",
            "revenge_motivation",
        ),
        notes="Use for historical scores, schedules, last-five form, H2H, and clean-sheet calculation.",
    ),
    DataSource(
        key="worldreferee",
        name="WorldReferee",
        kind="referee",
        access="free_scrape",
        update_frequency="pre_match",
        library_or_method="requests + BeautifulSoup",
        env_var="",
        factor_keys=(
            "referee_yellow_cards_per_game",
            "referee_red_cards_per_game",
            "referee_penalties_per_game",
            "var_intervention_rate",
            "red_card_probability",
            "penalty_probability",
        ),
        notes="Use respectfully with caching; referee data may need manual verification for major tournaments.",
    ),
    DataSource(
        key="openweathermap",
        name="OpenWeatherMap",
        kind="weather",
        access="free_api_key",
        update_frequency="real_time",
        library_or_method="requests",
        env_var="OPENWEATHERMAP_API_KEY",
        factor_keys=(
            "temperature_c",
            "humidity_pct",
            "rainfall_mm",
            "wind_speed_kmh",
            "altitude_m",
            "pitch_quality",
        ),
        notes="Use venue coordinates and kickoff time; pitch quality still needs stadium or report input.",
    ),
    DataSource(
        key="transfermarkt",
        name="Transfermarkt",
        kind="injuries_market_value",
        access="free_scrape",
        update_frequency="daily",
        library_or_method="requests + BeautifulSoup",
        env_var="",
        factor_keys=(
            "squad_market_value",
            "star_player_count",
            "defensive_core_absent",
            "midfield_core_absent",
            "captain_absent",
            "goalkeeper_absent",
            "key_player_returned",
            "yellow_card_suspensions",
            "red_card_suspensions",
            "average_age",
            "age_structure",
        ),
        notes="Use for squad values, injuries, suspensions, absences, returns, and age structure.",
    ),
    DataSource(
        key="jiebifen_007",
        name="Jiebao / 007 Scout",
        kind="odds",
        access="free_web",
        update_frequency="real_time",
        library_or_method="requests + BeautifulSoup",
        env_var="",
        factor_keys=(
            "win_draw_loss_odds_probability",
            "handicap_odds_confidence",
            "over_under_goal_expectation",
            "odds_trend",
            "kelly_index",
            "odds_dispersion",
            "late_odds_movement",
        ),
        notes="Use for market snapshots and movement. Scraping terms and availability should be checked before automation.",
    ),
]

TECH_STACK = {
    "collection": [
        "understatapi or underdata for xG/xA",
        "soccerdata for FBref, WhoScored, and Club Elo",
        "requests + BeautifulSoup for Transfermarkt, WorldReferee, and odds pages",
        "OpenWeatherMap API for venue weather",
    ],
    "processing": ["pandas", "numpy"],
    "storage": [
        "SQLite for local historical cache",
        "PostgreSQL for shared production cache",
        "Redis for real-time live score, weather, and odds cache",
    ],
}

SOURCE_BY_KEY = {source.key: source for source in DATA_SOURCES}
FACTOR_TO_SOURCES = {}
for source in DATA_SOURCES:
    for factor_key in source.factor_keys:
        FACTOR_TO_SOURCES.setdefault(factor_key, []).append(source.key)
