import json
from services.openrouter_service import OpenRouterService
from database import crud
from sqlalchemy.orm import Session
from loguru import logger

class PredictionAgent:
    def __init__(self):
        self.llm_service = OpenRouterService()

    async def execute(self, db: Session, research_data: dict, cities: list[str], event: str = "Rain Tomorrow"):
        """
        Analyzes research data for each city and produces a probability.
        """
        logger.info(f"Prediction Agent analyzing data for event: {event}")
        predictions = {}
        
        system_prompt = """
        You are a quantitative weather analysis AI. Your job is to analyze the provided weather data from multiple sources 
        and output a probability (0-100) and confidence (0-100) that the specified event will happen.
        You must reply strictly with a JSON object in this exact format:
        {
          "city": "CityName",
          "event": "EventName",
          "probability": 82,
          "confidence": 91,
          "explanation": "Brief reasoning here"
        }
        """

        for city in cities:
            data = research_data.get(city, {})
            user_prompt = f"City: {city}\nEvent: {event}\nData: {json.dumps(data)}"
            
            try:
                response = await self.llm_service.generate_completion(system_prompt, user_prompt)
                prediction = json.loads(response)
                
                # Default safety fallbacks
                prob = float(prediction.get("probability", 50.0))
                conf = float(prediction.get("confidence", 50.0))
                expl = prediction.get("explanation", "Failed to generate explanation.")
                
                predictions[city] = {
                    "probability": prob,
                    "confidence": conf,
                    "explanation": expl,
                    "event": event
                }
                
                crud.create_prediction(
                    db,
                    city_name=city,
                    event_predicted=event,
                    probability=prob,
                    confidence=conf,
                    reasoning=expl
                )
                logger.info(f"[{city}] Predicted {prob}% with {conf}% confidence for {event}")
            except Exception as e:
                logger.error(f"Failed to generate prediction for {city}: {e}")
                
        return predictions
