import numpy as np

def analyze_ers(data: dict) -> dict:
    recommendations = []

    ers = data.get("ers_battery", data.get("ers_percentage", 0))
    deployed = data.get("ers_deployed", 0)
    harvested = data.get("ers_harvested", 0)

    # NumPy se efficiency calculate karo
    ers_values = np.array([ers, deployed, harvested])
    efficiency = np.round(
        (harvested / deployed * 100) if deployed > 0 else 0, 2
    )

    if ers > 75:
        recommendations.append("ERS fully charged. Deploy for overtake opportunity.")
    elif ers < 25:
        recommendations.append("ERS critically low. Switch to harvest mode immediately.")
    else:
        recommendations.append("ERS moderate. Balanced deployment recommended.")

    gap = data.get("gap_to_leader", data.get("gap_to_ahead", 999))
    if gap < 1.5 and ers > 60:
        recommendations.append("Close gap detected. Overtake boost recommended now.")

    if deployed > 0 and harvested < deployed:
        recommendations.append(
            f"ERS harvesting behind deployment. Efficiency low."
        )

    return {
        "ers_status": int(ers),
        "ers_efficiency_percent": float(efficiency),
        "recommendations": recommendations
    }