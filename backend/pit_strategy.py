# pit_strategy.py

PIT_LOSS_SECONDS = 22.0  # average time lost in pit lane


class PitStrategy:
    def calculate_undercut(
        self,
        my_lap_time:    float,
        rival_lap_time: float,
        gap_to_rival:   float,
        tyre_deg_engine,
        my_compound:    str,
        my_tyre_age:    int,
        new_compound:   str = "SOFT",
    ) -> dict:
        """Pit one lap before rival to get fresh tyre advantage."""
        fresh_penalty   = tyre_deg_engine.calculate(new_compound, 0)["lap_time_penalty_sec"]
        current_penalty = tyre_deg_engine.calculate(my_compound, my_tyre_age)["lap_time_penalty_sec"]
        my_new_laptime  = my_lap_time - fresh_penalty + current_penalty

        laps_to_recover = PIT_LOSS_SECONDS / max(0.01, rival_lap_time - my_new_laptime)

        return {
            "strategy":         "UNDERCUT",
            "new_compound":     new_compound,
            "pit_loss_sec":     PIT_LOSS_SECONDS,
            "laps_to_recover":  round(laps_to_recover, 1),
            "recommended":      laps_to_recover < 8,
            "my_new_lap_time":  round(my_new_laptime, 3),
        }

    def optimal_pit_window(
        self,
        current_lap:  int,
        tyre_age:     int,
        compound:     str,
        total_laps:   int,
        tyre_engine,
    ) -> dict:
        deg_data        = tyre_engine.calculate(compound, tyre_age)
        latest_safe_lap = current_lap + deg_data["recommended_pit_in_laps"]
        optimal_lap     = max(current_lap + 1, latest_safe_lap - 3)

        return {
            "optimal_pit_lap": int(min(optimal_lap, total_laps - 5)),
            "latest_safe_lap": int(min(latest_safe_lap, total_laps - 3)),
            "urgency":         "URGENT" if tyre_age > 30 else "NORMAL",
        }
