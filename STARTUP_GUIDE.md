# HyperVolt System Startup Guide

This guide explains how to run all 4 modules of the HyperVolt energy management system in sync on a Windows machine with local development setup.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            HyperVolt Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐         MQTT           ┌──────────────────────────┐      │
│   │   Module 1   │  ──────────────────►   │        Module 2          │      │
│   │   Hardware   │   solar/data           │        Backend           │      │
│   │   (ESP32)    │   battery/data         │     (Django API)         │      │
│   │              │                        │   localhost:8000         │      │
│   └──────────────┘                        └───────────┬──────────────┘      │
│         │                                             │                      │
│         │                                    ┌────────┴────────┐             │
│         │                                    │                 │             │
│         │                           ┌────────▼───────┐  ┌──────▼─────────┐   │
│         │                           │    Module 3    │  │   Memurai      │   │
│         │                           │      AI        │  │   (Redis)      │   │
│         │                           │ Decision Engine│  │ localhost:6379 │   │
│         │                           └────────┬───────┘  └──────┬─────────┘   │
│         │                                    │                 │             │
│         │                                    └────────┬────────┘             │
│         │                                             │                      │
│         │                                    ┌────────▼───────┐              │
│         │                                    │    Module 4    │              │
│         └──────────── MQTT Commands ◄────────│    Website     │              │
│                                              │   (Next.js)    │              │
│                                              │ localhost:3000 │              │
│                                              └────────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

Before starting, ensure you have the following installed:

1. **Python 3.10+** - For API and AI modules
2. **Node.js 18+** - For the website
3. **Memurai** (Windows Redis alternative) - For WebSocket channel layer
4. **Mosquitto MQTT Broker** - For hardware communication

### Windows-Specific Setup

#### 1. Install Memurai (Redis for Windows)
Download and install from: https://www.memurai.com/
- Memurai runs as a Windows service on port 6379
- Alternatively, use Docker: `docker run -p 6379:6379 redis`

#### 2. Install Mosquitto MQTT Broker
Download from: https://mosquitto.org/download/
- Run as a service or start manually: `mosquitto -v`

## Module Startup Order

Start the modules in this specific order:

### Step 1: Start Memurai (Redis)
```powershell
# Memurai usually starts automatically as a Windows service
# Check if running:
net start memurai

# Or start manually if not a service:
memurai-server.exe
```

### Step 2: Start MQTT Broker (Mosquitto)
```powershell
# Start Mosquitto broker (without config file for basic setup)
mosquitto -v

# Or with a config file if you have one:
# mosquitto -v -c path/to/mosquitto.conf
```

### Step 3: Start Module 2 - Backend API
```powershell
# Navigate to the API directory
cd api

# Create and activate virtual environment (first time only)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Copy environment file (first time only)
copy .env.example .env
# Edit .env file with your settings

# Run database migrations (first time only)
python manage.py migrate

# Start the Django server with Daphne (for WebSocket support)
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

**Note:** You must use `daphne` (not `python manage.py runserver`) to enable WebSocket support.

### Step 4: Start Module 4 - Website
```powershell
# Navigate to the website directory
cd website

# Install dependencies (first time only)
npm install

# Copy environment file (first time only)
copy .env.example .env.local

# Start the development server
npm run dev
```

The website will be available at: http://localhost:3000

### Step 5: Start Module 3 - AI (Optional, Integrated)
Module 3 (AI) is integrated into the API and starts automatically. However, you can also run the live bridge for standalone AI:

```powershell
# Navigate to AI directory
cd ai

# Activate virtual environment
.\venv\Scripts\activate

# Run the live bridge
python live_bridge.py
```

### Step 6: Connect Hardware (ESP32)
Your ESP32 should publish sensor data to MQTT topics:
- Topic format: `solar/data`, `battery/data`, etc.
- Payload format (JSON):
```json
{
  "sensor_type": "current",
  "sensor_id": "curr_1",
  "value": 0.0,
  "unit": "mA",
  "location": "solar_array",
  "timestamp": "13:01:03"
}
```

## Quick Start Script

Create a `start_hypervolt.bat` file in the root directory:

```batch
@echo off
echo Starting HyperVolt System...

