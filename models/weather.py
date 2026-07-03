from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DailyForecast(BaseModel):
    """Represents a single day's weather forecast."""
    date: str = Field(..., description="Date of the forecast (YYYY-MM-DD)")
    temp_max_c: float = Field(..., description="Maximum temperature in Celsius")
    temp_min_c: float = Field(..., description="Minimum temperature in Celsius")
    precipitation_prob: float = Field(..., description="Probability of precipitation (0.0 to 1.0)")
    condition: str = Field(..., description="General weather condition (e.g., Rain, Sunny)")

class CityWeatherSummary(BaseModel):
    """Standardized weather summary for a specific city, combining global and local data."""
    city_name: str
    country: str
    current_temp_c: float
    source_global_reliability: float = Field(default=0.8, description="Assumed reliability of global data")
    source_local_reliability: float = Field(default=0.9, description="Assumed reliability of local data")
    forecast: List[DailyForecast]
    
    def to_llm_context(self) -> str:
        """Formats the data into a readable string for the LLM prompt."""
        context = f"Weather Profile for {self.city_name}, {self.country}:\n"
        context += f"Current Temperature: {self.current_temp_c}°C\n"
        context += "Upcoming Forecast:\n"
        for day in self.forecast:
            context += f"  - {day.date}: {day.condition}, Min: {day.temp_min_c}°C, Max: {day.temp_max_c}°C, Precip Prob: {day.precipitation_prob*100}%\n"
        return context
