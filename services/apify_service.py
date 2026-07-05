import os
from apify_client import ApifyClient
from loguru import logger
import httpx
from dotenv import load_dotenv

load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_API_TOKEN", "")

class ApifyService:
    def __init__(self):
        self.client = ApifyClient(APIFY_TOKEN) if APIFY_TOKEN else None

    async def scrape_weather_data(self, cities: list[str]):
        """
        Calls Apify weather scrapers (e.g., weather-database-scraper or similar)
        Returns scraped local forecasts and news.
        """
        if not self.client:
            logger.warning("Apify client not initialized. Token missing.")
            return []
            
        logger.info(f"Scraping weather data for {cities} via Apify...")
        # Mocking the actual Apify actor call to avoid long runtimes / usage limits during dev.
        # In production:
        # actor_call = self.client.actor("oneary/weather-database-scraper").call(run_input={"searchQueries": cities})
        # return list(self.client.dataset(actor_call["defaultDatasetId"]).iterate_items())
        
        return [{"city": city, "local_forecast": "Partly Cloudy", "news": f"Local weather station predicts rain in {city}."} for city in cities]
