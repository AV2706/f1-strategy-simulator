import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Race Simulator Telemetry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "Telemetry API is running perfectly."}

@app.get("/api/race-results")
async def get_race_results():
    return {
        "session": "Main Race",
        "winner": "Car 1",
        "fastest_lap": "1:28.145",
        "weather": "Dry"
    }

@app.get("/api/safety-car")
async def get_safety_car_status():
    return {
        "is_deployed": False,
        "laps_remaining": 0,
        "impact_on_strategy": "None"
    }

@app.websocket("/ws")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    print("Frontend client connected to telemetry stream!")
    try:
        while True:
            telemetry_data = {
                "speed": random.randint(100, 330),
                "rpm": random.randint(5000, 12500),
                "gear": random.randint(1, 8),
                "throttle": round(random.uniform(0.0, 100.0), 1),
                "tyre_wear": random.randint(20, 100),  
                "ers": random.randint(10, 100),        
                "damage": random.randint(0, 10)
            }
            
            await websocket.send_text(json.dumps(telemetry_data))
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        print("Frontend client disconnected.")
