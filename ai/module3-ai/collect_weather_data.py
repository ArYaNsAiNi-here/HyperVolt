"""
Weather Data Collector for Vesta Energy Orchestrator
Gathers historical and real-time weather data from Open-Meteo API
"""

import os
import json
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class WeatherDataCollector:
    """
    Collects weather data from Open-Meteo API
    Features collected: temperature, humidity, cloud cover, wind speed, 
                       shortwave/direct/diffuse radiation
    """
    
    # API configuration constants
    DEFAULT_MINUTELY_PARAMS = [
        'temperature_2m',
        'relative_humidity_2m',
        'shortwave_radiation',
        'direct_radiation',
        'diffuse_radiation',
        'wind_speed_10m'
    ]
    
    DEFAULT_HOURLY_PARAMS = [
        'temperature_2m',
        'relative_humidity_2m',
        'cloud_cover',
        'weather_code',
        'wind_speed_10m',
        'shortwave_radiation',
        'direct_radiation',
        'diffuse_radiation'
    ]
    
    def __init__(self, minutely_params: List[str] = None, hourly_params: List[str] = None):
        # Open-Meteo doesn't require an API key for free tier (10,000 calls/day)
        self.lat = float(os.getenv('LATITUDE', 12.9716))
        self.lon = float(os.getenv('LONGITUDE', 77.5946))
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.use_mock = False
        
        # Use default params if not provided
        self.minutely_params = minutely_params or self.DEFAULT_MINUTELY_PARAMS
        self.hourly_params = hourly_params or self.DEFAULT_HOURLY_PARAMS
    
    def get_current_weather(self) -> Dict:
        """Get current weather data using Open-Meteo's high-resolution 15-minute data"""
        if self.use_mock:
            return self._generate_mock_current_weather()
        
        params = {
            'latitude': self.lat,
            'longitude': self.lon,
            # High-resolution 15-minute data for immediate optimization
            'minutely_15': ','.join(self.minutely_params),
            # Daily data for sunrise/sunset
            'daily': 'sunrise,sunset',
            'timezone': 'auto',
            'forecast_days': 1
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract the first (current) 15-minute data point
            minutely = data.get('minutely_15', {})
            daily = data.get('daily', {})
            
            # Get current index (first value is most recent)
            idx = 0
            
            return {
                'timestamp': datetime.now().isoformat(),
                'temperature': minutely['temperature_2m'][idx] if 'temperature_2m' in minutely else 25.0,
                'humidity': minutely['relative_humidity_2m'][idx] if 'relative_humidity_2m' in minutely else 65.0,
                'shortwave_radiation': minutely['shortwave_radiation'][idx] if 'shortwave_radiation' in minutely else 0.0,
                'direct_radiation': minutely['direct_radiation'][idx] if 'direct_radiation' in minutely else 0.0,
                'diffuse_radiation': minutely['diffuse_radiation'][idx] if 'diffuse_radiation' in minutely else 0.0,
                'wind_speed': minutely['wind_speed_10m'][idx] if 'wind_speed_10m' in minutely else 2.0,
                'sunrise': daily['sunrise'][0] if 'sunrise' in daily else datetime.now().replace(hour=6, minute=0).isoformat(),
                'sunset': daily['sunset'][0] if 'sunset' in daily else datetime.now().replace(hour=18, minute=30).isoformat()
            }
        except Exception as e:
            print(f"Error fetching current weather from Open-Meteo: {e}")
            return self._generate_mock_current_weather()
    
    def get_forecast(self, days: int = 3) -> List[Dict]:
        """Get weather forecast for next N days using Open-Meteo"""
        if self.use_mock:
            return self._generate_mock_forecast(days)
        
        params = {
            'latitude': self.lat,
            'longitude': self.lon,
            # Hourly data for longer-term planning
            'hourly': ','.join(self.hourly_params),
            'timezone': 'auto',
            'forecast_days': days
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            hourly = data.get('hourly', {})
            times = hourly.get('time', [])
            
            forecast_data = []
            for i in range(len(times)):
                forecast_data.append({
                    'timestamp': times[i],
                    'temperature': hourly['temperature_2m'][i] if 'temperature_2m' in hourly else 25.0,
                    'humidity': hourly['relative_humidity_2m'][i] if 'relative_humidity_2m' in hourly else 65.0,
                    'cloud_cover': hourly['cloud_cover'][i] if 'cloud_cover' in hourly else 50.0,
                    'wind_speed': hourly['wind_speed_10m'][i] if 'wind_speed_10m' in hourly else 2.0,
                    'weather_code': hourly['weather_code'][i] if 'weather_code' in hourly else 0,
                    'shortwave_radiation': hourly['shortwave_radiation'][i] if 'shortwave_radiation' in hourly else 0.0,
                    'direct_radiation': hourly['direct_radiation'][i] if 'direct_radiation' in hourly else 0.0,
                    'diffuse_radiation': hourly['diffuse_radiation'][i] if 'diffuse_radiation' in hourly else 0.0
                })
            
            return forecast_data
        except Exception as e:
            print(f"Error fetching forecast from Open-Meteo: {e}")
            return self._generate_mock_forecast(days)
    
    def collect_historical_data(self, days: int = 30) -> pd.DataFrame:
        """
        Collect historical weather data
        Note: Open-Meteo provides historical data, but for simplicity we generate
        synthetic data with realistic solar radiation patterns
        """
        print(f"Generating synthetic historical weather data for {days} days...")
        
        dates = pd.date_range(
            end=datetime.now(),
            periods=days * 24,  # Hourly data
            freq='h'
        )
        
        # Generate realistic weather patterns
        import numpy as np
        
        # Base patterns with daily and seasonal variations
        hours = dates.hour.values
        day_of_year = dates.dayofyear.values
        
        # Temperature: varies by time of day and season
        temp_base = 25 + 5 * np.sin(2 * np.pi * day_of_year / 365)
        temp_daily = 8 * np.sin(2 * np.pi * hours / 24 - np.pi/2)
        temperature = temp_base + temp_daily + np.random.normal(0, 2, len(dates))
        
        # Humidity: inversely related to temperature
        humidity = 70 - (temperature - 25) * 2 + np.random.normal(0, 5, len(dates))
        humidity = np.clip(humidity, 30, 95)
        
        # Cloud cover: random with some persistence
        cloud_cover = np.cumsum(np.random.normal(0, 10, len(dates)))
        cloud_cover = np.clip(cloud_cover % 100, 0, 100)
        
        # Wind speed: higher during day
        wind_speed = 2 + 3 * (hours / 24) + np.random.normal(0, 1, len(dates))
        wind_speed = np.clip(wind_speed, 0, 15)
        
        # Solar radiation using realistic shortwave radiation (W/m²)
        # Maximum solar radiation at solar noon
        is_daylight = (hours >= 6) & (hours <= 18)
        solar_elevation = np.sin(2 * np.pi * (hours - 6) / 12) * is_daylight
        
        # Shortwave radiation (Global Horizontal Irradiance)
        max_ghi = 1000  # W/m² at peak
        shortwave_radiation = max_ghi * solar_elevation * (100 - cloud_cover) / 100
        shortwave_radiation = np.clip(shortwave_radiation, 0, 1000)
        
        # Direct radiation (beam radiation)
        direct_radiation = shortwave_radiation * 0.7 * (100 - cloud_cover) / 100
        direct_radiation = np.clip(direct_radiation, 0, 800)
        
        # Diffuse radiation (scattered radiation)
        diffuse_radiation = shortwave_radiation - direct_radiation
        diffuse_radiation = np.clip(diffuse_radiation, 0, 400)
        
        df = pd.DataFrame({
            'timestamp': dates,
            'temperature': temperature,
            'humidity': humidity,
            'cloud_cover': cloud_cover,
            'wind_speed': wind_speed,
            'shortwave_radiation': shortwave_radiation,
            'direct_radiation': direct_radiation,
            'diffuse_radiation': diffuse_radiation,
            'is_daylight': is_daylight
        })
        
        return df
    
    def _generate_mock_current_weather(self) -> Dict:
        """Generate mock current weather data"""
        import random
        now = datetime.now()
        hour = now.hour
        
        # Calculate solar radiation based on time of day
        is_daylight = 6 <= hour <= 18
        if is_daylight:
            solar_elevation = abs(np.sin(2 * np.pi * (hour - 6) / 12))
            shortwave_rad = 800 * solar_elevation
        else:
            shortwave_rad = 0.0
        
        return {
            'timestamp': now.isoformat(),
            'temperature': 25 + 8 * abs((hour - 12) / 12) + random.uniform(-2, 2),
            'humidity': 65 + random.uniform(-10, 10),
            'shortwave_radiation': shortwave_rad,
            'direct_radiation': shortwave_rad * 0.7,
            'diffuse_radiation': shortwave_rad * 0.3,
            'wind_speed': 2 + random.uniform(0, 3),
            'sunrise': now.replace(hour=6, minute=0).isoformat(),
            'sunset': now.replace(hour=18, minute=30).isoformat()
        }
    
    def _generate_mock_forecast(self, days: int) -> List[Dict]:
        """Generate mock forecast data"""
        import random
        import numpy as np
        forecast = []
        base_time = datetime.now()
        
        for i in range(days * 24):  # Hourly intervals
            timestamp = base_time + timedelta(hours=i)
            hour = timestamp.hour
            
            # Calculate solar radiation
            is_daylight = 6 <= hour <= 18
            if is_daylight:
                solar_elevation = abs(np.sin(2 * np.pi * (hour - 6) / 12))
                shortwave_rad = (800 + random.uniform(-100, 100)) * solar_elevation
            else:
                shortwave_rad = 0.0
            
            cloud = random.uniform(20, 80)
            
            forecast.append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': 25 + 8 * abs((hour - 12) / 12) + random.uniform(-2, 2),
                'humidity': 65 + random.uniform(-10, 10),
                'cloud_cover': cloud,
                'wind_speed': 2 + random.uniform(0, 3),
                'weather_code': random.choice([0, 1, 2, 3]),  # WMO codes
                'shortwave_radiation': shortwave_rad * (100 - cloud) / 100,
                'direct_radiation': shortwave_rad * 0.7 * (100 - cloud) / 100,
                'diffuse_radiation': shortwave_rad * 0.3
            })
        
        return forecast
    
    def save_to_csv(self, data: pd.DataFrame, filename: str):
        """Save collected data to CSV"""
        output_path = f"data/raw/{filename}"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        print(f"Weather data saved to {output_path}")
        return output_path


def main():
    """Main function to collect and save weather data"""
    collector = WeatherDataCollector()
    
    # Collect current weather
    print("Collecting current weather...")
    current = collector.get_current_weather()
    print(json.dumps(current, indent=2))
    
    # Collect forecast
    print("\nCollecting 3-day forecast...")
    forecast = collector.get_forecast(days=3)
    forecast_df = pd.DataFrame(forecast)
    collector.save_to_csv(forecast_df, 'weather_forecast.csv')
    
    # Generate historical data
    print("\nGenerating historical weather data...")
    historical = collector.collect_historical_data(days=30)
    collector.save_to_csv(historical, 'weather_historical.csv')
    
    print("\n✓ Weather data collection complete!")
    print(f"  - Current weather: {current['temperature']:.1f}°C")
    print(f"  - Forecast data points: {len(forecast)}")
    print(f"  - Historical data points: {len(historical)}")


if __name__ == "__main__":
    main()
