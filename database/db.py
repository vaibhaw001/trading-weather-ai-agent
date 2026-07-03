import sqlite3
import os
from datetime import datetime
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database connection and operations for persistent state."""
    
    def __init__(self):
        # Resolve path (sqlite:///weather_agent.db -> weather_agent.db)
        db_filename = settings.DATABASE_PATH.replace("sqlite:///", "")
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_filename)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initializes tables if they do not exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        city_name TEXT,
                        event_predicted TEXT,
                        probability REAL,
                        confidence REAL,
                        reasoning TEXT,
                        timestamp TEXT
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        order_id TEXT PRIMARY KEY,
                        city_name TEXT,
                        side TEXT,
                        size REAL,
                        price REAL,
                        kelly_fraction REAL,
                        timestamp TEXT
                    )
                ''')
                conn.commit()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            
    def insert_prediction(self, prediction_result):
        """Saves an LLM prediction to the DB."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO predictions (city_name, event_predicted, probability, confidence, reasoning, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    prediction_result.city_name,
                    prediction_result.event_predicted,
                    prediction_result.probability,
                    prediction_result.confidence,
                    prediction_result.reasoning,
                    datetime.utcnow().isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to insert prediction: {e}")

    def insert_trade(self, order, kelly_fraction: float):
        """Saves an executed paper trade to the DB."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO trades (order_id, city_name, side, size, price, kelly_fraction, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order.order_id,
                    order.city_name,
                    order.side,
                    order.size,
                    order.price,
                    kelly_fraction,
                    order.timestamp
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to insert trade: {e}")

    def get_all_predictions(self):
        """Fetches all predictions from the database."""
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM predictions ORDER BY timestamp DESC')
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch predictions: {e}")
            return []
            
    def get_all_trades(self):
        """Fetches all trades from the database."""
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC')
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch trades: {e}")
            return []
