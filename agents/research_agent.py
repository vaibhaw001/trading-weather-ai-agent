import json
from services.weather_service import WeatherService
from services.apify_service import ApifyService
from database import crud
from sqlalchemy.orm import Session
from loguru import logger

class ResearchAgent:
    def __init__(self):
        self.weather_service = WeatherService()
        self.apify_service = ApifyService()

    async def execute(self, db: Session, cities: list[str]):
        """
        Gathers data from multiple sources, normalizes it, and saves to DB.
        Returns a dictionary of normalized JSON structures per city.
        """
        logger.info(f"Research Agent starting data collection for {cities}")
        
        # 1. Open-Meteo & NOAA data
        weather_data = await self.weather_service.get_weather_for_cities(cities)
        
        # 2. Apify local forecasts & news
        local_data = await self.apify_service.scrape_weather_data(cities)
        
        normalized_results = {}
        for city in cities:
            city_weather = weather_data.get(city, {})
            city_local = next((item for item in local_data if item["city"] == city), {})
            
            combined_data = {
                "global_forecast": city_weather.get("open_meteo", {}),
                "noaa_alert": city_weather.get("noaa", {}),
                "local_forecast": city_local.get("local_forecast", "No local data"),
                "news": city_local.get("news", "No news")
            }
            
            normalized_results[city] = combined_data
            
            # Save to Database
            crud.create_weather_data(db, city_name=city, source="research_agent_combined", data=json.dumps(combined_data))
            
        logger.info("Research Agent data collection complete.")
        return normalized_results
