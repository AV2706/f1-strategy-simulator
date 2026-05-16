import numpy as np
import pandas as pd


def compare_strategies(data: dict) -> dict:
    strategies = {}

    # Create DataFrame from telemetry data
    strategy_df = pd.DataFrame([{
        'tyre_wear': data['tyre_wear'],
        'fuel_level': data['fuel_level']
    }])

    tyre_wear = strategy_df['tyre_wear'].values[0]
    fuel_level = strategy_df['fuel_level'].values[0]

    # NumPy array for strategy scoring
    strategy_scores = np.array([
        100 - tyre_wear,  # aggressive score — lower wear = better
        50,               # balanced score — always medium
        tyre_wear         # tyre_saving score — higher wear = more needed
    ])

    # Aggressive Strategy
    if tyre_wear < 50 and fuel_level > 25:
        strategies["aggressive"] = {
            "viable": True,
            "note": "Push pace. Tyre and fuel levels support aggressive driving."
        }
    else:
        strategies["aggressive"] = {
            "viable": False,
            "note": "Not recommended. High tyre wear or low fuel detected."
        }

    # Balanced Strategy
    strategies["balanced"] = {
        "viable": True,
        "note": "Maintain current pace. Extends tyre life and manages fuel."
    }

    # Tyre Saving Strategy
    if tyre_wear > 60:
        strategies["tyre_saving"] = {
            "viable": True,
            "note": "Reduce pace to extend tyre life. Pit later."
        }
    else:
        strategies["tyre_saving"] = {
            "viable": False,
            "note": "Not needed yet. Tyre wear within limits."
        }

    # Best recommendation using numpy score
    strategy_names = ["aggressive", "balanced", "tyre_saving"]
    best_index = int(np.argmax(strategy_scores))

    # Override with race logic
    if not strategies["aggressive"]["viable"] and tyre_wear > 60:
        best = "tyre_saving"
    elif fuel_level < 20:
        best = "balanced"
    else:
        best = strategy_names[best_index]

    return {"strategies": strategies, "recommended": best}