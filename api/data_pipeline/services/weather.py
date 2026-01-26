"""
Service for fetching weather data from OpenWeatherMap API.
"""
import requests
import logging
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service to fetch weather data from OpenWeatherMap API.
    """
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.lat = settings.LOCATION_LAT
        self.lon = settings.LOCATION_LON

    def get_current_weather(self):
        """
        Fetch current weather data for the configured location.
        
        Returns:
            dict: Weather data or None if failed
        """
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not configured")
            return None

        try:
            url = f"{self.BASE_URL}/weather"
            params = {
                "lat": self.lat,
                "lon": self.lon,
                "appid": self.api_key,
                "units": "metric"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            weather = data.get('weather', [{}])[0]
            main = data.get('main', {})
            clouds = data.get('clouds', {})
            
            return {
                'temperature': main.get('temp'),
                'humidity': main.get('humidity'),
                'cloud_cover': clouds.get('all'),
                'weather_condition': weather.get('main'),
                'description': weather.get('description'),
                'unit': 'metric',
                'timestamp': datetime.now().isoformat(),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in weather fetch: {e}")
            return None

    def get_mock_weather(self):
        """
        Return mock data for testing when API key is not available.
        """
        return {
            'temperature': 28,
            'humidity': 65,
            'cloud_cover': 40,
            'weather_condition': 'Clouds',
            'description': 'scattered clouds',
            'unit': 'metric',
            'timestamp': datetime.now().isoformat(),
        }
