"""
Weather Data Collector for Vesta Energy Orchestrator
Gathers historical and real-time weather data from OpenWeatherMap API
"""

import os
import json
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class WeatherDataCollector:
    """
    Collects weather data from OpenWeatherMap API
    Features collected: temperature, humidity, cloud cover, wind speed, solar radiation proxy
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.lat = float(os.getenv('LATITUDE', 12.9716))
        self.lon = float(os.getenv('LONGITUDE', 77.5946))
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key or self.api_key == 'your_openweather_api_key_here':
            print("WARNING: OpenWeatherMap API key not set. Using mock data.")
            self.use_mock = True
        else:
            self.use_mock = False
    
    def get_current_weather(self) -> Dict:
        """Get current weather data"""
        if self.use_mock:
            return self._generate_mock_current_weather()
        
        url = f"{self.base_url}/weather"
        params = {
            'lat': self.lat,
            'lon': self.lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'cloud_cover': data['clouds']['all'],
                'wind_speed': data['wind']['speed'],
                'weather_condition': data['weather'][0]['main'],
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).isoformat(),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).isoformat()
            }
        except Exception as e:
            print(f"Error fetching current weather: {e}")
            return self._generate_mock_current_weather()
    
    def get_forecast(self, days: int = 5) -> List[Dict]:
        """Get weather forecast for next N days"""
        if self.use_mock:
            return self._generate_mock_forecast(days)
        
        url = f"{self.base_url}/forecast"
        params = {
            'lat': self.lat,
            'lon': self.lon,
            'appid': self.api_key,
            'units': 'metric',
            'cnt': days * 8  # 8 readings per day (3-hour intervals)
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecast_data = []
            for item in data['list']:
                forecast_data.append({
                    'timestamp': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'cloud_cover': item['clouds']['all'],
                    'wind_speed': item['wind']['speed'],
                    'weather_condition': item['weather'][0]['main']
                })
            
            return forecast_data
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return self._generate_mock_forecast(days)
    
    def collect_historical_data(self, days: int = 30) -> pd.DataFrame:
        """
        Collect historical weather data
        Note: OpenWeatherMap free tier doesn't provide historical data
        This generates synthetic historical data based on patterns
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
        
        # Solar radiation proxy (inverse of cloud cover during daylight)
        is_daylight = (hours >= 6) & (hours <= 18)
        solar_proxy = is_daylight * (100 - cloud_cover) / 100
        
        df = pd.DataFrame({
            'timestamp': dates,
            'temperature': temperature,
            'humidity': humidity,
            'cloud_cover': cloud_cover,
            'wind_speed': wind_speed,
            'solar_radiation_proxy': solar_proxy,
            'is_daylight': is_daylight
        })
        
        return df
    
    def _generate_mock_current_weather(self) -> Dict:
        """Generate mock current weather data"""
        import random
        now = datetime.now()
        hour = now.hour
        
        return {
            'timestamp': now.isoformat(),
            'temperature': 25 + 8 * abs((hour - 12) / 12) + random.uniform(-2, 2),
            'humidity': 65 + random.uniform(-10, 10),
            'cloud_cover': random.uniform(20, 80),
            'wind_speed': 2 + random.uniform(0, 3),
            'weather_condition': random.choice(['Clear', 'Clouds', 'Rain']),
            'sunrise': now.replace(hour=6, minute=0).isoformat(),
            'sunset': now.replace(hour=18, minute=30).isoformat()
        }
    
    def _generate_mock_forecast(self, days: int) -> List[Dict]:
        """Generate mock forecast data"""
        import random
        forecast = []
        base_time = datetime.now()
        
        for i in range(days * 8):  # 3-hour intervals
            timestamp = base_time + timedelta(hours=i * 3)
            hour = timestamp.hour
            
            forecast.append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': 25 + 8 * abs((hour - 12) / 12) + random.uniform(-2, 2),
                'humidity': 65 + random.uniform(-10, 10),
                'cloud_cover': random.uniform(20, 80),
                'wind_speed': 2 + random.uniform(0, 3),
                'weather_condition': random.choice(['Clear', 'Clouds', 'Rain'])
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
    print("\nCollecting 5-day forecast...")
    forecast = collector.get_forecast(days=5)
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
