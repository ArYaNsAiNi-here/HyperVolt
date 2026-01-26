# HyperVolt - Vesta Energy Orchestrator

**Sustainergy Hackathon 2026 - Team HyperVolt**

## 🚀 Project Overview

**Vesta** is an AI-Driven Energy Orchestrator that doesn't just monitor energy - it predicts, optimizes, and acts as a "Brain" for your home's energy ecosystem. Using Digital Twin technology and Predictive Edge Intelligence, Vesta simulates the future and self-optimizes in real-time.

### The Vision

Most energy systems show you data. **Vesta simulates the future and self-optimizes in real-time.** It predicts a building's energy needs based on:
- External weather patterns
- Occupancy behavior
- Real-time carbon intensity of the power grid
- Time-of-use electricity pricing

### The "Mind-Blowing" Factor

- **Predictive Analytics**: Tells judges not what is happening now, but what will happen
- **Carbon Optimization**: Shifts heavy tasks to hours when the grid uses more renewable energy
- **Orchestrated Sources**: Intelligently switches between Grid/Solar/Battery to minimize cost and carbon
- **Adaptive Lighting**: Auto-adjusts brightness based on ambient light without user noticing
- **Visual Impact**: Sleek 3D Digital Twin dashboard that reacts to real-time sensor data

## 📁 Project Structure

```
HyperVolt/
├── module1-hardware/          # ESP32 sensors & connectivity
│   └── (Arduino/ESP32 code for sensors)
├── module2-backend/           # FastAPI backend & data pipeline
│   └── (Backend API, database handlers)
├── module3-ai/               # AI/ML brain (THE PROPHET) ⭐
│   ├── collect_all_data.py   # Master data collection script
│   ├── collect_weather_data.py
│   ├── collect_carbon_data.py
│   ├── generate_energy_data.py
│   ├── generate_sensor_data.py
│   └── README.md             # Module 3 documentation
├── module4-frontend/         # Next.js Digital Twin UI
│   └── (React/Next.js dashboard)
├── data/
│   ├── raw/                  # Raw datasets
│   └── processed/            # Processed ML-ready data
├── models/                   # Trained AI models
├── notebooks/                # Jupyter notebooks for analysis
├── scripts/                  # Utility scripts
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🎯 System Modules

### Module 1: The Sentinel (Edge Hardware)
**Status**: 🟡 Planning
- ESP32 microcontroller with Wi-Fi
- LDR (Light sensor) for ambient light detection
- ACS712 Current sensor for power monitoring
- DHT22 Temperature/Humidity sensor
- MQTT protocol for real-time data streaming

### Module 2: The Data Pipeline (Backend)
**Status**: 🟡 Planning
- FastAPI or Node.js backend
- InfluxDB for time-series data storage
- External API integrations:
  - OpenWeatherMap for weather forecasts
  - Electricity Maps for grid carbon intensity
- MQTT broker for IoT communication

### Module 3: The Prophet (AI Engine) ⭐
**Status**: 🟢 **COMPLETE - Phases 1 & 2**

This is the brain of Vesta! Features:
- ✅ **Dataset Collection**: Complete with 30 days of synthetic training data (Phase 1)
- ✅ **Demand Forecasting**: LSTM network predicts energy needs 6 hours ahead (Phase 2)
- ✅ **Source Optimization**: Decides Grid vs Solar vs Battery based on carbon + cost (Phase 2)
- ✅ **Retraining Capability**: Adapts to new data automatically (Phase 2)
- ✅ **Real-time Decision Engine**: Sub-second inference for live control (Phase 2)
- ✅ **Solar Dust Prediction**: ML model detects dust on solar panels using LDR + power output (Phase 2) **NEW!**

**Performance Metrics** (Phase 2):
- Forecasting: MAE 0.33 kWh, R² 0.67
- Optimization: 87.9% cost savings, 52.8% carbon reduction
- Solar Dust: MAE 1.86%, R² 0.97 **NEW!**
- Training: ~3 minutes for 50 epochs

**Ready Datasets** (in `data/raw/`):
- Weather patterns (temperature, solar radiation, cloud cover)
- Carbon intensity (grid cleanliness, renewable %)
- Energy consumption (lighting, appliances, HVAC)
- Sensor readings (LDR, current, temperature)
- Solar panel dust data (LDR, power output, efficiency) **NEW!**
- Integrated ML-ready dataset (27 features)

**Trained Models** (in `models/`):
- LSTM demand forecaster (TensorFlow/Keras)
- Source optimization algorithm
- Solar dust prediction (Random Forest) **NEW!**
- Scalers and configurations

👉 [See Module 3 Data README](module3-ai/README.md) | [See AI Models README](module3-ai/AI_MODELS_README.md) | [See Solar Dust README](module3-ai/SOLAR_DUST_README.md) **NEW!**

### Module 4: The Orchestrator (Digital Twin UI)
**Status**: 🟡 Planning
- Next.js / React frontend
- Three.js for 3D room visualization
- Real-time dashboard with live graphs
- User controls: brightness threshold slider
- Carbon savings counter

## 🛠️ Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend)
- ESP32 development board (for hardware)
- API Keys (optional, see Setup)

### Quick Start - Module 3 (Data Collection)

1. **Clone the repository**
   ```bash
   git clone https://github.com/ArYaNsAiNi-here/HyperVolt.git
   cd HyperVolt
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional)**
   ```bash
   cp .env.example .env
   # Edit .env to add API keys (or use mock data)
   ```

