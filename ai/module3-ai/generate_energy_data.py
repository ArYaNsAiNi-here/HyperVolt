"""
Energy Consumption Pattern Generator for Vesta Energy Orchestrator
Generates realistic energy consumption patterns for training the ai model
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class EnergyConsumptionGenerator:
    """
    Generates synthetic energy consumption data based on realistic patterns
    Includes patterns for: lighting, appliances, HVAC, and total consumption
    """
    
    def __init__(self):
        self.location = os.getenv('LOCATION_NAME', 'Bangalore')
    
    def generate_lighting_consumption(self, days: int = 30) -> pd.DataFrame:
        """
        Generate lighting consumption patterns
        Depends on: time of day, daylight availability, occupancy
        """
        dates = pd.date_range(
            end=datetime.now(),
            periods=days * 24,  # Hourly data
            freq='h'
        )
        
        hours = dates.hour.values
        day_of_week = dates.dayofweek.values
        
        # Base lighting power (watts)
        max_lighting_power = 200  # Total lighting capacity
        
        # Occupancy pattern (higher on weekdays during day, evenings)
        occupancy_weekday = np.zeros_like(hours, dtype=float)
        occupancy_weekday[(hours >= 6) & (hours <= 8)] = 0.8  # Morning
        occupancy_weekday[(hours >= 9) & (hours <= 17)] = 0.3  # Away at work
        occupancy_weekday[(hours >= 18) & (hours <= 23)] = 0.9  # Evening
        
        occupancy_weekend = np.zeros_like(hours, dtype=float)
        occupancy_weekend[(hours >= 7) & (hours <= 23)] = 0.7  # Home most of day
        
        is_weekend = day_of_week >= 5
        occupancy = np.where(is_weekend, occupancy_weekend, occupancy_weekday)
        
        # Daylight factor (less light needed during day)
        is_daylight = (hours >= 6) & (hours <= 18)
        daylight_factor = np.where(is_daylight, 0.3, 1.0)
        
        # Calculate lighting consumption with randomness
        lighting_power = (
            max_lighting_power * 
            occupancy * 
            daylight_factor *
            (1 + np.random.normal(0, 0.1, len(dates)))
        )
        lighting_power = np.clip(lighting_power, 0, max_lighting_power)
        
        # Energy consumed (kWh)
        lighting_energy = lighting_power / 1000  # Convert to kW
        
        return pd.DataFrame({
            'timestamp': dates,
            'lighting_power_w': lighting_power,
            'lighting_energy_kwh': lighting_energy,
            'occupancy_factor': occupancy,
            'daylight_factor': daylight_factor
        })
    
    def generate_appliance_consumption(self, days: int = 30) -> pd.DataFrame:
        """
        Generate appliance consumption patterns
        Includes: refrigerator (constant), washing machine, TV, computer, etc.
        """
        dates = pd.date_range(
            end=datetime.now(),
            periods=days * 24,
            freq='h'
        )
        
        hours = dates.hour.values
        day_of_week = dates.dayofweek.values
        
        # Refrigerator: constant ~150W with compressor cycles
        fridge_base = 150
        fridge_cycle = 50 * np.sin(2 * np.pi * hours / 4)  # 4-hour cycle
        refrigerator_power = fridge_base + fridge_cycle + np.random.normal(0, 10, len(dates))
        
        # TV: higher in evening
        tv_power = np.zeros_like(hours, dtype=float)
        tv_power[(hours >= 18) & (hours <= 23)] = 100 + np.random.normal(0, 20, len(dates[(hours >= 18) & (hours <= 23)]))
        
        # Computer/Work: weekdays 9-17, evenings
        computer_power = np.zeros_like(hours, dtype=float)
        is_weekday = day_of_week < 5
        computer_power[(hours >= 9) & (hours <= 17) & is_weekday] = 80
        computer_power[(hours >= 19) & (hours <= 22)] = 60
        computer_power += np.random.normal(0, 10, len(dates))
        computer_power = np.clip(computer_power, 0, 100)
        
        # Washing machine: random usage, more on weekends
        washing_power = np.zeros_like(hours, dtype=float)
        # 1-2 times per week, 1 hour runtime, 1500W
        washing_events = np.random.random(len(dates)) < (0.1 if day_of_week.any() >= 5 else 0.05)
        washing_power[washing_events] = 1500
        
        # Kitchen appliances: meal times
        kitchen_power = np.zeros_like(hours, dtype=float)
        kitchen_power[(hours >= 7) & (hours <= 9)] = 800  # Breakfast
        kitchen_power[(hours >= 12) & (hours <= 14)] = 600  # Lunch
        kitchen_power[(hours >= 18) & (hours <= 20)] = 1000  # Dinner
        kitchen_power += np.random.normal(0, 100, len(dates))
        kitchen_power = np.clip(kitchen_power, 0, 1500)
        
        # Total appliance power
        total_appliance_power = (
            refrigerator_power + 
            tv_power + 
            computer_power + 
            washing_power + 
            kitchen_power
        )
        
        # Energy consumed (kWh)
        total_appliance_energy = total_appliance_power / 1000
        
        return pd.DataFrame({
            'timestamp': dates,
            'refrigerator_power_w': refrigerator_power,
            'tv_power_w': tv_power,
            'computer_power_w': computer_power,
            'washing_power_w': washing_power,
            'kitchen_power_w': kitchen_power,
            'total_appliance_power_w': total_appliance_power,
            'total_appliance_energy_kwh': total_appliance_energy
        })
    
    def generate_hvac_consumption(self, days: int = 30, weather_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Generate HVAC (Heating, Ventilation, Air Conditioning) consumption
        Highly dependent on outdoor temperature
        """
        dates = pd.date_range(
            end=datetime.now(),
            periods=days * 24,
            freq='h'
        )
        
        hours = dates.hour.values
        
        # Get temperature data if available
        if weather_df is not None and 'temperature' in weather_df.columns:
            temperatures = weather_df['temperature'].values[:len(dates)]
        else:
            # Generate temperature pattern
            day_of_year = dates.dayofyear.values
            temp_base = 25 + 5 * np.sin(2 * np.pi * day_of_year / 365)
            temp_daily = 8 * np.sin(2 * np.pi * hours / 24 - np.pi/2)
            temperatures = temp_base + temp_daily + np.random.normal(0, 2, len(dates))
        
        # HVAC usage based on temperature deviation from comfort (22-26°C)
        comfort_temp = 24
        temp_deviation = np.abs(temperatures - comfort_temp)
        
        # HVAC power (0-1500W based on temperature)
        # Only runs when temperature is significantly outside comfort zone
        hvac_threshold = 2  # degrees
        hvac_active = temp_deviation > hvac_threshold
        
        # More power needed for larger deviations
        hvac_power = np.zeros_like(hours, dtype=float)
        hvac_power[hvac_active] = (
            300 + 
            (temp_deviation[hvac_active] - hvac_threshold) * 150 +
            np.random.normal(0, 50, np.sum(hvac_active))
        )
        hvac_power = np.clip(hvac_power, 0, 1500)
        
        # Reduce usage at night and when unoccupied
        is_night = (hours >= 23) | (hours <= 6)
        hvac_power[is_night] *= 0.3
        
        hvac_energy = hvac_power / 1000
        
        return pd.DataFrame({
            'timestamp': dates,
            'hvac_power_w': hvac_power,
            'hvac_energy_kwh': hvac_energy,
            'outdoor_temperature': temperatures,
            'hvac_active': hvac_active
        })
    
    def generate_complete_dataset(self, days: int = 30) -> pd.DataFrame:
        """
        Generate complete energy consumption dataset
        Combines lighting, appliances, and HVAC
        """
        print(f"Generating comprehensive energy consumption data for {days} days...")
        
        # Generate individual components
        lighting_df = self.generate_lighting_consumption(days)
        appliance_df = self.generate_appliance_consumption(days)
        hvac_df = self.generate_hvac_consumption(days)
        
        # Combine into single dataframe
        df = pd.DataFrame({
            'timestamp': lighting_df['timestamp'],
            'lighting_energy_kwh': lighting_df['lighting_energy_kwh'],
            'appliance_energy_kwh': appliance_df['total_appliance_energy_kwh'],
            'hvac_energy_kwh': hvac_df['hvac_energy_kwh'],
            'occupancy_factor': lighting_df['occupancy_factor'],
            'outdoor_temperature': hvac_df['outdoor_temperature']
        })
        
        # Calculate total energy consumption
        df['total_energy_kwh'] = (
            df['lighting_energy_kwh'] + 
            df['appliance_energy_kwh'] + 
            df['hvac_energy_kwh']
        )
        
        # Calculate cumulative energy
        df['cumulative_energy_kwh'] = df['total_energy_kwh'].cumsum()
        
        # Add time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'] >= 5
        df['is_peak_hour'] = ((df['hour'] >= 6) & (df['hour'] <= 10)) | ((df['hour'] >= 18) & (df['hour'] <= 22))
        
        return df
    
    def save_to_csv(self, data: pd.DataFrame, filename: str):
        """Save generated data to CSV"""
        output_path = f"data/raw/{filename}"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        print(f"Energy consumption data saved to {output_path}")
        return output_path


def main():
    """Main function to generate and save energy consumption data"""
    generator = EnergyConsumptionGenerator()
    
    # Generate complete dataset
    print("Generating energy consumption patterns...")
    energy_data = generator.generate_complete_dataset(days=30)
    
    # Save to CSV
    output_path = generator.save_to_csv(energy_data, 'energy_consumption.csv')
    
    # Print statistics
    print("\n✓ Energy consumption data generation complete!")
    print(f"  - Total data points: {len(energy_data)}")
    print(f"  - Average hourly consumption: {energy_data['total_energy_kwh'].mean():.3f} kWh")
    print(f"  - Peak consumption: {energy_data['total_energy_kwh'].max():.3f} kWh")
    print(f"  - Total consumption (30 days): {energy_data['total_energy_kwh'].sum():.1f} kWh")
    print(f"  - Average daily consumption: {energy_data['total_energy_kwh'].sum() / 30:.1f} kWh")


if __name__ == "__main__":
    main()
