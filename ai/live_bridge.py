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
            print("Note: Local SourceOptimizer not available. Using API endpoint for optimization.")
            # Use API endpoint for optimization - this is a valid alternative approach
            try:
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
            except requests.exceptions.RequestException as e:
                print(f"Failed to connect to API: {e}")
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
    # Default values used when API data is not available
    current_carbon = 450  # Default carbon intensity in gCO2eq/kWh
    current_solar = 0.8   # Default solar radiation factor (0-1)
    
    # Try to extract carbon intensity from grid data
    # The API returns different formats depending on the endpoint
    if grid:
        if isinstance(grid, list) and len(grid) > 0:
            # Grid data returned as list of readings
            current_carbon = grid[0].get('value', 450)
            print(f"  Using carbon intensity from grid list: {current_carbon}g")
        elif isinstance(grid, dict) and 'results' in grid:
            # Paginated response format
            results = grid.get('results', [])
            if results and len(results) > 0:
                current_carbon = results[0].get('value', 450)
                print(f"  Using carbon intensity from paginated response: {current_carbon}g")
        elif isinstance(grid, dict):
            # Single reading format
            current_carbon = grid.get('carbon_intensity', grid.get('value', 450))
            print(f"  Using carbon intensity from dict: {current_carbon}g")
    else:
        print(f"  Using default carbon intensity: {current_carbon}g")
    
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