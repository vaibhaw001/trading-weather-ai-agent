from services.market_service import MarketService
from database import crud
from sqlalchemy.orm import Session
from loguru import logger

class MarketAgent:
    def __init__(self):
        self.market_service = MarketService()

    async def execute(self, db: Session, predictions: dict, cities: list[str]):
        """
        Matches AI probability with Market probability to detect positive expected value (Edge).
        """
        logger.info("Market Agent evaluating edges...")
        market_analysis = {}
        
        for city in cities:
            if city not in predictions:
                continue
                
            ai_prob = predictions[city]["probability"] / 100.0  # Normalize to 0-1
            market_data = await self.market_service.get_current_odds(city)
            
            yes_price = market_data["yes_price"]
            no_price = market_data["no_price"]
            
            # Save market data to DB
            crud.create_market_data(db, city, yes_price, no_price, market_data.get("volume", 0.0))
            
            # Edge calculation
            edge_yes = ai_prob - yes_price
            edge_no = (1.0 - ai_prob) - no_price
            
            # Simple EV strategy: if our probability > market implied probability + threshold
            threshold = 0.05
            recommended_action = "WAIT"
            edge = 0.0
            price = 0.0
            win_prob = 0.0
            
            if edge_yes > threshold:
                recommended_action = "BUY_YES"
                edge = edge_yes
                price = yes_price
                win_prob = ai_prob
            elif edge_no > threshold:
                recommended_action = "BUY_NO"
                edge = edge_no
                price = no_price
                win_prob = 1.0 - ai_prob
                
            market_analysis[city] = {
                "action": recommended_action,
                "edge": edge,
                "price": price,
                "win_prob": win_prob
            }
            logger.info(f"[{city}] AI:{ai_prob:.2f} MKT_YES:{yes_price:.2f} -> Action: {recommended_action} (Edge: {edge:.2f})")
            
        return market_analysis
