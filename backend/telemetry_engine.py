# telemetry_engine.py  —  physics-based, no random jumps

import math
from tyre_strategy import TyreDegradation


class TelemetrySimulator:
    def __init__(self, total_laps: int = 57, compound: str = "SOFT"):
        self.lap           = 1
        self.total_laps    = total_laps
        self.compound      = compound
        self.tyre_age      = 0
        self.fuel          = 110.0   # kg
        self.ers_battery   = 100.0   # %
        self.gap_to_leader = 0.0     # seconds
        self._tyre_engine  = TyreDegradation()

    def generate_lap_data(self, driver_name: str = "Max Verstappen") -> dict:
        # ── Lap time ─────────────────────────────────────────────────────
        base_laptime = 90.0
        tyre_data    = self._tyre_engine.calculate(self.compound, self.tyre_age)
        tyre_effect  = tyre_data["lap_time_penalty_sec"]
        fuel_effect  = -self.fuel * 0.03          # lighter = faster

        # Smooth ±0.25 s track variation using sine — no random
        track_variation = 0.25 * math.sin(self.lap * 1.3)

        lap_time = base_laptime + tyre_effect + fuel_effect + track_variation

        # ── Car state updates ─────────────────────────────────────────────
        self.fuel      = max(0.0, self.fuel - 1.8)

        # ERS: smooth harvest using sine wave (3–7 % range, no random)
        ers_harvest    = 5.0 + 2.0 * math.sin(self.lap * 0.7)
        self.ers_battery = min(100.0, self.ers_battery - 5.0 + ers_harvest)

        self.tyre_age += 1

        # Gap to leader: smooth drift, never jumps
        gap_delta          = 0.1 + 0.15 * math.sin(self.lap * 0.5)
        self.gap_to_leader = max(0.0, self.gap_to_leader + gap_delta)

        # ── Speed simulation (physics-based per lap phase) ─────────────
        # Simulate average speed varying with tyre grip and fuel load
        base_speed   = 280.0
        speed_effect = (tyre_data["current_grip"] - 0.8) * 80   # grip affects speed
        fuel_speed   = (110.0 - self.fuel) * 0.05               # lighter = faster
        speed_kmh    = round(base_speed + speed_effect + fuel_speed, 1)

        # RPM from speed (realistic F1 range 8000–12500)
        rpm = int(8000 + (speed_kmh / 320) * 4500)
        rpm = max(8000, min(12500, rpm))

        # Gear from speed
        gear = max(1, min(8, int(speed_kmh / 40) + 1))

        # Throttle from tyre grip and fuel
        throttle = round(85.0 + tyre_data["current_grip"] * 10 - (110 - self.fuel) * 0.05, 1)
        throttle = max(0.0, min(100.0, throttle))

        return {
            "lap":                   self.lap,
            "driver":                driver_name,
            "lap_time":              round(lap_time, 3),
            "sector_1":              round(lap_time * 0.31, 3),
            "sector_2":              round(lap_time * 0.38, 3),
            "sector_3":              round(lap_time * 0.31, 3),
            "compound":              self.compound,
            "tyre_age":              self.tyre_age,
            "tyre_grip":             tyre_data["current_grip"],
            "tyre_penalty_sec":      tyre_data["lap_time_penalty_sec"],
            "overheating_risk":      tyre_data["overheating_risk"],
            "pit_in_laps":           tyre_data["recommended_pit_in_laps"],
            "fuel_remaining":        round(self.fuel, 2),
            "ers_battery":           round(self.ers_battery, 1),
            "gap_to_leader":         round(self.gap_to_leader, 3),
            # Extra fields frontend expects
            "speed_kmh":             speed_kmh,
            "engine_rpm":            rpm,
            "gear":                  gear,
            "throttle_percent":      throttle,
            "ers":                   round(self.ers_battery, 1),
        }
