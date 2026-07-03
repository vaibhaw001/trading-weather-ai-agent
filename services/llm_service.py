import os
from typing import Optional
from openai import OpenAI
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class LLMConnectionError(Exception):
    """Raised when the LLM service fails to connect or return a valid response."""
    pass


class LLMService:
    """Service to interact with OpenRouter via the OpenAI client interface."""
    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY is not set. API calls will fail.")
            
        # OpenRouter provides an OpenAI-compatible API
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.OPENROUTER_MODEL

    def generate_response(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Sends a request to OpenRouter and returns the text response."""
        try:
            logger.info(f"Requesting completion from OpenRouter using model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                # Temperature low for more deterministic probability outputs
                temperature=0.2, 
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenRouter LLM: {e}")
            raise LLMConnectionError(f"Failed to communicate with LLM: {e}")
