from pydantic import BaseModel, Field
import json
import logging
from services.llm_service import LLMService, LLMConnectionError
from models.weather import CityWeatherSummary
from database.db import DatabaseManager

logger = logging.getLogger(__name__)

class PredictionResult(BaseModel):
    """Structured output expected from the LLM."""
    city_name: str
    event_predicted: str
    probability: float = Field(..., ge=0.01, le=0.99, description="Win probability of the event occurring")
    confidence: float = Field(..., ge=0.01, le=0.99, description="Confidence in the prediction itself")
    reasoning: str

class PredictionAgent:
    """
    Hermes Agent node responsible for analyzing weather data and 
    outputting a trading probability.
    """
    def __init__(self):
        self.llm_service = LLMService()
        self.db = DatabaseManager()
        
    def predict_rain_probability(self, weather_summary: CityWeatherSummary) -> PredictionResult:
        """Predicts the probability of rain in the next 3 days based on ingested data."""
        logger.info(f"Generating prediction for {weather_summary.city_name}")
        
        # Simulation Mode bypass
        from config.settings import settings
        if settings.SIMULATION_MODE:
            import random
            # Deterministic/semi-random mock prediction based on city name for testing variety
            random.seed(hash(weather_summary.city_name))
            prob = round(random.uniform(0.15, 0.85), 2)
            conf = round(random.uniform(0.70, 0.95), 2)
            result = PredictionResult(
                city_name=weather_summary.city_name,
                event_predicted="Rain within 3 days",
                probability=prob,
                confidence=conf,
                reasoning=f"Simulation Mode: Estimated {prob*100:.0f}% chance of precipitation based on mock humidity ({random.randint(50, 90)}%) and historical summer trends."
            )
            self.db.insert_prediction(result)
            return result
        
        system_prompt = (
            "You are a highly sophisticated quantitative weather forecaster and Polymarket trading algorithm. "
            "Your task is to analyze the provided weather data and output a precise probability (between 0.01 and 0.99) "
            "that it will rain in the specified city within the next 3 days. "
            "You must also provide a confidence score representing how certain you are of your own probability.\n\n"
            "Respond ONLY with a valid JSON object matching this schema. No markdown formatting, no extra text:\n"
            "{\n"
            '  "city_name": "string",\n'
            '  "event_predicted": "string (e.g., Rain within 3 days)",\n'
            '  "probability": float (0.01 to 0.99),\n'
            '  "confidence": float (0.01 to 0.99),\n'
            '  "reasoning": "string (Explain why you chose this probability)"\n'
            "}"
        )
        
        user_prompt = f"Please analyze the following data and output the precise JSON prediction:\n\n{weather_summary.to_llm_context()}"
        
        response_text = self.llm_service.generate_response(system_prompt, user_prompt)
        
        if not response_text:
            raise LLMConnectionError(f"No response received from LLM for city {weather_summary.city_name}.")
            
        try:
            # Clean possible markdown formatting in case the LLM ignores instructions
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned_text)
            result = PredictionResult(**data)
            
            # Persist to database
            self.db.insert_prediction(result)
            return result
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}\nRaw output: {response_text}")
            raise LLMConnectionError(f"Failed to parse LLM prediction for {weather_summary.city_name}: {e}")