4. **Collect datasets for AI training**
   ```bash
   cd module3-ai
   python collect_all_data.py
   ```

   This generates:
   - 30 days of weather data
   - 30 days of carbon intensity patterns
   - 30 days of energy consumption
   - 30 days of sensor readings
   - Integrated ML-ready dataset

5. **Review collected data**
   ```bash
   ls -lh ../data/raw/
   # You'll see: weather_historical.csv, carbon_historical.csv, 
   # energy_consumption.csv, sensor_readings.csv, integrated_dataset.csv
   ```

## 📊 Key Features

### AI-Powered Optimization

```python
# The ai decides:
if carbon_intensity > threshold and battery_available:
    switch_to_battery()
elif solar_available and time_is_day:
    use_solar()
else:
    use_grid()
```

### Adaptive Lighting Logic

```
LDR senses: 400 lux (bright room)
AI predicts: User won't notice 20% dimming
Action: Dim lights, save 40W
Result: Invisible to user, 0.96 kWh saved daily
```

### Carbon Intelligence

```
Grid Carbon: 650 gCO2eq/kWh (high - coal plants running)
AI Decision: Delay EV charging to 2 AM when solar comes online
Saving: 2.4 kg CO2 per day
```

## 🎨 Tech Stack

**Hardware**: ESP32, LDR, ACS712, DHT22, MQTT  
**Backend**: Python, FastAPI, InfluxDB, Firebase  
**AI/ML**: TensorFlow, Keras, Scikit-learn, Pandas, NumPy  
**Frontend**: Next.js, React, Three.js, Recharts  
**APIs**: OpenWeatherMap, Electricity Maps  

## 📈 Expected Impact

### Metrics (30-day simulation):
- **Energy Savings**: 15-20% reduction in consumption
- **Cost Savings**: ₹300-500 per month
- **Carbon Reduction**: 120-150 kg CO2 per month
- **Peak Load Reduction**: 30% during grid peak hours

## 🏆 Hackathon Pitch

> "We didn't build a better light switch; we built a brain that understands energy context. Our hardware is just the ears and eyes; our software is the intelligence. Vesta doesn't just react to your energy needs - it predicts them, optimizes them, and makes your home carbon-aware."

### Wow Factors for Judges

1. **Real-time Digital Twin**: 3D room reacts to sensor data instantly
2. **Predictive Analytics**: Shows future energy savings, not just current usage
3. **Carbon Intelligence**: First-of-its-kind grid carbon integration
4. **Self-Optimization**: System makes decisions without user intervention
5. **Professional UI**: Looks like industrial IoT, built with basic hardware

## 📝 Development Roadmap

### Phase 1: Connectivity ✅ (Complete)
- [x] Project structure setup
- [x] Dataset collection framework
- [x] API integration templates
- [x] Mock data generators

### Phase 2: The Logic ✅ (Complete)
- [x] AI model training (LSTM for forecasting)
- [x] Optimization algorithms
- [x] Decision engine
- [x] Model evaluation
- [x] Retraining capability

### Phase 3: The Dashboard (Next)
- [ ] Next.js setup
- [ ] 3D Digital Twin (Three.js)
- [ ] Real-time graphs
- [ ] Control interface

### Phase 4: Integration
- [ ] ESP32 firmware
- [ ] Backend API
- [ ] MQTT communication
- [ ] End-to-end testing

### Phase 5: The Polish
- [ ] Dark mode UI
- [ ] Performance optimization
- [ ] Demo video
- [ ] Pitch deck

## 🤝 Contributing

This is a hackathon project. Team members:
- Hardware: ESP32 + Sensors
- Backend: FastAPI + Database
- AI/ML: Model Training + Optimization
- Frontend: UI/UX + Digital Twin

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🔗 Links

- **API Keys**: 
  - [OpenWeatherMap](https://openweathermap.org/api) (Free tier available)
  - [Electricity Maps](https://www.electricitymaps.com/) (Free tier available)
- **Documentation**: See individual module READMEs
- **Issues**: GitHub Issues tab

## 📞 Contact

Team HyperVolt - Sustainergy Hackathon 2026  
SMVIT College

---

**Built with ❤️ for a sustainable future**
