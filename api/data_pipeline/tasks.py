"""
Scheduled tasks for fetching external API data.
These tasks run periodically via Django-Q to fetch carbon intensity and weather data.
"""
import logging
from django.utils import timezone

from .models import GridData
from .services import ElectricityMapsService, WeatherService

logger = logging.getLogger(__name__)


def fetch_carbon_intensity():
    """
    Fetch current carbon intensity from Electricity Maps API.
    This task should be scheduled to run every 15-30 minutes.
    """
    try:
        service = ElectricityMapsService()
        
        # Try to get real data, fall back to mock if API key not configured
        data = service.get_carbon_intensity()
        if data is None:
            logger.warning("Using mock carbon intensity data")
            data = service.get_mock_carbon_intensity()
        
        # Save to database
        grid_data = GridData.objects.create(
            data_type='carbon_intensity',
            value=data['carbon_intensity'],
            unit=data['unit'],
            zone=data['zone'],
            metadata={
                'fossil_free_percentage': data.get('fossil_free_percentage'),
                'renewable_percentage': data.get('renewable_percentage'),
            },
            timestamp=timezone.now()
        )
        
        logger.info(f"Saved carbon intensity: {grid_data}")
        return f"Successfully fetched carbon intensity: {data['carbon_intensity']} {data['unit']}"
        
    except Exception as e:
        logger.error(f"Failed to fetch carbon intensity: {e}")
        raise


def fetch_weather_data():
    """
    Fetch current weather data from OpenWeatherMap API.
    This task should be scheduled to run every 15-30 minutes.
    """
    try:
        service = WeatherService()
        
        # Try to get real data, fall back to mock if API key not configured
        data = service.get_current_weather()
        if data is None:
            logger.warning("Using mock weather data")
            data = service.get_mock_weather()
        
        # Save temperature
        GridData.objects.create(
            data_type='weather',
            value=data['temperature'],
            unit='celsius',
            metadata={
                'humidity': data.get('humidity'),
                'cloud_cover': data.get('cloud_cover'),
                'weather_condition': data.get('weather_condition'),
                'description': data.get('description'),
            },
            timestamp=timezone.now()
        )
        
        logger.info(f"Saved weather data: {data['temperature']}°C, {data.get('description')}")
        return f"Successfully fetched weather: {data['temperature']}°C"
        
    except Exception as e:
        logger.error(f"Failed to fetch weather data: {e}")
        raise


def cleanup_old_data():
    """
    Clean up old sensor and grid data to prevent database bloat.
    Keep only the last 7 days of data.
    This task should be scheduled to run daily.
    """
    try:
        from datetime import timedelta
        from .models import SensorReading
        
        cutoff_date = timezone.now() - timedelta(days=7)
        
        # Delete old sensor readings
        sensor_count = SensorReading.objects.filter(timestamp__lt=cutoff_date).count()
        SensorReading.objects.filter(timestamp__lt=cutoff_date).delete()
        
        # Delete old grid data
        grid_count = GridData.objects.filter(timestamp__lt=cutoff_date).count()
        GridData.objects.filter(timestamp__lt=cutoff_date).delete()
        
        logger.info(f"Cleaned up {sensor_count} sensor readings and {grid_count} grid data entries")
        return f"Cleaned up {sensor_count} sensor readings and {grid_count} grid data entries"
        
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        raise
