# HyperVolt Simulation Guidelines

## Complete Guide to Running and Interconnecting All Modules

This document provides comprehensive instructions for running HyperVolt simulations and interconnecting all four modules of the system.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Module Descriptions](#module-descriptions)
5. [Quick Start - Simulation Without Sensors](#quick-start---simulation-without-sensors)
6. [Full Setup - Simulation With Real Sensors](#full-setup---simulation-with-real-sensors)
7. [Module Interconnection Guide](#module-interconnection-guide)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

---

## Overview

HyperVolt is an AI-Driven Energy Orchestrator that consists of four interconnected modules:

| Module | Name | Technology | Purpose |
|--------|------|------------|---------|
| 1 | Sentinel | Raspberry Pi + Sensors | Hardware data collection |
| 2 | Data Pipeline | Django + Redis | Backend API & real-time streaming |
| 3 | Prophet | TensorFlow + Scikit-learn | AI inference & decision making |
| 4 | Orchestrator | Next.js + Three.js | Frontend visualization |

The system supports two simulation modes:
1. **Without Sensors**: Uses synthetic data to demonstrate the system (Modules 2, 3, 4)
2. **With Sensors**: Uses real hardware sensors for full integration (All 4 Modules)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HyperVolt System                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐                                                   │
│  │    MODULE 1      │                                                   │
│  │   The Sentinel   │──────────┐                                        │
│  │  (Raspberry Pi)  │          │ MQTT                                   │
│  │  - LDR Sensor    │          │ (HyperVolt/sensors/#)                  │
│  │  - Current Sensor│          ▼                                        │
│  │  - DHT22         │    ┌───────────────────────────────────────┐     │
│  └──────────────────┘    │           MODULE 2                     │     │
│          OR              │       The Data Pipeline                │     │
│  ┌──────────────────┐    │       (Django Backend)                 │     │
│  │ Synthetic Data   │───▶│  ┌─────────┐  ┌─────────┐             │     │
│  │ Generator        │    │  │  MQTT   │  │  REST   │             │     │
│  │ (Simulation)     │    │  │Listener │  │  API    │             │     │
│  └──────────────────┘    │  └────┬────┘  └────┬────┘             │     │
│                          │       │            │                   │     │
│                          │       ▼            ▼                   │     │
│                          │  ┌─────────┐  ┌─────────┐             │     │
│                          │  │  Redis  │  │PostgreSQL│             │     │
│                          │  │(Hot Path│  │(Cold Path│             │     │
│                          │  └────┬────┘  └─────────┘             │     │
│                          └───────┼───────────────────────────────┘     │
│                                  │                                      │
│                                  │ API Calls                            │
│                                  ▼                                      │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │                        MODULE 3                                │     │
│  │                      The Prophet (AI)                          │     │
│  │                                                                │     │
│  │  ┌─────────────────┐  ┌────────────────┐  ┌──────────────┐   │     │
│  │  │ Demand Forecast │  │ Source         │  │ Decision     │   │     │
│  │  │ (LSTM Model)    │  │ Optimizer      │  │ Engine       │   │     │
│  │  └─────────────────┘  └────────────────┘  └──────────────┘   │     │
│  │                                                                │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                  │                                      │
│                                  │ WebSocket                            │
│                                  ▼ (ws://localhost:8000/ws/sensors/)    │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │                        MODULE 4                                │     │
│  │                   The Orchestrator (Frontend)                  │     │
│  │                                                                │     │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  │     │
│  │  │ 3D Digital│  │ Energy    │  │ Charts &  │  │ AI Log    │  │     │
│  │  │ Twin      │  │ Flow      │  │ Stats     │  │ Narrator  │  │     │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘  │     │
│  │                                                                │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Software Requirements

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| Python | 3.12+ | Backend & AI | `apt install python3` |
| Node.js | 18+ | Frontend | `nvm install 18` |
| Redis | 7+ | Hot path cache | `apt install redis-server` |
| PostgreSQL | 15+ (optional) | Cold path storage | `apt install postgresql` |
| Mosquitto | 2.0+ | MQTT broker | `apt install mosquitto` |

### Python Dependencies

```bash
# From repository root
pip install -r requirements.txt
```

### Node.js Dependencies

```bash
# From website directory
cd website
npm install
```

---

## Module Descriptions

### Module 1: The Sentinel (Hardware)

**Purpose**: Collects sensor data from the physical environment.

**Hardware Components**:
- Raspberry Pi 5 (8GB recommended)
- LDR (Light Dependent Resistor) - Measures ambient light
- ACS712 Current Sensor - Measures power consumption
- DHT22 - Temperature and humidity sensor

**MQTT Topics Published**:
- `HyperVolt/sensors/{location}/ldr`
- `HyperVolt/sensors/{location}/temperature`
- `HyperVolt/sensors/{location}/humidity`
- `HyperVolt/sensors/{location}/current`

### Module 2: The Data Pipeline (Backend)

**Purpose**: Manages data flow, API endpoints, and real-time streaming.

**Key Features**:
- REST API for all data operations
- MQTT listener for sensor data
- WebSocket streaming via Django Channels
- Hot path (Redis) for real-time data
- Cold path (PostgreSQL) for historical data

**API Endpoints**:
- `GET /api/sensor-readings/` - Sensor data
- `GET /api/grid-data/` - Carbon intensity and weather
- `POST /api/predictions/decide/` - AI decision
- `GET /api/predictions/forecast/` - Energy forecast

### Module 3: The Prophet (AI)

**Purpose**: Makes intelligent energy management decisions.

**Models**:
- **Demand Forecaster**: LSTM network for 6-hour demand prediction
- **Source Optimizer**: Selects optimal power source (Solar/Battery/Grid)
- **Load Manager**: Manages load shedding for carbon optimization

**Key Files**:
- `ai/module3-ai/train_demand_model.py` - Model training
- `ai/module3-ai/optimize_sources.py` - Source optimization
- `ai/module3-ai/decision_engine.py` - Decision making

### Module 4: The Orchestrator (Frontend)

**Purpose**: Visualizes the system in real-time.

**Features**:
- 3D Digital Twin (Room visualization)
- Energy Flow Diagram (Power routing)
- AI Strategy Narrator (Decision logs)
- Real-time Charts (Forecast vs actual)
- Brightness Control (User preferences)

---

## Quick Start - Simulation Without Sensors

This mode runs a simulation using synthetic data, demonstrating the full system **without physical hardware** (Modules 2, 3, 4 only).

### Step 1: Start Required Services

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start MQTT Broker (optional for this mode)
mosquitto -v
```

### Step 2: Start the Backend (Module 2)

```bash
# Terminal 3: Start Django with WebSocket support
cd api
python manage.py migrate  # First time only
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

### Step 3: Start the Frontend (Module 4)

```bash
# Terminal 4: Start Next.js development server
cd website
npm run dev
```

### Step 4: Run the Simulation

```bash
# Terminal 5: Run simulation script
python scripts/run_simulation_without_sensors.py
```

### Step 5: View the Dashboard

Open your browser to: **http://localhost:3000**

You should see:
- 3D room model with changing light levels
- Energy flow diagram showing power routing
- AI decision logs in the Strategy Narrator
- Real-time charts with forecast data

### Simulation Options

```bash
# Run for 30 minutes with 10-second intervals
python scripts/run_simulation_without_sensors.py --duration 30 --interval 10

# Start simulation at 6 AM (to see morning patterns)
python scripts/run_simulation_without_sensors.py --start-hour 6

# Accelerated mode (1 second = 1 simulated minute)
python scripts/run_simulation_without_sensors.py --accelerated

# Disable AI decisions (data only)
python scripts/run_simulation_without_sensors.py --no-ai
```

---

## Full Setup - Simulation With Real Sensors

This mode uses **real hardware sensors** connected via MQTT (All 4 Modules).

### Step 1: Hardware Setup (Module 1)

#### Raspberry Pi Wiring

| Sensor | Raspberry Pi Pin | Notes |
|--------|------------------|-------|
| LDR + 10kΩ resistor | GPIO + ADC (MCP3008) | Voltage divider |
| ACS712 OUT | ADC Channel 1 | 5V tolerant ADC needed |
| DHT22 DATA | GPIO 4 | 10kΩ pull-up resistor |
| DHT22 VCC | 3.3V | - |
| DHT22 GND | GND | - |

#### Raspberry Pi Code

Create a file `sensor_publisher.py` on your Raspberry Pi:

```python
import time
import json
import paho.mqtt.client as mqtt
import Adafruit_DHT
import Adafruit_MCP3008

# Configuration
# SECURITY NOTE: Replace with your computer's IP address
# For production, use authentication and TLS encryption
MQTT_BROKER = "YOUR_LAPTOP_IP"  # Replace with your computer's IP
MQTT_PORT = 1883
LOCATION = "living_room"

# Initialize sensors
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
mcp = Adafruit_MCP3008.MCP3008(clk=11, cs=8, miso=9, mosi=10)

# MQTT client
client = mqtt.Client()
# For secured MQTT, uncomment and configure:
# client.username_pw_set("username", "password")
# client.tls_set()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

def publish_reading(sensor_type, value, unit):
    topic = f"HyperVolt/sensors/{LOCATION}/{sensor_type}"
    payload = {
        "sensor_type": sensor_type,
        "sensor_id": f"{sensor_type}_1",
        "value": value,
        "unit": unit,
        "location": LOCATION,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    client.publish(topic, json.dumps(payload))
    print(f"Published: {sensor_type} = {value}")

while True:
    # Read DHT22
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        publish_reading("temperature", round(temperature, 1), "celsius")
        publish_reading("humidity", round(humidity, 1), "percent")
    
    # Read LDR (assuming channel 0)
    ldr_value = mcp.read_adc(0)
    publish_reading("ldr", ldr_value, "raw")
    
    # Read Current Sensor (assuming channel 1)
    current_raw = mcp.read_adc(1)
    current_amps = (current_raw - 512) * 0.0264  # Calibration formula
    publish_reading("current", round(current_amps, 2), "amperes")
    
    time.sleep(2)  # Publish every 2 seconds
```

### Step 2: Start Services on Your Computer

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: MQTT Broker (allow external connections)
mosquitto -c /etc/mosquitto/mosquitto.conf -v

# Terminal 3: Django Backend
# NOTE: Using 0.0.0.0 allows connections from Raspberry Pi on local network
# For local-only development, use 127.0.0.1 instead
cd api
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application

# Terminal 4: Frontend
cd website
npm run dev
```

> ⚠️ **Security Note**: Binding to `0.0.0.0` exposes the server to your entire network.
> For production deployments, use a reverse proxy (nginx) with proper authentication.

### Step 3: Start Sensor Publisher on Raspberry Pi

```bash
# On Raspberry Pi
python3 sensor_publisher.py
```

### Step 4: Run the Simulation with Real Sensors

```bash
# Terminal 5: On your computer
python scripts/run_simulation_with_sensors.py --mqtt-host localhost
```

### Step 5: View the Dashboard

Open your browser to: **http://localhost:3000**

You should see real sensor data flowing through the system!

---

## Module Interconnection Guide

### Data Flow Overview

```
Hardware Sensors → MQTT → Django Backend → Redis Cache → AI Inference
                                              ↓
WebSocket ← Django Channels ← AI Decision ← Source Optimizer
    ↓
Frontend Dashboard
```

### 1. Module 1 ↔ Module 2 (Sensors to Backend)

**Protocol**: MQTT  
**Topic Format**: `HyperVolt/sensors/{location}/{sensor_type}`

**Setup**:
```bash
# Start MQTT listener in Django
cd api
python manage.py mqtt_listener
```

**Payload Format**:
```json
{
  "sensor_type": "ldr",
  "sensor_id": "ldr_1",
  "value": 2500,
  "unit": "raw",
  "location": "living_room",
  "timestamp": "2026-01-28T12:00:00Z"
}
```

### 2. Module 2 ↔ Module 3 (Backend to AI)

**Protocol**: Internal Python calls  
**Integration Point**: `api/data_pipeline/services/ai_inference.py`

**Key Configuration**:
```python
# In ai_inference.py
USE_SIMULATION_FILE = True   # Use synthetic data
USE_SIMULATION_FILE = False  # Use real sensor data from DB
```

**API Endpoints**:
```bash
# Get AI status
GET /api/ai/status/

# Get energy forecast
GET /api/predictions/forecast/?hours=6

# Make AI decision
POST /api/predictions/decide/

# Trigger model retraining
POST /api/predictions/retrain/
```

### 3. Module 2 ↔ Module 4 (Backend to Frontend)

**Protocol**: WebSocket + REST API

**WebSocket URL**: `ws://localhost:8000/ws/sensors/`

**Message Format**:
```json
{
  "type": "sensor_update",
  "data": {
    "sensor_type": "ldr",
    "value": 2500,
    "location": "living_room"
  }
}
```

**REST Endpoints Used by Frontend**:
```bash
GET /api/sensor-readings/latest/
GET /api/energy-sources/available/
GET /api/grid-data/carbon_intensity/
GET /api/ai/forecast/?hours=6
POST /api/ai/decide/
PATCH /api/preferences/{key}/
```

### 4. AI Commands to Hardware (Module 3 → Module 1)

**Protocol**: MQTT  
**Topic**: `HyperVolt/commands/control`

**Payload Format**:
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
  "timestamp": "2026-01-28T12:00:00Z"
}
```

---

## Troubleshooting

### Common Issues

#### 1. "API is not available"

**Cause**: Django backend not running or wrong port.

**Solution**:
```bash
cd api
python manage.py runserver
# or with WebSockets:
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

#### 2. "MQTT broker not available"

**Cause**: Mosquitto not running.

**Solution**:
```bash
# Start Mosquitto
mosquitto -v

# Or as a service
sudo systemctl start mosquitto
```

#### 3. "AI models not available"

**Cause**: Pre-trained models not found.

**Solution**:
```bash
# Train models
cd ai/module3-ai
python train_demand_model.py
python decision_engine.py
```

#### 4. WebSocket connection failed

**Cause**: Using `runserver` instead of `daphne`.

**Solution**:
```bash
# Use daphne for WebSocket support
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

#### 5. No sensor data appearing on frontend

**Cause**: MQTT listener not running or wrong topics.

**Solution**:
```bash
# Check MQTT messages
mosquitto_sub -t "HyperVolt/#" -v

# Start MQTT listener
cd api
python manage.py mqtt_listener
```

#### 6. Redis connection refused

**Cause**: Redis server not running.

**Solution**:
```bash
# Start Redis
redis-server

# Test connection
redis-cli ping
# Should return: PONG
```

### Debug Mode

Enable debug logging:

```bash
# Django debug
export DEBUG=true

# Verbose simulation
python scripts/run_simulation_without_sensors.py --duration 5 --interval 2
```

---

## Advanced Configuration

### Environment Variables

Create a `.env` file in the `api` directory:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/hypervolt

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883

# External APIs
ELECTRICITY_MAPS_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here

# Location
LOCATION_LAT=12.9716
LOCATION_LON=77.5946
LOCATION_ZONE=IN-KA

# AI Settings
AI_MODEL_PATH=../ai/models
USE_SIMULATION_FILE=true
```

> ⚠️ **Security Warning**: 
> - Never commit your `.env` file to version control
> - Replace placeholder API keys with your actual keys
> - Use strong, unique passwords for database connections
> - Rotate API keys regularly

### Custom AI Weights

Adjust AI optimization priorities:

```python
# In Django admin or via API
# Set cost priority (0-100)
# Higher = prioritize cost savings
# Lower = prioritize carbon reduction

POST /api/preferences/
{
    "preference_key": "cost_priority",
    "preference_value": 70
}
```

### Model Retraining

Retrain AI models with new data:

```bash
# Via API
curl -X POST http://localhost:8000/api/predictions/retrain/

# Or manually
cd ai/module3-ai
python train_demand_model.py
```

### Adding New Sensors

1. Update hardware to publish to new topic:
   ```
   HyperVolt/sensors/{location}/{new_sensor_type}
   ```

2. Update `ai_inference.py` to process new sensor:
   ```python
   column_map = {
       'temperature': 'temperature',
       'new_sensor': 'new_feature_name',
   }
   ```

3. Retrain models with new data.

---

## Summary Commands

### Quick Reference

```bash
# ===== Start All Services =====
# Terminal 1: Redis
redis-server

# Terminal 2: MQTT
mosquitto -v

# Terminal 3: Backend (use 127.0.0.1 for local-only access)
cd api && daphne -b 127.0.0.1 -p 8000 hypervolt_backend.asgi:application

# Terminal 4: Frontend
cd website && npm run dev

# Terminal 5A: Simulation WITHOUT sensors
python scripts/run_simulation_without_sensors.py

# Terminal 5B: Simulation WITH sensors
python scripts/run_simulation_with_sensors.py

# ===== View Dashboard =====
# Open browser: http://localhost:3000
```

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the module-specific READMEs:
   - `api/MODULE2_README.md` - Backend details
   - `ai/MODULE3_SUMMARY.md` - AI module details
   - `website/README.md` - Frontend details
3. Open an issue on GitHub

---

**Built with ❤️ by HyperHawks Team for SMVIT Sustainergy Hackathon 2026**
