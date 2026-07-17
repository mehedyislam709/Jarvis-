import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JARVIS.MAIN")

# Load environment variables
load_dotenv()

def get_weather_service(plugin_manager: Any, city: str) -> Optional[str]:
    """
    Retrieves weather data using secure credential injection.
    """
    # Security: Retrieve the KEY NAME from env, not the literal secret
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        logger.error("CRITICAL: API_KEY not found in environment variables!")
        return None

    try:
        # Execute plugin with sanitized input
        result = plugin_manager.execute(
            "WeatherPlugin",
            city=city.strip(),
            api_key=api_key
        )
        return result
    except Exception as e:
        logger.error(f"Plugin Execution Failed: {e}")
        return None

# Execution Flow
weather_report = get_weather_service(plugin_manager, "Dhaka")
if weather_report:
    print(f"[SYSTEM] {weather_report}")
