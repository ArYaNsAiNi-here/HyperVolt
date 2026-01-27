# HyperVolt

**SMVIT Sustainergy Hackathon 2026**

## The AI-Driven Energy Orchestrator

HyperVolt is an intelligent energy management system that doesn't just monitor energy consumption—it predicts, optimizes, and orchestrates energy usage in real-time. Using a software-heavy approach with predictive edge intelligence, HyperVolt acts as the "brain" that understands energy context and makes smart decisions.

## 🎯 Project Vision

Most energy systems show you data. **HyperVolt simulates the future and self-optimizes in real-time.**

### The Mind-Blowing Angle
- **Predictive Analytics**: Tells you what will happen, not just what is happening
- **Carbon-Aware**: Integrates grid carbon intensity to suggest optimal usage times
- **Self-Optimizing**: Uses AI to automatically select the best power source
- **Visual Impact**: Real-time digital twin with 3D visualization

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       HyperVolt System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │   Module 1   │────→│   Module 2  │────→│   Module 3  │  │
│  │  Sentinel    │     │ Data Pipeline│     │    Prophet  │  │
│  │  (Hardware)  │     │  (Backend)   │     │     (AI)    │  │
│  └──────────────┘     └─────────────┘     └─────────────┘  │
│         ↓                     ↓                    ↓         │
│  Raspberry Pi 5        Django + MQTT         TensorFlow     │
│  Sensors + MQTT        Redis + Channels      Scikit-learn   │
│                                                              │
│                    ┌─────────────┐                          │
│                    │   Module 4  │                          │
│                    │ Orchestrator│                          │
│                    │  (Frontend) │                          │
│                    └─────────────┘                          │
│                      Next.js + 3D                           │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Project Modules

### Module 1: The Sentinel (Hardware & Connectivity)
- Raspberry Pi 5 with sensors (LDR, Current sensor)
- MQTT protocol for real-time data streaming
- Basic circuit for adaptive lighting control

### Module 2: The Data Pipeline ✅ **[COMPLETED]**
- Django backend with REST API
- MQTT listener for sensor data ingestion
- Dual-path processing: Hot Path (Redis) + Cold Path (PostgreSQL)
- Real-time WebSocket streaming via Django Channels
- External API integration (Carbon intensity, Weather)
- Scheduled tasks for periodic data fetching

**📚 [See detailed Module 2 documentation](./MODULE2_README.md)**

### Module 3: The Prophet (AI Inference Engine) ✅ **[ENHANCED]**
- LSTM network for demand forecasting
- Power source selection algorithm with dynamic user preference weights
- Real-time decision-making based on context
- MQTT integration for hardware control
- Simulation mode for testing without hardware sensors
- Model retraining capabilities

**📚 Key Features:**
- **Dynamic Weights**: User preferences control AI optimization priorities (cost vs carbon)
- **Sensor Data Switching**: Toggle between simulation file and real hardware sensors
- **MQTT Publishing**: Automatically sends decisions to hardware for actuation
- **Model Retraining**: API endpoint to retrain models with recent data

### Module 4: The Orchestrator (Digital Twin UI)
*Coming Soon*
- Next.js frontend with Three.js 3D visualization
- Real-time dashboard with live graphs
- User controls for preferences
- Carbon footprint tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL (optional)
- Redis
- MQTT Broker (Mosquitto)
- Node.js 18+ (for frontend)

### Installation

```bash
# Clone the repository
git clone https://github.com/HyperHawks/HyperVolt.git
cd HyperVolt

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Start the system (see Module 2 README for details)
```

## 📊 Key Features

### ✨ Software Sophistication
- **Predictive Analytics**: Not what is happening, but what will happen
- **Context-Aware**: Considers weather, occupancy, grid carbon intensity
- **Real-time Optimization**: Makes decisions in milliseconds

### 🌱 Sustainability Focus
- **Grid Carbon Intensity API**: Shifts heavy tasks to renewable energy hours
- **Smart Load Balancing**: Reduces carbon footprint automatically
- **Energy Source Orchestration**: Selects optimal power source (Grid/Solar/Battery)

### 💡 Intelligent Lighting
- **Adaptive Brightness**: Automatically adjusts based on ambient light
- **User Preferences**: Configurable thresholds via UI
- **Predictive Dimming**: Learns patterns and predicts optimal levels

### 📈 Visual Impact
- **3D Digital Twin**: Real-time visualization of energy flow
- **Live Dashboards**: Graphs showing savings and predictions
- **Dark-Themed UI**: Professional, industrial aesthetic

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Real-time**: Django Channels + Redis
- **Database**: PostgreSQL (with SQLite fallback)
- **Task Queue**: Django-Q2
- **Communication**: MQTT (Paho)

### AI/ML
- TensorFlow / Scikit-learn
- LSTM for time-series prediction
- Random Forest for classification

### Frontend
- Next.js (React)
- Three.js / React Three Fiber (3D)
- Recharts (Data visualization)
- WebSocket for real-time updates

