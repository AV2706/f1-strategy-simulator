from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analytics.recommendation_engine.recommender import StrategyRecommender
from analytics.granite_integration.gemini_client import get_ai_summary
from analytics.simulation_analytics.simulation_analyzer import analyze_simulation, compare_race_pace

app = FastAPI(title="F1 Race Strategy Analytics", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender = StrategyRecommender()

# ─── Models ────────────────────────────────────────

class TelemetryData(BaseModel):
    lap: int
    sector_times: list[float]
    tyre_wear: int
    tyre_compound: str
    fuel_level: int
    ers_battery: int
    ers_deployed: int
    ers_harvested: int
    pace_delta: float
    position: int
    gap_to_leader: float
    traffic_ahead: bool

class SimulationData(BaseModel):
    scenario_type: str
    pit_lap: int | None = None
    tyre_compound: str | None = None
    current_position: int | None = None
    gap_to_ahead: float | None = None
    gap_to_behind: float | None = None
    tyre_wear: int | None = None
    fuel_level: int | None = None
    ers_percentage: int | None = None
    safety_car_active: bool | None = False
    strategy_mode: str | None = "balanced"
    laps_remaining: int | None = None

class PaceData(BaseModel):
    laps: list[dict]

# ─── Endpoints ─────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "F1 Race Analytics API is Working Successfully! ✅"}

@app.get("/health")
async def health():
    return {"status": "OK", "message": "Analytics Engine Running"}

# ─── NEW: Live Telemetry Snapshot Endpoint ──────────
@app.get("/api/telemetry/snapshot")
async def telemetry_snapshot():
    """
    Live telemetry snapshot endpoint — Langflow HTTP node will fetch this
    automatically and feed the JSON data directly into the prompt.
    """
    return {
        "lap": 18,
        "sector_times": [28.4, 32.1, 26.8],
        "tyre_wear": 74,
        "tyre_compound": "Medium",
        "fuel_level": 18,
        "ers_battery": 45,
        "ers_deployed": 30,
        "ers_harvested": 20,
        "pace_delta": 0.08,
        "position": 4,
        "gap_to_leader": 2.3,
        "traffic_ahead": True
    }

@app.post("/analyze")
async def analyze_telemetry(data: TelemetryData):
    """Telemetry data analyze karo aur strategy recommendations lo"""
    result = recommender.generate_recommendation(data.dict())
    ai_summary = get_ai_summary(result)
    result["ai_summary"] = ai_summary
    return result

@app.post("/simulate")
async def simulate_scenario(data: SimulationData):
    """What-If simulation scenarios analyze karo"""
    result = analyze_simulation(data.dict())
    return result

@app.post("/pace-analysis")
async def pace_analysis(data: PaceData):
    """Multiple laps ka pace trend analyze karo"""
    result = compare_race_pace(data.laps)
    return result