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

## 🚀 Quick Start - How to Run

### Prerequisites
- Python 3.11+ (3.11 or 3.12)
- Node.js 18+ (for frontend)
- Redis (optional - for caching)

### Step 1: Clone and Setup Backend

```bash
# Clone the repository
git clone https://github.com/ArYaNsAiNi-here/HyperVolt.git
cd HyperVolt

# Install Python dependencies
cd api
pip install django djangorestframework django-environ django-cors-headers daphne channels channels-redis django-q2 django-redis pandas

# Run database migrations
python manage.py migrate

# (Optional) Add sample sensor data to database
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hypervolt_backend.settings')
import django
django.setup()
from data_pipeline.models import SensorReading, GridData, EnergySource

# Sample sensor readings
sensors = [
    ('temperature', 'esp32_001', 28.5, 'celsius'),
    ('humidity', 'esp32_001', 45.0, 'percent'),
    ('ldr', 'esp32_001', 3200, 'raw'),
    ('current', 'esp32_001', 1.5, 'amperes'),
    ('voltage', 'esp32_001', 228, 'volts'),
]
for sensor_type, sensor_id, value, unit in sensors:
    SensorReading.objects.create(sensor_type=sensor_type, sensor_id=sensor_id, value=value, unit=unit)
    print(f'Created {sensor_type}: {value}')

# Energy sources
for source_type, capacity, priority in [('solar', 3000, 3), ('battery', 10000, 2), ('grid', 10000, 1)]:
    EnergySource.objects.get_or_create(source_type=source_type, defaults={'capacity': capacity, 'priority': priority, 'is_available': True})
print('Database populated!')
"

# Start Django backend (Terminal 1)
python manage.py runserver 0.0.0.0:8000
```

### Step 2: Setup and Run Frontend

```bash
# Open new terminal, navigate to website folder
cd website

# Install dependencies
npm install --legacy-peer-deps

# Start development server (Terminal 2)
npm run dev
```

### Step 3: Access the Dashboard

Open your browser and go to:
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/

### Quick API Testing

```bash
# Test AI Status
curl http://localhost:8000/api/ai/status/

# Get sensor data from database
curl http://localhost:8000/api/sensor-readings/all_latest/

# Make AI decision (saves to database)
curl -X POST http://localhost:8000/api/ai/decide/

# Get AI decision history
curl http://localhost:8000/api/ai-decisions/history/?limit=5

# Get energy forecast
curl http://localhost:8000/api/ai/forecast/?hours=6
```

### What You'll See

1. **Dashboard Header**: Shows AI status and DB connection status
2. **Current Energy Source**: Displays which source (Solar/Battery/Grid) the AI recommends
3. **Sensor Data**: Temperature, humidity, LDR, current, voltage from database
4. **Energy Flow Visualization**: 3D representation of energy routing
5. **AI Decision History**: Past decisions saved in database
6. **Energy Forecast Chart**: Predicted demand for next hours

---

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

## 🔧 AI Configuration

### Data Source
The AI reads sensor data directly from the database:
- Sensor readings from `SensorReading` table
- Carbon intensity from `GridData` table
- AI decisions are saved to `AIDecision` table

### Adding Sensor Data

You can add sensor data via:

1. **Django Admin**: http://localhost:8000/admin/
2. **REST API**:
```bash
curl -X POST http://localhost:8000/api/sensor-readings/ \
  -H "Content-Type: application/json" \
  -d '{"sensor_type": "temperature", "sensor_id": "esp32_001", "value": 28.5, "unit": "celsius"}'
```
3. **Hardware (ESP32/Raspberry Pi)**: Send data via MQTT to topic `HyperVolt/sensors/{location}/{sensor_type}`

### API Endpoints

#### AI Endpoints
```bash
GET  /api/ai/status/          # Check AI service status
GET  /api/ai/forecast/        # Get energy demand forecast
POST /api/ai/decide/          # Make AI decision (saves to DB)
GET  /api/ai/conditions/      # Get current conditions
```

#### Data Endpoints
```bash
GET  /api/sensor-readings/all_latest/  # All sensors as one object
GET  /api/ai-decisions/history/        # AI decision history
GET  /api/ai-decisions/latest/         # Most recent decision
GET  /api/energy-sources/available/    # Available power sources
```

---

**Built with ❤️ for Sustainergy Hackathon 2026**
