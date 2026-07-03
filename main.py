import time
import logging
import concurrent.futures
from services.weather_service import WeatherService
from services.llm_service import LLMConnectionError
from services.market_service import MarketService
from agents.prediction_agent import PredictionAgent
from agents.risk_agent import RiskAgent
from agents.trading_agent import TradingAgent
from agents.settlement_agent import SettlementAgent

# Configure standard logging for the daemon
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_city(city, summary, prediction_agent, market_service, risk_agent, trading_agent):
    """Processes a single city's prediction and trading pipeline."""
    try:
        # Phase 2: Reasoning & Prediction
        prediction = prediction_agent.predict_rain_probability(summary)
        logger.info(f"[{city}] Prob: {prediction.probability*100:.1f}% | Conf: {prediction.confidence*100:.1f}%")
        logger.info(f"[{city}] Reasoning: {prediction.reasoning}\n")
        
        # Phase 3: Risk Management & Trading
        market = market_service.get_current_odds(prediction.city_name)
        logger.info(f"[{prediction.city_name}] Market Odds - YES: ${market.yes_price:.2f} | NO: ${market.no_price:.2f}")
        
        decision = risk_agent.evaluate_trade(prediction, market)
        order = trading_agent.execute_trade(decision, market)
        
    except LLMConnectionError as e:
        logger.warning(f"[{city}] Skipped trading due to LLM Circuit Breaker: {e}")
    except Exception as e:
        logger.error(f"[{city}] Error processing city pipeline: {e}")

def run_hermes_daemon():
    """
    Initializes and runs the main daemon loop for the Hermes Weather Trading Agent.
    This acts as the orchestrator for the multi-agent system.
    """
    logger.info("Initializing Hermes Agent Daemon...")
    
    # Initialize Services and Agents
    weather_service = WeatherService()
    prediction_agent = PredictionAgent()
    market_service = MarketService()
    risk_agent = RiskAgent()
    trading_agent = TradingAgent()
    
    logger.info("Daemon started. Running one execution cycle...")
    
    try:
        # Phase 1: Data Ingestion
        logger.info("--- PHASE 1: Data Ingestion ---")
        summaries = weather_service.get_standardized_data()
        
        logger.info("--- PHASE 2 & 3: Concurrent Prediction & Trading Execution ---")
        
        # Concurrently process each city to prevent blocking
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(summaries) if summaries else 1) as executor:
            futures = [
                executor.submit(process_city, city, summary, prediction_agent, market_service, risk_agent, trading_agent)
                for city, summary in summaries.items()
            ]
            concurrent.futures.wait(futures)
            
        logger.info(f"Total Open Orders Added This Cycle: {len(trading_agent.open_orders)}")
        
        # Phase 4: Trade Settlement
        logger.info("--- PHASE 4: Trade Settlement ---")
        settlement_agent = SettlementAgent()
        settlement_agent.simulate_settlement()
        
        logger.info("Cycle completed successfully.")
        
    except Exception as e:
        logger.error(f"Daemon encountered a fatal error during cycle: {e}")

if __name__ == "__main__":
    # Start the daemon
    run_hermes_daemon()
