import asyncio
import websockets
import requests
import json
import os
import threading
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
from collections import deque
from groq import Groq
from dotenv import load_dotenv
from docling_core.types.doc import DoclingDocument, DocItemLabel

# ── Create output folders ─────────────────────────────
os.makedirs("documentation/race_reports",        exist_ok=True)
os.makedirs("documentation/telemetry_summaries", exist_ok=True)
os.makedirs("documentation/strategy_analysis",   exist_ok=True)
os.makedirs("documentation/simulator_reports",   exist_ok=True)

# Ye .env file se keys ko memory me load kar dega
load_dotenv()
# ── API Configuration ─────────────────────────────────
ANALYTICS_IP = "192.168.18.76" 
BACKEND_URL  = "https://f1-strategy-simulator-p015.onrender.com" 
WS_URL       = "wss://f1-strategy-simulator-p015.onrender.com/ws"
# ── Groq Setup ───
api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=api_key)

# ── IBM Granite — Will be integrated later  ─────
# from ibm_watsonx_ai import Credentials
# from ibm_watsonx_ai.foundation_models import ModelInference
# granite_model = ModelInference(
#     model_id="ibm/granite-13b-chat-v2",
#     credentials=Credentials(api_key="GRANITE_KEY", url="GRANITE_URL"),
#     project_id="PROJECT_ID"
# )

# ════════════════════════════════════════════════════════
# LIVE DATA STORAGE — For visualization
# ════════════════════════════════════════════════════════
MAX_POINTS       = 40
speed_history    = deque(maxlen=MAX_POINTS)
rpm_history      = deque(maxlen=MAX_POINTS)
throttle_history = deque(maxlen=MAX_POINTS)
gear_history     = deque(maxlen=MAX_POINTS)

live_data = {
    "speed_kmh":        0,
    "engine_rpm":       0,
    "gear":             0,
    "throttle_percent": 0,
    "connected":        False,
}

# Panel data updated by APIs
# Default values from Analytics sample data (same as except block)
# When Analytics is LIVE, these will be automatically overridden
panel_data = {
    "strategy":      "TYRE SAVING",
    "fuel_mode":     "SAVE",
    "risk_level":    "MEDIUM",
    "pit_window":    "Lap 18-20",
    "tyre_wear":     "65%",
    "fuel_level":    "42%",
    "ers_battery":   "55%",
    "position":      "P4",
    "lap":           "18",
    "ai_insight":    "Fetching AI insights...",
    "reports_done":  False,
    "backend_live":  False,
    "analytics_live":False,
}

# ════════════════════════════════════════════════════════
# STEP 1 — WEBSOCKET THREAD (continuous live feed)
# ════════════════════════════════════════════════════════
def ws_thread():
    async def connect():
        while True:
            try:
                print("[WebSocket] Connecting...")
                async with websockets.connect(WS_URL, open_timeout=15) as ws:
                    live_data["connected"] = True
                    print("[WebSocket] LIVE!")
                    while True:
                        msg  = await ws.recv()
                        data = json.loads(msg)
                        live_data.update(data)
                        speed_history.append(data.get("speed_kmh", 0))
                        rpm_history.append(data.get("engine_rpm", 0))
                        throttle_history.append(data.get("throttle_percent", 0))
                        gear_history.append(data.get("gear", 0))
            except Exception as e:
                live_data["connected"] = False
                print(f"[WebSocket] Reconnecting in 4s... ({e})")
                await asyncio.sleep(4)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect())

