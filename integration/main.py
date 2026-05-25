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
        # Starting values (Loop ke bahar)
        current_speed = 100
        current_tyre = 99.0
        current_fuel = 95.0

        while True:
            # 1. Speed dheere-dheere badhegi (acceleration)
            current_speed += random.randint(2, 15) 
            
            # Agar speed 320 cross kare, toh break maro!
            if current_speed > 320:
                current_speed = random.randint(100, 130)
                
            # 2. Gear automatic speed ke hisaab se shift hoga
            current_gear = max(1, min(8, int(current_speed / 40) + 1))
            
            # 3. Tyre aur Fuel dheere-dheere drop honge (AI Insights ke liye)
            current_tyre -= 0.1
            current_fuel -= 0.05
            if current_tyre < 0: current_tyre = 0
            if current_fuel < 0: current_fuel = 0

            # 4. Final Data jo Frontend aur AI ko jayega
            telemetry_data = {
                "speed_kmh": int(current_speed),
                "engine_rpm": int(7000 + (current_speed % 40) * 100),
                "gear": int(current_gear),
                "throttle_percent": round(random.uniform(70.0, 100.0) if current_speed < 300 else random.uniform(10.0, 30.0), 1),
                "lap": 18,
                "tyreHealth": round(current_tyre, 1),
                "fuel": round(current_fuel, 1),
                "ers": random.randint(60, 90)
            }

            # Data ko JSON format me frontend ko bhejna
            await websocket.send_text(json.dumps(telemetry_data))
            
            # Har 1 second me update bhejo
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Frontend client disconnected.")
