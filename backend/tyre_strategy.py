# tyre_strategy.py

COMPOUND_DATA = {
    "SOFT":   {"peak_grip": 1.0,  "degradation_rate": 0.015, "lifespan": 20},
    "MEDIUM": {"peak_grip": 0.94, "degradation_rate": 0.008, "lifespan": 35},
    "HARD":   {"peak_grip": 0.88, "degradation_rate": 0.004, "lifespan": 50},
}


class TyreDegradation:
    def calculate(self, compound: str, tyre_age: int) -> dict:
        data = COMPOUND_DATA[compound]
        grip = data["peak_grip"] * (1 - data["degradation_rate"] * tyre_age)
        grip = max(0.6, grip)  # floor — tyres don't fall to zero grip

        overheating_risk = (
            "HIGH"   if tyre_age > data["lifespan"] * 0.8 else
            "MEDIUM" if tyre_age > data["lifespan"] * 0.5 else
            "LOW"
        )

        lap_time_penalty = (data["peak_grip"] - grip) * 5  # seconds lost per lap

        return {
            "compound":               compound,
            "tyre_age":               tyre_age,
            "current_grip":           round(grip, 3),
            "lap_time_penalty_sec":   round(lap_time_penalty, 3),
            "overheating_risk":       overheating_risk,
            "recommended_pit_in_laps": max(0, data["lifespan"] - tyre_age),
        }
