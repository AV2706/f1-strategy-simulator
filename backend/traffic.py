# traffic.py


class TrafficAnalysis:
    def predict_rejoin(
        self,
        pit_loss_sec:    float,
        gap_ahead:       float,
        gap_behind:      float,
        laps_remaining:  int,
    ) -> dict:
        """Predict if driver rejoins in clean air or traffic."""
        rejoins_ahead_of_car_behind = gap_behind > pit_loss_sec
        rejoins_behind_car_ahead    = gap_ahead  < pit_loss_sec

        if rejoins_ahead_of_car_behind and not rejoins_behind_car_ahead:
            air_condition = "CLEAN AIR"
        elif not rejoins_ahead_of_car_behind:
            air_condition = "TRAFFIC — car behind will pass"
        else:
            air_condition = "TRAFFIC — stuck behind car ahead"

        return {
            "air_condition":         air_condition,
            "gap_ahead_after_pit":   round(gap_ahead  - pit_loss_sec, 2),
            "gap_behind_after_pit":  round(gap_behind - pit_loss_sec, 2),
            "clean_air_laps_needed": max(0, round(pit_loss_sec / 1.5)),
        }
