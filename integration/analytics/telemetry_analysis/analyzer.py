import pandas as pd
import numpy as np

def analyze_telemetry(data: dict) -> dict:
    insights = []
    warnings = []

    # Analyze using Pandas Series
    telemetry_series = pd.Series({
        'tyre_wear': data['tyre_wear'],
        'fuel_level': data['fuel_level'],
        'ers_battery': data.get('ers_battery', 0),
        'pace_delta': data.get('pace_delta', 0)
    })

    # Tyre check
    if telemetry_series['tyre_wear'] > 70:
        warnings.append("Tyre degradation critical.")
    elif telemetry_series['tyre_wear'] > 50:
        insights.append("Tyre wear moderate. Monitor closely.")

    # Fuel check
    if telemetry_series['fuel_level'] < 15:
        warnings.append("Fuel level low. Lift-and-coast recommended.")
    elif telemetry_series['fuel_level'] < 25:
        insights.append("Fuel level moderate. Consider fuel saving mode.")

    # ERS check
    ers = telemetry_series['ers_battery']
    if ers < 30:
        insights.append("ERS deployment inefficient. Harvesting needed.")
    elif ers > 80:
        insights.append("ERS ready. Overtake boost available.")

    # Pace check using numpy
    pace_delta = telemetry_series['pace_delta']
    if pace_delta > 0.05:
        warnings.append("Pace dropping. Investigate tyre or fuel issue.")

    # Pit window
    if telemetry_series['tyre_wear'] > 65 and data['lap'] >= 15:
        insights.append(
            f"Pit window suggested: Lap {data['lap'] + 1} to {data['lap'] + 3}."
        )

    # Traffic check
    if data.get("traffic_ahead", False):
        insights.append("Traffic ahead detected. Monitor gap for overtake opportunity.")

    return {
        "lap": data["lap"],
        "warnings": warnings,
        "insights": insights
    }