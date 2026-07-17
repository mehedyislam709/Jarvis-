import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("766b3d955b2b085bfb6faab1a6646b7d")

weather = self.plugins.execute(
    "WeatherPlugin",
    city="Dhaka",
    api_key=api_key
)
print(weather)
