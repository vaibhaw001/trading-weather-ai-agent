import logging
from config.settings import settings
from agents.prediction_agent import PredictionResult
from models.trading import MarketOdds, TradeDecision

logger = logging.getLogger(__name__)

class RiskAgent:
    """
    Evaluates AI predictions against market odds and applies quantitative 
    finance principles (Kelly Criterion) to size positions safely.
    """
    def __init__(self):
        self.bankroll = settings.STARTING_BANKROLL
        self.max_exposure = settings.MAX_EXPOSURE_PER_TRADE

    def evaluate_trade(self, prediction: PredictionResult, market: MarketOdds) -> TradeDecision:
        """
        Calculates optimal bet size using the Kelly Criterion: f* = p - (q / b)
        """
        logger.info(f"[{prediction.city_name}] Risk Agent analyzing edge...")
        
        # p = AI's predicted win probability
        p = prediction.probability
        q = 1.0 - p
        
        action = "HOLD"
        kelly_fraction = 0.0
        
        # Check if we have an edge on the 'YES' side
        if p > market.yes_price:
            action = "BUY_YES"
            # b = decimal odds minus 1. In binary prediction markets, a winning $1 share pays $1. 
            # Decimal odds = 1 / price. So b = (1 / price) - 1
            b = (1.0 / market.yes_price) - 1.0
            kelly_fraction = p - (q / b) if b > 0 else 0
            
        # Check if we have an edge on the 'NO' side
        elif (1 - p) > market.no_price:
            action = "BUY_NO"
            p_no = 1.0 - p
            q_no = 1.0 - p_no
            b = (1.0 / market.no_price) - 1.0
            kelly_fraction = p_no - (q_no / b) if b > 0 else 0
            
        if action == "HOLD" or kelly_fraction <= 0:
            logger.info(f"[{prediction.city_name}] No edge found or Kelly <= 0. Holding.")
            return TradeDecision(
                city_name=prediction.city_name,
                action="HOLD",
                confidence=prediction.confidence,
                predicted_probability=p,
                kelly_fraction=0.0,
                recommended_position_size=0.0
            )
            
        # Risk Management: Cap the Kelly fraction to our max allowable exposure
        # Often quant strategies use 'Half-Kelly' to reduce variance. 
        safe_kelly = min(kelly_fraction, self.max_exposure)
        position_size = self.bankroll * safe_kelly
        
        logger.info(f"[{prediction.city_name}] Edge found! Action: {action} | Kelly: {kelly_fraction:.4f} | Safe Alloc: {safe_kelly*100:.1f}%")
        
        return TradeDecision(
            city_name=prediction.city_name,
            action=action,
            confidence=prediction.confidence,
            predicted_probability=p,
            kelly_fraction=kelly_fraction,
            recommended_position_size=position_size
        )