### Hardware
- Raspberry Pi 5 (8GB)
- LDR (Light sensor)
- ACS712 (Current sensor)
- DHT22 (Temperature/Humidity)

## 📡 API Documentation

### REST API
- **Base URL**: `http://localhost:8000/api/`
- **Endpoints**: See [Module 2 README](./MODULE2_README.md)

### WebSocket
- **URL**: `ws://localhost:8000/ws/sensors/`
- **Protocol**: JSON messages for sensor updates

### MQTT Topics
- **Sensors**: `HyperVolt/sensors/{location}/{sensor_type}`
- **Commands**: `HyperVolt/commands/{device_id}`

## 🎓 For the Hackathon

### The Pitch
> "We didn't build a better light switch; we built a brain that understands energy context. Our hardware is just the ears and eyes; our software is the intelligence."

### Judging Criteria Alignment
1. **Innovation**: Predictive AI + Carbon awareness
2. **Sustainability**: Optimizes for renewable energy usage
3. **Technical Complexity**: Full-stack with ML and real-time systems
4. **Scalability**: Modular architecture, cloud-ready
5. **Impact**: Measurable carbon footprint reduction

## 🎯 Development Roadmap

- [x] Module 2: Data Pipeline Backend
- [ ] Module 3: AI Inference Engine
- [ ] Module 4: Frontend Digital Twin
- [ ] Module 1: Hardware Integration
- [ ] Testing & Integration
- [ ] Documentation & Demo

## 👥 Team

**HyperHawks** - SMVIT 2026

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a hackathon project. For any questions or collaboration, please open an issue.

## 📞 Support

For technical issues or questions about Module 2 (Data Pipeline), see the [Module 2 README](./MODULE2_README.md).

## 🔧 AI Inference Configuration

### Sensor Data Modes

The AI inference service supports two modes for reading sensor data:

#### 1. Simulation Mode (Default)
Perfect for testing without physical hardware. Edit `api/data/simulation_sensors.csv` to simulate different conditions:

```csv
timestamp,sensor_type,value
2026-01-27 12:00:00,temperature,28.5
2026-01-27 12:00:00,humidity,45.0
2026-01-27 12:00:00,ldr,3500
2026-01-27 12:00:00,current,1.2
2026-01-27 12:00:00,voltage,230.0
```

**LDR Values:**
- High (3000+) = Daytime / High solar availability
- Low (<500) = Nighttime / No solar

#### 2. Real Hardware Mode
When you connect physical sensors, switch to real mode:

```python
# In api/data_pipeline/services/ai_inference.py
USE_SIMULATION_FILE = False  # Change to False
```

The system will automatically read from your database populated by MQTT sensors.

### Dynamic User Preferences

Control AI behavior through user preferences:

```python
# Set cost priority (0-100)
UserPreferences.objects.create(
    preference_key='cost_priority',
    preference_value=70  # 70% cost focus, 30% carbon focus
)
```

The AI will automatically fetch and apply these weights before each optimization.

### API Endpoints

#### Forecast Energy Demand
```bash
GET /api/predictions/forecast/?hours=6
```

#### Get Source Recommendation
```bash
POST /api/predictions/recommend_source/
{
    "load_name": "HVAC Living Room",
    "load_priority": 75,
    "load_power": 2000
}
```

#### Make Comprehensive Decision
```bash
POST /api/predictions/decide/
```

This endpoint:
- Forecasts energy demand
- Optimizes source allocation
- Publishes decision to MQTT (`HyperVolt/commands/control`)

#### Retrain AI Model
```bash
POST /api/predictions/retrain/
```

Exports recent data from database, retrains the model, and reloads it into memory.

### MQTT Integration

The AI service publishes decisions to MQTT for hardware actuation:

**Topic:** `HyperVolt/commands/control`

**Payload:**
```json
{
    "command": "switch_source",
    "source": "solar",
    "details": {
        "predicted_demand_kwh": 1.5,
        "source_allocation": [["solar", 1.0], ["battery", 0.5]],
        "cost": 3.5,
        "carbon": 250.0
    },
    "timestamp": "2026-01-27T12:00:00Z"
}
```

Your hardware (ESP32/Raspberry Pi) should subscribe to this topic and execute the physical switch.

### Testing the AI Service

1. **Check AI Status:**
```bash
GET /api/predictions/status/
```

2. **Test with Simulation Data:**
```bash
# Edit api/data/simulation_sensors.csv
# Change ldr to 4000 (daytime)
GET /api/predictions/forecast/

# Expected: Recommends solar power
```

3. **Test Night Scenario:**
```bash
# Change ldr to 100 (nighttime)
GET /api/predictions/forecast/

# Expected: Recommends grid/battery
```

4. **Switch to Real Sensors:**
```python
# Set USE_SIMULATION_FILE = False
# Restart Django server
# AI will now read from SensorReading database table
```

---

**Built with ❤️ for Sustainergy Hackathon 2026**
