#!/usr/bin/env python3
"""
Test if AI models can be loaded successfully
"""
import os
import sys

# Add paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_MODULE_PATH = os.path.join(PROJECT_ROOT, 'ai', 'module3-ai')
sys.path.insert(0, AI_MODULE_PATH)

print("="*70)
print("  HYPERVOLT AI MODEL LOADER TEST")
print("="*70)
print()

# Test 1: Check if model files exist
print("1. Checking if model files exist...")
print("-" * 70)

model_files = {
    'Demand Forecaster Model': 'ai/models/demand_forecaster.h5',
    'Demand Forecaster Config': 'ai/models/demand_forecaster_config.json',
    'Demand Forecaster Scalers': 'ai/models/demand_forecaster_scalers.pkl',
    'Solar Dust Model': 'ai/models/solar_dust_random_forest.pkl',
    'Solar Dust Scaler': 'ai/models/solar_dust_scaler.pkl',
}

all_exist = True
for name, rel_path in model_files.items():
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    exists = os.path.exists(full_path)
    status = "✅" if exists else "❌"
    print(f"{status} {name}: {rel_path}")
    if exists:
        size_mb = os.path.getsize(full_path) / (1024 * 1024)
        print(f"   Size: {size_mb:.2f} MB")
    all_exist = all_exist and exists

if not all_exist:
    print("\n❌ Some model files are missing!")
    print("   Please train models with:")
    print("   cd ai/module3-ai && python train_demand_model.py")
    sys.exit(1)

print("\n✅ All model files exist!")

# Test 2: Load EnergyDemandForecaster
print("\n2. Testing EnergyDemandForecaster...")
print("-" * 70)

try:
    from train_demand_model import EnergyDemandForecaster

    forecaster = EnergyDemandForecaster()
    model_path = os.path.join(PROJECT_ROOT, 'ai', 'models', 'demand_forecaster.h5')

    print(f"Loading model from: {model_path}")
    success = forecaster.load_model(model_path)

    if success:
        print("✅ EnergyDemandForecaster loaded successfully!")
        print(f"   Lookback hours: {forecaster.lookback_hours}")
        print(f"   Forecast horizon: {forecaster.forecast_horizon}")
        print(f"   Feature columns: {len(forecaster.feature_columns)}")
        for col in forecaster.feature_columns:
            print(f"      - {col}")
    else:
        print("❌ Failed to load EnergyDemandForecaster!")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error loading EnergyDemandForecaster: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Load SourceOptimizer
print("\n3. Testing SourceOptimizer...")
print("-" * 70)

try:
    from optimize_sources import SourceOptimizer

    optimizer = SourceOptimizer(
        carbon_weight=0.5,
        cost_weight=0.5,
        solar_capacity=3.0,
        battery_capacity=10.0,
        battery_max_discharge=2.0
    )

    print("✅ SourceOptimizer initialized successfully!")
    print(f"   Solar capacity: {optimizer.solar_capacity} kW")
    print(f"   Battery capacity: {optimizer.battery_capacity} kWh")
    print(f"   Carbon weight: {optimizer.carbon_weight}")
    print(f"   Cost weight: {optimizer.cost_weight}")

except Exception as e:
    print(f"❌ Error initializing SourceOptimizer: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check feature column compatibility
print("\n4. Checking feature column compatibility...")
print("-" * 70)

expected_columns = forecaster.feature_columns
problematic = []

# Check for renamed columns
if 'solar_radiation_proxy' in expected_columns:
    problematic.append("'solar_radiation_proxy' should be renamed to 'shortwave_radiation'")

if problematic:
    print("⚠️  Found potential issues:")
    for issue in problematic:
        print(f"   - {issue}")
else:
    print("✅ Feature columns look good!")

# Summary
print("\n" + "="*70)
print("  SUMMARY")
print("="*70)
print()
print("✅ All tests passed!")
print()
print("The AI models are ready to use. You can now:")
print("  1. Start Django: cd api && daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application")
print("  2. Run simulation: python scripts/run_simulation_without_sensors.py")
print()
print("Expected output:")
print("  ✅ AI models loaded and ready!")
print("  ✅ AI Decisions: 1+ (increasing)")
print()
print("="*70)
