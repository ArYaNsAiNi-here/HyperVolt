# HyperVolt - Running All 4 Modules in Sync

This guide provides step-by-step instructions to run all 4 modules of HyperVolt together on a Windows laptop with data coming from ESP32 via MQTT.

## Prerequisites

Before starting, ensure you have:
- **Python 3.12+** installed
- **Node.js 18+** installed  
- **Memurai** (Redis for Windows) installed and running
- **Mosquitto MQTT Broker** installed
- **ESP32** connected to your WiFi and publishing to MQTT

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Module 1      │     │   Module 2      │     │   Module 3      │
│   ESP32         │────►│   Django API    │◄───►│   AI Engine     │
│   (Hardware)    │MQTT │   (Backend)     │     │   (Integrated)  │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                          Redis/Memurai
                          (Channels +
                           Cache)
                                 │
                        ┌────────▼────────┐
                        │   Module 4      │
                        │   Next.js       │
                        │   (Website)     │
                        └─────────────────┘
```

## Data Flow

1. **ESP32** publishes sensor data to MQTT topic `solar/data`
2. **Django MQTT Listener** receives data, saves to DB, and broadcasts via WebSocket
3. **AI Engine** (integrated in Django) processes data and makes decisions
4. **Next.js Website** receives real-time updates via WebSocket

## Step-by-Step Instructions

### Terminal 1: Start Memurai (Redis for Windows)

```powershell
# If Memurai is installed as a service, it starts automatically
# Otherwise, start it manually:
memurai-server
```

Verify it's running:
```powershell
memurai-cli ping
# Should return: PONG
```

### Terminal 2: Start Mosquitto MQTT Broker

```powershell
# Navigate to Mosquitto installation directory
cd "C:\Program Files\mosquitto"

# Start with configuration (if you have one)
mosquitto -c mosquitto.conf -v

# Or start with default settings allowing anonymous connections
mosquitto -v
```

**Important**: Ensure your `mosquitto.conf` allows connections:
```
listener 1883
allow_anonymous true
```

### Terminal 3: Start Django Backend (Module 2)

```powershell
# Navigate to the API directory
cd C:\path\to\HyperVolt\api

# Activate virtual environment (if using one)
.\venv\Scripts\activate

# Run database migrations (first time only)
python manage.py migrate

# Start Django with Daphne (ASGI server for WebSocket support)
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

You should see:
```
Starting server at tcp:0.0.0.0:8000
HTTP/2 support not enabled (install the http2 and tls Twisted extras)
Listening on TCP address 0.0.0.0:8000
```

### Terminal 4: Start MQTT Listener (Module 2 - Data Ingestion)

```powershell
# Navigate to the API directory
cd C:\path\to\HyperVolt\api

# Activate virtual environment
.\venv\Scripts\activate

# Start the MQTT listener
python manage.py mqtt_listener
```

You should see:
```
Starting MQTT Listener...
Connecting to MQTT broker at localhost:1883
Connected to MQTT broker
Subscribed to: solar/data
```

When ESP32 sends data, you'll see:
```
Received on solar/data: {'sensor_type': 'current', 'sensor_id': 'curr_1', 'value': 0.0, 'unit': 'mA', ...}
✓ Processed sensor reading: current=0.0mA
```

### Terminal 5: Start Next.js Website (Module 4)

```powershell
# Navigate to the website directory
cd C:\path\to\HyperVolt\website

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

You should see:
```
   ▲ Next.js 16.x.x
   - Local:        http://localhost:3000
   - Ready in xxms
```

### Terminal 6: (Optional) Monitor with MQTT Explorer

For debugging, you can use MQTT Explorer to:
- See all messages published by ESP32
- Manually publish test messages
- Monitor AI command responses

## ESP32 Configuration

Ensure your ESP32 is configured with:
- Correct WiFi credentials
- MQTT broker IP (your Windows laptop's IP address)
- Publishing to topic: `solar/data`

Example ESP32 output:
```
Received on solar/data: {
  'sensor_type': 'current',
  'sensor_id': 'curr_1',
  'value': 0.0,
  'unit': 'mA',
  'location': 'solar_array',
  'timestamp': '13:01:03'
}
```

## API Endpoints (Module 2)

### REST API (Base URL: `http://localhost:8000/api/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sensor-readings/` | GET | List all sensor readings |
| `/api/sensor-readings/latest/` | GET | Get latest readings per sensor |
| `/api/grid-data/` | GET | List grid data (carbon, weather) |
| `/api/energy-sources/` | GET | List energy sources |
| `/api/loads/` | GET | List electrical loads |
| `/api/ai/status/` | GET | Check AI service status |
| `/api/ai/forecast/` | GET | Get AI energy forecast |
| `/api/ai/recommend_source/` | POST | Get AI source recommendation |
| `/api/ai/decide/` | POST | Make AI comprehensive decision |

