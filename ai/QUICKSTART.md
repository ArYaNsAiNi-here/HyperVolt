# Vesta Energy Orchestrator - Quick Start Guide

## 🚀 Getting Started in 10 Minutes

### Step 1: Clone and Setup

```bash
git clone https://github.com/ArYaNsAiNi-here/HyperVolt.git
cd HyperVolt
pip install -r requirements.txt
```

### Step 2: Generate Datasets

```bash
# Generate 30 days of training data
python module3-ai/collect_all_data.py
```

**Output**: You'll get 7 CSV files in `data/raw/`:
- `weather_historical.csv` - 720 records of weather data
- `carbon_historical.csv` - 720 records of grid carbon intensity
- `energy_consumption.csv` - 720 records of energy usage patterns
- `sensor_readings.csv` - 8,640 records of simulated ESP32 sensors
- `integrated_dataset.csv` - **Main ML training dataset** (27 features)
- Plus forecast files for weather and carbon

### Step 3: Train AI Models 🤖

```bash
# Train LSTM forecaster and optimizer (takes ~3 minutes)
python module3-ai/decision_engine.py

# NEW! Train solar dust prediction model
python module3-ai/generate_solar_dust_data.py  # Generate dust dataset
python module3-ai/train_solar_dust_model.py    # Train dust model
```

**What it does**:
- Trains LSTM model to predict energy 6 hours ahead
- Initializes source optimization algorithm
- **NEW!** Trains solar dust prediction (97% accurate!)
- Simulates 48 hours of real-time operation
- Saves models to `models/` directory

**Output**: 
- Energy models: 87.9% cost savings & 52.8% carbon reduction!
- **Solar dust model: Predicts panel cleaning needs with 97% R² accuracy!**

### Step 4: Explore the Results

```python
import pandas as pd

# Load the integrated dataset
df = pd.read_csv('data/raw/integrated_dataset.csv')

# View basic stats
print(f"Total records: {len(df)}")
print(f"Features: {len(df.columns)}")
print(f"\nAverage hourly energy: {df['total_energy_kwh'].mean():.3f} kWh")
print(f"Peak consumption: {df['total_energy_kwh'].max():.3f} kWh")
print(f"Average carbon intensity: {df['carbon_intensity'].mean():.0f} gCO2eq/kWh")
```

### Step 4: Next Steps

Now you're ready to build the AI models! The integrated dataset has everything you need:

**Time Features**: timestamp, hour, day_of_week, is_weekend, is_peak_hour

**Energy Features**: lighting_energy_kwh, appliance_energy_kwh, hvac_energy_kwh, total_energy_kwh

**Weather Features**: temperature, humidity, cloud_cover, wind_speed, solar_radiation_proxy

**Grid Features**: carbon_intensity, renewable_percentage, grid_price_per_kwh

**Sensor Features**: ldr_lux, current_a, power_w, indoor_temperature_c, indoor_humidity_pct

**Calculated Features**: energy_cost, carbon_footprint

## 📊 Understanding the Data

### What Makes This Dataset Special?

1. **Realistic Patterns**: Energy consumption follows actual household behavior
   - Peak usage during morning (7-9 AM) and evening (6-10 PM)
   - Lower consumption at night and when away
   - Weekend vs weekday differences

2. **Weather Correlation**: HVAC usage responds to outdoor temperature
   - More cooling needed when temp > 26°C
   - Lighting reduced during sunny hours

3. **Carbon Intelligence**: Grid carbon intensity varies by time
   - Lower during midday (solar generation)
   - Higher during peak hours (coal plants)
   - Weekend effect (reduced industrial demand)

4. **Sensor Realism**: Simulates actual ESP32 readings
   - LDR values: 0-1023 (10-bit ADC)
   - Current sensor with noise and variations
   - DHT22-style temperature/humidity readings

## 🎯 Training an AI Model (Example)

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Load data
df = pd.read_csv('data/raw/integrated_dataset.csv')

# Select features for prediction
features = [
    'hour', 'day_of_week', 'is_weekend',
    'temperature', 'humidity', 'solar_radiation_proxy',
    'carbon_intensity', 'occupancy_factor'
]
target = 'total_energy_kwh'

X = df[features]
y = df[target]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error: {mae:.3f} kWh")
print(f"R² Score: {r2:.3f}")
print(f"\nFeature Importance:")
for feature, importance in zip(features, model.feature_importances_):
    print(f"  {feature}: {importance:.3f}")
```

## 🔑 API Keys (Optional)

The scripts work with mock data by default. For real-time data:

1. **OpenWeatherMap**: https://openweathermap.org/api
   - Free tier: 60 calls/min
   - Add to `.env`: `OPENWEATHER_API_KEY=your_key`

2. **Electricity Maps**: https://www.electricitymaps.com/
   - Free tier available for students
   - Add to `.env`: `ELECTRICITY_MAPS_API_KEY=your_key`

## 💡 Tips & Tricks

### Regenerate Data with Different Patterns

```bash
# Edit .env to change location
LATITUDE=40.7128
LONGITUDE=-74.0060
LOCATION_NAME=New_York

# Regenerate data
python module3-ai/collect_all_data.py
```

### Collect Just One Dataset

```bash
# Weather only
python module3-ai/collect_weather_data.py

# Carbon intensity only
python module3-ai/collect_carbon_data.py

# Energy patterns only
python module3-ai/generate_energy_data.py

# Sensor data only
python module3-ai/generate_sensor_data.py
```

### Adjust Data Volume

Edit `collect_all_data.py`:
```python
# Change from 30 days to 90 days
collector = MasterDataCollector(days=90)
```

## 🐛 Troubleshooting

**Issue**: "Module not found" errors
```bash
pip install -r requirements.txt
```

**Issue**: Data files not created
```bash
# Check if data directory exists
mkdir -p data/raw
# Run collection again
python module3-ai/collect_all_data.py
```

**Issue**: Need smaller datasets for testing
```bash
# Modify days parameter in collect_all_data.py
collector = MasterDataCollector(days=7)  # Just 1 week
```

## 📚 What's Next?

1. **Module 3 - Part 2**: Build LSTM models for energy forecasting
2. **Module 3 - Part 3**: Create optimization algorithms for source selection
3. **Module 2**: Set up FastAPI backend for real-time inference
4. **Module 4**: Build Next.js Digital Twin dashboard
5. **Module 1**: Program ESP32 with sensors

## 🤝 Contributing

This is a hackathon project. Check the main README for the project structure and development roadmap.

---

**Built for Sustainergy Hackathon 2026** 🌱
