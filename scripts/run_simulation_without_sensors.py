#!/usr/bin/env python3
"""
HyperVolt Simulation Script - WITHOUT Hardware Sensors
=========================================================

This script runs a complete simulation of the HyperVolt energy management system
by interconnecting Modules 2 (Backend), 3 (AI), and 4 (Frontend) without requiring
physical sensors (Module 1).

The simulation generates synthetic sensor data and streams it through the system
to demonstrate the AI-driven energy optimization in real-time on the website.

Usage:
    python scripts/run_simulation_without_sensors.py

Requirements:
    - Redis server running (redis-server)
    - Django backend running (python manage.py runserver or daphne)
    - Optional: Frontend running (npm run dev in website/)

Author: HyperVolt Team
Date: 2026
"""

import os
import sys
import json
import time
import random
import signal
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import math

# Add project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_PATH = os.path.join(PROJECT_ROOT, 'api')
AI_PATH = os.path.join(PROJECT_ROOT, 'ai', 'module3-ai')

sys.path.insert(0, API_PATH)
sys.path.insert(0, AI_PATH)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hypervolt_backend.settings')

try:
    import django
    django.setup()
    DJANGO_AVAILABLE = True
except Exception as e:
    print(f"Warning: Django not available: {e}")
    DJANGO_AVAILABLE = False

import requests

# Configuration
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')
SIMULATION_DURATION_MINUTES = int(os.environ.get('SIMULATION_DURATION', 60))  # Default 60 minutes
UPDATE_INTERVAL_SECONDS = int(os.environ.get('UPDATE_INTERVAL', 5))  # Default 5 seconds
ENABLE_AI_DECISIONS = os.environ.get('ENABLE_AI_DECISIONS', 'true').lower() == 'true'

# Global flag for graceful shutdown
shutdown_flag = threading.Event()


class SyntheticDataGenerator:
    """
    Generates realistic synthetic sensor data for simulation.
    Simulates a day's worth of conditions including:
    - Light levels (LDR)
    - Temperature and humidity
    - Current consumption
    - Solar radiation patterns
    - Grid carbon intensity patterns
    """
    
    def __init__(self, start_hour: int = None):
        """
        Initialize the data generator.
        
        Args:
            start_hour: Starting hour of simulation (0-23). If None, uses current hour.
        """
        self.current_hour = start_hour if start_hour is not None else datetime.now().hour
        self.current_minute = datetime.now().minute
        self.iteration = 0
        
        # Base values with realistic ranges
        self.base_temperature = 25.0  # °C
        self.base_humidity = 55.0  # %
        self.base_current = 1.5  # Amps
        
    def _get_solar_factor(self, hour: int) -> float:
        """Calculate solar availability factor based on time of day."""
        if hour < 6 or hour >= 19:
            return 0.0  # No sun
        elif hour < 8:
            return (hour - 6) / 2 * 0.5  # Morning ramp up
        elif hour < 16:
            return 0.6 + 0.4 * math.sin((hour - 8) * math.pi / 8)  # Peak midday
        else:
            return (19 - hour) / 3 * 0.6  # Evening ramp down
    
    def _get_occupancy_factor(self, hour: int) -> float:
        """Calculate occupancy factor affecting energy consumption."""
        if 0 <= hour < 6:
            return 0.2  # Night - minimal
        elif 6 <= hour < 9:
            return 0.8  # Morning rush
        elif 9 <= hour < 17:
            return 0.4  # Work hours
        elif 17 <= hour < 22:
            return 1.0  # Evening peak
        else:
            return 0.3  # Late night
    
    def _get_carbon_intensity(self, hour: int) -> float:
        """Calculate grid carbon intensity (gCO2eq/kWh) based on time."""
        # Higher during evening peak, lower during solar hours
        base = 450
        if 10 <= hour <= 14:
            return base - 100 + random.uniform(-20, 20)  # Low during solar peak
        elif 18 <= hour <= 21:
            return base + 150 + random.uniform(-20, 20)  # High during evening peak
        else:
            return base + random.uniform(-30, 30)
    
    def _get_grid_price(self, hour: int) -> float:
        """Calculate grid electricity price (₹/kWh) based on time."""
        if 22 <= hour or hour < 6:
            return 4.0 + random.uniform(-0.5, 0.5)  # Off-peak
        elif 9 <= hour <= 11 or 18 <= hour <= 21:
            return 8.0 + random.uniform(-0.5, 0.5)  # Peak
        else:
            return 6.0 + random.uniform(-0.5, 0.5)  # Normal
    
    def generate_sensor_readings(self) -> Dict:
        """Generate a complete set of synthetic sensor readings."""
        hour = self.current_hour
        minute = self.current_minute
        
        # Calculate factors
        solar_factor = self._get_solar_factor(hour)
        occupancy_factor = self._get_occupancy_factor(hour)
        
        # LDR (Light Dependent Resistor) - 0 to 4095 (12-bit ADC)
        # Higher values mean more light
        if solar_factor > 0:
            base_ldr = 2000 + solar_factor * 2000
            # Add some cloud variation
            ldr_value = base_ldr + random.uniform(-300, 300)
        else:
            # Indoor lighting at night
            ldr_value = 500 + occupancy_factor * 800 + random.uniform(-100, 100)
        ldr_value = max(0, min(4095, ldr_value))
        
        # Temperature - varies with time of day and solar heating
        temp_variation = solar_factor * 5 + random.uniform(-1, 1)
        temperature = self.base_temperature + temp_variation
        
        # Humidity - inversely related to temperature
        humidity = self.base_humidity - temp_variation * 2 + random.uniform(-3, 3)
        humidity = max(30, min(90, humidity))
        
        # Current consumption - based on occupancy and time
        current = self.base_current * occupancy_factor + random.uniform(-0.2, 0.5)
        current = max(0.3, min(10, current))
        
        # Voltage - relatively stable with small fluctuations
        voltage = 230 + random.uniform(-3, 3)
        
        readings = {
            'timestamp': datetime.now().isoformat(),
            'hour': hour,
            'minute': minute,
            'sensors': {
                'ldr': round(ldr_value, 0),
                'temperature': round(temperature, 1),
                'humidity': round(humidity, 1),
                'current': round(current, 2),
                'voltage': round(voltage, 1),
            },
            'environment': {
                'solar_factor': round(solar_factor, 2),
                'occupancy_factor': round(occupancy_factor, 2),
                'carbon_intensity': round(self._get_carbon_intensity(hour), 0),
                'grid_price': round(self._get_grid_price(hour), 2),
            }
        }
        
        return readings
    
    def advance_time(self, minutes: int = 1):
        """Advance simulation time by given minutes."""
        self.current_minute += minutes
        while self.current_minute >= 60:
            self.current_minute -= 60
            self.current_hour = (self.current_hour + 1) % 24
        self.iteration += 1


