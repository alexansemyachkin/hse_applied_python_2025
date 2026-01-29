import requests
from config import OPENWEATHER_API_KEY


def get_temperature(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    return response.json()["main"]["temp"]
