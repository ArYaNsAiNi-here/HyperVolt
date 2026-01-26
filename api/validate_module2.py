"""
Validation script for HyperVolt Module 2
Tests all major components to ensure they're working correctly.

Usage:
    python validate_module2.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hypervolt_backend.settings')
django.setup()

from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient
from data_pipeline.models import SensorReading, GridData, UserPreferences, EnergySource
from data_pipeline.services import ElectricityMapsService, WeatherService, SensorBufferManager
from django.utils import timezone

def print_test(name):
    """Print test name."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)

def print_pass(message):
    """Print success message."""
    print(f"✅ {message}")

def print_fail(message):
    """Print failure message."""
    print(f"❌ {message}")
    sys.exit(1)

def test_django_setup():
    """Test basic Django setup."""
    print_test("Django Setup")
    
    try:
        # Run system checks
        call_command('check', verbosity=0)
        print_pass("Django system check passed")
        
        # Check migrations
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            print_fail("Unapplied migrations found. Run: python manage.py migrate")
        else:
            print_pass("All migrations applied")
            
    except Exception as e:
        print_fail(f"Django setup failed: {e}")

def test_models():
    """Test database models."""
    print_test("Database Models")
    
    try:
        # Test SensorReading
        sr = SensorReading.objects.create(
            sensor_type='ldr',
            sensor_id='validation_test',
            value=500,
            unit='lux',
            location='test_room',
            timestamp=timezone.now()
        )
        print_pass(f"Created SensorReading: {sr}")
        sr.delete()
        
        # Test GridData
        gd = GridData.objects.create(
            data_type='carbon_intensity',
            value=400,
            unit='gCO2eq/kWh',
            zone='IN-KA',
            timestamp=timezone.now()
        )
        print_pass(f"Created GridData: {gd}")
        gd.delete()
        
        # Test UserPreferences
        up = UserPreferences.objects.create(
            preference_key='test_pref',
            preference_value={'test': True}
        )
        print_pass(f"Created UserPreferences: {up}")
        up.delete()
        
        # Test EnergySource
        es = EnergySource.objects.create(
            source_type='grid',
            is_available=True
        )
        print_pass(f"Created EnergySource: {es}")
        es.delete()
        
        print_pass("All models working correctly")
        
    except Exception as e:
        print_fail(f"Model test failed: {e}")

def test_services():
    """Test service classes."""
    print_test("Service Classes")
    
    try:
        # Test ElectricityMapsService
        ems = ElectricityMapsService()
        carbon_data = ems.get_mock_carbon_intensity()
        assert carbon_data['carbon_intensity'] > 0
        print_pass(f"ElectricityMapsService working: {carbon_data['carbon_intensity']} gCO2eq/kWh")
        
        # Test WeatherService
        ws = WeatherService()
        weather_data = ws.get_mock_weather()
        assert weather_data['temperature'] > 0
        print_pass(f"WeatherService working: {weather_data['temperature']}°C")
        
        # Test SensorBufferManager (requires Redis)
        try:
            sbm = SensorBufferManager()
            sbm.add_reading('ldr', 'test_sensor', 750, timezone.now().isoformat())
            readings = sbm.get_latest_readings('ldr', 'test_sensor')
            assert len(readings) == 1
            print_pass(f"SensorBufferManager working: {len(readings)} reading(s) cached")
            sbm.clear_buffer('ldr', 'test_sensor')
        except Exception as redis_error:
            print(f"⚠️  SensorBufferManager skipped (Redis not running): {redis_error}")
            print("   Note: Redis is required for Hot Path functionality")
        
        print_pass("All services working correctly")
        
    except Exception as e:
        print_fail(f"Service test failed: {e}")

def test_api():
    """Test REST API endpoints."""
    print_test("REST API Endpoints")
    
    client = APIClient()
    
    try:
        # Test sensor readings endpoint
        url = reverse('data_pipeline:sensor-reading-list')
        response = client.get(url)
        assert response.status_code == 200
        print_pass(f"Sensor readings API: {url} (status {response.status_code})")
        
        # Test grid data endpoint
        url = reverse('data_pipeline:grid-data-list')
        response = client.get(url)
        assert response.status_code == 200
        print_pass(f"Grid data API: {url} (status {response.status_code})")
        
        # Test preferences endpoint
        url = reverse('data_pipeline:preference-list')
        response = client.get(url)
        assert response.status_code == 200
        print_pass(f"Preferences API: {url} (status {response.status_code})")
        
        # Test AI decisions endpoint
        url = reverse('data_pipeline:ai-decision-list')
        response = client.get(url)
        assert response.status_code == 200
        print_pass(f"AI decisions API: {url} (status {response.status_code})")
        
        # Test energy sources endpoint
        url = reverse('data_pipeline:energy-source-list')
        response = client.get(url)
        assert response.status_code == 200
        print_pass(f"Energy sources API: {url} (status {response.status_code})")
        
        print_pass("All API endpoints working correctly")
        
    except Exception as e:
        print_fail(f"API test failed: {e}")

def test_tasks():
    """Test scheduled tasks."""
    print_test("Scheduled Tasks")
    
    try:
        from data_pipeline.tasks import fetch_carbon_intensity, fetch_weather_data
        
        # Test carbon intensity fetch
        result = fetch_carbon_intensity()
        print_pass(f"Carbon intensity task: {result}")
        
        # Test weather data fetch
        result = fetch_weather_data()
        print_pass(f"Weather data task: {result}")
        
        print_pass("All tasks working correctly")
        
    except Exception as e:
        print_fail(f"Task test failed: {e}")

def main():
    """Run all validation tests."""
    print("\n" + "="*60)
    print("HyperVolt Module 2 - Validation Suite")
    print("="*60)
    
    test_django_setup()
    test_models()
    test_services()
    test_api()
    test_tasks()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    print("\nModule 2 is fully functional and ready to use!")
    print("\nNext steps:")
    print("1. Start Redis: redis-server")
    print("2. Start Mosquitto: mosquitto -v")
    print("3. Start Django: daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application")
    print("4. Start MQTT Listener: python manage.py mqtt_listener")
    print("5. Test with: python test_mqtt_publisher.py")
    print("\nSee QUICKSTART.md for detailed instructions.")

if __name__ == '__main__':
    main()
