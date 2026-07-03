import os
import requests
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Handles broadcasting real-time alerts to external services like Telegram."""
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
    def send_telegram_alert(self, message: str):
        """Sends a markdown-formatted message to the configured Telegram chat."""
        if not self.bot_token or not self.chat_id or self.bot_token == "your_telegram_bot_token_here":
            logger.info("Telegram not configured. Suppressing alert.")
            return
            
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info("Telegram alert sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