# ════════════════════════════════════════════════════════
# STEP 2 — FETCH LIVE DATA FROM BACKEND (Abdul - Ngrok)
# ════════════════════════════════════════════════════════
def fetch_backend_data():
    print("\n[Backend] Connecting to API...")

    telemetry_payload = {
        "lap": 18, "sector_times": [28.5, 32.1, 29.8],
        "tyre_wear": 65, "tyre_compound": "soft",
        "fuel_level": 42, "ers_battery": 55,
        "ers_deployed": 30, "ers_harvested": 20,
        "pace_delta": 0.3, "position": 4,
        "gap_to_leader": 8.5, "traffic_ahead": True
    }
    simulation_payload = {
        "scenario_type": "pit_stop", "pit_lap": 19,
        "tyre_compound": "medium", "current_position": 4,
        "gap_to_ahead": 2.3, "gap_to_behind": 4.1,
        "tyre_wear": 65, "fuel_level": 42,
        "ers_percentage": 55, "safety_car_active": False,
        "strategy_mode": "balanced", "laps_remaining": 40
    }

    backend = {}

    # Fetch telemetry from backend
    try:
        r = requests.post(
            f"{BACKEND_URL}/analyze",
            json=telemetry_payload, timeout=10,
            headers={"ngrok-skip-browser-warning": "true"}
        )
        backend["telemetry"] = r.json()
        d = backend["telemetry"]
        panel_data["tyre_wear"]    = f"{d.get('tyre_wear', 65)}%"
        panel_data["fuel_level"]   = f"{d.get('fuel_level', 42)}%"
        panel_data["ers_battery"]  = f"{d.get('ers_battery', 55)}%"
        panel_data["position"]     = f"P{d.get('position', 4)}"
        panel_data["lap"]          = str(d.get("lap", 18))
        panel_data["backend_live"] = True
        print("[Backend] /analyze LIVE!")
    except:
        print("[Backend] /analyze offline — using sample data")
        backend["telemetry"] = {
            "lap": 18, "tyre_wear": 65, "tyre_compound": "soft",
            "fuel_level": 42, "ers_battery": 55,
            "position": 4, "gap_to_leader": 8.5
        }

    # Fetch simulation from backend
    try:
        r = requests.post(
            f"{BACKEND_URL}/simulate",
            json=simulation_payload, timeout=10,
            headers={"ngrok-skip-browser-warning": "true"}
        )
        backend["simulation"] = r.json()
        panel_data["risk_level"] = backend["simulation"].get("risk_level", "medium").upper()
        print("[Backend] /simulate LIVE!")
    except:
        print("[Backend] /simulate offline — using sample data")
        backend["simulation"] = {
            "scenario_type": "pit_stop",
            "risk_level": "medium",
            "analysis": [
                "Undercut possible — gap to car ahead is 2.3s, pit now.",
                "Overcut risky — gap behind is tight at 4.1s.",
                "Optimal pit window: Lap 18 to Lap 20."
            ]
        }

    return backend

# ════════════════════════════════════════════════════════
# STEP 3 — FETCH STRATEGY DATA FROM ANALYTICS API
# ════════════════════════════════════════════════════════
def fetch_analytics_data():
    print("\n[Analytics] Connecting...")

    analyze_payload = {
        "lap": 18, "sector_times": [28.5, 32.1, 29.8],
        "tyre_wear": 65, "tyre_compound": "soft",
        "fuel_level": 42, "ers_battery": 55,
        "ers_deployed": 30, "ers_harvested": 20,
        "pace_delta": 0.3, "position": 4,
        "gap_to_leader": 8.5, "traffic_ahead": True
    }
    simulate_payload = {
        "scenario_type": "pit_stop", "pit_lap": 19,
        "tyre_compound": "medium", "current_position": 4,
        "gap_to_ahead": 2.3, "gap_to_behind": 4.1,
        "tyre_wear": 65, "fuel_level": 42,
        "ers_percentage": 55, "safety_car_active": False,
        "strategy_mode": "balanced", "laps_remaining": 40
    }

    # Fetch strategy recommendation
    try:
        r = requests.post(
            f"http://{ANALYTICS_IP}:8000/analyze",
            json=analyze_payload, timeout=8
        )
        strategy = r.json()
        panel_data["strategy"]       = strategy.get("recommended_strategy", "tyre_saving").upper()
        panel_data["fuel_mode"]      = strategy.get("fuel_mode", "save").upper()
        panel_data["analytics_live"] = True
        print(f"[Analytics] Strategy: {panel_data['strategy']} LIVE!")
    except:
        print("[Analytics] /analyze offline — using sample data")
        strategy = {
            "lap": 18,
            "recommended_strategy": "tyre_saving",
            "fuel_mode": "save",
            "ai_summary": "Tyre degradation critical. Pit window Lap 19-21 recommended. Switch to fuel saving mode.",
            "strategy_details": {
                "aggressive":  {"viable": False, "note": "High tyre wear detected."},
                "balanced":    {"viable": True,  "note": "Maintains pace and manages fuel."},
                "tyre_saving": {"viable": True,  "note": "Extends tyre life. Pit later."}
            },
            "all_insights": [
                "Tyre degradation critical.",
                "Pace dropping — investigate tyre or fuel issue.",
                "Fuel level moderate — consider fuel saving mode.",
                "Pit window suggested: Lap 19 to 21.",
                "Traffic ahead detected — monitor gap for overtake.",
                "ERS moderate — balanced deployment recommended."
            ]
        }

    # Fetch pit stop simulation
    try:
        r = requests.post(
            f"http://{ANALYTICS_IP}:8000/simulate",
            json=simulate_payload, timeout=8
        )
        pit = r.json()
        panel_data["risk_level"] = pit.get("risk_level", "medium").upper()
        print("[Analytics] /simulate LIVE!")
    except:
        print("[Analytics] /simulate offline — using sample data")
        pit = {
            "scenario_type": "pit_stop",
            "risk_level": "medium",
            "analysis": [
                "Undercut possible — gap to car ahead is 2.3s, pit now.",
                "Overcut risky — gap behind is tight at 4.1s.",
                "Optimal pit window: Lap 18 to Lap 20."
            ]
        }

    return strategy, pit

