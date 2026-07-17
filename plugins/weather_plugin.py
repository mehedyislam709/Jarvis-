import requests

class WeatherPlugin:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city_name):
        url = f"{self.base_url}?q={city_name}&appid={self.api_key}&units=metric"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                weather_desc = data['weather'][0]['description']
                return f"The temperature is {temp}°C with {weather_desc}."
            else:
                return "Failed to get weather data."
        except Exception as e:
            return f"An error occurred: {e}"

# আপনি এখানে আপনার API কি-টি বসাতে পারেন
api_key = "আপনার_এপিআই_কি_এখানে_দিন"
