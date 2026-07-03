import logging
import uuid
from typing import List, Optional
from models.trading import TradeDecision, Order, MarketOdds
from services.notification_service import NotificationService
from database.db import DatabaseManager

logger = logging.getLogger(__name__)

class TradingAgent:
    """
    Simulates order execution against a prediction market like Polymarket.
    Tracks active positions and paper balances.
    """
    def __init__(self):
        self.open_orders: List[Order] = []
        self.notifier = NotificationService()
        self.db = DatabaseManager()
        
    def execute_trade(self, decision: TradeDecision, market: MarketOdds) -> Optional[Order]:
        """Places a paper trade based on the Risk Agent's decision."""
        if decision.action == "HOLD" or decision.recommended_position_size <= 0:
            return None
            
        # Determine the entry price based on the side we are taking
        price = market.yes_price if decision.action == "BUY_YES" else market.no_price
        
        # Calculate number of shares (In Polymarket, $1 = 1 payout share)
        shares_to_buy = decision.recommended_position_size / price
        
        order = Order(
            order_id=str(uuid.uuid4()),
            city_name=decision.city_name,
            side=decision.action,
            size=shares_to_buy,
            price=price
        )
        
        self.open_orders.append(order)
        self.db.insert_trade(order, decision.kelly_fraction)
        logger.info(f"[{decision.city_name}] EXECUTED {order.side} ORDER: {order.size:.2f} shares @ ${order.price:.2f} | Total Stake: ${decision.recommended_position_size:.2f}")
        
        # Broadcast trade alert via Telegram
        alert_msg = (
            f"🚨 *NEW TRADE EXECUTED*\n\n"
            f"🌍 *Market:* {decision.city_name}\n"
            f"📈 *Action:* {order.side}\n"
            f"💰 *Stake:* ${decision.recommended_position_size:.2f}\n"
            f"🎫 *Shares:* {order.size:.2f} @ ${order.price:.2f}\n"
            f"🧠 *AI Confidence:* {decision.confidence*100:.1f}%\n"
            f"⚖️ *Kelly Allocation:* {decision.kelly_fraction*100:.1f}%"
        )
        self.notifier.send_telegram_alert(alert_msg)
        
        return order
