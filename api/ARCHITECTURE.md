# HyperVolt Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HyperVolt System                              │
│                  AI-Driven Energy Orchestrator                       │
└─────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │ Raspberry Pi │
                              │   Sensors    │
                              └──────┬───────┘
                                     │
                     ┌───────────────┼───────────────┐
                     │               │               │
              ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
              │     LDR     │ │   Current   │ │Temperature │
              │   Sensor    │ │   Sensor    │ │   Sensor   │
              └─────────────┘ └─────────────┘ └────────────┘
                     │               │               │
                     └───────────────┼───────────────┘
                                     │ MQTT Protocol
                                     │
                              ┌──────▼───────┐
                              │   Mosquitto  │
                              │ MQTT Broker  │
                              └──────┬───────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                   Module 2: Data Pipeline                │
        │                                                           │
        │  ┌────────────────┐              ┌────────────────┐     │
        │  │ MQTT Listener  │              │  Django REST   │     │
        │  │  (Management   │              │      API       │     │
        │  │   Command)     │              │  (Endpoints)   │     │
        │  └───────┬────────┘              └────────┬───────┘     │
        │          │                                │              │
        │          │                                │              │
        │    ┌─────▼─────┐                   ┌─────▼──────┐      │
        │    │           │                   │            │      │
        │    │  Hot Path │                   │ Cold Path  │      │
        │    │  (Redis   │                   │(PostgreSQL)│      │
        │    │   Cache)  │                   │            │      │
        │    │           │                   │            │      │
        │    │ Sliding   │                   │ Historical │      │
        │    │ Window:   │                   │   Data     │      │
        │    │ Last 60   │                   │  Storage   │      │
        │    │ Readings  │                   │            │      │
        │    │           │                   │            │      │
        │    └─────┬─────┘                   └─────┬──────┘      │
        │          │                               │              │
        │          │         ┌─────────────┐       │              │
        │          │         │  External   │       │              │
        │          │         │    APIs     │       │              │
        │          │         │             │       │              │
        │          │         │ • Carbon    │───────┘              │
        │          │         │   Intensity │                      │
        │          │         │ • Weather   │                      │
        │          │         │             │                      │
        │          │         │ (Scheduled  │                      │
        │          │         │   Tasks)    │                      │
        │          │         └─────────────┘                      │
        │          │                                               │
        │          │                                               │
        │    ┌─────▼──────────────────────────────────┐           │
        │    │         WebSocket Broadcast            │           │
        │    │       (Django Channels)                │           │
        │    │                                         │           │
        │    │  • Real-time sensor updates            │           │
        │    │  • Group messaging                     │           │
        │    │  • Redis channel layer                 │           │
        │    └─────┬──────────────────────────────────┘           │
        │          │                                               │
        └──────────┼───────────────────────────────────────────────┘
                   │
                   │ WebSocket (ws://)
                   │
        ┌──────────▼──────────────────────────┐
        │     Module 4: Frontend              │
        │                                      │
        │  ┌────────────────────────────┐     │
        │  │    Next.js Dashboard       │     │
        │  │                            │     │
        │  │  • 3D Digital Twin         │     │
        │  │    (Three.js)              │     │
        │  │                            │     │
        │  │  • Real-time Graphs        │     │
        │  │    (Recharts)              │     │
        │  │                            │     │
        │  │  • User Controls           │     │
        │  │    (Threshold Sliders)     │     │
        │  │                            │     │
        │  │  • Carbon Savings          │     │
        │  │    Counter                 │     │
        │  └────────────────────────────┘     │
        │                                      │
        └──────────────────────────────────────┘

        ┌──────────────────────────────────────┐
        │    Module 3: AI Inference Engine     │
        │                                      │
        │  ┌────────────────────────────┐     │
        │  │   LSTM Neural Network      │     │
        │  │                            │     │
        │  │  • Demand Forecasting      │     │
        │  │  • Load Prediction         │     │
        │  └────────────────────────────┘     │
        │                                      │
        │  ┌────────────────────────────┐     │
        │  │  Decision Engine           │     │
        │  │                            │     │
        │  │  • Power Source Selection  │     │
        │  │  • Light Dimming Logic     │     │
        │  │  • Load Shifting           │     │
        │  └────────────────────────────┘     │
        │                                      │
        │  Reads from Hot Path ───────────────┘
        │  Writes to Cold Path
        └──────────────────────────────────────┘
```

## Data Flow

### Sensor Data Flow (Real-time)

```
1. Raspberry Pi Sensor
      ↓
2. MQTT Publish (HyperVolt/sensors/...)
      ↓
3. Mosquitto Broker
      ↓
4. MQTT Listener (Django Command)
      ↓
   ┌──┴──┐
   ↓     ↓
5. Cold Path         6. Hot Path
   (PostgreSQL)         (Redis)
   - Historical         - Last 60 readings
   - Analytics          - AI Inference
      ↓                     ↓
   Archive          7. WebSocket Broadcast
                          ↓
                    8. Frontend Update
                       (3D Model + Graphs)
```

### AI Decision Flow

```
1. Scheduled Trigger (every 10s)
      ↓
2. Read Hot Path (Redis)
   - Last 60 sensor readings
      ↓
3. Read Context Data
   - Carbon intensity
   - Weather
   - User preferences
      ↓
4. AI Inference
   - LSTM prediction
   - Decision algorithm
      ↓
5. Store Decision
   - AIDecision model
      ↓
6. Execute Action
   - MQTT command to Pi
   - Update frontend
```

### External API Flow

```
1. Scheduled Task (every 15 min)
      ↓
2. Fetch from External APIs
   - Electricity Maps (carbon)
   - OpenWeatherMap (weather)
      ↓
3. Store in GridData model
      ↓
4. Available for AI context
```

## Component Details

### Module 2: Data Pipeline (✅ Complete)

**Technology Stack:**
- Django 5.0
- Django REST Framework
- Django Channels 4.0
- PostgreSQL / SQLite
- Redis
- MQTT (Paho)

**Key Features:**
- MQTT listener for sensor ingestion
- Dual-path architecture (Hot + Cold)
- REST API with custom actions
- WebSocket real-time streaming
- External API integration
- Scheduled task system

**API Endpoints:**
- `/api/sensor-readings/`
- `/api/grid-data/`
- `/api/preferences/`
- `/api/ai-decisions/`
- `/api/energy-sources/`

**WebSocket:**
- `ws://localhost:8000/ws/sensors/`

### Module 3: AI Engine (🚧 Planned)

**Technology Stack:**
- TensorFlow / Scikit-learn
- Python
- NumPy / Pandas

**Components:**
- LSTM for time-series prediction
- Random Forest for classification
- Optimization algorithms
- Online learning support

### Module 4: Frontend (🚧 Planned)

**Technology Stack:**
- Next.js
- React
- Three.js / React Three Fiber
- Recharts
- WebSocket client

**Features:**
- 3D digital twin visualization
- Real-time data graphs
- User preference controls
- Carbon savings dashboard

### Module 1: Hardware (🚧 Planned)

**Components:**
- Raspberry Pi 5 (8GB)
- LDR sensor
- Current sensor (ACS712)
- DHT22 (temp/humidity)
- Relay modules

**Software:**
- Python sensor reading scripts
- MQTT publisher
- GPIO control

## Communication Protocols

### MQTT Messages

**Sensor Data (Pi → Backend):**
```json
{
  "sensor_type": "ldr",
  "sensor_id": "ldr_1",
  "value": 750,
  "unit": "lux",
  "location": "living_room",
  "timestamp": "2026-01-26T08:00:00Z"
}
```

**Commands (Backend → Pi):**
```json
{
  "command": "set_brightness",
  "value": 75,
  "timestamp": "2026-01-26T08:00:00Z"
}
```

### WebSocket Messages

**Sensor Update (Backend → Frontend):**
```json
{
  "type": "sensor_update",
  "data": {
    "sensor_type": "ldr",
    "sensor_id": "ldr_1",
    "value": 750,
    "unit": "lux",
    "location": "living_room",
    "timestamp": "2026-01-26T08:00:00Z"
  }
}
```

## Deployment Architecture

### Development

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    Redis     │  │  Mosquitto   │  │  PostgreSQL  │
│ localhost:   │  │ localhost:   │  │ localhost:   │
│    6379      │  │    1883      │  │    5432      │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                  │
        └────────────────┼──────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Django (Daphne)   │
              │   localhost:8000    │
              └─────────────────────┘
```

### Production (Future)

```
┌──────────────────────────────────────────┐
│           Load Balancer                   │
└───────────┬──────────────────────────────┘
            │
    ┌───────┼───────┐
    │       │       │
┌───▼───┐ ┌─▼─────┐ ┌──▼────┐
│Django │ │Django │ │Django │
│  #1   │ │  #2   │ │  #3   │
└───┬───┘ └───┬───┘ └───┬───┘
    │         │         │
    └─────────┼─────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼────┐ ┌──▼──────┐ ┌──▼────┐
│ Redis  │ │PostgreSQL│ │ MQTT  │
│Cluster │ │  Master  │ │Cluster│
└────────┘ └──────────┘ └───────┘
```

## Security Architecture

```
┌──────────────────────────────────────┐
│         Security Layers               │
├──────────────────────────────────────┤
│                                       │
│  1. Network Level                     │
│     • Firewall rules                  │
│     • VPC isolation                   │
│     • TLS/SSL encryption              │
│                                       │
│  2. Application Level                 │
│     • CORS configuration              │
│     • ALLOWED_HOSTS validation        │
│     • Input sanitization              │
│     • Rate limiting (TODO)            │
│                                       │
│  3. Authentication (TODO)             │
│     • JWT tokens                      │
│     • OAuth2                          │
│     • API keys                        │
│                                       │
│  4. Data Level                        │
│     • Environment variables           │
│     • Encrypted secrets               │
│     • Database encryption             │
│                                       │
└──────────────────────────────────────┘
```

## Monitoring & Observability (Future)

```
┌──────────────────────────────────────┐
│         Monitoring Stack              │
├──────────────────────────────────────┤
│                                       │
│  Application Metrics                  │
│  ├── Prometheus                       │
│  └── Grafana Dashboards              │
│                                       │
│  Logging                              │
│  ├── ELK Stack                        │
│  └── Centralized logs                 │
│                                       │
│  Error Tracking                       │
│  └── Sentry                           │
│                                       │
│  Performance                          │
│  ├── APM (New Relic / Datadog)       │
│  └── Query monitoring                 │
│                                       │
└──────────────────────────────────────┘
```

## Status

- ✅ **Module 2**: Complete and validated
- 🚧 **Module 3**: Not started
- 🚧 **Module 4**: Not started
- 🚧 **Module 1**: Not started

---

**Last Updated**: January 26, 2026  
**Version**: 1.0  
**Status**: Module 2 Complete
