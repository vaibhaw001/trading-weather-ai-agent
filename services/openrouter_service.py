import os
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")

class OpenRouterService:
    def __init__(self):
        self.model = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY', '')}",
            "Content-Type": "application/json"
        }

    async def generate_completion(self, system_prompt: str, user_prompt: str) -> str:
        """
        Calls OpenRouter API to generate predictions.
        """
        current_api_key = os.getenv('OPENROUTER_API_KEY', '')
        if not current_api_key:
            logger.warning("OPENROUTER_API_KEY is not set. Using mocked LLM response.")
            return "{\"probability\": 82, \"confidence\": 91, \"explanation\": \"Mocked explanation due to missing API key.\"}"
            
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=self._get_headers(), json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}")
            return "{}"
