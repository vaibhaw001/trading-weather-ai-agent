import logging
import random
from database.db import DatabaseManager

logger = logging.getLogger(__name__)

class SettlementAgent:
    """Simulates market resolution to close paper trades and calculate PnL."""
    
    def __init__(self):
        self.db = DatabaseManager()

    def _verify_historical_weather(self, city_name: str) -> bool:
        """
        Simulates an API call to Open-Meteo to check if precipitation occurred in the past 3 days.
        Returns True if rain was recorded, False otherwise.
        """
        import time
        logger.info(f"[{city_name}] Calling Open-Meteo Historical API for precipitation data...")
        time.sleep(0.5) # Simulate network latency
        
        # Simulate realistic weather based on the city (just for mock purposes)
        # In production, this parses the actual JSON response for precipitation > 0
        if city_name in ["London", "Miami", "Tokyo"]:
            logger.info(f"[{city_name}] Rain recorded in historical data.")
            return True
        logger.info(f"[{city_name}] No rain recorded in historical data.")
        return False

    def simulate_settlement(self, force=False):
        """
        Fetches all OPEN trades and resolves them by verifying actual weather.
        """
        logger.info("Starting Trade Settlement Cycle...")
        open_trades = self.db.get_open_trades()
        
        if not open_trades:
            logger.info("No open trades to settle.")
            return

        from datetime import datetime, timedelta
        
        settled_count = 0
        for trade in open_trades:
            # Trades take 3 days to resolve (unless forced)
            trade_time = datetime.fromisoformat(trade['timestamp'])
            if not force and (datetime.utcnow() - trade_time < timedelta(days=3)):
                logger.info(f"Trade for {trade['city_name']} is too new to settle. Leaving OPEN.")
                continue
                
            order_id = trade['order_id']
            size = trade['size']
            price = trade['price']
            city_name = trade['city_name']
            side = trade['side']
            
            # Fetch real-world outcome
            did_it_rain = self._verify_historical_weather(city_name)
            
            # Determine if our trade won based on the outcome
            if side == "BUY_YES" and did_it_rain:
                is_win = True
            elif side == "BUY_NO" and not did_it_rain:
                is_win = True
            else:
                is_win = False
            
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
