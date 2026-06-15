from fastapi import FastAPI
from pydantic import BaseModel
from prediction_model import PredictionModel, TeamStats
import time

app = FastAPI(title="世界杯预测API")
model = PredictionModel()

class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    home_elo: int
    away_elo: int
    home_avg_xg: float = 1.2
    away_avg_xg: float = 1.0
    group_pressure: bool = False

@app.get("/")
async def root():
    return {"service": "世界杯预测API", "version": "3.0"}

@app.post("/predict")
async def predict(req: PredictRequest):
    start = time.time()
    home = TeamStats(
        name=req.home_team, elo_rating=req.home_elo,
        avg_goals_per_game=req.home_avg_xg*0.9, avg_xg=req.home_avg_xg,
        missing_defensive_key_players=req.home_missing_defense,
        missing_offensive_key_players=0, group_pressure=req.group_pressure
    )
    away = TeamStats(
        name=req.away_team, elo_rating=req.away_elo,
        avg_goals_per_game=req.away_avg_xg*0.9, avg_xg=req.away_avg_xg,
        missing_defensive_key_players=req.away_missing_defense,
        missing_offensive_key_players=0, group_pressure=req.group_pressure
    )
    result = model.predict(home, away)
    result["time_ms"] = round((time.time() - start) * 1000, 2)
