import asyncio
import json
import os

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from telemetry_engine import TelemetrySimulator
from tyre_strategy    import TyreDegradation
from pit_strategy     import PitStrategy
from safety_car       import SafetyCarLogic
from traffic          import TrafficAnalysis

app = FastAPI(title="F1 Race Simulator Telemetry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tyre_engine    = TyreDegradation()
pit_engine     = PitStrategy()
safety_engine  = SafetyCarLogic()
traffic_engine = TrafficAnalysis()


@app.get("/")
async def root():
    return {"status": "online", "message": "F1 Telemetry API is running!"}


# ── Groq AI Insight — key safe on server ──────────────────────────────────────
@app.post("/ai-insight")
async def ai_insight(payload: dict):
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return {"insight": "AI unavailable — GROQ_API_KEY not set on server."}

    prompt = payload.get("prompt", "")
    if not prompt:
        return {"insight": "No prompt received."}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":      "llama-3.3-70b-versatile",
                    "max_tokens": 150,
                    "messages":   [{"role": "user", "content": prompt}],
                },
            )
        data    = response.json()
        insight = data["choices"][0]["message"]["content"]
        return {"insight": insight}

    except Exception as e:
        return {"insight": f"AI error: {str(e)}"}


@app.websocket("/ws")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    print("✅ Frontend connected!")

    sim = TelemetrySimulator(total_laps=57, compound="SOFT")

    try:
        while sim.lap <= sim.total_laps:

            data = sim.generate_lap_data(driver_name="Max Verstappen")

            pit_window = pit_engine.optimal_pit_window(
                current_lap = sim.lap,
                tyre_age    = sim.tyre_age,
                compound    = sim.compound,
                total_laps  = sim.total_laps,
                tyre_engine = tyre_engine,
            )

            traffic = traffic_engine.predict_rejoin(
                pit_loss_sec   = 22.0,
                gap_ahead      = data["gap_to_leader"],
                gap_behind     = data["gap_to_leader"] + 3.5,
                laps_remaining = sim.total_laps - sim.lap,
            )

            payload = {
                **data,
                "optimal_pit_lap": pit_window["optimal_pit_lap"],
                "latest_safe_lap": pit_window["latest_safe_lap"],
                "pit_urgency":     pit_window["urgency"],
                "air_condition":   traffic["air_condition"],
                "laps_remaining":  sim.total_laps - sim.lap,
            }

            await websocket.send_text(json.dumps(payload))
            sim.lap += 1
            await asyncio.sleep(1)

        await websocket.send_text(json.dumps({
            "status":     "RACE_FINISHED",
            "message":    "Chequered flag! 🏁",
            "total_laps": sim.total_laps,
        }))

    except WebSocketDisconnect:
        print("❌ Client disconnected.")
