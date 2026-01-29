#!/usr/bin/env python3
"""
Create 24 hours of fake historical sensor data for AI training
"""
import os
import sys
import django

# Setup Django
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_PATH = os.path.join(PROJECT_ROOT, 'api')
sys.path.insert(0, API_PATH)
os.chdir(API_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hypervolt_backend.settings')
django.setup()

from data_pipeline.models import SensorReading
from django.utils import timezone
from datetime import timedelta
import random

print("=" * 70)
print("  CREATING HISTORICAL SENSOR DATA")
print("=" * 70)
print()

now = timezone.now()
created_count = 0

print("Creating 24 hours of sensor readings...")
print()

for i in range(24):
    timestamp = now - timedelta(hours=24-i)

    # Temperature (20-30°C)
    SensorReading.objects.create(
        sensor_type='temperature',
        sensor_id='temp_sim_1',
        value=25.0 + random.uniform(-3, 3),
        unit='celsius',
        timestamp=timestamp
    )
    created_count += 1

    # LDR (300-800 raw)
    SensorReading.objects.create(
        sensor_type='ldr',
        sensor_id='ldr_sim_1',
        value=500 + random.uniform(-200, 300),
        unit='raw',
        timestamp=timestamp
    )
    created_count += 1

    # Current (0.2-1.0 A)
    SensorReading.objects.create(
        sensor_type='current',
        sensor_id='current_sim_1',
        value=0.6 + random.uniform(-0.3, 0.4),
        unit='amperes',
        timestamp=timestamp
    )
    created_count += 1

    # Humidity (40-80%)
    SensorReading.objects.create(
        sensor_type='humidity',
        sensor_id='humidity_sim_1',
        value=60.0 + random.uniform(-15, 15),
        unit='percent',
        timestamp=timestamp
    )
    created_count += 1

    # Voltage (220-240V)
    SensorReading.objects.create(
        sensor_type='voltage',
        sensor_id='voltage_sim_1',
        value=230.0 + random.uniform(-8, 8),
        unit='volts',
        timestamp=timestamp
    )
    created_count += 1

    print(f"  Hour {i+1}/24: Created 5 readings at {timestamp.strftime('%Y-%m-%d %H:%M')}")

print()
print("=" * 70)
print(f"✅ SUCCESS! Created {created_count} historical sensor readings")
print("=" * 70)
print()
print("Historical data coverage:")
print(f"  From: {(now - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M')}")
print(f"  To:   {now.strftime('%Y-%m-%d %H:%M')}")
print()
print("The AI now has 24 hours of data to make predictions!")
print()
print("Next steps:")
print("  1. Restart Django")
print("  2. Run simulation")
print("  3. Wait for iteration 6 to see AI decisions")
print()
print("=" * 70)
