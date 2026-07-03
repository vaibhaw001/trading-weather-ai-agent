from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MarketOdds(BaseModel):
    """Represents the current price/implied probability of a market on Polymarket."""
    city_name: str
    yes_price: float = Field(..., ge=0.01, le=0.99, description="Current price of the 'YES' share ($0.01 to $0.99)")
    no_price: float = Field(..., ge=0.01, le=0.99, description="Current price of the 'NO' share")

class TradeDecision(BaseModel):
    """The final decision payload calculated by the Risk Agent."""
    city_name: str
    action: str = Field(..., description="'BUY_YES', 'BUY_NO', or 'HOLD'")
    confidence: float
    predicted_probability: float
    kelly_fraction: float
    recommended_position_size: float = 0.0

class Order(BaseModel):
    """Simulated executed order on Polymarket."""
    order_id: str
    city_name: str
    side: str
    size: float
    price: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
