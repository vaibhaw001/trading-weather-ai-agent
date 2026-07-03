import random
from models.trading import MarketOdds

class MarketService:
    """
    Service for interacting with the Polymarket API.
    Currently mocks live odds to allow for paper trading simulation.
    """
    def get_current_odds(self, city_name: str) -> MarketOdds:
        """Fetches the current price (implied probability) for the YES and NO shares."""
        # Mock random odds between $0.20 and $0.80 for demonstration
        yes_price = round(random.uniform(0.2, 0.8), 2)
        return MarketOdds(
            city_name=city_name,
            yes_price=yes_price,
            no_price=round(1.0 - yes_price, 2)
        )
