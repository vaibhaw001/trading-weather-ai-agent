import pytest
from agents.risk_agent import RiskAgent
from models.trading import MarketOdds, TradeDecision
from agents.prediction_agent import PredictionResult
from config.settings import settings

@pytest.fixture
def risk_agent():
    return RiskAgent()

def test_kelly_edge_yes(risk_agent):
    """Test Kelly Criterion when AI predicts higher probability than market for YES."""
    prediction = PredictionResult(
        city_name="TestCity",
        event_predicted="Rain",
        probability=0.8, # AI believes 80% chance
        confidence=0.9,
        reasoning="Test"
    )
    market = MarketOdds(
        city_name="TestCity",
        yes_price=0.5, # Market believes 50% chance
        no_price=0.5
    )
    
    # Kelly = p - (q / b)
    # p = 0.8, q = 0.2
    # price = 0.5 -> decimal odds = 2 -> b = 1
    # Kelly = 0.8 - (0.2 / 1) = 0.6
    
    decision = risk_agent.evaluate_trade(prediction, market)
    assert decision.action == "BUY_YES"
    assert decision.kelly_fraction == pytest.approx(0.6, 0.01)

def test_kelly_edge_no(risk_agent):
    """Test Kelly Criterion when AI predicts lower probability than market for YES (Edge on NO)."""
    prediction = PredictionResult(
        city_name="TestCity",
        event_predicted="Rain",
        probability=0.2, # AI believes 20% chance of rain (80% chance NO)
        confidence=0.9,
        reasoning="Test"
    )
    market = MarketOdds(
        city_name="TestCity",
        yes_price=0.5, 
        no_price=0.5 # Market believes 50% chance NO
    )
    
    # Edge on NO side
    # p_no = 0.8, q_no = 0.2
    # price = 0.5 -> b = 1
    # Kelly = 0.8 - (0.2 / 1) = 0.6
    
    decision = risk_agent.evaluate_trade(prediction, market)
    assert decision.action == "BUY_NO"
    assert decision.kelly_fraction == pytest.approx(0.6, 0.01)

def test_kelly_no_edge(risk_agent):
    """Test Kelly Criterion when AI prediction matches market perfectly."""
    prediction = PredictionResult(
        city_name="TestCity",
        event_predicted="Rain",
        probability=0.5,
        confidence=0.9,
        reasoning="Test"
    )
    market = MarketOdds(
        city_name="TestCity",
        yes_price=0.5,
        no_price=0.5
    )
    
    decision = risk_agent.evaluate_trade(prediction, market)
    assert decision.action == "HOLD"
    assert decision.kelly_fraction == 0.0

def test_max_exposure_cap(risk_agent):
    """Test that recommended position size respects the max exposure cap."""
    prediction = PredictionResult(
        city_name="TestCity",
        event_predicted="Rain",
        probability=0.99, # Massive edge -> huge kelly fraction
        confidence=0.9,
        reasoning="Test"
    )
    market = MarketOdds(
        city_name="TestCity",
        yes_price=0.1,
        no_price=0.9
    )
    
    decision = risk_agent.evaluate_trade(prediction, market)
    # The Kelly fraction will be very high (close to 1.0)
    assert decision.kelly_fraction > settings.MAX_EXPOSURE_PER_TRADE
    
    # However, position size should be strictly capped
    expected_size = settings.STARTING_BANKROLL * settings.MAX_EXPOSURE_PER_TRADE
    assert decision.recommended_position_size == pytest.approx(expected_size, 0.01)
