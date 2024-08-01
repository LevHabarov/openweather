import requests
import config

def get_geo(city):
    BASE_URL_GEO = 'http://api.openweathermap.org/geo/1.0/direct?'
    contents = requests.get(f'{BASE_URL_GEO}q={city}&limit=5&appid={config.API_KEY}').json()
    return contents

def get_current_weather(lat, lon):
    BASE_URL_WEATHER = 'https://api.openweathermap.org/data/2.5/weather?'
    contents = requests.get(f'{BASE_URL_WEATHER}lat={lat}&lon={lon}&appid={config.API_KEY}&units=metric&lang=ru').json()
    return contents

def get_forecast_weather(lat, lon):
    BASE_URL_WEATHER = 'https://api.openweathermap.org/data/2.5/weather?'
    contents = requests.get(f'{BASE_URL_WEATHER}lat={lat}&lon={lon}&appid={config.API_KEY}&units=metric&lang=ru').json()
    return contents