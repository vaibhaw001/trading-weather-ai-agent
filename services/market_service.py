import random
import httpx
from loguru import logger

class MarketService:
    """
    Service for interacting with the Polymarket Gamma API.
    Attempts to fetch live odds, falls back to simulation if no active markets are found.
    """
    def __init__(self):
        self.base_url = "https://gamma-api.polymarket.com/events"
        
    async def get_current_odds(self, city_name: str) -> dict:
        """Fetches the current price (implied probability) for the YES and NO shares."""
        logger.info(f"[{city_name}] Fetching live Polymarket odds...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}?active=true&closed=false&limit=50", timeout=10.0)
                if response.status_code == 200:
                    events = response.json()
                    for event in events:
                        title = event.get("title", "").lower()
                        if city_name.lower() in title and ("rain" in title or "temperature" in title):
                            markets = event.get("markets", [])
                            if markets:
                                market = markets[0]
                                prices = market.get("outcomePrices", [])
                                if len(prices) >= 2:
                                    yes_price = float(prices[0])
                                    no_price = float(prices[1])
                                    if yes_price > 0 and no_price > 0:
                                        logger.info(f"[{city_name}] Live market found: '{event.get('title')}'")
                                        return {
                                            "city_name": city_name,
                                            "yes_price": yes_price,
                                            "no_price": no_price,
                                            "volume": float(market.get("volume", 0.0))
                                        }
                logger.warning(f"[{city_name}] No live Polymarket event found. Falling back to simulated odds.")
        except Exception as e:
            logger.error(f"[{city_name}] Polymarket API Error ({e}). Falling back to simulated odds.")
            
        # Fallback Mock random odds
        yes_price = round(random.uniform(0.2, 0.8), 2)
        return {
            "city_name": city_name,
            "yes_price": yes_price,
            "no_price": round(1.0 - yes_price, 2),
            "volume": round(random.uniform(1000, 50000), 2)
        }
