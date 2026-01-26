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

### Module 3: The Prophet (AI Inference Engine)
*Coming Soon*
- LSTM network for demand forecasting
- Power source selection algorithm
- Real-time decision-making based on context

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

---

**Built with ❤️ for Sustainergy Hackathon 2026**
