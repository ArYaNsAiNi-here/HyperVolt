"""
Service for fetching grid carbon intensity data from Electricity Maps API.
"""
import requests
import logging
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)


class ElectricityMapsService:
    """
    Service to fetch carbon intensity data from Electricity Maps API.
    """
    BASE_URL = "https://api.electricitymap.org/v3"

    def __init__(self):
        self.api_key = settings.ELECTRICITY_MAPS_API_KEY
        self.zone = settings.LOCATION_ZONE

    def get_carbon_intensity(self):
        """
        Fetch current carbon intensity for the configured zone.
        
        Returns:
            dict: Carbon intensity data or None if failed
        """
        if not self.api_key:
            logger.warning("Electricity Maps API key not configured")
            return None

        try:
            url = f"{self.BASE_URL}/carbon-intensity/latest"
            headers = {
                "auth-token": self.api_key
            }
            params = {
                "zone": self.zone
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return {
                'carbon_intensity': data.get('carbonIntensity'),
                'unit': 'gCO2eq/kWh',
                'zone': self.zone,
                'timestamp': data.get('datetime'),
                'fossil_free_percentage': data.get('fossilFreePercentage'),
                'renewable_percentage': data.get('renewablePercentage'),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch carbon intensity: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in carbon intensity fetch: {e}")
            return None

    def get_mock_carbon_intensity(self):
        """
        Return mock data for testing when API key is not available.
        """
        return {
            'carbon_intensity': 450,  # gCO2eq/kWh (typical for India)
            'unit': 'gCO2eq/kWh',
            'zone': self.zone,
            'timestamp': datetime.now().isoformat(),
            'fossil_free_percentage': 25,
            'renewable_percentage': 20,
        }