### WebSocket (Real-time Updates)

Connect to: `ws://localhost:8000/ws/sensors/`

Message format received:
```json
{
  "type": "sensor_update",
  "data": {
    "sensor_type": "ldr",
    "sensor_id": "ldr_1",
    "value": 3500,
    "unit": "raw",
    "location": "solar_array",
    "timestamp": "2026-01-30T13:01:03+05:30"
  }
}
```

## Troubleshooting

### Website shows "DISCONNECTED"

1. **Check Memurai is running:**
   ```powershell
   memurai-cli ping
   ```
   
2. **Check Django is running with Daphne (not runserver):**
   ```powershell
   daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
   ```

3. **Check Redis channel layer in Django settings:**
   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               "hosts": [('localhost', 6379)],
           },
       },
   }
   ```

### "Insufficient Resources" Error

This usually means WebSocket connections are being exhausted. Solutions:

1. **Increase Redis connection pool:**
   Add to Django settings:
   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               "hosts": [('localhost', 6379)],
               "capacity": 1500,
               "expiry": 10,
           },
       },
   }
   ```

2. **Check for connection leaks in browser:**
   - Open browser DevTools → Network → WS tab
   - Ensure only one WebSocket connection exists

3. **Restart Memurai:**
   ```powershell
   net stop memurai
   net start memurai
   ```

### MQTT Listener Not Receiving Data

1. **Verify ESP32 is publishing:**
   Use MQTT Explorer to check topic `solar/data`

2. **Check Mosquitto is running:**
   ```powershell
   netstat -an | findstr 1883
   ```

3. **Verify ESP32 MQTT broker IP matches your laptop's IP**

### Data Not Showing on Website

1. **Check MQTT Listener terminal for incoming data**

2. **Check browser DevTools Console for errors**

3. **Verify WebSocket connection in browser:**
   - Open DevTools → Network → WS
   - Should show `ws://localhost:8000/ws/sensors/`

## Quick Start Checklist

- [ ] Memurai is running (`memurai-cli ping` returns PONG)
- [ ] Mosquitto is running on port 1883
- [ ] Django is running with Daphne on port 8000
- [ ] MQTT Listener is connected and receiving data
- [ ] Next.js website is running on port 3000
- [ ] ESP32 is connected and publishing to `solar/data`

## Environment Variables

Create `.env` file in `/api/` directory:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database (SQLite by default)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Redis/Memurai
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_CLIENT_ID=hypervolt_django
```

Create `.env.local` file in `/website/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Module 3 (AI) Configuration

The AI module is integrated into Django. To configure:

### Switch Between Simulation and Real Sensors

Edit `api/data_pipeline/services/ai_inference.py`:

```python
# For testing without hardware:
USE_SIMULATION_FILE = True

# For real ESP32 data:
USE_SIMULATION_FILE = False
```

### Simulation Data File

Edit `api/data/simulation_sensors.csv`:

```csv
timestamp,sensor_type,value
2026-01-30 12:00:00,temperature,28.5
2026-01-30 12:00:00,humidity,45.0
2026-01-30 12:00:00,ldr,3500
2026-01-30 12:00:00,current,1.2
2026-01-30 12:00:00,voltage,230.0
```

---

## Summary: Start Order

1. **Memurai** (Redis) - Must be first
2. **Mosquitto** (MQTT Broker)
3. **Django Daphne** (Backend API + WebSocket)
4. **MQTT Listener** (Data Ingestion)
5. **Next.js** (Website)
6. **ESP32** (Hardware - should already be running)

Open http://localhost:3000 in your browser to see the dashboard!

---

**Built with ❤️ by HyperHawks Team**
