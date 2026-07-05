import os
import sys
from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import uvicorn
from loguru import logger
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from database import models, crud
from agents.research_agent import ResearchAgent
from agents.prediction_agent import PredictionAgent
from agents.market_agent import MarketAgent
from agents.risk_agent import RiskAgent
from agents.trading_agent import TradingAgent
from agents.analytics_agent import AnalyticsAgent

load_dotenv()
db_filename = os.getenv("DATABASE_PATH", "sqlite:///weather_agent.db").replace("sqlite:///", "")
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_filename)
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Weather Trading AI Agent")

# Agent Instances
research_agent = ResearchAgent()
prediction_agent = PredictionAgent()
market_agent = MarketAgent()
risk_agent = RiskAgent()
trading_agent = TradingAgent()
analytics_agent = AnalyticsAgent()

is_running = False

async def run_hermes_cycle():
    """Runs a full cycle of the agent pipeline."""
    global is_running
    is_running = True
    load_dotenv(override=True)
    
    db = Session(bind=engine)
    try:
        cities = ["Delhi", "London", "New York", "Tokyo", "Paris"]
        
        # 1. Research
        research_data = await research_agent.execute(db, cities)
        
        # 2. Prediction
        predictions = await prediction_agent.execute(db, research_data, cities, event="Rain Tomorrow")
        
        # 3. Market
        market_analysis = await market_agent.execute(db, predictions, cities)
        
        # 4. Risk
        risk_assessments = await risk_agent.execute(db, market_analysis)
        
        # 5. Trading
        executed_trades = await trading_agent.execute(db, risk_assessments)
        
        # 6. Analytics
        await analytics_agent.execute(db)
        
        logger.info("Hermes Agent Cycle Completed Successfully.")
    except Exception as e:
        logger.error(f"Hermes Agent Cycle Failed: {e}")
    finally:
        db.close()
        is_running = False

@app.post("/start-agent")
async def start_agent(background_tasks: BackgroundTasks):
    global is_running
    if is_running:
        return {"status": "Already running"}
    background_tasks.add_task(run_hermes_cycle)
    return {"status": "Agent cycle started"}

@app.get("/agent-status")
def get_agent_status():
    global is_running
    return {"is_running": is_running}

@app.post("/stop-agent")
def stop_agent():
    # Placeholder for a more complex cancellation token logic
    return {"status": "Agent stop requested (not immediately forced)"}

@app.post("/reset-data")
def reset_data():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    return {"status": "Data reset successfully"}

@app.get("/weather")
def get_weather(db: Session = Depends(get_db)):
    return crud.get_weather_data(db)

@app.get("/predictions")
def get_predictions(db: Session = Depends(get_db)):
    return crud.get_predictions(db)

@app.get("/markets")
def get_markets(db: Session = Depends(get_db)):
    return crud.get_market_data(db)

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return crud.get_orders(db)

@app.get("/portfolio")
def get_portfolio(db: Session = Depends(get_db)):
    return crud.get_latest_portfolio(db)

@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    return crud.get_latest_analytics(db)

@app.get("/settings")
def get_settings():
    return {
        "max_daily_loss": os.getenv("MAX_DAILY_LOSS", "100.0"),
        "starting_bankroll": os.getenv("STARTING_BANKROLL", "1000.0"),
        "max_exposure": os.getenv("MAX_EXPOSURE_PER_TRADE", "0.10")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
