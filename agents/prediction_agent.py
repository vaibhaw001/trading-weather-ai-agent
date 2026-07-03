from pydantic import BaseModel, Field
import json
import logging
from services.llm_service import LLMService
from models.weather import CityWeatherSummary

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
        
    def predict_rain_probability(self, weather_summary: CityWeatherSummary) -> PredictionResult:
        """Predicts the probability of rain in the next 3 days based on ingested data."""
        logger.info(f"Generating prediction for {weather_summary.city_name}")
        
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
            logger.error("No response received from LLM.")
            return self._fallback_prediction(weather_summary.city_name)
            
        try:
            # Clean possible markdown formatting in case the LLM ignores instructions
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned_text)
            return PredictionResult(**data)
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}\nRaw output: {response_text}")
            return self._fallback_prediction(weather_summary.city_name)
            
    def _fallback_prediction(self, city_name: str) -> PredictionResult:
        """Returns a neutral fallback prediction in case of failure."""
        return PredictionResult(
            city_name=city_name,
            event_predicted="Rain within 3 days",
            probability=0.5,
            confidence=0.1,
            reasoning="Fallback due to LLM parsing or connection error."
        )
