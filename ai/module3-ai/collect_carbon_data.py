"""
Carbon Intensity Data Collector for Vesta Energy Orchestrator
Gathers grid carbon intensity data from Electricity Maps API (or simulated data)
"""

import os
import json
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class CarbonIntensityCollector:
    """
    Collects carbon intensity data from Electricity Maps API
    Carbon intensity indicates how "clean" the electricity grid is at any given time
    """
    
    def __init__(self):
        self.api_key = os.getenv('ELECTRICITY_MAPS_API_KEY')
        self.lat = float(os.getenv('LATITUDE', 12.9716))
        self.lon = float(os.getenv('LONGITUDE', 77.5946))
        self.zone = 'IN-KA'  # Karnataka, India - adjust based on location
        self.base_url = "https://api.electricitymap.org/v3"
        
        if not self.api_key or self.api_key == 'your_electricity_maps_api_key_here':
            print("WARNING: Electricity Maps API key not set. Using mock data.")
            self.use_mock = True
        else:
            self.use_mock = False
    
    def get_current_carbon_intensity(self) -> Dict:
        """Get current carbon intensity of the electricity grid"""
        if self.use_mock:
            return self._generate_mock_current_intensity()
        
        url = f"{self.base_url}/carbon-intensity/latest"
        headers = {'auth-token': self.api_key}
        params = {'zone': self.zone}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'zone': self.zone,
                'carbon_intensity': data.get('carbonIntensity', 500),  # gCO2eq/kWh
                'fossil_fuel_percentage': data.get('fossilFuelPercentage', 70),
                'renewable_percentage': data.get('renewablePercentage', 30)
            }
        except Exception as e:
            print(f"Error fetching carbon intensity: {e}")
            return self._generate_mock_current_intensity()
    
    def get_forecast_carbon_intensity(self, hours: int = 24) -> List[Dict]:
        """Get forecasted carbon intensity for next N hours"""
        if self.use_mock:
            return self._generate_mock_forecast_intensity(hours)
        
        url = f"{self.base_url}/carbon-intensity/forecast"
        headers = {'auth-token': self.api_key}
        params = {'zone': self.zone}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecast_data = []
            for item in data.get('forecast', [])[:hours]:
                forecast_data.append({
                    'timestamp': item['datetime'],
                    'carbon_intensity': item['carbonIntensity'],
                    'zone': self.zone
                })
            
            return forecast_data
        except Exception as e:
            print(f"Error fetching carbon forecast: {e}")
            return self._generate_mock_forecast_intensity(hours)
    
    def collect_historical_carbon_data(self, days: int = 30) -> pd.DataFrame:
        """
        Generate historical carbon intensity patterns
        Based on typical grid behavior: lower carbon at night and midday (solar), higher during peak hours
        """
        print(f"Generating synthetic carbon intensity data for {days} days...")
        
        dates = pd.date_range(
            end=datetime.now(),
            periods=days * 24,  # Hourly data
            freq='h'
        )
        
        import numpy as np
        
        hours = dates.hour.values
        day_of_week = dates.dayofweek.values
        
        # Base carbon intensity (500 gCO2eq/kWh is average for India)
        base_intensity = 500
        
        # Daily pattern: higher during peak hours (morning and evening)
        # Lower at night and midday (when solar is available)
        morning_peak = 100 * np.exp(-((hours - 8) ** 2) / 8)
        evening_peak = 120 * np.exp(-((hours - 19) ** 2) / 8)
        midday_solar = -80 * np.exp(-((hours - 13) ** 2) / 6)  # Solar reduces carbon
        
        # Weekend effect: slightly lower demand
        weekend_factor = np.where(day_of_week >= 5, -30, 0)
        
        # Combine patterns with some randomness
        carbon_intensity = (
            base_intensity + 
            morning_peak + 
            evening_peak + 
            midday_solar + 
            weekend_factor +
            np.random.normal(0, 30, len(dates))
        )
        
        # Ensure realistic bounds (200-800 gCO2eq/kWh)
        carbon_intensity = np.clip(carbon_intensity, 200, 800)
        
        # Calculate renewable percentage (inversely related to carbon intensity)
        renewable_pct = 100 * (1 - (carbon_intensity - 200) / 600)
        fossil_pct = 100 - renewable_pct
        
        # Grid pricing (typically higher during high carbon periods)
        # Base price: ₹6/kWh, varies with demand
        grid_price = 6 + 3 * (carbon_intensity - 500) / 300 + np.random.normal(0, 0.5, len(dates))
        grid_price = np.clip(grid_price, 4, 10)
        
        df = pd.DataFrame({
            'timestamp': dates,
            'carbon_intensity': carbon_intensity,
            'renewable_percentage': renewable_pct,
            'fossil_fuel_percentage': fossil_pct,
            'grid_price_per_kwh': grid_price,
            'is_peak_hour': (hours >= 6) & (hours <= 10) | (hours >= 18) & (hours <= 22),
            'is_weekend': day_of_week >= 5
        })
        
        return df
    
    def _generate_mock_current_intensity(self) -> Dict:
        """Generate mock current carbon intensity"""
        import random
        hour = datetime.now().hour
        
        # Higher carbon during peak hours
        base_intensity = 500
        if 6 <= hour <= 10 or 18 <= hour <= 22:
            base_intensity = 600
        elif 11 <= hour <= 15:  # Midday solar
            base_intensity = 400
        
        carbon = base_intensity + random.uniform(-50, 50)
        renewable = max(10, min(60, 100 - (carbon - 200) / 6))
        
        return {
            'timestamp': datetime.now().isoformat(),
            'zone': self.zone,
            'carbon_intensity': carbon,
            'fossil_fuel_percentage': 100 - renewable,
            'renewable_percentage': renewable
        }
    
    def _generate_mock_forecast_intensity(self, hours: int) -> List[Dict]:
        """Generate mock forecast carbon intensity"""
        import random
        forecast = []
        base_time = datetime.now()
        
        for i in range(hours):
            timestamp = base_time + timedelta(hours=i)
            hour = timestamp.hour
            
            base_intensity = 500
            if 6 <= hour <= 10 or 18 <= hour <= 22:
                base_intensity = 600
            elif 11 <= hour <= 15:
                base_intensity = 400
            
            carbon = base_intensity + random.uniform(-50, 50)
            
            forecast.append({
                'timestamp': timestamp.isoformat(),
                'carbon_intensity': carbon,
                'zone': self.zone
            })
        
        return forecast
    
    def save_to_csv(self, data: pd.DataFrame, filename: str):
        """Save collected data to CSV"""
        output_path = f"data/raw/{filename}"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        print(f"Carbon intensity data saved to {output_path}")
        return output_path


def main():
    """Main function to collect and save carbon intensity data"""
    collector = CarbonIntensityCollector()
    
    # Collect current carbon intensity
    print("Collecting current carbon intensity...")
    current = collector.get_current_carbon_intensity()
    print(json.dumps(current, indent=2))
    
    # Collect forecast
    print("\nCollecting 24-hour carbon intensity forecast...")
    forecast = collector.get_forecast_carbon_intensity(hours=24)
    forecast_df = pd.DataFrame(forecast)
    collector.save_to_csv(forecast_df, 'carbon_forecast.csv')
    
    # Generate historical data
    print("\nGenerating historical carbon intensity data...")
    historical = collector.collect_historical_carbon_data(days=30)
    collector.save_to_csv(historical, 'carbon_historical.csv')
    
    print("\n✓ Carbon intensity data collection complete!")
    print(f"  - Current carbon intensity: {current['carbon_intensity']:.0f} gCO2eq/kWh")
    print(f"  - Renewable percentage: {current['renewable_percentage']:.1f}%")
    print(f"  - Forecast data points: {len(forecast)}")
    print(f"  - Historical data points: {len(historical)}")


if __name__ == "__main__":
    main()
