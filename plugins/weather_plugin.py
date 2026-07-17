import logging
import requests
from typing import Optional, Dict, Any

# Logger initialized to track network requests
logger = logging.getLogger("JARVIS.WEATHER")

class WeatherPlugin:
    """
    Enterprise-grade Weather Plugin for Jarvis.
    Features: Connection pooling, secure API handling, and detailed error reporting.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        # Using a session for connection pooling (faster, more efficient)
        self.session = requests.Session()
        self.session.params = {"appid": self.api_key, "units": "metric"}

    def get_weather(self, city_name: str) -> str:
        """Fetches and processes current weather data for a given city."""
        if not self.api_key or self.api_key == "YOUR_API_KEY":
            return "Error: API key is not configured."

        try:
            response = self.session.get(self.base_url, params={"q": city_name}, timeout=10)
            
            # Handle specific HTTP errors
            if response.status_code == 404:
                return f"City '{city_name}' not found."
            elif response.status_code == 401:
                return "Error: Invalid API Key."
            
            response.raise_for_status() # Raises exception for other 4xx/5xx errors
            
            data = response.json()
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            
            return f"The current temperature in {city_name} is {temp}°C with {desc}."

        except requests.exceptions.Timeout:
            logger.error("Weather API request timed out.")
            return "Error: Weather service is currently unreachable (Timeout)."
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API communication failure: {e}")
            return "Error: Unable to fetch weather data."

# --- Usage Example ---
if __name__ == "__main__":
    # In production, load this from environment variables (python-dotenv)
    weather_engine = WeatherPlugin(api_key="YOUR_ACTUAL_API_KEY")
    print(weather_engine.get_weather("Dhaka"))
