import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Race Simulator Telemetry API")

# Basic health check route
@app.get("/")
async def root():
    return {"status": "online", "message": "Telemetry API is running perfectly."}

# Real-time WebSocket endpoint
@app.websocket("/ws")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    print("Frontend client connected to telemetry stream!")
    try:
        while True:
            # Generating dummy telemetry data for testing
            telemetry_data = {
                "speed_kmh": random.randint(100, 330),
                "engine_rpm": random.randint(5000, 12500),
                "gear": random.randint(1, 8),
                "throttle_percent": round(random.uniform(0.0, 100.0), 1)
            }
            
            # Sending the data as a JSON string
            await websocket.send_text(json.dumps(telemetry_data))
            
            # Pause for 1 second before sending the next update
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        print("Frontend client disconnected.")
