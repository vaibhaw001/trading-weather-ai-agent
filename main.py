import time
import logging
from services.weather_service import WeatherService
from agents.prediction_agent import PredictionAgent

# Configure standard logging for the daemon
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_hermes_daemon():
    """
    Initializes and runs the main daemon loop for the Hermes Weather Trading Agent.
    This acts as the orchestrator for the multi-agent system.
    """
    logger.info("Initializing Hermes Agent Daemon...")
    
    # Initialize Services and Agents
    weather_service = WeatherService()
    prediction_agent = PredictionAgent()
    
    logger.info("Daemon started. Running one execution cycle...")
    
    try:
        # Phase 1: Data Ingestion
        logger.info("--- PHASE 1: Data Ingestion ---")
        summaries = weather_service.get_standardized_data()
        
        # Phase 2: Reasoning & Prediction
        logger.info("--- PHASE 2: Reasoning Engine ---")
        predictions = []
        for city, summary in summaries.items():
            prediction = prediction_agent.predict_rain_probability(summary)
            predictions.append(prediction)
            logger.info(f"[{city}] Prob: {prediction.probability*100:.1f}% | Conf: {prediction.confidence*100:.1f}%")
            logger.info(f"[{city}] Reasoning: {prediction.reasoning}\n")
            
        # Phase 3: Risk Management & Trading
        logger.info("--- PHASE 3: Risk Management & Trading Execution ---")
        from services.market_service import MarketService
        from agents.risk_agent import RiskAgent
        from agents.trading_agent import TradingAgent
        
        market_service = MarketService()
        risk_agent = RiskAgent()
        trading_agent = TradingAgent()
        
        for prediction in predictions:
            market = market_service.get_current_odds(prediction.city_name)
            logger.info(f"[{prediction.city_name}] Market Odds - YES: ${market.yes_price:.2f} | NO: ${market.no_price:.2f}")
            
            decision = risk_agent.evaluate_trade(prediction, market)
            order = trading_agent.execute_trade(decision, market)
            
        logger.info(f"Total Open Orders: {len(trading_agent.open_orders)}")
        
        # Phase 4: Trade Settlement
        logger.info("--- PHASE 4: Trade Settlement ---")
        from agents.settlement_agent import SettlementAgent
        settlement_agent = SettlementAgent()
        settlement_agent.simulate_settlement()
        
        logger.info("Cycle completed successfully.")
        
    except Exception as e:
        logger.error(f"Daemon encountered a fatal error during cycle: {e}")

if __name__ == "__main__":
    # Start the daemon
    run_hermes_daemon()
