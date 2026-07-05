import httpx
from loguru import logger
import asyncio
from typing import Dict, Any

class WeatherService:
    """Service to ingest data via Open-Meteo and NOAA (mocked if NOAA unavailable)"""

    def __init__(self):
        # Open-Meteo doesn't require an API key for basic usage
        self.open_meteo_url = "https://api.open-meteo.com/v1/forecast"
        
        # Mapping cities to coordinates for Open-Meteo
        self.city_coordinates = {
            "Delhi": {"lat": 28.6139, "lon": 77.2090},
            "London": {"lat": 51.5074, "lon": -0.1278},
            "New York": {"lat": 40.7128, "lon": -74.0060},
            "Tokyo": {"lat": 35.6762, "lon": 139.6503},
            "Paris": {"lat": 48.8566, "lon": 2.3522},
            "Sydney": {"lat": -33.8688, "lon": 151.2093},
            "Miami": {"lat": 25.7617, "lon": -80.1918}
        }

    async def fetch_open_meteo_data(self, city: str) -> Dict[str, Any]:
        """Fetches forecast data from Open-Meteo for a given city."""
        coords = self.city_coordinates.get(city)
        if not coords:
            logger.warning(f"Coordinates for {city} not found. Returning empty.")
            return {}

        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.open_meteo_url, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch Open-Meteo data for {city}: {e}")
            return {}

    async def fetch_noaa_data(self, city: str) -> Dict[str, Any]:
        """Mocked NOAA fetcher. Real NOAA API only covers US locations mostly."""
        # For a production app, we would use gridpoints endpoint for US cities only
        return {"source": "NOAA", "forecast": "Normal conditions expected", "alert": None}

    async def get_weather_for_cities(self, cities: list[str]) -> Dict[str, Any]:
        """Runs concurrent fetches for all requested cities."""
        results = {}
        
        async def fetch_city(city):
            om_data = await self.fetch_open_meteo_data(city)
            noaa_data = await self.fetch_noaa_data(city)
            return city, {"open_meteo": om_data, "noaa": noaa_data}
            
        tasks = [fetch_city(city) for city in cities]
        completed = await asyncio.gather(*tasks)
        
        for city, data in completed:
            results[city] = data
            
        return results
