from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import math

app = FastAPI(title="RunCalc Pro")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

class PaceRequest(BaseModel):
    distance_km: float
    time_hours: int
    time_minutes: int
    time_seconds: int

class RacePredictor(BaseModel):
    known_distance_km: float
    known_time_minutes: float
    target_distance_km: float

class TrainingZones(BaseModel):
    max_hr: int

class SplitsRequest(BaseModel):
    distance_km: float
    target_pace_per_km_seconds: int
    strategy: str

class VO2MaxRequest(BaseModel):
    distance_km: float
    time_minutes: float

def seconds_to_pace_str(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

def riegel_prediction(t1, d1, d2):
    return t1 * ((d2 / d1) ** 1.06)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/pace")
async def calculate_pace(data: PaceRequest):
    total_seconds = (data.time_hours * 3600) + (data.time_minutes * 60) + data.time_seconds
    if data.distance_km <= 0 or total_seconds <= 0:
        return {"error": "Distance and time must be greater than zero"}
    pace_sec_per_km = total_seconds / data.distance_km
    pace_sec_per_mile = pace_sec_per_km * 1.60934
    speed_kmh = (data.distance_km / total_seconds) * 3600
    return {
        "pace_per_km": seconds_to_pace_str(pace_sec_per_km),
        "pace_per_mile": seconds_to_pace_str(pace_sec_per_mile),
        "speed_kmh": round(speed_kmh, 2),
        "speed_mph": round(speed_kmh / 1.60934, 2),
        "total_time": f"{data.time_hours:02d}:{data.time_minutes:02d}:{data.time_seconds:02d}",
    }

@app.post("/api/predict-race")
async def predict_race(data: RacePredictor):
    if data.known_distance_km <= 0 or data.known_time_minutes <= 0 or data.target_distance_km <= 0:
        return {"error": "All values must be greater than zero"}
    t1 = data.known_time_minutes * 60
    predicted_seconds = riegel_prediction(t1, data.known_distance_km, data.target_distance_km)
    hours = int(predicted_seconds // 3600)
    minutes = int((predicted_seconds % 3600) // 60)
    seconds = int(predicted_seconds % 60)
    pace_per_km = predicted_seconds / data.target_distance_km
    return {
        "predicted_time": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
        "pace_per_km": seconds_to_pace_str(pace_per_km),
        "pace_per_mile": seconds_to_pace_str(pace_per_km * 1.60934),
    }

@app.post("/api/training-zones")
async def training_zones(data: TrainingZones):
    if data.max_hr <= 0 or data.max_hr > 250:
        return {"error": "Max HR must be between 1 and 250"}
    mhr = data.max_hr
    zones = [
        {"zone": 1, "name": "Recovery", "min_pct": 50, "max_pct": 60, "min_hr": round(mhr*0.50), "max_hr": round(mhr*0.60), "color": "#34d399"},
        {"zone": 2, "name": "Aerobic Base", "min_pct": 60, "max_pct": 70, "min_hr": round(mhr*0.60), "max_hr": round(mhr*0.70), "color": "#a3e635"},
        {"zone": 3, "name": "Aerobic", "min_pct": 70, "max_pct": 80, "min_hr": round(mhr*0.70), "max_hr": round(mhr*0.80), "color": "#fbbf24"},
        {"zone": 4, "name": "Threshold", "min_pct": 80, "max_pct": 90, "min_hr": round(mhr*0.80), "max_hr": round(mhr*0.90), "color": "#f97316"},
        {"zone": 5, "name": "VO2 Max", "min_pct": 90, "max_pct": 100, "min_hr": round(mhr*0.90), "max_hr": mhr, "color": "#ef4444"},
    ]
    return {"zones": zones, "max_hr": mhr}

@app.post("/api/splits")
async def calculate_splits(data: SplitsRequest):
    if data.distance_km <= 0 or data.target_pace_per_km_seconds <= 0:
        return {"error": "Invalid input"}
    total_km = data.distance_km
    base_pace = data.target_pace_per_km_seconds
    splits = []
    cumulative = 0
    km_markers = list(range(1, int(total_km) + 1))
    remainder = total_km - int(total_km)
    if remainder > 0.01:
        km_markers.append(round(total_km, 2))
    for i, km in enumerate(km_markers):
        split_dist = km - (km_markers[i-1] if i > 0 else 0)
        if data.strategy == "negative":
            factor = 1.0 + (0.03 * (1 - (km / total_km)))
        elif data.strategy == "positive":
            factor = 1.0 - (0.03 * (1 - (km / total_km)))
        else:
            factor = 1.0
        split_pace = base_pace * factor
        split_time = split_pace * split_dist
        cumulative += split_time
        splits.append({
            "km": round(km, 2),
            "split_pace": seconds_to_pace_str(split_pace),
            "split_time": seconds_to_pace_str(split_time),
            "cumulative": seconds_to_pace_str(cumulative),
        })
    return {"splits": splits, "total_time": seconds_to_pace_str(cumulative)}

@app.post("/api/vo2max")
async def estimate_vo2max(data: VO2MaxRequest):
    if data.distance_km <= 0 or data.time_minutes <= 0:
        return {"error": "Invalid input"}
    t = data.time_minutes
    v = (data.distance_km * 1000) / t
    vo2 = -4.60 + 0.182258 * v + 0.000104 * (v ** 2)
    frac = 0.8 + 0.1894393 * math.exp(-0.012778 * t) + 0.2989558 * math.exp(-0.1932605 * t)
    vo2max = vo2 / frac
    if vo2max >= 60: category, emoji = "Elite", "🏆"
    elif vo2max >= 50: category, emoji = "Excellent", "⭐"
    elif vo2max >= 40: category, emoji = "Good", "💪"
    elif vo2max >= 30: category, emoji = "Average", "👟"
    else: category, emoji = "Below Average", "🎯"
    return {"vo2max": round(vo2max, 1), "category": category, "emoji": emoji}
