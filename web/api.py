from web.search import search
from web.weather import get_weather_by_city, get_weather_by_coords
from web.news import fetch_headlines

__all__ = [
    'search',
    'get_weather_by_city',
    'get_weather_by_coords',
    'fetch_headlines'
]