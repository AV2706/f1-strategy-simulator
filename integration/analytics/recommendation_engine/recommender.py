from analytics.telemetry_analysis.analyzer import analyze_telemetry
from analytics.ers_analysis.ers_analyzer import analyze_ers
from analytics.fuel_analysis.fuel_analyzer import analyze_fuel
from analytics.strategy_insights.strategy_comparator import compare_strategies


class StrategyRecommender:

    def generate_recommendation(self, telemetry_data: dict) -> dict:
        telemetry_result = analyze_telemetry(telemetry_data)
        ers_result = analyze_ers(telemetry_data)
        fuel_result = analyze_fuel(telemetry_data)
        strategy_result = compare_strategies(telemetry_data)

        all_messages = (
            telemetry_result["warnings"] +
            telemetry_result["insights"] +
            ers_result["recommendations"] +
            fuel_result["recommendations"]
        )

        return {
            "lap": telemetry_data["lap"],
            "recommended_strategy": strategy_result["recommended"],
            "strategy_details": strategy_result["strategies"],
            "all_insights": all_messages,
            "fuel_mode": fuel_result["recommended_mode"]
        }