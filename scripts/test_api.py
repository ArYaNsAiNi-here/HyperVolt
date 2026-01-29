#!/usr/bin/env python3
"""
Quick API Test - Tests if Django API is responding correctly
"""

import requests
import json

API_URL = "http://localhost:8000"

print("="*60)
print("HYPERVOLT API QUICK TEST")
print("="*60)

# Test 1: API Health
print("\n1. Testing API health...")
try:
    response = requests.get(f"{API_URL}/api/ai/status/", timeout=5)
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ API is running!")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"   ❌ Unexpected status code")
        print(f"   Response: {response.text}")
except requests.exceptions.ConnectionError:
    print(f"   ❌ Cannot connect to {API_URL}")
    print(f"   Make sure Django is running with:")
    print(f"      cd api && daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application")
    exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 2: POST Sensor Reading
print("\n2. Testing POST sensor reading...")
data = {
    'sensor_type': 'temperature',
    'sensor_id': 'test_1',
    'value': 25.5,
    'unit': 'celsius',
    'location': 'test_room',
}
try:
    response = requests.post(
        f"{API_URL}/api/sensor-readings/",
        json=data,
        timeout=5
    )
    print(f"   Status Code: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"   ✅ Sensor POST works!")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"   ❌ POST failed")
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: GET Sensor Readings
print("\n3. Testing GET sensor readings...")
try:
    response = requests.get(f"{API_URL}/api/sensor-readings/", timeout=5)
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        count = len(data.get('results', data)) if isinstance(data, dict) else len(data)
        print(f"   ✅ GET works! Found {count} readings")
    else:
        print(f"   ❌ GET failed")
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: AI Decision
print("\n4. Testing AI decision...")
try:
    response = requests.post(
        f"{API_URL}/api/ai/decide/",
        timeout=10
    )
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        available = data.get('available', False)
        if available:
            print(f"   ✅ AI Decision works!")
            print(f"   Recommendation: {data.get('recommendation', 'N/A')}")
        else:
            print(f"   ⚠️  AI models not available")
            print(f"   Response: {json.dumps(data, indent=2)}")
    else:
        print(f"   ❌ AI Decision failed")
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("Test Complete!")
print("="*60 + "\n")
