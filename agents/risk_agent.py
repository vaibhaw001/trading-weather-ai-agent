import os
from database import crud
from sqlalchemy.orm import Session
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", "100.0"))
STARTING_BANKROLL = float(os.getenv("STARTING_BANKROLL", "1000.0"))
MAX_EXPOSURE_PER_TRADE = float(os.getenv("MAX_EXPOSURE_PER_TRADE", "0.10"))
KELLY_FRACTION = float(os.getenv("KELLY_FRACTION", "0.25")) # Fractional Kelly

class RiskAgent:
    def __init__(self):
        self.bankroll = STARTING_BANKROLL
        self.max_exposure = MAX_EXPOSURE_PER_TRADE

    async def execute(self, db: Session, market_analysis: dict):
        """
        Applies Kelly Criterion to determine bet size.
        """
        logger.info("Risk Agent evaluating position sizing (Kelly Criterion)...")
        risk_assessments = {}
        
        # Get current portfolio state
        portfolio = crud.get_latest_portfolio(db)
        if portfolio:
            self.bankroll = portfolio.total_capital
            
        for city, analysis in market_analysis.items():
            action = analysis["action"]
            if action == "WAIT":
                continue
                
            price = analysis["price"]
            win_prob = analysis["win_prob"]
            
            # Kelly Criterion Formula: f* = (bp - q) / b
            # Where b = odds received (decimal odds - 1), p = probability of winning, q = probability of losing (1-p)
            # In prediction markets where payout is $1:
            # b = (1 - price) / price
            
            b = (1.0 - price) / price if price > 0 else 0
            q = 1.0 - win_prob
            
            kelly_percentage = 0.0
            if b > 0:
                kelly_percentage = (b * win_prob - q) / b
                
            # Apply fractional Kelly for safety
            safe_kelly = max(0.0, kelly_percentage * KELLY_FRACTION)
            
            # Cap at max exposure
            final_allocation_pct = min(safe_kelly, self.max_exposure)
            bet_size = self.bankroll * final_allocation_pct
            
            if bet_size > 0:
                risk_assessments[city] = {
                    "action": action,
                    "price": price,
                    "bet_size": bet_size,
                    "kelly_fraction": final_allocation_pct
                }
                logger.info(f"[{city}] Risk approved: {action} | Size: ${bet_size:.2f} (Kelly: {final_allocation_pct:.2%})")
            else:
                logger.info(f"[{city}] Risk rejected: Kelly suggested 0 allocation.")
                
        return risk_assessments
