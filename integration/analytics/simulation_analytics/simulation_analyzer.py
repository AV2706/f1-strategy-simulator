import numpy as np
import pandas as pd


def analyze_simulation(scenario: dict) -> dict:
    """
    Analyzes What-If simulation output
    """

    results = []
    risk_level = "low"

    # ─── Pit Stop Scenario ───────────────────────────
    if scenario.get("scenario_type") == "pit_stop":
        pit_lap = scenario.get("pit_lap", 0)
        gap_ahead = scenario.get("gap_to_ahead", 999)
        gap_behind = scenario.get("gap_to_behind", 999)

        # Analyze gaps using NumPy
        gaps = np.array([gap_ahead, gap_behind])
        min_gap = np.min(gaps)

        if gap_ahead < 3.0:
            results.append(
                f"Undercut possible. Gap to car ahead is {gap_ahead}s — pit now to jump ahead."
            )
        else:
            results.append(
                f"Undercut not needed. Gap to ahead is {gap_ahead}s — safe to stay out."
            )

        if gap_behind > 5.0:
            results.append(
                f"Overcut viable. Gap behind is {gap_behind}s — extending stint possible."
            )
        else:
            results.append(
                f"Gap behind is tight ({gap_behind}s). Overcut risky — consider pitting soon."
            )
            risk_level = "medium"

        results.append(
            f"Optimal pit window: Lap {pit_lap} to Lap {pit_lap + 2}."
        )

    # ─── Safety Car Scenario ─────────────────────────
    elif scenario.get("scenario_type") == "safety_car":
        tyre_wear = scenario.get("tyre_wear", 0)
        position = scenario.get("current_position", 10)

        # Analyze Safety Car data using Pandas Series
        sc_data = pd.Series({
            'tyre_wear': tyre_wear,
            'position': position
        })

        results.append("Safety Car deployed. Free pit stop window open.")

        if sc_data['tyre_wear'] > 50:
            results.append(
                "Tyre wear is high — pit under Safety Car strongly recommended."
            )
            risk_level = "high"
        else:
            results.append(
                "Tyre wear acceptable. Pitting still beneficial for track position."
            )

        if sc_data['position'] <= 5:
            results.append(
                f"Currently P{position} — pitting may drop position temporarily but fresh tyres will help."
            )
        else:
            results.append(
                f"Currently P{position} — pit stop recommended to gain positions on restart."
            )

    # ─── Strategy Comparison Scenario ────────────────
    elif scenario.get("scenario_type") == "strategy_comparison":
        mode = scenario.get("strategy_mode", "balanced")
        tyre_wear = scenario.get("tyre_wear", 0)
        fuel_level = scenario.get("fuel_level", 0)

        # Calculate strategy scores using NumPy
        strategy_scores = np.array([
            100 - tyre_wear,   # aggressive score
            50,                # balanced score
            tyre_wear          # tyre_saving score
        ])
        best_index = np.argmax(strategy_scores)
        strategy_names = ["aggressive", "balanced", "tyre_saving"]

        comparison = {
            "aggressive": {
                "viable": bool(tyre_wear < 50 and fuel_level > 25),
                "note": "Push hard. Risk of tyre degradation is high."
                if tyre_wear >= 50
                else "Conditions support aggressive driving."
            },
            "balanced": {
                "viable": True,
                "note": "Maintain pace. Best option for tyre and fuel management."
            },
            "tyre_saving": {
                "viable": bool(tyre_wear > 60),
                "note": "Reduce pace to extend tyre life and pit later."
                if tyre_wear > 60
                else "Not needed yet. Tyre wear within safe limits."
            }
        }

        best = "balanced"
        if tyre_wear > 60:
            best = "tyre_saving"
        elif tyre_wear < 40 and fuel_level > 30:
            best = "aggressive"

        results.append(f"Best strategy for current conditions: {best.upper()}")
        results.append(comparison[best]["note"])

        return {
            "scenario_type": "strategy_comparison",
            "recommended_strategy": best,
            "comparison": comparison,
            "analysis": results,
            "risk_level": risk_level
        }

    # ─── Tyre Compound Change Scenario ───────────────
    elif scenario.get("scenario_type") == "tyre_change":
        current_compound = scenario.get("tyre_compound", "Medium")
        tyre_wear = scenario.get("tyre_wear", 0)
        laps_remaining = scenario.get("laps_remaining", 20)

        # Organize tyre data using Pandas
        tyre_df = pd.DataFrame([{
            'compound': current_compound,
            'wear': tyre_wear,
            'laps_remaining': laps_remaining
        }])

        wear_val = tyre_df['wear'].values[0]
        laps_val = tyre_df['laps_remaining'].values[0]

        if laps_val > 25:
            results.append(
                "Many laps remaining. Hard compound recommended for longer stint."
            )
        elif laps_val > 10:
            results.append(
                "Medium compound recommended. Balanced performance for remaining laps."
            )
        else:
            results.append(
                "Few laps remaining. Soft compound recommended for maximum pace."
            )

        if wear_val > 65:
            results.append(
                f"Current compound: {current_compound}. Tyre wear at {tyre_wear}% — change recommended."
            )
        else:
            results.append(
                f"Current compound: {current_compound}. Tyre wear at {tyre_wear}% — still manageable."
            )

    # ─── Unknown Scenario ────────────────────────────
    else:
        results.append("Unknown scenario type. Please provide a valid scenario.")
        risk_level = "unknown"

    return {
        "scenario_type": scenario.get("scenario_type", "unknown"),
        "analysis": results,
        "risk_level": risk_level
    }


def compare_race_pace(laps_data: list) -> dict:
    """
    Analyzes pace trends across multiple laps
    """

    if not laps_data or len(laps_data) < 2:
        return {"error": "Not enough lap data to analyze pace trend."}

    # Perform pace calculations using NumPy
    paces = np.array([lap["pace"] for lap in laps_data])

    avg_pace = np.round(np.mean(paces), 3)
    pace_delta = np.round(paces[-1] - paces[0], 3)
    std_dev = np.round(np.std(paces), 4)
    max_pace = np.round(np.max(paces), 3)
    min_pace = np.round(np.min(paces), 3)

    # Analyze pace trends using Pandas DataFrame
    pace_df = pd.DataFrame(laps_data)
    pace_df['pace_change'] = pace_df['pace'].diff()
    degrading_laps = int((pace_df['pace_change'] > 0).sum())

    trend = "stable"
    trend_note = ""

    if pace_delta > 0.05:
        trend = "degrading"
        trend_note = "Pace dropping significantly. Tyre or fuel issue suspected."
    elif pace_delta < -0.05:
        trend = "improving"
        trend_note = "Pace improving. Driver in good rhythm."
    else:
        trend_note = "Pace stable. No immediate action needed."

    return {
        "laps_analyzed": len(laps_data),
        "average_pace": float(avg_pace),
        "pace_trend": trend,
        "pace_delta": float(pace_delta),
        "std_deviation": float(std_dev),
        "fastest_lap_pace": float(min_pace),
        "slowest_lap_pace": float(max_pace),
        "degrading_laps_count": degrading_laps,
        "analysis": trend_note
    }