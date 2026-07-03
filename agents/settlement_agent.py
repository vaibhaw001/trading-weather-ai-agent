import logging
import random
from database.db import DatabaseManager

logger = logging.getLogger(__name__)

class SettlementAgent:
    """Simulates market resolution to close paper trades and calculate PnL."""
    
    def __init__(self):
        self.db = DatabaseManager()

    def simulate_settlement(self):
        """
        Fetches all OPEN trades and randomly resolves them.
        In a production environment, this would verify actual weather conditions.
        """
        logger.info("Starting Trade Settlement Cycle...")
        open_trades = self.db.get_open_trades()
        
        if not open_trades:
            logger.info("No open trades to settle.")
            return

        settled_count = 0
        for trade in open_trades:
            order_id = trade['order_id']
            size = trade['size']
            price = trade['price']
            
            # Simulate a 50/50 win or loss
            is_win = random.choice([True, False])
            
            if is_win:
                status = 'CLOSED_WIN'
                # Profit = Total Payout ($1 per share) - Initial Stake
                pnl = size - (size * price)
                logger.info(f"Settling Trade {order_id} [{trade['city_name']}]: WIN (+${pnl:.2f})")
            else:
                status = 'CLOSED_LOSS'
                # Loss = Initial Stake
                pnl = -(size * price)
                logger.info(f"Settling Trade {order_id} [{trade['city_name']}]: LOSS (${pnl:.2f})")
                
            self.db.update_trade_status(order_id, status, pnl)
            settled_count += 1
            
        logger.info(f"Settlement Cycle Complete. Resolved {settled_count} trades.")
