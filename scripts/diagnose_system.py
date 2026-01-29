#!/usr/bin/env python3
"""
HyperVolt System Diagnostic Tool
=================================

This script checks all components of the HyperVolt system to identify issues.

Usage:
    python scripts/diagnose_system.py
"""

import os
import sys
import requests
import time

# Add project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_PATH = os.path.join(PROJECT_ROOT, 'api')
sys.path.insert(0, API_PATH)

# Configuration
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')
WEBSOCKET_URL = 'ws://localhost:8000/ws/sensors/'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_result(check_name, passed, details=""):
    """Print a check result"""
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")
    if details:
        print(f"   └─ {details}")

def check_redis():
    """Check if Redis is running"""
    print_header("CHECKING REDIS")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print_result("Redis Connection", True, "Redis is running")

        # Check channels support
        info = r.info('server')
        print_result("Redis Version", True, f"Version {info.get('redis_version', 'unknown')}")
        return True
    except Exception as e:
        print_result("Redis Connection", False, f"Error: {e}")
        print("   ⚠️  Solution: Start Redis with 'redis-server'")
        return False

def check_api_health():
    """Check if Django API is running"""
    print_header("CHECKING DJANGO API")
    try:
        response = requests.get(f"{API_BASE_URL}/api/ai/status/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result("API Health", True, "Django API is running")
            print_result("AI Models Available", data.get('available', False),
                        f"Models loaded: {data.get('models_loaded', False)}")
            return True
        else:
            print_result("API Health", False, f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_result("API Health", False, "Connection refused")
        print("   ⚠️  Solution: Start Django with:")
        print("      cd api && daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application")
        return False
    except Exception as e:
        print_result("API Health", False, f"Error: {e}")
        return False

def check_api_endpoints():
    """Check if key API endpoints are working"""
    print_header("CHECKING API ENDPOINTS")

    endpoints = [
        ('/api/sensor-readings/', 'Sensor Readings'),
        ('/api/grid-data/', 'Grid Data'),
        ('/api/energy-sources/', 'Energy Sources'),
        ('/api/ai/status/', 'AI Status'),
        ('/api/predictions/forecast/?hours=6', 'AI Forecast'),
    ]

    all_passed = True
    for path, name in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{path}", timeout=5)
            passed = response.status_code in [200, 201]
            print_result(name, passed, f"Status: {response.status_code}")
            all_passed = all_passed and passed
        except Exception as e:
            print_result(name, False, f"Error: {e}")
            all_passed = False

    return all_passed

def test_sensor_post():
    """Test posting a sensor reading"""
    print_header("TESTING SENSOR DATA POST")
    try:
        data = {
            'sensor_type': 'temperature',
            'sensor_id': 'test_sensor_1',
            'value': 25.5,
            'unit': 'celsius',
            'location': 'test_room',
        }
        response = requests.post(
            f"{API_BASE_URL}/api/sensor-readings/",
            json=data,
            timeout=5
        )
        passed = response.status_code in [200, 201]
        print_result("POST Sensor Reading", passed,
                    f"Status: {response.status_code}")
        if passed:
            print(f"   └─ Response: {response.json()}")
        return passed
    except Exception as e:
        print_result("POST Sensor Reading", False, f"Error: {e}")
        return False

def check_ai_decision():
    """Test AI decision endpoint"""
    print_header("TESTING AI DECISION")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/predictions/decide/",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            available = data.get('available', False)
            print_result("AI Decision", available,
                        f"Available: {available}")
            if available:
                current = data.get('current_decision', {})
                print(f"   └─ Predicted Demand: {current.get('predicted_demand_kwh', 0):.3f} kWh")
                print(f"   └─ Recommendation: {data.get('recommendation', 'N/A')[:60]}")
            return available
        else:
            print_result("AI Decision", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("AI Decision", False, f"Error: {e}")
        return False

def check_websocket():
    """Check if WebSocket is accessible"""
    print_header("CHECKING WEBSOCKET")
    try:
        import websocket
        ws = websocket.create_connection(WEBSOCKET_URL, timeout=5)
        print_result("WebSocket Connection", True, "Connected successfully")
        ws.close()
        return True
    except ImportError:
        print_result("WebSocket Connection", False, "websocket-client not installed")
        print("   ⚠️  Solution: pip install websocket-client")
        return False
    except Exception as e:
        print_result("WebSocket Connection", False, f"Error: {e}")
        print("   ⚠️  Make sure you're using daphne (not runserver)")
        return False

def check_ai_models():
    """Check if AI model files exist"""
    print_header("CHECKING AI MODEL FILES")

    model_paths = [
        ('ai/models/demand_forecaster.h5', 'Demand Forecaster'),
        ('ai/models/demand_forecaster_config.json', 'Forecaster Config'),
        ('ai/models/demand_forecaster_scalers.pkl', 'Forecaster Scalers'),
        ('ai/models/solar_dust_random_forest.pkl', 'Solar Dust Model'),
        ('ai/models/solar_dust_scaler.pkl', 'Solar Dust Scaler'),
    ]

    all_exist = True
    for rel_path, name in model_paths:
        abs_path = os.path.join(PROJECT_ROOT, rel_path)
        exists = os.path.exists(abs_path)
        print_result(name, exists, abs_path if exists else "Not found")
        all_exist = all_exist and exists

    if not all_exist:
        print("\n   ⚠️  Solution: Train models with:")
        print("      cd ai/module3-ai")
        print("      python train_demand_model.py")

    return all_exist

def check_simulation_file():
    """Check if simulation data file exists"""
    print_header("CHECKING SIMULATION DATA FILE")

    sim_file = os.path.join(PROJECT_ROOT, 'api', 'data', 'simulation_sensors.csv')
    exists = os.path.exists(sim_file)
    print_result("Simulation File", exists, sim_file)

    if exists:
        try:
            with open(sim_file, 'r') as f:
                lines = f.readlines()
                print(f"   └─ File has {len(lines)} lines")
                if len(lines) > 1:
                    print(f"   └─ Last line: {lines[-1].strip()}")
        except Exception as e:
            print(f"   └─ Could not read file: {e}")

    return exists

def main():
    """Run all diagnostic checks"""
    print("\n" + "="*70)
    print("  HYPERVOLT SYSTEM DIAGNOSTICS")
    print("  Checking all components...")
    print("="*70)

    results = {}

    # Run checks
    results['redis'] = check_redis()
    results['api'] = check_api_health()
    results['endpoints'] = check_api_endpoints()
    results['sensor_post'] = test_sensor_post()
    results['ai_decision'] = check_ai_decision()
    results['websocket'] = check_websocket()
    results['models'] = check_ai_models()
    results['simulation'] = check_simulation_file()

    # Summary
    print_header("DIAGNOSTIC SUMMARY")

    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)

    print(f"Checks Passed: {passed_checks}/{total_checks}")
    print()

    if passed_checks == total_checks:
        print("✅ All checks passed! System is ready.")
        print()
        print("To run simulation:")
        print("  python scripts/run_simulation_without_sensors.py")
        print()
        print("To view dashboard:")
        print("  Open http://localhost:3000 in your browser")
    else:
        print("❌ Some checks failed. Please review the issues above.")
        print()
        print("Common Solutions:")
        print("  1. Start Redis: redis-server")
        print("  2. Start Django: cd api && daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application")
        print("  3. Start Frontend: cd website && npm run dev")
        print("  4. Train AI models: cd ai/module3-ai && python train_demand_model.py")

    print("="*70 + "\n")

    return passed_checks == total_checks


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
