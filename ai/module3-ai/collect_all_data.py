"""
Master Data Collection Script for Vesta Energy Orchestrator
Runs all data collection scripts and generates a comprehensive dataset for Module 3
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add module3-ai to path
sys.path.append(os.path.dirname(__file__))

from collect_weather_data import WeatherDataCollector
from collect_carbon_data import CarbonIntensityCollector
from generate_energy_data import EnergyConsumptionGenerator
from generate_sensor_data import SensorDataGenerator


class MasterDataCollector:
    """
    Orchestrates all data collection and generation for the ai model
    """
    
    def __init__(self, days: int = 30):
        self.days = days
        self.data_dir = "data/raw"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def collect_all_datasets(self):
        """
        Collect all required datasets for training the ai model
        """
        print("=" * 70)
        print("VESTA ENERGY ORCHESTRATOR - DATA COLLECTION")
        print("=" * 70)
        print(f"Collecting {self.days} days of data for ai training...\n")
        
        datasets = {}
        
        # Generate common timestamps for all hourly data (for alignment)
        common_timestamps = pd.date_range(
            end=datetime.now().replace(minute=0, second=0, microsecond=0),
            periods=self.days * 24,
            freq='h'
        )
        
        # 1. Weather Data
        print("\n[1/4] Collecting Weather Data...")
        print("-" * 70)
        weather_collector = WeatherDataCollector()
        weather_historical = weather_collector.collect_historical_data(days=self.days)
        # Align timestamps
        weather_historical['timestamp'] = common_timestamps
        weather_collector.save_to_csv(weather_historical, 'weather_historical.csv')
        datasets['weather'] = weather_historical
        print(f"✓ Weather data collected: {len(weather_historical)} records")
        
        # Also get current weather and forecast
        current_weather = weather_collector.get_current_weather()
        forecast_weather = weather_collector.get_forecast(days=5)
        forecast_df = pd.DataFrame(forecast_weather)
        weather_collector.save_to_csv(forecast_df, 'weather_forecast.csv')
        print(f"✓ Weather forecast collected: {len(forecast_df)} records")
        
        # 2. Carbon Intensity Data
        print("\n[2/4] Collecting Carbon Intensity Data...")
        print("-" * 70)
        carbon_collector = CarbonIntensityCollector()
        carbon_historical = carbon_collector.collect_historical_carbon_data(days=self.days)
        # Align timestamps
        carbon_historical['timestamp'] = common_timestamps
        carbon_collector.save_to_csv(carbon_historical, 'carbon_historical.csv')
        datasets['carbon'] = carbon_historical
        print(f"✓ Carbon intensity data collected: {len(carbon_historical)} records")
        
        # Also get current and forecast
        current_carbon = carbon_collector.get_current_carbon_intensity()
        forecast_carbon = carbon_collector.get_forecast_carbon_intensity(hours=24)
        forecast_carbon_df = pd.DataFrame(forecast_carbon)
        carbon_collector.save_to_csv(forecast_carbon_df, 'carbon_forecast.csv')
        print(f"✓ Carbon forecast collected: {len(forecast_carbon_df)} records")
        
        # 3. Energy Consumption Data
        print("\n[3/4] Generating Energy Consumption Patterns...")
        print("-" * 70)
        energy_generator = EnergyConsumptionGenerator()
        energy_data = energy_generator.generate_complete_dataset(days=self.days)
        # Align timestamps
        energy_data['timestamp'] = common_timestamps
        energy_generator.save_to_csv(energy_data, 'energy_consumption.csv')
        datasets['energy'] = energy_data
        print(f"✓ Energy consumption data generated: {len(energy_data)} records")
        
        # 4. Sensor Data
        print("\n[4/4] Generating Sensor Readings...")
        print("-" * 70)
        sensor_generator = SensorDataGenerator()
        sensor_data = sensor_generator.generate_complete_sensor_dataset(days=self.days)
        sensor_generator.save_to_csv(sensor_data, 'sensor_readings.csv')
        datasets['sensor'] = sensor_data
        print(f"✓ Sensor data generated: {len(sensor_data)} records")
        
        # 5. Create Integrated Dataset
        print("\n[5/5] Creating Integrated Dataset...")
        print("-" * 70)
        integrated_df = self.create_integrated_dataset(datasets)
        output_path = f"{self.data_dir}/integrated_dataset.csv"
        integrated_df.to_csv(output_path, index=False)
        print(f"✓ Integrated dataset created: {len(integrated_df)} records")
        print(f"✓ Saved to: {output_path}")
        
        # Print summary
        self.print_summary(datasets, integrated_df)
        
        return datasets, integrated_df
    
    def create_integrated_dataset(self, datasets: dict) -> pd.DataFrame:
        """
        Combine all datasets into a single integrated dataset
        This is the main dataset for training the ai model
        """
        # Start with energy data (hourly)
        df = datasets['energy'].copy()
        
        # Merge with weather data (hourly)
        weather_df = datasets['weather'].copy()
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        df = pd.merge(
            df, 
            weather_df[['timestamp', 'temperature', 'humidity', 'cloud_cover', 'wind_speed', 'solar_radiation_proxy']],
            on='timestamp',
            how='left',
            suffixes=('', '_weather')
        )
        
        # Merge with carbon intensity data (hourly)
        carbon_df = datasets['carbon'].copy()
        carbon_df['timestamp'] = pd.to_datetime(carbon_df['timestamp'])
        
        df = pd.merge(
            df,
            carbon_df[['timestamp', 'carbon_intensity', 'renewable_percentage', 'grid_price_per_kwh']],
            on='timestamp',
            how='left'
        )
        
        # Aggregate sensor data to hourly (from 5-min intervals)
        sensor_df = datasets['sensor'].copy()
        sensor_df['timestamp'] = pd.to_datetime(sensor_df['timestamp'])
        sensor_df['timestamp_hour'] = sensor_df['timestamp'].dt.floor('h')
        
        sensor_hourly = sensor_df.groupby('timestamp_hour').agg({
            'ldr_lux': 'mean',
            'current_a': 'mean',
            'power_w': 'mean',
            'indoor_temperature_c': 'mean',
            'indoor_humidity_pct': 'mean'
        }).reset_index()
        sensor_hourly.rename(columns={'timestamp_hour': 'timestamp'}, inplace=True)
        
        df = pd.merge(
            df,
            sensor_hourly,
            on='timestamp',
            how='left'
        )
        
        # Add calculated features
        df['energy_cost'] = df['total_energy_kwh'] * df['grid_price_per_kwh']
        df['carbon_footprint'] = df['total_energy_kwh'] * df['carbon_intensity'] / 1000  # kg CO2
        
        # Fill any missing values
        df = df.ffill().bfill()
        
        return df
    
    def print_summary(self, datasets: dict, integrated_df: pd.DataFrame):
        """
        Print a summary of collected data
        """
        print("\n" + "=" * 70)
        print("DATA COLLECTION SUMMARY")
        print("=" * 70)
        
        print("\n📊 Individual Datasets:")
        print(f"  Weather Data:          {len(datasets['weather']):,} records")
        print(f"  Carbon Intensity:      {len(datasets['carbon']):,} records")
        print(f"  Energy Consumption:    {len(datasets['energy']):,} records")
        print(f"  Sensor Readings:       {len(datasets['sensor']):,} records")
        
        print(f"\n📈 Integrated Dataset:   {len(integrated_df):,} records")
        print(f"  Features:              {len(integrated_df.columns)} columns")
        print(f"  Time span:             {self.days} days")
        print(f"  Frequency:             Hourly")
        
        print("\n💡 Key Statistics:")
        print(f"  Avg Energy Usage:      {integrated_df['total_energy_kwh'].mean():.3f} kWh/hour")
        print(f"  Total Energy (30d):    {integrated_df['total_energy_kwh'].sum():.1f} kWh")
        print(f"  Avg Carbon Intensity:  {integrated_df['carbon_intensity'].mean():.0f} gCO2eq/kWh")
        print(f"  Total Carbon (30d):    {integrated_df['carbon_footprint'].sum():.1f} kg CO2")
        print(f"  Avg Grid Price:        ₹{integrated_df['grid_price_per_kwh'].mean():.2f}/kWh")
        print(f"  Total Energy Cost:     ₹{integrated_df['energy_cost'].sum():.2f}")
        
        print("\n🌡️  Environmental Stats:")
        print(f"  Avg Temperature:       {integrated_df['temperature'].mean():.1f}°C")
        print(f"  Avg Humidity:          {integrated_df['humidity'].mean():.1f}%")
        print(f"  Avg Solar Radiation:   {integrated_df['solar_radiation_proxy'].mean():.2f}")
        print(f"  Avg Renewable %:       {integrated_df['renewable_percentage'].mean():.1f}%")
        
        print("\n" + "=" * 70)
        print("✓ ALL DATASETS READY FOR MODULE 3 (ai Training)")
        print("=" * 70)
        print("\nNext Steps:")
        print("  1. Review datasets in 'data/raw/' directory")
        print("  2. Run data preprocessing (optional)")
        print("  3. Start training ai models (Module 3)")
        print("  4. Use 'integrated_dataset.csv' for ML model training")
        print("\n")


def main():
    """
    Main execution function
    """
    # Collect 30 days of data by default
    collector = MasterDataCollector(days=30)
    datasets, integrated_df = collector.collect_all_datasets()
    
    print("Data collection completed successfully!")
    print(f"All datasets saved in: {os.path.abspath('data/raw')}")


if __name__ == "__main__":
    main()
