import requests
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.getcwd(), 'engine', 'ai'))

# CONFIGURATION
# Replace with your machine's IP if running remotely, or use localhost
API_HOST = os.environ.get('API_HOST', 'localhost')
API_URL = f"http://{API_HOST}:8000/api"


def get_live_data():
    """Fetch real-time data from the Backend API"""
    try:
        # 1. Get latest Grid Data (Carbon, Weather)
        grid_resp = requests.get(f"{API_URL}/grid-data/weather/?hours=24")
        grid_data = grid_resp.json()

        # 2. Get latest Sensor Data (Energy usage)
        sensor_resp = requests.get(f"{API_URL}/sensor-readings/latest/")
        sensor_data = sensor_resp.json()

        print("✓ Connected to Backend API")
        return grid_data, sensor_data
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None, None


def run_optimization():
    """Run energy optimization using the AI API endpoint"""
    try:
        from optimize_sources import SourceOptimizer, EnergySource
    except ImportError:
        # Try alternative import path
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), 'module3-ai'))
            from optimize_sources import SourceOptimizer, EnergySource
        except ImportError:
            print("Error: Could not import SourceOptimizer. Using API endpoint instead.")
            # Use API endpoint for optimization
            response = requests.post(f"{API_URL}/ai/decide/", timeout=10)
            if response.status_code == 200:
                result = response.json()
                print("\n--- AI DECISION (via API) ---")
                print(f"Recommendation: {result.get('recommendation', 'N/A')}")
                if 'current_decision' in result:
                    current = result['current_decision']
                    print(f"Sources: {current.get('source_allocation', [])}")
                    print(f"Cost: ₹{current.get('cost', 0):.2f}")
                    print(f"Carbon: {current.get('carbon', 0):.2f}g")
            else:
                print(f"API Error: {response.status_code}")
            return
    
    # Initialize the specific Optimizer logic
    optimizer = SourceOptimizer(
        carbon_weight=0.5,
        cost_weight=0.5,
        solar_capacity=3.0,
        battery_capacity=10.0
    )

    print("\n--- FETCHING LIVE CONTEXT ---")
    grid, sensors = get_live_data()

    if not grid or not sensors:
        return

    # Extract Live Values (Falling back to defaults if API is empty)
    # Note: In a real run, these keys depend on your exact API response structure
    current_carbon = 450
    current_solar = 0.8
    
    if isinstance(grid, list) and len(grid) > 0:
        current_carbon = grid[0].get('value', 450)
    elif isinstance(grid, dict):
        current_carbon = grid.get('carbon_intensity', 450)
    
    current_power_need = 1.5  # Example: Could be derived from 'current_sensor' amps

    # Run the Real Algorithm
    conditions = {
        'solar_radiation': current_solar,
        'cloud_cover': 10,  # Example: Get from weather API
        'hour': datetime.now().hour,
        'carbon_intensity': current_carbon,
        'grid_price': 12.0  # Standard rate
    }

    print(f"Current Conditions: Carbon={current_carbon}g | Power Need={current_power_need}kW")

    # The Magic Moment: AI Decides
    allocation, metrics = optimizer.optimize_source(current_power_need, conditions)

    print("\n--- AI DECISION ---")
    print(f"Sources Selected: {allocation}")
    print(f"Cost: ₹{metrics['cost']:.2f}")
    print(f"Carbon: {metrics['carbon']:.2f}g")


if __name__ == "__main__":
    run_optimization()