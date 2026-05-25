# telemetry_engine.py

import random
from tyre_strategy import TyreDegradation


class TelemetrySimulator:
    def __init__(self, total_laps: int = 57, compound: str = "SOFT"):
        self.lap            = 1
        self.total_laps     = total_laps
        self.compound       = compound
        self.tyre_age       = 0
        self.fuel           = 110.0   # kg, starts full
        self.ers_battery    = 100.0   # percentage
        self.gap_to_leader  = 0.0     # seconds — grows realistically
        self._tyre_engine   = TyreDegradation()

    def generate_lap_data(self, driver_name: str = "Max Verstappen") -> dict:
        # ── Lap time built from real physics, not random ──────────────────
        base_laptime    = 90.0                          # base race lap (sec)
        tyre_data       = self._tyre_engine.calculate(self.compound, self.tyre_age)
        tyre_effect     = tyre_data["lap_time_penalty_sec"]
        fuel_effect     = -self.fuel * 0.03             # lighter car = faster
        # Small ±0.3 s track variation (wind, micro-kerb etc.) — acceptable
        track_variation = random.uniform(-0.3, 0.3)

        lap_time = base_laptime + tyre_effect + fuel_effect + track_variation

        # ── Update car state ──────────────────────────────────────────────
        self.fuel        = max(0.0, self.fuel - 1.8)         # burn ~1.8 kg/lap
        # ERS: deploy 5%, recover 3–7% per lap (realistic harvest range)
        ers_harvest      = random.uniform(3.0, 7.0)
        self.ers_battery = min(100.0, self.ers_battery - 5.0 + ers_harvest)
        self.tyre_age   += 1

        # Gap to leader: realistic drift — small changes each lap, never jumps
        gap_delta           = random.uniform(-0.2, 0.4)
        self.gap_to_leader  = max(0.0, self.gap_to_leader + gap_delta)

        return {
            "lap":                    self.lap,
            "driver":                 driver_name,
            "lap_time":               round(lap_time, 3),
            "sector_1":               round(lap_time * 0.31, 3),
            "sector_2":               round(lap_time * 0.38, 3),
            "sector_3":               round(lap_time * 0.31, 3),
            "compound":               self.compound,
            "tyre_age":               self.tyre_age,
            "tyre_grip":              tyre_data["current_grip"],
            "tyre_penalty_sec":       tyre_data["lap_time_penalty_sec"],
            "overheating_risk":       tyre_data["overheating_risk"],
            "pit_in_laps":            tyre_data["recommended_pit_in_laps"],
            "fuel_remaining":         round(self.fuel, 2),
            "ers_battery":            round(self.ers_battery, 1),
            "gap_to_leader":          round(self.gap_to_leader, 3),
        }
