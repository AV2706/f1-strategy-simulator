# IBM Granite Integration (Planned)
# IBM Granite was the original AI model planned for this project.
# It requires IBM WatsonX API key with international payment method.
# Will be integrated by the team lead when credentials are available.
# Planned model: ibm/granite-3-8b-instruct
# Planned endpoint: https://us-south.ml.cloud.ibm.com/ml/v1/text/generation
# ---------------------------------------------------------
# from ibm_watsonx_ai import APIClient, Credentials
# credentials = Credentials(url=os.getenv("IBM_URL"), api_key=os.getenv("IBM_API_KEY"))
# client = APIClient(credentials)
# model = ModelInference(model_id="ibm/granite-3-8b-instruct", api_client=client)
# response = model.generate_text(prompt=prompt)
# ---------------------------------------------------------

import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_ai_summary(recommendation: dict) -> str:
    insights_text = "\n".join(recommendation.get("all_insights", []))

    prompt = f"""
You are an expert F1 race engineer assistant.
Based on the following telemetry analysis for Lap {recommendation.get('lap', '?')}:

Insights:
{insights_text}

Recommended Strategy: {recommendation.get('recommended_strategy', 'balanced')}
Fuel Mode: {recommendation.get('fuel_mode', 'balanced')}

Give a short, clear race strategy recommendation in 2-3 sentences.
Speak like a real F1 race engineer on team radio.
"""

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-lite:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI summary unavailable: {str(e)}"