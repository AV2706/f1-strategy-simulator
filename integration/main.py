import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Race Simulator Telemetry API")

@app.get("/")
async def root():
    return {"status": "online", "message": "Telemetry API is running perfectly."}

@app.websocket("/ws")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    print("Frontend client connected!")
    try:
        current_speed = 100
        current_tyre  = 99.0
        current_fuel  = 95.0
        current_ers   = 100.0
        current_lap   = 1        # lap 1 se shuru, badhega
        lap_distance  = 0        # 0-100 track progress

        while True:
            # Speed physics
            current_speed += 5
            lap_distance  += 3

            # Braking zone simulate karein
            if lap_distance >= 85:
                current_speed = max(80, current_speed - 40)

            if lap_distance >= 100:
                lap_distance  = 0
                current_lap  += 1   # Lap complete

            if current_lap > 57:
                await websocket.send_text(json.dumps({
                    "status": "RACE_FINISHED", "message": "Chequered flag! 🏁"
                }))
                break

            if current_speed > 320:
                current_speed = 110

            # Gear
            current_gear = max(1, min(8, int(current_speed / 40) + 1))

            # Throttle — speed se calculate, random nahi
            if current_speed < 200:
                throttle = round(60 + (current_speed / 200) * 40, 1)
            elif current_speed > 280:
                throttle = round(100 - (current_speed - 280) * 2, 1)
            else:
                throttle = 100.0
            throttle = max(0, min(100, throttle))

            # Tyre & Fuel drop
            current_tyre = max(0, round(current_tyre - 0.1, 1))
            current_fuel = max(0, round(current_fuel - 0.05, 1))

            # ERS — regen on braking, use on acceleration
            if current_speed > 250:
                current_ers = max(0,   round(current_ers - 1.5, 1))
            else:
                current_ers = min(100, round(current_ers + 0.8, 1))

            # RPM — gear aur speed se
            rpm = int(5000 + (current_speed % 40) * 187)
            rpm = max(5000, min(12500, rpm))

            telemetry_data = {
                "speed_kmh":        int(current_speed),
                "engine_rpm":       rpm,
                "gear":             int(current_gear),
                "throttle_percent": throttle,
                "lap":              current_lap,
                "tyreHealth":       current_tyre,
                "fuel":             current_fuel,
                "ers":              current_ers
            }

            await websocket.send_text(json.dumps(telemetry_data))
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected.")
