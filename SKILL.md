---
name: worldcup-prediction-skill
description: World Cup match prediction helper using the bundled FastAPI service and Python prediction model. Use when the user asks Codex to predict football/soccer match outcomes, run or modify the World Cup prediction API, compare teams by Elo/xG/injuries/group pressure, or explain the prediction model behavior.
---

# World Cup Prediction Skill

Use this skill for soccer match prediction tasks that can be modeled with Elo ratings, expected goals, defensive absences, and group-stage pressure.

## Bundled Files

- `prediction_model.py`: Core prediction logic with `TeamStats` and `PredictionModel`.
- `api.py`: FastAPI wrapper exposing `GET /` and `POST /predict`.
- `requirements.txt`: Python dependencies for the local API.

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
  "home_missing_defense": 0,
  "away_missing_defense": 1,
  "group_pressure": true
}
```

## Notes

- Treat outputs as heuristic predictions, not betting advice.
- If the user asks for real current team ratings, injuries, schedules, or odds, browse or use current data sources first.
- Keep changes to the model explicit: name what variables changed and how they affect expected goals or flags.
