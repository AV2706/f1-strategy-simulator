import pandas as pd
import numpy as np

def analyze_fuel(data: dict) -> dict:
    recommendations = []
    mode = "balanced"

    # Analyze fuel using Pandas DataFrame
    fuel_df = pd.DataFrame([{
        'fuel_level': data['fuel_level'],
        'lap': data['lap'],
        'pace_delta': data.get('pace_delta', 0)
    }])

    fuel_level = fuel_df['fuel_level'].values[0]

    # Estimate fuel consumption rate
    estimated_consumption_per_lap = np.round(fuel_level / max(data['lap'], 1), 2)

    if fuel_level < 10:
        recommendations.append(
            "CRITICAL: Fuel extremely low. Immediate lift-and-coast required."
        )
        mode = "save"
    elif fuel_level < 20:
        recommendations.append(
            "Fuel saving mode recommended. Avoid aggressive acceleration zones."
        )
        mode = "save"
    else:
        recommendations.append(
            "Fuel sufficient. Aggressive mode available if needed."
        )
        mode = "aggressive"

    return {
        "fuel_level": int(fuel_level),
        "estimated_consumption_per_lap": float(estimated_consumption_per_lap),
        "recommended_mode": mode,
        "recommendations": recommendations
    }