# World Cup Prediction Skill v4.0

## Quick Start

```bash
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

## API Endpoints

- `POST /predict` - Match prediction
- `GET /` - Service info
- `GET /factors` - 100-factor registry, including keys, labels, scopes, categories, and weights
- `GET /data-sources` - Free data-source registry and factor coverage map
- `GET /data-sources/{factor_key}` - Free sources for one factor key

## 100-Factor Model

The model now implements the full 100-factor structure:

- strength: 8 factors
- attack: 12 factors
- defense: 10 factors
- midfield control: 8 factors
- form: 10 factors
- individual player: 12 factors
- motivation: 10 factors
- head-to-head: 8 factors
- environment and referee: 10 factors
- market and odds: 8 factors
- special events: 4 factors

Send team-side values in `home_factors` and `away_factors`; send shared match values in `match_factors`.
Use `GET /factors` to retrieve the exact supported keys.

## Quantified Categories 1-6

The first six categories are implemented as concrete formulas in `quantification.py`:

- `q_strength`: ELO difference, FIFA ranking, market-value ratio, stars, age, height, continent, youth index
- `q_attack`: xG, goals average, shot conversion, shot quality, big chances, box entries, pressing, fast-break efficiency
- `q_defense`: xGA, clean sheets, duel rate, interception efficiency, line cohesion, aerial duels, goalkeeper save rate, absences
- `q_midfield`: possession, pass success, final-third passing, key passes, chance creation, midfield absences, transition, high press
- `q_form`: last-5 results, handicap/over rates, scoring/conceding streaks, core player ratings, morale
- `q_player`: top scorer, assist leader, captain/goalkeeper absences, suspensions, returnees, age mix, experience, penalty/set-piece takers, stamina

Prediction responses include these values under `factor_model.home_quantified` and `factor_model.away_quantified`.

## Free Data Sources

The free-source mapping is implemented in `data_sources.py`:

- xG/xA: Understat via `understatapi` or `underdata`
- player ratings: `soccerdata` WhoScored
- team stats: `soccerdata` FBref
- Elo: `soccerdata` Club Elo, with national-team Elo needing a national-team feed
- fixtures and results: Football-Data.org
- referee cards and penalties: WorldReferee
- weather: OpenWeatherMap
- injuries and market value: Transfermarkt
- odds: Jiebao / 007 Scout style public odds pages

Collector dependencies are optional:

```bash
pip install -r requirements-collectors.txt
```

Example for a live Sweden vs Tunisia state where the current score is 5-1:

```json
{
  "home_team": "Sweden",
  "away_team": "Tunisia",
  "home_elo": 1780,
  "away_elo": 1620,
  "home_avg_xg": 1.5,
  "away_avg_xg": 1.0,
  "home_live_goals": 5,
  "away_live_goals": 1,
  "match_minute": 90,
  "group_pressure": true,
  "home_factors": {
    "fifa_ranking": 28,
    "squad_market_value": 330,
    "goals_per_game": 1.8,
    "shot_conversion_rate": 15,
    "core_forward_rating": 7.4,
    "group_qualification_pressure": 80
  },
  "away_factors": {
    "fifa_ranking": 42,
    "squad_market_value": 70,
    "goals_conceded_per_game": 1.6,
    "defensive_core_absent": 1,
    "goalkeeper_save_rate": 61,
    "travel_fatigue": 3200
  },
  "match_factors": {
    "referee_yellow_cards_per_game": 4.8,
    "referee_penalties_per_game": 0.32,
    "historic_rivalry": 20,
    "temperature_c": 28,
    "humidity_pct": 65,
    "over_under_goal_expectation": 3.1
  }
}
```
