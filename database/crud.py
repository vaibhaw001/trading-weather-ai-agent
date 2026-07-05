from sqlalchemy.orm import Session
from . import models
from datetime import datetime

# Weather Data CRUD
def create_weather_data(db: Session, city_name: str, source: str, data: str):
    db_item = models.WeatherData(city_name=city_name, source=source, data=data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_weather_data(db: Session, city_name: str = None, limit: int = 100):
    query = db.query(models.WeatherData)
    if city_name:
        query = query.filter(models.WeatherData.city_name == city_name)
    return query.order_by(models.WeatherData.timestamp.desc()).limit(limit).all()

# Predictions CRUD
def create_prediction(db: Session, city_name: str, event_predicted: str, probability: float, confidence: float, reasoning: str):
    db_item = models.Predictions(
        city_name=city_name,
        event_predicted=event_predicted,
        probability=probability,
        confidence=confidence,
        reasoning=reasoning
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_predictions(db: Session, city_name: str = None, limit: int = 100):
    query = db.query(models.Predictions)
    if city_name:
        query = query.filter(models.Predictions.city_name == city_name)
    return query.order_by(models.Predictions.timestamp.desc()).limit(limit).all()

# Market Data CRUD
def create_market_data(db: Session, city_name: str, yes_price: float, no_price: float, volume: float = 0.0):
    db_item = models.MarketData(city_name=city_name, yes_price=yes_price, no_price=no_price, volume=volume)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_market_data(db: Session, city_name: str = None, limit: int = 100):
    query = db.query(models.MarketData)
    if city_name:
        query = query.filter(models.MarketData.city_name == city_name)
    return query.order_by(models.MarketData.timestamp.desc()).limit(limit).all()

# Orders CRUD
def create_order(db: Session, order_id: str, city_name: str, side: str, size: float, price: float, kelly_fraction: float):
    db_item = models.Orders(
        order_id=order_id,
        city_name=city_name,
        side=side,
        size=size,
        price=price,
        kelly_fraction=kelly_fraction
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_orders(db: Session, status: str = None, limit: int = 100):
    query = db.query(models.Orders)
    if status:
        query = query.filter(models.Orders.status == status)
    return query.order_by(models.Orders.timestamp.desc()).limit(limit).all()

def update_order_status(db: Session, order_id: str, status: str, pnl: float):
    db_item = db.query(models.Orders).filter(models.Orders.order_id == order_id).first()
    if db_item:
        db_item.status = status
        db_item.pnl = pnl
        db.commit()
        db.refresh(db_item)
    return db_item

# Portfolio CRUD
def update_portfolio(db: Session, total_capital: float, active_exposure: float):
    db_item = models.Portfolio(total_capital=total_capital, active_exposure=active_exposure)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_latest_portfolio(db: Session):
    return db.query(models.Portfolio).order_by(models.Portfolio.timestamp.desc()).first()

# Analytics CRUD
def update_analytics(db: Session, win_rate: float, roi: float, sharpe_ratio: float, drawdown: float):
    db_item = models.Analytics(win_rate=win_rate, roi=roi, sharpe_ratio=sharpe_ratio, drawdown=drawdown)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_latest_analytics(db: Session):
    return db.query(models.Analytics).order_by(models.Analytics.timestamp.desc()).first()
