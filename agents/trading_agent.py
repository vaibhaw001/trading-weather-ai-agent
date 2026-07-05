import uuid
from database import crud
from sqlalchemy.orm import Session
from loguru import logger

class TradingAgent:
    def __init__(self):
        pass

    async def execute(self, db: Session, risk_assessments: dict):
        """
        Executes simulated trades and updates portfolio.
        """
        logger.info("Trading Agent executing paper trades...")
        executed_trades = []
        
        portfolio = crud.get_latest_portfolio(db)
        if portfolio:
            current_capital = portfolio.total_capital
            current_exposure = portfolio.active_exposure
        else:
            from agents.risk_agent import STARTING_BANKROLL
            current_capital = STARTING_BANKROLL
            current_exposure = 0.0
            
        for city, risk in risk_assessments.items():
            order_id = str(uuid.uuid4())
            action = risk["action"]
            price = risk["price"]
            bet_size = risk["bet_size"]
            shares = bet_size / price if price > 0 else 0
            
            # Save trade
            crud.create_order(
                db,
                order_id=order_id,
                city_name=city,
                side=action,
                size=shares,
                price=price,
                kelly_fraction=risk["kelly_fraction"]
            )
            
            executed_trades.append(order_id)
            current_exposure += bet_size
            
            logger.info(f"[{city}] EXECUTED {action}: {shares:.2f} shares @ ${price:.2f} | Stake: ${bet_size:.2f}")
            
            # Send Telegram Notification
            msg = (
                f"🚨 <b>NEW TRADE EXECUTED</b> 🚨\n"
                f"📍 <b>City:</b> {city}\n"
                f"📈 <b>Action:</b> {action}\n"
                f"💰 <b>Shares:</b> {shares:.2f} @ ${price:.2f}\n"
                f"💵 <b>Stake:</b> ${bet_size:.2f}\n"
                f"📊 <b>Kelly:</b> {risk['kelly_fraction']:.2%}"
            )
            from services.telegram_service import TelegramService
            tg = TelegramService()
            await tg.send_message(msg)
            
        # Update Portfolio
        if executed_trades:
            crud.update_portfolio(db, current_capital, current_exposure)
            
        return executed_trades
