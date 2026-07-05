import os
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class TelegramService:
    def __init__(self):
        self.enabled = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
        if not self.enabled:
            logger.warning("Telegram Bot Token or Chat ID not found. Notifications disabled.")
            
    async def send_message(self, text: str):
        if not self.enabled:
            return False
            
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info("Telegram notification sent successfully.")
                return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to send Telegram notification: {e} - Response: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
