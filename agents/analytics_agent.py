from database import crud
from sqlalchemy.orm import Session
from loguru import logger

class AnalyticsAgent:
    def __init__(self):
        pass

    async def execute(self, db: Session):
        """
        Calculates Win Rate, ROI, Sharpe Ratio, Drawdown.
        """
        logger.info("Analytics Agent generating metrics...")
        
        # In a real scenario, this would aggregate over all closed orders.
        # This is a simplified calculation.
        
        closed_orders = crud.get_orders(db, status="CLOSED_WIN") + crud.get_orders(db, status="CLOSED_LOSS")
        total_closed = len(closed_orders)
        wins = len([o for o in closed_orders if o.status == "CLOSED_WIN"])
        
        win_rate = (wins / total_closed * 100) if total_closed > 0 else 0.0
        
        # Dummy values for ROI, Sharpe, Drawdown as placeholders for complex financial math
        roi = 0.0
        if total_closed > 0:
            total_pnl = sum([o.pnl for o in closed_orders])
            portfolio = crud.get_latest_portfolio(db)
            start_cap = portfolio.total_capital if portfolio else 1000.0 # From initial
            roi = (total_pnl / start_cap) * 100 if start_cap > 0 else 0.0
            
        sharpe_ratio = 1.2 # Placeholder
        drawdown = 5.0 # Placeholder
        
        crud.update_analytics(db, win_rate, roi, sharpe_ratio, drawdown)
        logger.info(f"Analytics Generated -> Win Rate: {win_rate:.1f}% | ROI: {roi:.2f}%")
        
        return {
            "win_rate": win_rate,
            "roi": roi,
            "sharpe_ratio": sharpe_ratio,
            "drawdown": drawdown
        }
