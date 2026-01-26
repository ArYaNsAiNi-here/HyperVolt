# Module 3: The Prophet (AI Inference Engine)

## Overview

Module 3 is the "brain" of the Vesta Energy Orchestrator. It uses machine learning to predict energy demand, optimize energy source selection, and minimize both cost and carbon footprint.

## What This Module Does

1. **Demand Forecasting**: Predicts energy consumption for the next 6-24 hours
2. **Source Optimization**: Decides which energy source to use (Grid/Solar/Battery)
3. **Carbon Optimization**: Shifts energy-intensive tasks to low-carbon periods
4. **Cost Optimization**: Reduces electricity bills by avoiding peak hours

## Dataset Collection

### Available Datasets

All datasets are stored in `../data/raw/` directory:

1. **Weather Data** (`weather_historical.csv`, `weather_forecast.csv`)
   - Temperature, humidity, cloud cover, wind speed
   - Solar radiation proxy (for solar panel prediction)
   - 30 days historical + 5 days forecast

2. **Carbon Intensity** (`carbon_historical.csv`, `carbon_forecast.csv`)
   - Grid carbon intensity (gCO2eq/kWh)
   - Renewable vs fossil fuel percentage
   - Grid electricity pricing
   - 30 days historical + 24 hours forecast

3. **Energy Consumption** (`energy_consumption.csv`)
   - Lighting, appliances, HVAC energy usage
   - Total household consumption patterns
   - Occupancy and behavioral patterns
   - 30 days of hourly data

4. **Sensor Readings** (`sensor_readings.csv`)
   - LDR (Light Dependent Resistor) readings
   - Current sensor (ACS712) measurements
   - DHT22 temperature/humidity readings
   - 30 days of 5-minute interval data

5. **Integrated Dataset** (`integrated_dataset.csv`)
   - All above datasets merged into one
   - Ready for ML model training
   - 30 days of hourly data with 25+ features

### How to Collect Datasets

#### Option 1: Collect All Datasets at Once (Recommended)

```bash
cd module3-ai
python collect_all_data.py
```

This will:
- Collect weather data from OpenWeatherMap API (or generate mock data)
- Collect carbon intensity from Electricity Maps API (or generate mock data)
- Generate realistic energy consumption patterns
- Generate sensor readings (simulating ESP32)
- Create an integrated dataset ready for ML training

#### Option 2: Collect Individual Datasets

```bash
# Weather data only
python collect_weather_data.py

# Carbon intensity only
python collect_carbon_data.py

# Energy consumption patterns
python generate_energy_data.py

# Sensor readings
python generate_sensor_data.py
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r ../requirements.txt
```

### 2. Configure API Keys (Optional)

Copy the example environment file and add your API keys:

```bash
cp ../.env.example ../.env
```

Edit `.env` and add:
- `OPENWEATHER_API_KEY`: Get free API key from [OpenWeatherMap](https://openweathermap.org/api)
- `ELECTRICITY_MAPS_API_KEY`: Get API key from [Electricity Maps](https://www.electricitymaps.com/)

**Note**: API keys are optional. If not provided, the scripts will generate realistic synthetic data.

### 3. Adjust Location Settings

Edit `.env` to set your location:
```
LATITUDE=12.9716
LONGITUDE=77.5946
LOCATION_NAME=Bangalore
```

## Dataset Features

### Integrated Dataset Features (25+ columns)

**Time Features:**
- timestamp, hour, day_of_week, is_weekend, is_peak_hour

**Energy Features:**
- lighting_energy_kwh, appliance_energy_kwh, hvac_energy_kwh
- total_energy_kwh, cumulative_energy_kwh

**Weather Features:**
- temperature, humidity, cloud_cover, wind_speed
- solar_radiation_proxy, is_daylight

**Carbon & Grid Features:**
- carbon_intensity (gCO2eq/kWh)
- renewable_percentage, fossil_fuel_percentage
- grid_price_per_kwh

**Sensor Features:**
- ldr_lux (ambient light level)
- current_a (current draw)
- power_w (instantaneous power)
- indoor_temperature_c, indoor_humidity_pct

**Calculated Features:**
- energy_cost (₹)
- carbon_footprint (kg CO2)

## Next Steps: Building the AI Model

After collecting datasets, you can:

1. **Exploratory Data Analysis (EDA)**
   - Visualize energy patterns
   - Identify peak consumption hours
   - Analyze correlation between features

2. **Feature Engineering**
   - Create lag features (previous hour/day consumption)
   - Add time-based features (season, month)
   - Normalize/scale features

3. **Model Training**
   - LSTM for time series forecasting
   - Random Forest for source selection
   - Optimization algorithms for cost/carbon reduction

4. **Model Evaluation**
   - Test prediction accuracy
   - Validate on unseen data
   - Measure cost and carbon savings

## Data Statistics

After running `collect_all_data.py`, you'll see statistics like:

```
📊 Individual Datasets:
  Weather Data:          720 records (30 days, hourly)
  Carbon Intensity:      720 records (30 days, hourly)
  Energy Consumption:    720 records (30 days, hourly)
  Sensor Readings:       8,640 records (30 days, 5-min intervals)

📈 Integrated Dataset:   720 records
  Features:              25+ columns
  Time span:             30 days
  Frequency:             Hourly

💡 Key Statistics:
  Avg Energy Usage:      ~2.5 kWh/hour
  Total Energy (30d):    ~1,800 kWh
  Avg Carbon Intensity:  ~500 gCO2eq/kWh
  Total Carbon (30d):    ~900 kg CO2
```

## API Keys - Getting Started

### OpenWeatherMap API
1. Sign up at https://openweathermap.org/
2. Go to API Keys section
3. Generate a free API key (free tier: 60 calls/min)
4. Add to `.env` file

### Electricity Maps API
1. Sign up at https://www.electricitymaps.com/
2. Request API access
3. Add API key to `.env` file

**Note**: Both APIs have free tiers suitable for hackathon projects!

## Troubleshooting

**Issue**: API rate limits exceeded
**Solution**: Scripts automatically fall back to synthetic data generation

**Issue**: Missing dependencies
**Solution**: Run `pip install -r ../requirements.txt`

**Issue**: Data files not created
**Solution**: Check if `../data/raw/` directory exists and is writable

## File Structure

```
module3-ai/
├── collect_weather_data.py       # Weather data collector
├── collect_carbon_data.py        # Carbon intensity collector
├── generate_energy_data.py       # Energy consumption generator
├── generate_sensor_data.py       # Sensor data generator
├── collect_all_data.py           # Master data collection script
└── README.md                     # This file

../data/
├── raw/                          # Raw collected datasets
│   ├── weather_historical.csv
│   ├── weather_forecast.csv
│   ├── carbon_historical.csv
│   ├── carbon_forecast.csv
│   ├── energy_consumption.csv
│   ├── sensor_readings.csv
│   └── integrated_dataset.csv    # Main ML training dataset
└── processed/                    # Processed datasets (for ML)
```

## Credits

Built for **Sustainergy Hackathon 2026** by Team HyperVolt