class SimulationRunner:
    """
    Main simulation runner that coordinates data generation,
    API calls, and AI decision making.
    """
    
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.data_generator = SyntheticDataGenerator()
        self.decision_history = []
        self.stats = {
            'total_iterations': 0,
            'successful_api_calls': 0,
            'ai_decisions_made': 0,
            'total_cost': 0.0,
            'total_carbon': 0.0,
        }
        
    def check_api_health(self) -> bool:
        """Check if the API is available."""
        try:
            response = requests.get(f"{self.api_url}/api/ai/status/", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def update_simulation_file(self, readings: Dict):
        """Update the simulation sensor file for AI inference."""
        csv_path = os.path.join(API_PATH, 'data', 'simulation_sensors.csv')
        
        csv_content = "timestamp,sensor_type,value\n"
        timestamp = readings['timestamp']
        
        for sensor_type, value in readings['sensors'].items():
            csv_content += f"{timestamp},{sensor_type},{value}\n"
        
        # Also add environment data
        for env_type, value in readings['environment'].items():
            csv_content += f"{timestamp},{env_type},{value}\n"
        
        try:
            with open(csv_path, 'w') as f:
                f.write(csv_content)
            return True
        except Exception as e:
            print(f"  ⚠ Failed to update simulation file: {e}")
            return False
    
    def post_sensor_reading(self, sensor_type: str, value: float, unit: str, location: str = 'living_room'):
        """Post a sensor reading to the API."""
        try:
            data = {
                'sensor_type': sensor_type,
                'sensor_id': f'{sensor_type}_sim_1',
                'value': value,
                'unit': unit,
                'location': location,
            }
            response = requests.post(
                f"{self.api_url}/api/sensor-readings/",
                json=data,
                timeout=5
            )
            return response.status_code in [200, 201]
        except requests.exceptions.RequestException:
            return False
    
    def trigger_ai_decision(self) -> Dict:
        """Trigger the AI to make an energy management decision."""
        try:
            response = requests.post(
                f"{self.api_url}/api/ai/decide/",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def get_ai_forecast(self, hours: int = 6) -> Dict:
        """Get AI energy demand forecast."""
        try:
            response = requests.get(
                f"{self.api_url}/api/ai/forecast/?hours={hours}",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def run_iteration(self) -> Dict:
        """Run a single simulation iteration."""
        # Generate synthetic data
        readings = self.data_generator.generate_sensor_readings()
        
        # Update simulation file for AI
        self.update_simulation_file(readings)
        
        # Post sensor readings to API
        sensor_units = {
            'ldr': 'raw',
            'temperature': 'celsius',
            'humidity': 'percent',
            'current': 'amperes',
            'voltage': 'volts',
        }
        
        api_success = True
        for sensor_type, value in readings['sensors'].items():
            success = self.post_sensor_reading(
                sensor_type, value, sensor_units.get(sensor_type, 'unit')
            )
            api_success = api_success and success
        
        if api_success:
            self.stats['successful_api_calls'] += 1
        
        # Trigger AI decision if enabled
        decision = None
        if ENABLE_AI_DECISIONS and self.stats['total_iterations'] % 6 == 0:  # Every 30 seconds
            decision = self.trigger_ai_decision()
            if decision and decision.get('available'):
                self.stats['ai_decisions_made'] += 1
                self.decision_history.append(decision)
                
                # Update stats
                current_decision = decision.get('current_decision', {})
                self.stats['total_cost'] += current_decision.get('cost', 0)
                self.stats['total_carbon'] += current_decision.get('carbon', 0)
        
        self.stats['total_iterations'] += 1
        
        return {
            'readings': readings,
            'api_success': api_success,
            'decision': decision,
        }
    
    def print_status(self, result: Dict):
        """Print the current simulation status."""
        readings = result['readings']
        decision = result.get('decision')
        
        hour = readings['hour']
        minute = readings['minute']
        sensors = readings['sensors']
        env = readings['environment']
        
        print(f"\n{'='*60}")
        print(f"  Simulation Time: {hour:02d}:{minute:02d}")
        print(f"  Real Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"  Iteration: {self.stats['total_iterations']}")
        print(f"{'='*60}")
        
        print(f"\n  📊 Sensor Readings:")
        print(f"     LDR:         {sensors['ldr']:.0f} (raw)")
        print(f"     Temperature: {sensors['temperature']:.1f}°C")
        print(f"     Humidity:    {sensors['humidity']:.1f}%")
        print(f"     Current:     {sensors['current']:.2f} A")
        print(f"     Voltage:     {sensors['voltage']:.1f} V")
        print(f"     Power:       {sensors['current'] * sensors['voltage']:.1f} W")
        
        print(f"\n  🌍 Environment:")
        print(f"     Solar Factor:     {env['solar_factor']:.0%}")
        print(f"     Occupancy:        {env['occupancy_factor']:.0%}")
        print(f"     Carbon Intensity: {env['carbon_intensity']:.0f} gCO2eq/kWh")
        print(f"     Grid Price:       ₹{env['grid_price']:.2f}/kWh")
        
        if decision and decision.get('available'):
            current = decision.get('current_decision', {})
            allocation = current.get('source_allocation', [])
            
            print(f"\n  🤖 AI Decision:")
            print(f"     Predicted Demand: {current.get('predicted_demand_kwh', 0):.3f} kWh")
            print(f"     Source Allocation:")
            for source, power in allocation:
                print(f"       - {source}: {power:.3f} kW")
            print(f"     Cost: ₹{current.get('cost', 0):.2f}")
            print(f"     Carbon: {current.get('carbon', 0):.0f} gCO2eq")
            print(f"     Recommendation: {decision.get('recommendation', 'N/A')[:60]}...")
        
        print(f"\n  📈 Cumulative Stats:")
        print(f"     API Success Rate: {self.stats['successful_api_calls']}/{self.stats['total_iterations']}")
        print(f"     AI Decisions: {self.stats['ai_decisions_made']}")
        print(f"     Total Cost: ₹{self.stats['total_cost']:.2f}")
        print(f"     Total Carbon: {self.stats['total_carbon']/1000:.2f} kg CO2")
    
    def run(self, duration_minutes: int = SIMULATION_DURATION_MINUTES, 
            interval_seconds: int = UPDATE_INTERVAL_SECONDS,
            accelerated: bool = False):
        """
        Run the simulation.
        
        Args:
            duration_minutes: How long to run the simulation
            interval_seconds: Time between updates
            accelerated: If True, simulate time faster (1 real second = 1 sim minute)
        """
        print("\n" + "="*60)
        print("  HYPERVOLT SIMULATION - WITHOUT SENSORS")
        print("  Interconnecting Modules 2 (Backend), 3 (AI), 4 (Frontend)")
        print("="*60)
        
        # Check API health
        print("\n  Checking API health...")
        if not self.check_api_health():
            print("  ❌ API is not available! Please start the Django backend:")
            print("     cd api && python manage.py runserver")
            print("  Or with WebSockets:")
            print("     cd api && daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application")
            return
        print("  ✅ API is available!")
        
        # Get initial AI status
        print("\n  Checking AI models...")
        try:
            response = requests.get(f"{self.api_url}/api/ai/status/", timeout=5)
            ai_status = response.json()
            if ai_status.get('available'):
                print("  ✅ AI models loaded and ready!")
            else:
                print("  ⚠ AI models not available. Using simulation mode.")
        except Exception:
            print("  ⚠ Could not check AI status.")
        
        print(f"\n  Starting simulation:")
        print(f"    Duration: {duration_minutes} minutes")
        print(f"    Update interval: {interval_seconds} seconds")
        print(f"    AI decisions: {'Enabled' if ENABLE_AI_DECISIONS else 'Disabled'}")
        print(f"    Accelerated time: {'Yes' if accelerated else 'No'}")
        print(f"\n  Press Ctrl+C to stop\n")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time and not shutdown_flag.is_set():
                # Run iteration
                result = self.run_iteration()
                
                # Print status
                self.print_status(result)
                
                # Advance simulation time if accelerated
                if accelerated:
                    self.data_generator.advance_time(1)  # 1 minute per iteration
                # In normal mode, time advances naturally with real clock
                
                # Wait for next iteration
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\n  Simulation stopped by user.")
        
        # Print final summary
        self.print_summary()
    
    def print_summary(self):
        """Print final simulation summary."""
        print("\n" + "="*60)
        print("  SIMULATION SUMMARY")
        print("="*60)
        print(f"\n  Total Iterations: {self.stats['total_iterations']}")
        print(f"  Successful API Calls: {self.stats['successful_api_calls']}")
        print(f"  AI Decisions Made: {self.stats['ai_decisions_made']}")
        print(f"  Total Simulated Cost: ₹{self.stats['total_cost']:.2f}")
        print(f"  Total Simulated Carbon: {self.stats['total_carbon']/1000:.2f} kg CO2")
        
        if self.decision_history:
            print(f"\n  Last AI Decision:")
            last_decision = self.decision_history[-1]
            current = last_decision.get('current_decision', {})
            print(f"    Allocation: {current.get('source_allocation', [])}")
            print(f"    Recommendation: {last_decision.get('recommendation', 'N/A')}")
        
        print("\n" + "="*60)
        print("  Simulation complete! Check the HyperVolt dashboard for results.")
        print("  Frontend URL: http://localhost:3000")
        print("="*60 + "\n")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n  Received shutdown signal...")
    shutdown_flag.set()


def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments (simple version)
    import argparse
    parser = argparse.ArgumentParser(
        description='HyperVolt Simulation - Without Sensors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_simulation_without_sensors.py
  python run_simulation_without_sensors.py --duration 30 --interval 10
  python run_simulation_without_sensors.py --accelerated --start-hour 6
        """
    )
    parser.add_argument('--duration', type=int, default=SIMULATION_DURATION_MINUTES,
                        help='Simulation duration in minutes (default: 60)')
    parser.add_argument('--interval', type=int, default=UPDATE_INTERVAL_SECONDS,
                        help='Update interval in seconds (default: 5)')
    parser.add_argument('--accelerated', action='store_true',
                        help='Run accelerated simulation (1 sec = 1 sim minute)')
    parser.add_argument('--start-hour', type=int, default=None,
                        help='Starting hour of simulation (0-23, default: current)')
    parser.add_argument('--api-url', type=str, default=API_BASE_URL,
                        help=f'Backend API URL (default: {API_BASE_URL})')
    parser.add_argument('--no-ai', action='store_true',
                        help='Disable AI decision making')
    
    args = parser.parse_args()
    
    # Update global config
    global ENABLE_AI_DECISIONS
    if args.no_ai:
        ENABLE_AI_DECISIONS = False
    
    # Create and run simulation
    runner = SimulationRunner(api_url=args.api_url)
    
    if args.start_hour is not None:
        runner.data_generator = SyntheticDataGenerator(start_hour=args.start_hour)
    
    runner.run(
        duration_minutes=args.duration,
        interval_seconds=args.interval,
        accelerated=args.accelerated
    )


if __name__ == '__main__':
    main()
