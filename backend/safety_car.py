# safety_car.py


class SafetyCarLogic:
    def recalculate(
        self,
        current_positions: list,
        pit_strategy_engine,
        tyre_engine,
        laps_remaining: int,
    ) -> dict:
        """When SC deploys, everyone bunches up — recalculate strategy."""
        recommendations = []

        for car in current_positions:
            # Safety car neutralises gaps — free pit window within 30 s
            free_pit    = car["gap_to_leader"] < 30
            new_compound = "HARD" if laps_remaining > 20 else "SOFT"

            if free_pit:
                rec          = "PIT NOW — free stop under safety car"
            else:
                rec          = "STAY OUT — position advantage"
                new_compound = car["current_compound"]

            recommendations.append({
                "driver":             car["driver"],
                "recommendation":     rec,
                "suggested_compound": new_compound,
                "position_after":     car["position"],
            })

        return {
            "safety_car_active":      True,
            "recommendations":        recommendations,
            "restart_lap_estimate":   laps_remaining - 3,
        }
