import asyncio
import json
import websockets
from fastapi import FastAPI, BackgroundTasks
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

# ─── LIVE TELEMETRY STATE (Real-time memory) ────────
live_car_data = {
    "lap": 1,
    "sector_times": [0.0, 0.0, 0.0],
    "tyre_wear": 100,
    "tyre_compound": "Medium",
    "fuel_level": 100,
    "ers_battery": 100,
    "ers_deployed": 0,
    "ers_harvested": 0,
    "pace_delta": 0.0,
    "position": 1,
    "gap_to_leader": 0.0,
    "traffic_ahead": False,
    "speed": 0, 
    "rpm": 0    
}

# ─── BACKGROUND WEBSOCKET LISTENER ─────────────────
async def start_websocket_client():
    url = "wss://backendserver-2eul.onrender.com/ws"
    while True:
        try:
            print(f"Connecting to live F1 telemetry at {url}...")
            async with websockets.connect(url) as websocket:
                print("✅ Successfully connected to Abdul's F1 Car!")
                while True:
                    raw_data = await websocket.recv()
                    incoming_data = json.loads(raw_data)
                    
                    global live_car_data
                    live_car_data["speed"] = incoming_data.get("speed", live_car_data["speed"])
                    live_car_data["tyre_wear"] = incoming_data.get("tyre_wear", live_car_data["tyre_wear"])
                    live_car_data["ers_battery"] = incoming_data.get("ers", live_car_data["ers_battery"])
                    
                    
        except Exception as e:
            print(f"❌ Connection Error: {e}. Reconnecting in 3 seconds...")
            await asyncio.sleep(3)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_websocket_client())


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

@app.get("/api/telemetry/snapshot")
async def telemetry_snapshot():
    
    return live_car_data

@app.post("/analyze")
async def analyze_telemetry(data: TelemetryData):
    result = recommender.generate_recommendation(data.dict())
    ai_summary = get_ai_summary(result)
    result["ai_summary"] = ai_summary
    return result

@app.post("/simulate")
async def simulate_scenario(data: SimulationData):
    result = analyze_simulation(data.dict())
    return result

@app.post("/pace-analysis")
async def pace_analysis(data: PaceData):
    result = compare_race_pace(data.laps)
    return result
