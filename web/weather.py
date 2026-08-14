"""
Open-Meteo weather integration. No API key required.

Provides simple helpers to get current weather by city name (uses Open-Meteo
geocoding) or by coordinates.
"""
from typing import Optional, Dict
import requests
import logging
from .cache import get_cache, set_cache

logger = logging.getLogger(__name__)

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL = 600


def geocode_city(city: str) -> Optional[Dict]:
    if not city:
        return None
    cache_key = f"geocode:{city}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    try:
        resp = requests.get(GEOCODE_URL, params={"name": city, "count": 1}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get('results')
        if results:
            entry = results[0]
            set_cache(cache_key, entry, ttl=CACHE_TTL)
            return entry
        return None
    except Exception as e:
        logger.exception("Geocoding failed: %s", e)
        return None


def get_weather_by_coords(lat: float, lon: float) -> Optional[Dict]:
    cache_key = f"weather:{lat}:{lon}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    try:
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': True,
            'timezone': 'auto'
        }
        resp = requests.get(WEATHER_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cw = data.get('current_weather')
        if cw:
            set_cache(cache_key, cw, ttl=CACHE_TTL)
            return cw
        return None
    except Exception as e:
        logger.exception("Weather fetch failed: %s", e)
        return None


def get_weather_by_city(city: str) -> Optional[Dict]:
    geo = geocode_city(city)
    if not geo:
        return None
    lat = geo.get('latitude')
    lon = geo.get('longitude')
    return get_weather_by_coords(lat, lon)
