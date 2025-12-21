import requests
import aiohttp


def get_weather_sync(city, api_key):
   
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=10)
    return response.json()


async def get_weather_async(city, api_key):
   
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=10) as response:
            return await response.json()
