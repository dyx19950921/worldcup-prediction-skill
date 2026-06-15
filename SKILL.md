---
name: worldcup-prediction-skill
description: World Cup match prediction helper using the bundled FastAPI service and Python prediction model. Use when the user asks Codex to predict football/soccer match outcomes, run or modify the World Cup prediction API, compare teams by Elo/xG/injuries/group pressure, or explain the prediction model behavior.
---

# World Cup Prediction Skill

Use this skill for soccer match prediction tasks that can be modeled with the full 100-factor registry: strength, attack, defense, midfield control, form, individual player state, motivation, head-to-head history, referee/environment, market odds, special events, and live score state.

## Bundled Files

- `factor_definitions.py`: The 100-factor registry with ids, stable keys, labels, categories, scopes, neutral values, directions, and weights.
- `quantification.py`: Concrete quantitative formulas for categories 1-6: strength, attack, defense, midfield, form, and player factors.
- `data_sources.py`: Free data-source registry mapping factor keys to Understat, soccerdata, Football-Data.org, WorldReferee, OpenWeatherMap, Transfermarkt, and odds pages.
- `prediction_model.py`: Core prediction logic with `TeamStats` and `PredictionModel`.
- `api.py`: FastAPI wrapper exposing `GET /` and `POST /predict`.
- `requirements.txt`: Python dependencies for the local API.
- `requirements-collectors.txt`: Optional collector dependencies for data ingestion.

## Quick Workflow

1. Read `prediction_model.py` before changing prediction logic.
2. For direct predictions, instantiate `TeamStats` and call `PredictionModel().predict(home, away)`.
3. For API usage, install dependencies and run:

```powershell
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

4. Send `POST /predict` JSON with:

```json
{
  "home_team": "Brazil",
  "away_team": "Germany",
  "home_elo": 2100,
  "away_elo": 2000,
  "home_avg_xg": 1.8,
  "away_avg_xg": 1.5,
  "home_factors": {
    "fifa_ranking": 3,
    "squad_market_value": 950,
    "goals_per_game": 2.1,
    "core_forward_rating": 7.5
  },
  "away_factors": {
    "fifa_ranking": 12,
    "squad_market_value": 650,
    "goals_conceded_per_game": 1.1,
    "defensive_core_absent": 1
  },
  "match_factors": {
    "referee_yellow_cards_per_game": 4.2,
    "historic_rivalry": 35,
    "over_under_goal_expectation": 2.8
  },
  "match_minute": 90,
  "home_live_goals": 5,
  "away_live_goals": 1,
  "group_pressure": true
}
```

## Notes

- Treat outputs as heuristic predictions, not betting advice.
- If the user asks for real current team ratings, injuries, schedules, or odds, browse or use current data sources first.
- Keep changes to the model explicit: name what variables changed and how they affect expected goals, live remaining goals, top scores, or flags.
- When live score data is available, pass `match_minute`, `home_live_goals`, and `away_live_goals`; the model will anchor score probabilities to the observed score instead of returning a stale pre-match scoreline.
- Use `GET /factors` or read `factor_definitions.py` for exact factor keys. Team-scoped keys go in `home_factors` and `away_factors`; match-scoped keys go in `match_factors`.
- The response includes `factor_model.home_quantified` and `factor_model.away_quantified`; check `q_strength`, `q_attack`, `q_defense`, `q_midfield`, `q_form`, `q_player`, and `q_team` to explain how categories 1-6 affected expected goals.
- Use `GET /data-sources` to see which free source can populate each factor. Keep scraping sources cached and respectful of site terms.
