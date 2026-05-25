# main.py

import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from telemetry_engine import TelemetrySimulator
from tyre_strategy    import TyreDegradation
from pit_strategy     import PitStrategy
from safety_car       import SafetyCarLogic
from traffic          import TrafficAnalysis

app = FastAPI(title="F1 Race Simulator Telemetry API")

# ── Engine instances ──────────────────────────────────────────────────────────
tyre_engine    = TyreDegradation()
pit_engine     = PitStrategy()
safety_engine  = SafetyCarLogic()
traffic_engine = TrafficAnalysis()


@app.get("/")
async def root():
    return {"status": "online", "message": "F1 Telemetry API is running!"}


@app.websocket("/ws")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    print("✅ Frontend connected!")

    # Fresh simulator per connection so every session starts from lap 1
    sim = TelemetrySimulator(total_laps=57, compound="SOFT")

    try:
        while sim.lap <= sim.total_laps:

            # ── 1. Real telemetry from physics engine ─────────────────────
            data = sim.generate_lap_data(driver_name="Max Verstappen")

            # ── 2. Pit window recommendation ──────────────────────────────
            pit_window = pit_engine.optimal_pit_window(
                current_lap = sim.lap,
                tyre_age    = sim.tyre_age,
                compound    = sim.compound,
                total_laps  = sim.total_laps,
                tyre_engine = tyre_engine,
            )

            # ── 3. Traffic prediction after hypothetical pit stop ─────────
            traffic = traffic_engine.predict_rejoin(
                pit_loss_sec   = 22.0,
                gap_ahead      = data["gap_to_leader"],
                gap_behind     = data["gap_to_leader"] + 3.5,
                laps_remaining = sim.total_laps - sim.lap,
            )

            # ── 4. Combine everything and send ────────────────────────────
            payload = {
                **data,
                "optimal_pit_lap":  pit_window["optimal_pit_lap"],
                "latest_safe_lap":  pit_window["latest_safe_lap"],
                "pit_urgency":      pit_window["urgency"],
                "air_condition":    traffic["air_condition"],
                "laps_remaining":   sim.total_laps - sim.lap,
            }

            await websocket.send_text(json.dumps(payload))

            sim.lap += 1
            await asyncio.sleep(1)

        # ── Race finished ─────────────────────────────────────────────────
        await websocket.send_text(json.dumps({
            "status":      "RACE_FINISHED",
            "message":     "Chequered flag! 🏁",
            "total_laps":  sim.total_laps,
        }))

    except WebSocketDisconnect:
        print("❌ Client disconnected.")
