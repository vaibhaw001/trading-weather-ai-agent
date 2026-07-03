import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Settings:
    """Application configuration settings loaded from environment variables."""
    
    # API Keys
    APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3-70b-instruct")
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "sqlite:///weather_agent.db")
    
    # Risk parameters
    MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", 100.0))
    STARTING_BANKROLL = float(os.getenv("STARTING_BANKROLL", 1000.0))
    MAX_EXPOSURE_PER_TRADE = float(os.getenv("MAX_EXPOSURE_PER_TRADE", 0.10))

settings = Settings()
