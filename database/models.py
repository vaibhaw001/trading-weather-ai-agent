from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class WeatherData(Base):
    __tablename__ = 'weather_data'
    
    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, index=True)
    source = Column(String)  # 'apify', 'open-meteo', 'noaa', 'news'
    data = Column(String)    # JSON string representation
    timestamp = Column(DateTime, default=datetime.utcnow)

class Predictions(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, index=True)
    event_predicted = Column(String)
    probability = Column(Float)
    confidence = Column(Float)
    reasoning = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MarketData(Base):
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, index=True)
    yes_price = Column(Float)
    no_price = Column(Float)
    volume = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Orders(Base):
    __tablename__ = 'orders'
    
    order_id = Column(String, primary_key=True, index=True)
    city_name = Column(String, index=True)
    side = Column(String) # BUY_YES, BUY_NO
    size = Column(Float)
    price = Column(Float)
    kelly_fraction = Column(Float)
    status = Column(String, default='OPEN') # OPEN, CLOSED_WIN, CLOSED_LOSS
    pnl = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Portfolio(Base):
    __tablename__ = 'portfolio'
    
    id = Column(Integer, primary_key=True, index=True)
    total_capital = Column(Float)
    active_exposure = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    win_rate = Column(Float)
    roi = Column(Float)
    sharpe_ratio = Column(Float)
    drawdown = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
