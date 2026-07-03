import logging
from typing import Dict, List, Any
import pandas as pd
from apify_client import ApifyClient
from config.settings import settings
from models.weather import CityWeatherSummary, DailyForecast

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class WeatherService:
    """Service to ingest and normalize weather data via Apify."""
    
    # Using 5 target cities for Polymarket relevance
    TARGET_CITIES = ["New York", "London", "Tokyo", "Sydney", "Miami"]

    def __init__(self):
        if not settings.APIFY_API_TOKEN:
            logger.warning("APIFY_API_TOKEN is not set. Data fetching will fail.")
        self.client = ApifyClient(settings.APIFY_API_TOKEN)

    def fetch_global_data(self) -> List[Dict[str, Any]]:
        """Fetches data using the 'weather-api' Apify actor."""
        logger.info("Fetching global weather data via Apify (weather-api)...")
        # In a real scenario, you use the exact actor ID, e.g., 'janes/weather-api'
        # We will mock the structure expected from the actor run.
        run_input = {
            "locations": self.TARGET_CITIES,
            "forecastDays": 7
        }
        
        try:
            # actor_call = self.client.actor("username/weather-api").call(run_input=run_input)
            # return list(self.client.dataset(actor_call["defaultDatasetId"]).iterate_items())
            
            # Mocking the response for the architecture assessment
            logger.info("Mocking global API call due to placeholder actor ID.")
            return [
                {"city": city, "temp_c": 22.5, "forecast": [{"date": "2023-11-01", "max": 25, "min": 18, "precip": 0.2, "condition": "Cloudy"}]}
                for city in self.TARGET_CITIES
            ]
        except Exception as e:
            logger.error(f"Error fetching global data: {e}")
            return []

    def fetch_local_data(self) -> List[Dict[str, Any]]:
        """Fetches data using the 'weather-database-scraper' Apify actor."""
        logger.info("Fetching local weather data via Apify (weather-database-scraper)...")
        run_input = {
            "searchQueries": self.TARGET_CITIES,
        }
        
        try:
            # actor_call = self.client.actor("username/weather-database-scraper").call(run_input=run_input)
            # return list(self.client.dataset(actor_call["defaultDatasetId"]).iterate_items())
            
            # Mocking the response
            logger.info("Mocking local scraper API call due to placeholder actor ID.")
            return [
                {"location": city, "current_temp": 23.0, "predictions": [{"day": "2023-11-01", "high": 24, "low": 19, "rain_chance": 0.1, "desc": "Partly Cloudy"}]}
                for city in self.TARGET_CITIES
            ]
        except Exception as e:
            logger.error(f"Error fetching local data: {e}")
            return []

    def get_standardized_data(self) -> Dict[str, CityWeatherSummary]:
        """
        Merges global and local data, standardizing it into Pydantic models (and Pandas for analysis if needed).
        """
        global_data = self.fetch_global_data()
        local_data = self.fetch_local_data()
        
        standardized_summaries = {}
        
        # Simplified merging logic for demonstration
        for i, city in enumerate(self.TARGET_CITIES):
            g_item = global_data[i] if i < len(global_data) else {}
            l_item = local_data[i] if i < len(local_data) else {}
            
            # Use local data for current temp as it might be more accurate/live
            current_temp = l_item.get("current_temp", g_item.get("temp_c", 20.0))
            
            # Normalize forecast (averaging or preferring one source)
            forecast_list = []
            if "forecast" in g_item:
                for day_data in g_item["forecast"]:
                    forecast_list.append(DailyForecast(
                        date=day_data["date"],
                        temp_max_c=day_data["max"],
                        temp_min_c=day_data["min"],
                        precipitation_prob=day_data["precip"],
                        condition=day_data["condition"]
                    ))
            
            summary = CityWeatherSummary(
                city_name=city,
                country="Unknown", # Would map dynamically in prod
                current_temp_c=current_temp,
                forecast=forecast_list
            )
            standardized_summaries[city] = summary
            
        return standardized_summaries

    def get_data_as_dataframe(self) -> pd.DataFrame:
        """Exports the standardized summaries as a Pandas DataFrame."""
        summaries = self.get_standardized_data()
        rows = []
        for city, summary in summaries.items():
            for day in summary.forecast:
                rows.append({
                    "city": summary.city_name,
                    "date": day.date,
                    "current_temp_c": summary.current_temp_c,
                    "max_temp_c": day.temp_max_c,
                    "min_temp_c": day.temp_min_c,
                    "precip_prob": day.precipitation_prob,
                    "condition": day.condition
                })
        return pd.DataFrame(rows)