# ════════════════════════════════════════════════════════
# STEP 4 — GENERATE AI INSIGHTS USING GROQ
# ════════════════════════════════════════════════════════
def get_groq_insights(ws_data, strategy, backend):
    print("\n[Groq] Fetching AI insights...")

    telemetry = backend.get("telemetry", {})
    prompt = f"""
You are an F1 race strategy engineer. Analyze this live race data:

Live Telemetry (Frontend WebSocket):
- Speed    : {ws_data.get('speed_kmh')} km/h
- RPM      : {ws_data.get('engine_rpm')}
- Gear     : {ws_data.get('gear')}
- Throttle : {ws_data.get('throttle_percent')}%

Backend Race Data:
- Lap           : {telemetry.get('lap', 18)}
- Tyre Wear     : {telemetry.get('tyre_wear', 65)}%
- Tyre Compound : {str(telemetry.get('tyre_compound', 'soft')).upper()}
- Fuel Level    : {telemetry.get('fuel_level', 42)}%
- ERS Battery   : {telemetry.get('ers_battery', 55)}%
- Position      : P{telemetry.get('position', 4)}
- Gap to Leader : {telemetry.get('gap_to_leader', 8.5)}s

Analytics Strategy Recommendation: {strategy.get('recommended_strategy', 'tyre_saving').upper()}

Give professional F1 race engineer analysis:
1. AI Summary (2 lines)
2. Top 5 Race Insights
3. Pit Stop Recommendation
4. Risk Assessment
"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        insight = response.choices[0].message.content.strip()
        panel_data["ai_insight"] = insight
        print("[Groq] AI Insight received LIVE!")
        return insight
    except Exception as e:
        print(f"[Groq] Error — {e}")
        fallback = "Tyre degradation critical. Maintain tyre saving mode to preserve position."
        panel_data["ai_insight"] = fallback
        return fallback

# ════════════════════════════════════════════════════════
# STEP 5 — GENERATE DOCLING REPORTS
# ════════════════════════════════════════════════════════
def save_report(doc, folder, filename):
    # Save report as both Markdown and JSON
    md_path   = f"documentation/{folder}/{filename}.md"
    json_path = f"documentation/{folder}/{filename}.json"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(doc.export_to_markdown())
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(doc.export_to_dict(), f, indent=2)
    print(f"[Docling] Saved: {md_path}")


def build_telemetry_report(ws_data, backend, groq_text):
    # Generate telemetry summary from frontend + backend data
    telemetry = backend.get("telemetry", {})
    doc = DoclingDocument(name="F1 Live Telemetry Summary")
    doc.add_heading(text="F1 Live Telemetry Summary — Monaco GP 2025", level=1)

    # Real-time data from frontend WebSocket
    doc.add_heading(text="Real-Time Data (Frontend WebSocket)", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Speed        : {ws_data.get('speed_kmh')} km/h")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Engine RPM   : {ws_data.get('engine_rpm')}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Gear         : {ws_data.get('gear')}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Throttle     : {ws_data.get('throttle_percent')}%")

    # Detailed lap data from backend
    doc.add_heading(text="Backend Race Data (Abdul - Ngrok)", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Lap          : {telemetry.get('lap', 18)}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Tyre Wear    : {telemetry.get('tyre_wear', 65)}%")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Tyre Compound: {str(telemetry.get('tyre_compound', 'soft')).upper()}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Fuel Level   : {telemetry.get('fuel_level', 42)}%")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"ERS Battery  : {telemetry.get('ers_battery', 55)}%")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Position     : P{telemetry.get('position', 4)}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Gap to Leader: {telemetry.get('gap_to_leader', 8.5)}s")

    # AI analysis from Groq
    doc.add_heading(text="AI Analysis (Groq — Llama 3.3)", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH, text=groq_text)

    save_report(doc, "telemetry_summaries", "live_telemetry_report")


def build_strategy_report(strategy, pit, backend, groq_text):
    # Generate strategy analysis report from Analytics + Backend data
    doc = DoclingDocument(name="F1 Strategy Analysis Report")
    doc.add_heading(text="F1 Strategy Analysis Report — Monaco GP 2025", level=1)

    # Race status from analytics
    doc.add_heading(text="Race Status", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Current Lap  : {strategy.get('lap', 18)}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Fuel Mode    : {strategy.get('fuel_mode','N/A').upper()}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Recommended  : {strategy.get('recommended_strategy','N/A').upper()}")

    # AI analysis from Groq
    doc.add_heading(text="AI Analysis (Groq — Llama 3.3)", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH, text=groq_text)

    # AI summary generated by Analytics Lead
    if "ai_summary" in strategy:
        doc.add_heading(text="Analytics Lead AI Summary", level=2)
        doc.add_text(label=DocItemLabel.PARAGRAPH, text=strategy["ai_summary"])

    # Detailed insights from Analytics API
    if "all_insights" in strategy:
        doc.add_heading(text="Strategy Insights", level=2)
        for insight in strategy["all_insights"]:
            doc.add_text(label=DocItemLabel.PARAGRAPH, text=f"- {insight}")

    # Strategy viability comparison
    if "strategy_details" in strategy:
        doc.add_heading(text="Strategy Viability", level=2)
        for name, detail in strategy["strategy_details"].items():
            status = "Viable" if detail["viable"] else "Not Viable"
            doc.add_text(label=DocItemLabel.PARAGRAPH,
                         text=f"{name.upper()} — {status}: {detail.get('note','')}")

    # Pit stop analysis
    doc.add_heading(text="Pit Stop Analysis", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Scenario   : {pit.get('scenario_type','N/A').upper()}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Risk Level : {pit.get('risk_level','N/A').upper()}")
    if "analysis" in pit:
        for item in pit["analysis"]:
            doc.add_text(label=DocItemLabel.PARAGRAPH, text=f"- {item}")

    save_report(doc, "strategy_analysis", "live_strategy_report")


def build_simulation_report(backend):
    # Generate what-if simulation report from backend data
    simulation = backend.get("simulation", {})
    doc = DoclingDocument(name="F1 What-If Simulation Report")
    doc.add_heading(text="F1 What-If Simulation Report — Monaco GP 2025", level=1)

    # Scenario details from backend
    doc.add_heading(text="Scenario Details (Backend - Abdul)", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Scenario   : {simulation.get('scenario_type','pit_stop').upper()}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Risk Level : {simulation.get('risk_level','medium').upper()}")

    if "analysis" in simulation:
        doc.add_heading(text="Simulation Analysis", level=2)
        for item in simulation["analysis"]:
            doc.add_text(label=DocItemLabel.PARAGRAPH, text=f"- {item}")

    # Data source information
    doc.add_heading(text="Data Source", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Backend API   : {BACKEND_URL}/simulate")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text="Report Engine : IBM Docling — Automated Documentation System")

    save_report(doc, "simulator_reports", "live_simulation_report")


def build_race_report(ws_data, strategy, backend, groq_text):
    # Generate combined race summary using all data sources
    telemetry = backend.get("telemetry", {})
    doc = DoclingDocument(name="F1 Race Summary Report")
    doc.add_heading(text="F1 Race Summary Report — Monaco GP 2025", level=1)

    # Live telemetry from frontend WebSocket
    doc.add_heading(text="Live Telemetry (Frontend WebSocket)", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Speed    : {ws_data.get('speed_kmh')} km/h")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"RPM      : {ws_data.get('engine_rpm')}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Gear     : {ws_data.get('gear')}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Throttle : {ws_data.get('throttle_percent')}%")

    # Race data from backend
    doc.add_heading(text="Race Data (Backend - Abdul)", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Lap          : {telemetry.get('lap', 18)}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Position     : P{telemetry.get('position', 4)}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Tyre Wear    : {telemetry.get('tyre_wear', 65)}%")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Fuel Level   : {telemetry.get('fuel_level', 42)}%")

    # AI analysis from Groq
    doc.add_heading(text="AI Strategy Analysis (Groq — Llama 3.3)", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH, text=groq_text)

    # Strategy recommendation from Analytics API
    doc.add_heading(text="Strategy Recommendation (Analytics)", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Recommended : {strategy.get('recommended_strategy','N/A').upper()}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Fuel Mode   : {strategy.get('fuel_mode','N/A').upper()}")

    if "ai_summary" in strategy:
        doc.add_heading(text="Analytics AI Summary", level=2)
        doc.add_text(label=DocItemLabel.PARAGRAPH, text=strategy["ai_summary"])

    # All data sources used in this report
    doc.add_heading(text="Data Sources", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Frontend WebSocket : {WS_URL}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Backend API        : {BACKEND_URL}")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text=f"Analytics API      : http://{ANALYTICS_IP}:8000")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text="AI Engine          : Groq — Llama 3.3 70B")
    doc.add_text(label=DocItemLabel.PARAGRAPH,
                 text="Report Engine      : IBM Docling — Automated Documentation System")

    save_report(doc, "race_reports", "live_race_report")


def generate_all_reports(ws_data, strategy, pit, backend, groq_text):
    print("\n[5/5] Generating Docling reports...")
    build_telemetry_report(ws_data, backend, groq_text)
    build_strategy_report(strategy, pit, backend, groq_text)
    build_simulation_report(backend)
    build_race_report(ws_data, strategy, backend, groq_text)
    panel_data["reports_done"] = True
    print("[Docling] All 4 reports done!")


# ════════════════════════════════════════════════════════
# VISUALIZATION — Matplotlib Live Dashboard
# ════════════════════════════════════════════════════════
plt.rcParams.update({
    "figure.facecolor": "#0d0d0d",
    "axes.facecolor":   "#1a1a1a",
    "axes.edgecolor":   "#2a2a2a",
    "text.color":       "#ffffff",
    "xtick.color":      "#555555",
    "ytick.color":      "#888888",
    "grid.color":       "#2a2a2a",
    "grid.linestyle":   "--",
    "font.family":      "monospace",
})

fig = plt.figure(figsize=(16, 9))
fig.patch.set_facecolor("#0d0d0d")
fig.suptitle(
    "F1 Command Center  —  Live Integration Dashboard",
    fontsize=13, fontweight="bold", color="#ffffff", y=0.97
)

gs = gridspec.GridSpec(
    4, 5, figure=fig,
    hspace=0.6, wspace=0.4,
    left=0.04, right=0.97,
    top=0.91, bottom=0.06
)

# ── Row 0: Metric Cards ───────────────────────────────
ax_cards = [fig.add_subplot(gs[0, i]) for i in range(5)]
card_cfg  = [
    ("SPEED",     "km/h",    "#00ff88"),
    ("RPM",       "x1000",   "#378add"),
    ("GEAR",      "current", "#e24b4a"),
    ("THROTTLE",  "%",       "#f5a623"),
    ("POSITION",  "lap",     "#aa88ff"),
]
card_texts = []
for ax, (label, unit, color) in zip(ax_cards, card_cfg):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    for sp in ax.spines.values():
        sp.set_visible(True)
        sp.set_edgecolor("#2a2a2a")
        sp.set_linewidth(0.8)
    ax.set_title(label, fontsize=8, color="#888888", pad=3)
    t = ax.text(0.5, 0.5, "—", ha="center", va="center",
                fontsize=22, fontweight="bold", color=color,
                transform=ax.transAxes)
    ax.text(0.5, 0.1, unit, ha="center", fontsize=7,
            color="#555555", transform=ax.transAxes)
    card_texts.append(t)

txt_speed, txt_rpm, txt_gear, txt_throttle, txt_pos = card_texts

# ── Row 1-2: Left charts ──────────────────────────────
ax_speed = fig.add_subplot(gs[1, 0:3])
ax_rpm   = fig.add_subplot(gs[2, 0:3])

# ── Row 1-2: Right panels ─────────────────────────────
ax_strategy = fig.add_subplot(gs[1, 3:5])
ax_ai       = fig.add_subplot(gs[2, 3:5])

# ── Row 3: Bottom charts + status ─────────────────────
ax_throttle = fig.add_subplot(gs[3, 0:2])
ax_gear_ch  = fig.add_subplot(gs[3, 2:4])
ax_status   = fig.add_subplot(gs[3, 4])


def setup_chart(ax, title, color, ymin, ymax, ylabel):
    ax.set_title(title, fontsize=8, color="#888888", pad=3, loc="left")
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(0, MAX_POINTS)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=7)
    ax.set_ylabel(ylabel, fontsize=7)
    for sp in ax.spines.values():
        sp.set_edgecolor("#2a2a2a")
    line, = ax.plot([], [], color=color, linewidth=1.8)
    return line

line_speed    = setup_chart(ax_speed,    "Speed (km/h)",  "#00ff88", 0,   350, "km/h")
line_rpm      = setup_chart(ax_rpm,      "Engine RPM",    "#378add", 0, 18000, "RPM")
line_throttle = setup_chart(ax_throttle, "Throttle (%)",  "#f5a623", 0,   100, "%")
line_gear_ch  = setup_chart(ax_gear_ch,  "Gear",          "#e24b4a", 0,     8, "gear")

# ── Strategy Panel ────────────────────────────────────
ax_strategy.set_xlim(0, 1); ax_strategy.set_ylim(0, 1); ax_strategy.axis("off")
for sp in ax_strategy.spines.values():
    sp.set_visible(True); sp.set_edgecolor("#2a2a2a"); sp.set_linewidth(0.8)
ax_strategy.set_title("Strategy Panel", fontsize=8, color="#888888", pad=3)
txt_strat = ax_strategy.text(0.05, 0.80, "Strategy:   —", fontsize=9, color="#00ff88", transform=ax_strategy.transAxes)
txt_fuel  = ax_strategy.text(0.05, 0.62, "Fuel Mode:  —", fontsize=9, color="#f5a623", transform=ax_strategy.transAxes)
txt_risk  = ax_strategy.text(0.05, 0.44, "Risk:       —", fontsize=9, color="#e24b4a", transform=ax_strategy.transAxes)
txt_pit   = ax_strategy.text(0.05, 0.26, "Pit Window: —", fontsize=9, color="#aa88ff", transform=ax_strategy.transAxes)
txt_tyre  = ax_strategy.text(0.05, 0.10, "Tyre: —  Fuel: —  ERS: —", fontsize=8, color="#888888", transform=ax_strategy.transAxes)

# ── AI Insight Panel ──────────────────────────────────
ax_ai.set_xlim(0, 1); ax_ai.set_ylim(0, 1); ax_ai.axis("off")
ax_ai.set_facecolor("#1a0a00")
for sp in ax_ai.spines.values():
    sp.set_visible(True); sp.set_edgecolor("#993300"); sp.set_linewidth(0.8)
ax_ai.set_title("AI Insight  (Groq — Llama 3.3)", fontsize=8, color="#f5a623", pad=3)
txt_ai = ax_ai.text(
    0.05, 0.55, "Fetching AI insights...",
    fontsize=8, color="#ffcc88",
    transform=ax_ai.transAxes,
    va="center", multialignment="left",
    wrap=True
)

# ── Status Panel ──────────────────────────────────────
ax_status.set_xlim(0, 1); ax_status.set_ylim(0, 1); ax_status.axis("off")
ax_status.set_title("Status", fontsize=8, color="#888888", pad=3)
txt_ws   = ax_status.text(0.05, 0.80, "WebSocket:  —", fontsize=7, color="#555555", transform=ax_status.transAxes)
txt_back = ax_status.text(0.05, 0.60, "Backend:    —", fontsize=7, color="#555555", transform=ax_status.transAxes)
txt_anal = ax_status.text(0.05, 0.40, "Analytics:  —", fontsize=7, color="#555555", transform=ax_status.transAxes)
txt_rep  = ax_status.text(0.05, 0.20, "Reports:    —", fontsize=7, color="#555555", transform=ax_status.transAxes)

# ════════════════════════════════════════════════════════
# ANIMATION UPDATE FUNCTION
# ════════════════════════════════════════════════════════
frame_count = [0]

def update(frame):
    frame_count[0] += 1

    # Update metric cards with live WebSocket data
    txt_speed.set_text(f"{live_data['speed_kmh']:.0f}")
    txt_rpm.set_text(f"{live_data['engine_rpm']/1000:.1f}k")
    txt_gear.set_text(f"{int(live_data['gear'])}")
    txt_throttle.set_text(f"{live_data['throttle_percent']:.1f}")
    txt_pos.set_text(panel_data["position"])

    # Update live charts
    def update_chart(ax, line, history, color):
        y = list(history)
        if len(y) > 1:
            x = list(range(len(y)))
            line.set_data(x, y)
            for c in ax.collections:
                c.remove()
            ax.fill_between(x, y, alpha=0.18, color=color)

    update_chart(ax_speed,    line_speed,    speed_history,    "#00ff88")
    update_chart(ax_rpm,      line_rpm,      rpm_history,      "#378add")
    update_chart(ax_throttle, line_throttle, throttle_history, "#f5a623")
    update_chart(ax_gear_ch,  line_gear_ch,  gear_history,     "#e24b4a")

    # Update strategy panel with Analytics + Backend data
    txt_strat.set_text(f"Strategy:   {panel_data['strategy']}")
    txt_fuel.set_text(f"Fuel Mode:  {panel_data['fuel_mode']}")
    txt_risk.set_text(f"Risk:       {panel_data['risk_level']}")
    txt_pit.set_text(f"Pit Window: {panel_data['pit_window']}")
    txt_tyre.set_text(
        f"Tyre: {panel_data['tyre_wear']}  "
        f"Fuel: {panel_data['fuel_level']}  "
        f"ERS: {panel_data['ers_battery']}"
    )

    # Update AI insight panel with Groq data
    insight = panel_data["ai_insight"]
    # Wrap long text manually for display
    words = insight.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > 55:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    txt_ai.set_text("\n".join(lines[:4]))

    # Update status panel
    ws_live = live_data.get("connected", False)
    txt_ws.set_text(f"WebSocket:  {'LIVE' if ws_live else 'offline'}")
    txt_ws.set_color("#00ff88" if ws_live else "#e24b4a")

    txt_back.set_text(f"Backend:    {'LIVE' if panel_data['backend_live'] else 'offline'}")
    txt_back.set_color("#00ff88" if panel_data["backend_live"] else "#e24b4a")

    txt_anal.set_text(f"Analytics:  {'LIVE' if panel_data['analytics_live'] else 'offline'}")
    txt_anal.set_color("#00ff88" if panel_data["analytics_live"] else "#e24b4a")

    rep_done = panel_data["reports_done"]
    txt_rep.set_text(f"Reports:    {'4/4 done' if rep_done else 'generating...'}")
    txt_rep.set_color("#00ff88" if rep_done else "#f5a623")

    # Auto-save dashboard snapshot every 20 frames
    if frame_count[0] % 20 == 0:
        fig.savefig(
            "documentation/strategy_analysis/live_dashboard.png",
            dpi=100, bbox_inches="tight", facecolor="#0d0d0d"
        )


# ════════════════════════════════════════════════════════
# BACKGROUND THREAD — APIs + Groq + Docling
# ════════════════════════════════════════════════════════
def background_task():
    import time
    time.sleep(2)  # Wait for WebSocket to connect first

    # Fetch one-time snapshot from WebSocket for reports
    ws_snapshot = dict(live_data)

    backend          = fetch_backend_data()
    strategy, pit    = fetch_analytics_data()
    groq_text        = get_groq_insights(ws_snapshot, strategy, backend)
    generate_all_reports(ws_snapshot, strategy, pit, backend, groq_text)


# ════════════════════════════════════════════════════════
# MAIN — START ALL SYSTEMS
# ════════════════════════════════════════════════════════
print("=" * 55)
print("  F1 MASTER INTEGRATION")
print("  Frontend + Backend + Analytics + Groq + Docling")
print("=" * 55)

# Start WebSocket live feed thread
threading.Thread(target=ws_thread, daemon=True).start()

# Start background API + Docling thread
threading.Thread(target=background_task, daemon=True).start()

# Start live dashboard animation
ani = animation.FuncAnimation(
    fig, update,
    interval=500,
    cache_frame_data=False
)

plt.show()
