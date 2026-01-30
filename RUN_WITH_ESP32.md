# Running HyperVolt with ESP32 Hardware

This guide explains how to run all 4 modules of HyperVolt in sync on a Windows laptop with ESP32 hardware providing real sensor data.

## Architecture Overview

```
ESP32 (Sensors) → MQTT → Django API → Redis/Memurai → Next.js Website
                           ↓
                     AI Decision Engine
```

## Prerequisites

### Software Requirements
- **Python 3.12+** with pip
- **Node.js 18+** with npm
- **Memurai** (Redis for Windows) - Download from https://www.memurai.com/
- **Mosquitto MQTT Broker** - Download from https://mosquitto.org/download/

### Hardware Requirements
- ESP32 microcontroller
- DHT11 Temperature/Humidity sensor
- LDR (Light Dependent Resistor)
- Solar voltage sensor (voltage divider circuit)

## Step-by-Step Startup Guide

### Step 1: Start Memurai (Redis for Windows)

Memurai is the Redis-compatible cache that enables real-time communication between the Django API and the Website via WebSockets.

```cmd
:: Start Memurai (if installed as service, it may already be running)
memurai-server

:: Or if installed as a service:
net start memurai
```

**Verify**: Open a new terminal and run:
```cmd
redis-cli ping
:: Should respond with: PONG
```

### Step 2: Start Mosquitto MQTT Broker

```cmd
:: Navigate to Mosquitto installation directory
cd "C:\Program Files\mosquitto"

:: Start with default config (or your custom config)
mosquitto -v

:: Or if installed as a service:
net start mosquitto
```

**Verify**: You should see output like:
```
mosquitto version X.X.X starting
Opening ipv4 listen socket on port 1883
```

### Step 3: Start the Django API (Module 2)

Open a new terminal:

```cmd
:: Navigate to the API directory
cd path\to\HyperVolt\api

:: Create and activate virtual environment (first time only)
python -m venv venv
venv\Scripts\activate

:: Install dependencies (first time only)
pip install -r requirements.txt

:: Run database migrations (first time only)
python manage.py migrate

:: Start the Django server with Daphne (for WebSocket support)
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

**Important**: Use `daphne` instead of `python manage.py runserver` for proper WebSocket support.

**Verify**: 
- API Health: http://localhost:8000/api/ai/status/
- Should return JSON with `"available": true` or `"available": false`

### Step 4: Start the MQTT Listener

Open another terminal:

```cmd
cd path\to\HyperVolt\api
venv\Scripts\activate

:: Start the MQTT listener to receive data from ESP32
python manage.py mqtt_listener
```

**Verify**: You should see:
```
Starting MQTT Listener...
Connecting to MQTT broker at localhost:1883
Connected to MQTT broker
Subscribed to: solar/data
```

### Step 5: Start the AI Decision Loop (Module 3)

Open another terminal:

```cmd
cd path\to\HyperVolt
venv\Scripts\activate

:: Start the AI decision loop
python run_ai_loop.py
```

**Verify**: You should see:
```
Starting AI Decision Loop...
Press Ctrl+C to stop.
✅ AI Update: <recommendation message>
```

### Step 6: Start the Website (Module 4)

Open another terminal:

```cmd
cd path\to\HyperVolt\website

:: Install dependencies (first time only)
npm install

:: Create .env.local file (first time only)
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
echo NEXT_PUBLIC_WS_URL=ws://localhost:8000 >> .env.local

:: Start the development server
npm run dev
```

**Verify**: Open http://localhost:3000 in your browser

### Step 7: Power On ESP32 (Module 1)

1. Flash the ESP32 with the code from `hardware/ESP32_Sensor_Publisher/ESP32_Sensor_Publisher.ino`
2. Update the WiFi credentials and MQTT broker IP in the code
3. Power on the ESP32
4. The ESP32 should connect to your WiFi and start publishing to MQTT

**Verify**: In the MQTT listener terminal, you should see:
```
Received on solar/data: {'sensor_type': 'temperature', 'sensor_id': 'temp_1', 'value': 25.0, ...}
✓ Processed sensor reading: temperature=25.0Celsius
```

## Data Flow Verification

Once all modules are running, you should see:

1. **ESP32** publishes sensor data to MQTT topic `solar/data`
2. **MQTT Listener** receives data and:
   - Saves to database
   - Broadcasts via WebSocket to connected clients
3. **Website** receives WebSocket updates and displays real-time data
4. **AI Decision Loop** periodically calls `/api/ai/decide/` and:
   - Gets energy demand forecast
   - Optimizes source allocation
   - Publishes decision to MQTT and WebSocket

## Troubleshooting

### WebSocket Disconnection Issues

**Problem**: Website shows "DISCONNECTED" or "Insufficient Resources"

**Solutions**:

1. **Verify Memurai is running**:
   ```cmd
   redis-cli ping
   ```

2. **Check Daphne is serving WebSockets**:
   - Ensure you're using `daphne` not `python manage.py runserver`
   - Check console for WebSocket connection logs

3. **Check browser console**:
   - Press F12 → Console tab
   - Look for WebSocket connection errors

4. **Verify CORS settings** in `api/hypervolt_backend/settings.py`:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",
       "http://127.0.0.1:3000",
   ]
   ```

### MQTT Connection Issues

**Problem**: MQTT listener shows connection failed

**Solutions**:

1. **Check Mosquitto is running**:
   ```cmd
   netstat -an | findstr 1883
   ```

2. **Check firewall**:
   - Allow port 1883 in Windows Firewall

3. **Verify ESP32 IP configuration**:
   - Make sure `mqtt_server` in ESP32 code matches your laptop's IP

### No Data Showing on Website

**Problem**: Website loads but shows dummy data

**Solutions**:

1. **Check API connection**:
   - Open browser dev tools → Network tab
   - Look for API calls to localhost:8000

2. **Check WebSocket connection**:
   - In dev tools, look for WS connection to ws://localhost:8000/ws/sensors/

3. **Verify data in database**:
   ```cmd
   cd api
   python manage.py shell
   >>> from data_pipeline.models import SensorReading
   >>> SensorReading.objects.count()
   ```

## Quick Start Commands Summary

Open 5 terminal windows and run in order:

**Terminal 1 - Memurai/Redis**:
```cmd
memurai-server
```

**Terminal 2 - Mosquitto**:
```cmd
mosquitto -v
```

**Terminal 3 - Django API**:
```cmd
cd api && daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

**Terminal 4 - MQTT Listener**:
```cmd
cd api && python manage.py mqtt_listener
```

**Terminal 5 - Website**:
```cmd
cd website && npm run dev
```

**Terminal 6 (Optional) - AI Loop**:
```cmd
python run_ai_loop.py
```

## ESP32 Configuration

Update these values in `ESP32_Sensor_Publisher.ino`:

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqtt_server = "YOUR_LAPTOP_IP";  // e.g., "192.168.1.100"
```

To find your laptop's IP:
```cmd
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter.

## Expected Sensor Data Format

The ESP32 publishes JSON messages to `solar/data`:

```json
{
  "sensor_type": "temperature",
  "sensor_id": "temp_1",
  "value": 25.5,
  "unit": "Celsius",
  "location": "solar_array",
  "timestamp": "13:01:03"
}
```

Sensor types published:
- `temperature` - DHT11 temperature in Celsius
- `humidity` - DHT11 humidity in %
- `light` - LDR raw value (0-4095) - mapped to `ldr` in the system
- `voltage` - Solar panel voltage in V
- `current` - Calculated current in mA

---

**Built with ❤️ for Sustainergy Hackathon 2026**
