# telemetry_engine.py  —  physics-based, no random jumps
import math
from tyre_strategy import TyreDegradation

class TelemetrySimulator:
    def __init__(self, total_laps: int = 57, compound: str = "SOFT"):
        self.lap           = 1
        self.total_laps    = total_laps
        self.compound      = compound
        self.tyre_age      = 0
        self.fuel          = 110.0
        self.ers_battery   = 100.0
        self.gap_to_leader = 0.0
        self._tyre_engine  = TyreDegradation()

    def generate_lap_data(self, driver_name: str = "Max Verstappen") -> dict:
        base_laptime    = 90.0
        tyre_data       = self._tyre_engine.calculate(self.compound, self.tyre_age)
        tyre_effect     = tyre_data["lap_time_penalty_sec"]
        fuel_effect     = -self.fuel * 0.03
        track_variation = 0.25 * math.sin(self.lap * 1.3)
        lap_time        = base_laptime + tyre_effect + fuel_effect + track_variation

        self.fuel        = max(0.0, self.fuel - 1.8)
        ers_harvest      = 5.0 + 2.0 * math.sin(self.lap * 0.7)
        self.ers_battery = min(100.0, self.ers_battery - 5.0 + ers_harvest)
        self.tyre_age   += 1

        gap_delta          = 0.1 + 0.15 * math.sin(self.lap * 0.5)
        self.gap_to_leader = max(0.0, self.gap_to_leader + gap_delta)

        base_speed   = 280.0
        speed_effect = (tyre_data["current_grip"] - 0.8) * 80
        fuel_speed   = (110.0 - self.fuel) * 0.05
        speed_kmh    = round(base_speed + speed_effect + fuel_speed, 1)

        rpm      = int(8000 + (speed_kmh / 320) * 4500)
        rpm      = max(8000, min(12500, rpm))
        gear     = max(1, min(8, int(speed_kmh / 40) + 1))
        throttle = round(85.0 + tyre_data["current_grip"] * 10 - (110 - self.fuel) * 0.05, 1)
        throttle = max(0.0, min(100.0, throttle))

        # tyre_wear: 0-100 percentage based on age and compound
        wear_rate  = {"SOFT": 2.8, "MEDIUM": 1.9, "HARD": 1.2}.get(self.compound, 2.0)
        tyre_wear  = min(100.0, round(self.tyre_age * wear_rate, 1))

        return {
            "lap":               self.lap,
            "driver":            driver_name,
            "lap_time":          round(lap_time, 3),
            "sector_1":          round(lap_time * 0.31, 3),
            "sector_2":          round(lap_time * 0.38, 3),
            "sector_3":          round(lap_time * 0.31, 3),
            "compound":          self.compound,
            "tyre_age":          self.tyre_age,
            "tyre_wear":         tyre_wear,
            "tyre_grip":         tyre_data["current_grip"],
            "tyre_penalty_sec":  tyre_data["lap_time_penalty_sec"],
            "overheating_risk":  tyre_data["overheating_risk"],
            "pit_in_laps":       tyre_data["recommended_pit_in_laps"],
            "fuel_remaining":    round(self.fuel, 2),
            "ers_battery":       round(self.ers_battery, 1),
            "gap_to_leader":     round(self.gap_to_leader, 3),
            # Fields frontend expects (both naming styles)
            "speed":             speed_kmh,
            "speed_kmh":         speed_kmh,
            "rpm":               rpm,
            "engine_rpm":        rpm,
            "gear":              gear,
            "throttle":          throttle,
            "throttle_percent":  throttle,
            "ers":               round(self.ers_battery, 1),
            "ers_deploy":        round(100 - self.ers_battery, 1),
            "drs":               speed_kmh > 290,
            "brake_pressure":    round(max(0, (1 - tyre_data["current_grip"]) * 0.6), 2),
            "total_laps":        self.total_laps,
        }
