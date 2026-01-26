"""
Sensor Data Generator for Vesta Energy Orchestrator
Simulates ESP32 sensor readings: LDR (light), current sensor, and other IoT data
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class SensorDataGenerator:
    """
    Generates synthetic sensor data that mimics ESP32 readings
    Sensors: LDR (light dependent resistor), ACS712 (current sensor), DHT22 (temp/humidity)
    """
    
    def __init__(self):
        self.sensor_id = "ESP32_NODE_001"
    
    def generate_ldr_readings(self, days: int = 30) -> pd.DataFrame:
        """
        Generate LDR (Light Dependent Resistor) sensor readings
        Values: 0-1023 (10-bit ADC on ESP32)
        Higher values = more light detected
        """
        dates = pd.date_range(
            end=datetime.now(),
            periods=days * 24 * 12,  # 5-minute intervals
            freq='5min'
        )
        
        hours = dates.hour.values
        minutes = dates.minute.values
        
        # Base light level: high during day, low at night
        # Sunrise at 6 AM, sunset at 6 PM
        hour_decimal = hours + minutes / 60
        
        # Daylight pattern (bell curve centered at noon)
        daylight_level = 1023 * np.exp(-((hour_decimal - 12) ** 2) / 24)
        
        # Room lights: on during evening/morning when dark outside
        room_lights = np.zeros_like(hour_decimal)
        room_lights[(hour_decimal >= 18) | (hour_decimal <= 7)] = 600
        
        # Combine natural and artificial light
        total_light = daylight_level + room_lights
        
        # Add realistic noise and variations
        noise = np.random.normal(0, 30, len(dates))
        total_light = total_light + noise
        
        # Random events (someone walks by, temporarily blocks light)
        blocking_events = np.random.random(len(dates)) < 0.02  # 2% chance
        total_light[blocking_events] *= 0.3
        
        # Clip to valid ADC range
        total_light = np.clip(total_light, 0, 1023)
        
        # Convert to lux (approximate)
        # LDR typically: 0-1023 maps to roughly 0-1000 lux for indoor
        lux_values = (total_light / 1023) * 1000
        
        return pd.DataFrame({
            'timestamp': dates,
            'sensor_id': self.sensor_id,
            'ldr_raw': total_light.astype(int),
            'ldr_lux': lux_values,
            'is_daylight': (hour_decimal >= 6) & (hour_decimal <= 18),
            'room_lights_on': room_lights > 0
        })
    
    def generate_current_readings(self, days: int = 30, energy_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Generate ACS712 current sensor readings
        Measures current flowing through the circuit
        """
        dates = pd.date_range(
            end=datetime.now(),
            periods=days * 24 * 12,  # 5-minute intervals
            freq='5min'
        )
        
        # If energy consumption data is provided, use it
        if energy_df is not None and 'total_energy_kwh' in energy_df.columns:
            # Resample energy data to 5-minute intervals
            energy_resampled = np.interp(
                np.arange(len(dates)),
                np.linspace(0, len(dates), len(energy_df)),
                energy_df['total_energy_kwh'].values
            )
            # Convert kWh to instantaneous power (kW)
            # Assuming voltage is 230V (India standard)
            voltage = 230
            power_w = energy_resampled * 1000  # kW to W
            current_a = power_w / voltage
        else:
            # Generate synthetic current pattern
            hours = dates.hour.values
            
            # Base current varies by time of day
            base_current = np.zeros_like(hours, dtype=float)
            base_current[(hours >= 6) & (hours <= 9)] = 3.0  # Morning
            base_current[(hours >= 10) & (hours <= 17)] = 2.0  # Day
            base_current[(hours >= 18) & (hours <= 23)] = 4.5  # Evening peak
            base_current[(hours >= 0) & (hours <= 5)] = 1.0  # Night
            
            # Add variations and noise
            current_a = base_current + np.random.normal(0, 0.3, len(dates))
            current_a = np.clip(current_a, 0, 10)
        
        # ACS712 output voltage (2.5V center, ±2.5V range for ACS712-20A)
        # Sensitivity: 100mV/A for ACS712-20A
        adc_center = 512  # 2.5V on 10-bit ADC (0-5V range)
        sensitivity = 20  # ADC units per Ampere
        adc_reading = adc_center + (current_a * sensitivity)
        adc_reading = np.clip(adc_reading, 0, 1023)
        
        # Calculate power (P = V * I)
        voltage = 230  # Volts (India standard)
        power_w = voltage * current_a
        energy_kwh = (power_w / 1000) * (5 / 60)  # 5-minute interval
        
        return pd.DataFrame({
            'timestamp': dates,
            'sensor_id': self.sensor_id,
            'current_a': current_a,
            'current_adc': adc_reading.astype(int),
            'voltage_v': voltage,
            'power_w': power_w,
            'energy_kwh': energy_kwh
        })
    
    def generate_dht22_readings(self, days: int = 30, weather_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Generate DHT22 temperature and humidity sensor readings
        Indoor readings, influenced by outdoor weather and HVAC
        """
        dates = pd.date_range(
            end=datetime.now(),
            periods=days * 24 * 12,  # 5-minute intervals
            freq='5min'
        )
        
        hours = dates.hour.values
        
        # Get outdoor temperature if available
        if weather_df is not None and 'temperature' in weather_df.columns:
            outdoor_temp = np.interp(
                np.arange(len(dates)),
                np.linspace(0, len(dates), len(weather_df)),
                weather_df['temperature'].values
            )
        else:
            # Generate outdoor temperature pattern
            day_of_year = dates.dayofyear.values
            temp_base = 25 + 5 * np.sin(2 * np.pi * day_of_year / 365)
            temp_daily = 8 * np.sin(2 * np.pi * hours / 24 - np.pi/2)
            outdoor_temp = temp_base + temp_daily + np.random.normal(0, 2, len(dates))
        
        # Indoor temperature: more stable than outdoor, influenced by HVAC
        # Indoor target: 22-26°C
        target_temp = 24
        
        # Indoor temp follows outdoor with dampening and HVAC control
        indoor_temp = target_temp + (outdoor_temp - target_temp) * 0.3
        indoor_temp += np.random.normal(0, 0.5, len(dates))
        
        # DHT22 accuracy: ±0.5°C
        indoor_temp = np.round(indoor_temp, 1)
        
        # Humidity: inversely related to temperature, higher at night
        base_humidity = 65
        temp_effect = -(indoor_temp - 24) * 2
        time_effect = 10 * np.sin(2 * np.pi * hours / 24)
        
        humidity = base_humidity + temp_effect + time_effect + np.random.normal(0, 3, len(dates))
        humidity = np.clip(humidity, 30, 90)
        
        # DHT22 accuracy: ±2% RH
        humidity = np.round(humidity, 1)
        
        return pd.DataFrame({
            'timestamp': dates,
            'sensor_id': self.sensor_id,
            'indoor_temperature_c': indoor_temp,
            'indoor_humidity_pct': humidity,
            'outdoor_temperature_c': outdoor_temp
        })
    
    def generate_complete_sensor_dataset(self, days: int = 30) -> pd.DataFrame:
        """
        Generate complete sensor dataset with all sensors
        Uses shared timestamps to ensure all sensor data is properly aligned
        """
        print(f"Generating synthetic sensor data for {days} days...")
        
        # Generate timestamps once for all sensors (5-minute intervals)
        dates = pd.date_range(
            end=datetime.now(),
            periods=days * 24 * 12,  # 5-minute intervals
            freq='5min'
        )
        
        # Generate individual sensor readings
        ldr_df = self.generate_ldr_readings(days)
        current_df = self.generate_current_readings(days)
        dht22_df = self.generate_dht22_readings(days)
        
        # Combine all sensor data with shared timestamps
        df = pd.DataFrame({
            'timestamp': dates,
            'sensor_id': self.sensor_id,
            'ldr_raw': ldr_df['ldr_raw'].values,
            'ldr_lux': ldr_df['ldr_lux'].values,
            'is_daylight': ldr_df['is_daylight'].values,
            'room_lights_on': ldr_df['room_lights_on'].values,
            'current_a': current_df['current_a'].values,
            'current_adc': current_df['current_adc'].values,
            'voltage_v': current_df['voltage_v'].values,
            'power_w': current_df['power_w'].values,
            'energy_kwh': current_df['energy_kwh'].values,
            'indoor_temperature_c': dht22_df['indoor_temperature_c'].values,
            'indoor_humidity_pct': dht22_df['indoor_humidity_pct'].values,
            'outdoor_temperature_c': dht22_df['outdoor_temperature_c'].values
        })
        
        # Add metadata
        df['data_quality'] = np.random.choice(
            ['good', 'good', 'good', 'fair', 'poor'],
            size=len(df),
            p=[0.85, 0.10, 0.03, 0.015, 0.005]
        )
        
        # Simulate occasional sensor disconnections (mark as null)
        disconnect_mask = np.random.random(len(df)) < 0.001  # 0.1% failure rate
        if disconnect_mask.any():
            df.loc[disconnect_mask, ['ldr_raw', 'current_a', 'indoor_temperature_c']] = np.nan
            df.loc[disconnect_mask, 'data_quality'] = 'sensor_offline'
        
        return df
    
    def save_to_csv(self, data: pd.DataFrame, filename: str):
        """Save generated data to CSV"""
        output_path = f"data/raw/{filename}"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        data.to_csv(output_path, index=False)
        print(f"Sensor data saved to {output_path}")
        return output_path


def main():
    """Main function to generate and save sensor data"""
    generator = SensorDataGenerator()
    
    # Generate complete sensor dataset
    print("Generating sensor readings...")
    sensor_data = generator.generate_complete_sensor_dataset(days=30)
    
    # Save to CSV
    output_path = generator.save_to_csv(sensor_data, 'sensor_readings.csv')
    
    # Print statistics
    print("\n✓ Sensor data generation complete!")
    print(f"  - Total data points: {len(sensor_data)}")
    print(f"  - Average LDR reading: {sensor_data['ldr_raw'].mean():.0f} (0-1023)")
    print(f"  - Average current: {sensor_data['current_a'].mean():.2f} A")
    print(f"  - Average power: {sensor_data['power_w'].mean():.0f} W")
    print(f"  - Average indoor temp: {sensor_data['indoor_temperature_c'].mean():.1f}°C")
    print(f"  - Average humidity: {sensor_data['indoor_humidity_pct'].mean():.1f}%")
    print(f"  - Data quality 'good': {(sensor_data['data_quality'] == 'good').sum() / len(sensor_data) * 100:.1f}%")


if __name__ == "__main__":
    main()