:: Start Memurai if not running
echo Checking Memurai...
sc query memurai | find "RUNNING" >nul
if errorlevel 1 (
    echo Starting Memurai...
    net start memurai
)

:: Start Mosquitto in a new window
echo Starting Mosquitto MQTT Broker...
start "Mosquitto" cmd /k "mosquitto -v"

:: Wait for services to initialize
timeout /t 3

:: Start API in a new window
echo Starting API Server...
start "HyperVolt API" cmd /k "cd api && .\venv\Scripts\activate && daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application"

:: Wait for API to initialize
timeout /t 5

:: Start Website in a new window
echo Starting Website...
start "HyperVolt Website" cmd /k "cd website && npm run dev"

echo.
echo =====================================================
echo HyperVolt System Started!
echo =====================================================
echo API:     http://localhost:8000
echo Website: http://localhost:3000
echo MQTT:    localhost:1883
echo Redis:   localhost:6379
echo =====================================================
echo.
pause
```

## API Endpoints Reference

### Sensor Data
- `GET /api/sensor-readings/` - List all sensor readings
- `GET /api/sensor-readings/latest/` - Get latest readings
- `POST /api/sensor-readings/` - Create new reading

### AI Endpoints
- `GET /api/ai/status/` - Check AI model status
- `GET /api/ai/forecast/?hours=6` - Get demand forecast
- `POST /api/ai/recommend_source/` - Get source recommendation
- `POST /api/ai/decide/` - Trigger AI decision

### Energy Sources
- `GET /api/energy-sources/` - List energy sources
- `GET /api/energy-sources/available/` - Get available sources

### Loads
- `GET /api/loads/` - List all loads
- `GET /api/loads/high_priority/` - Get high priority loads

### Optimization
- `POST /api/optimization/recommend/` - Get optimization recommendation
- `GET /api/optimization/context/` - Get current context

## WebSocket Connection

The website connects to WebSocket for real-time updates:
- URL: `ws://localhost:8000/ws/sensors/`
- Protocol: Django Channels with Redis backend

## MQTT Topics

### Sensor Data (Hardware → API)
| Topic | Description | Example Payload |
|-------|-------------|-----------------|
| `solar/data` | Solar sensor data | `{"sensor_type": "current", "value": 0.0, ...}` |
| `battery/data` | Battery sensor data | `{"sensor_type": "voltage", "value": 12.6, ...}` |
| `HyperVolt/sensors/{location}/{type}` | Full format | `{"value": 25.5, "unit": "C"}` |

### Control Commands (API → Hardware)
| Topic | Description |
|-------|-------------|
| `HyperVolt/commands/control` | Switch source commands |
| `HyperVolt/commands/load_{id}` | Load-specific commands |

## Troubleshooting

### "Redis connection refused"
- Ensure Memurai is running: `net start memurai`
- Check port 6379 is not blocked by firewall

### "MQTT connection failed"
- Ensure Mosquitto is running: `mosquitto -v`
- Check port 1883 is not blocked

### "WebSocket connection failed"
- Ensure you're using `daphne` not `runserver`
- Check that Redis is running
- Verify CORS settings in Django

### "AI models not available"
- Check if model files exist in `ai/models/`
- Run model training: `python ai/module3-ai/train_demand_model.py`

## Running the Simulation

For testing without real hardware:

```powershell
# Run simulation with synthetic data
python scripts/run_simulation_without_sensors.py --duration 60 --interval 5

# Run simulation with real sensors (requires MQTT + hardware)
python scripts/run_simulation_with_sensors.py --duration 60 --interval 5
```

## Environment Variables

### API (.env)
```ini
DEBUG=True
SECRET_KEY=your-secret-key
REDIS_HOST=localhost
REDIS_PORT=6379
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
```

### Website (.env.local)
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### AI (.env) - Optional
```ini
HYPERVOLT_API_HOST=localhost
HYPERVOLT_API_PORT=8000
```

## Data Flow Summary

1. **ESP32** publishes sensor data to MQTT topic `solar/data`
2. **Simulation script** (or MQTT bridge) receives data and POSTs to API
3. **API** stores data in database and broadcasts via WebSocket
4. **AI module** (integrated in API) processes data and makes decisions
5. **Website** receives updates via WebSocket and displays in real-time
6. **Commands** are published back to MQTT for hardware execution
