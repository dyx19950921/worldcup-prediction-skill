# 世界杯预测Skill v3.0

## 快速启动

```bash
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

## 测试
```bash
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"home_team\":\"德国\",\"away_team\":\"库拉索\",\"home_elo\":2017,\"away_elo\":850}"
```
