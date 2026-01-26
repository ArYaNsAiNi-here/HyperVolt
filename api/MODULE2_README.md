# HyperVolt - Module 2: Data Pipeline Backend

## Overview

HyperVolt Module 2 is the "Nervous System" of the HyperVolt AI-Driven Energy Orchestrator. It handles data ingestion from Raspberry Pi sensors, external API integration, real-time WebSocket streaming, and provides REST APIs for the frontend.

## Architecture

```
┌─────────────────┐
│  Raspberry Pi   │
│   (Sensors)     │
└────────┬────────┘
         │ MQTT
         ↓
┌─────────────────┐      ┌──────────────┐
│ MQTT Listener   │─────→│  Hot Path    │
│  (Django Cmd)   │      │ (Redis Cache)│
└────────┬────────┘      └──────────────┘
         │                       ↓
         │                  AI Inference
         ↓
┌─────────────────┐      ┌──────────────┐
│   Cold Path     │      │  WebSocket   │
│  (PostgreSQL)   │      │  (Channels)  │
└─────────────────┘      └──────┬───────┘
         ↑                       ↓
         │                Frontend (3D Digital Twin)
         │
┌─────────────────┐
│  External APIs  │
│ (Carbon/Weather)│
└─────────────────┘
```

## Features

### 1. Data Ingestion (MQTT)
- **Real-time sensor data** from Raspberry Pi via MQTT
- **Dual-path processing**: Cold Path (database) + Hot Path (cache)
- **Automatic validation** and enrichment of sensor data
- **WebSocket broadcasting** for instant frontend updates

### 2. External API Integration
- **Carbon Intensity**: Electricity Maps API
- **Weather Data**: OpenWeatherMap API
- **Scheduled tasks**: Automatic periodic data fetching via Django-Q

### 3. Hot Path (In-Memory Cache)
- **Sliding window buffer** (last 60 readings)
- **Redis-based** for ultra-fast access
- **Designed for AI inference** without database queries

### 4. REST API
- **Comprehensive endpoints** for all data models
- **Custom actions** for common queries (latest, recent, buffer)
- **Filtering and pagination** support

### 5. Real-time WebSockets
- **Django Channels** for WebSocket support
- **Automatic broadcasting** of sensor updates
- **Group-based messaging** for scalability

## Installation

### Prerequisites
- Python 3.12+
- PostgreSQL (optional, defaults to SQLite)
- Redis
- MQTT Broker (Mosquitto)

### Setup Steps

1. **Clone the repository**:
   ```bash
   cd /path/to/HyperVolt
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

## Running the System

### 1. Start Redis
```bash
redis-server
```

### 2. Start MQTT Broker (Mosquitto)
```bash
mosquitto -v
```

### 3. Start Django Development Server
```bash
python manage.py runserver
```

Or for WebSocket support (recommended):
```bash
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

### 4. Start MQTT Listener
In a separate terminal:
```bash
python manage.py mqtt_listener
```

### 5. Start Django-Q Worker (for scheduled tasks)
In another terminal:
```bash
python manage.py qcluster
```

## API Endpoints

### Sensor Readings
- `GET /api/sensor-readings/` - List all sensor readings
- `GET /api/sensor-readings/latest/` - Get latest reading per sensor
- `GET /api/sensor-readings/recent/?hours=1` - Get recent readings
- `GET /api/sensor-readings/buffer/?sensor_type=ldr&sensor_id=ldr_1` - Get hot path buffer

### Grid Data
- `GET /api/grid-data/` - List all grid data
- `GET /api/grid-data/latest/` - Get latest data per type
- `GET /api/grid-data/carbon_intensity/?hours=24` - Get carbon intensity history
- `GET /api/grid-data/weather/?hours=24` - Get weather history

### User Preferences
- `GET /api/preferences/` - List all preferences
- `GET /api/preferences/get_preference/?key=brightness_threshold` - Get specific preference
- `POST /api/preferences/` - Create new preference
- `PUT /api/preferences/{key}/` - Update preference

### AI Decisions
- `GET /api/ai-decisions/` - List all AI decisions
- `GET /api/ai-decisions/recent/?hours=24` - Get recent decisions
- `POST /api/ai-decisions/` - Record new decision

### Energy Sources
- `GET /api/energy-sources/` - List all energy sources
- `GET /api/energy-sources/available/` - Get available sources only
- `PUT /api/energy-sources/{id}/` - Update source status

## WebSocket Connection

Connect to: `ws://localhost:8000/ws/sensors/`

**Receive format**:
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

## MQTT Message Format

### Sensor Data (Publish)
**Topic**: `HyperVolt/sensors/{location}/{sensor_type}`

**Payload**:
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

### Commands (Subscribe)
**Topic**: `HyperVolt/commands/{device_id}`

**Payload** (example):
```json
{
  "command": "set_brightness",
  "value": 75,
  "timestamp": "2026-01-26T08:00:00Z"
}
```

## Scheduled Tasks

Configure in Django admin under "Django Q" > "Scheduled tasks":

1. **Fetch Carbon Intensity**
   - Function: `data_pipeline.tasks.fetch_carbon_intensity`
   - Schedule: Every 15-30 minutes

2. **Fetch Weather Data**
   - Function: `data_pipeline.tasks.fetch_weather_data`
   - Schedule: Every 15-30 minutes

3. **Cleanup Old Data**
   - Function: `data_pipeline.tasks.cleanup_old_data`
   - Schedule: Daily at 2 AM

## Database Models

### SensorReading
Stores time-series sensor data from Raspberry Pi.

### GridData
Stores external API data (carbon intensity, weather).

### UserPreferences
User-configurable settings (brightness thresholds, etc.).

### AIDecision
Audit trail of AI recommendations.

### EnergySource
Tracks available energy sources and their status.

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Key settings**:
- `MQTT_BROKER_HOST`: MQTT broker address (default: localhost)
- `REDIS_HOST`: Redis server address (default: localhost)
- `ELECTRICITY_MAPS_API_KEY`: Carbon intensity API key
- `OPENWEATHER_API_KEY`: Weather API key
- `LOCATION_LAT`, `LOCATION_LON`: Location coordinates
- `LOCATION_ZONE`: Grid zone identifier (e.g., IN-KA)

## Development

### Running Tests
```bash
python manage.py test data_pipeline
```

### Checking Migrations
```bash
python manage.py showmigrations
```

### Django Shell
```bash
python manage.py shell
```

### Admin Interface
Access at: `http://localhost:8000/admin/`

## Troubleshooting

### MQTT Connection Issues
- Ensure Mosquitto is running: `sudo systemctl status mosquitto`
- Check broker logs: `mosquitto -v`
- Verify port 1883 is accessible

### Redis Connection Issues
- Check if Redis is running: `redis-cli ping`
- Should respond with `PONG`

### WebSocket Connection Issues
- Use Daphne instead of `runserver` for WebSocket support
- Check Django Channels configuration in settings

### No Data in Hot Path
- Ensure Redis is running
- Check MQTT listener is active: `ps aux | grep mqtt_listener`
- Verify sensor data is being published to MQTT

## Next Steps

### Module 3: AI Inference Engine
- Integrate this backend with the AI decision-making logic
- Use the Hot Path buffer for real-time predictions
- Implement power source selection algorithms

### Module 4: Frontend (Digital Twin)
- Connect to WebSocket endpoint
- Display real-time sensor updates
- Show 3D visualization of room/building

## Contributing

When extending this module:
1. Follow Django best practices
2. Write tests for new functionality
3. Update this documentation
4. Use type hints where appropriate
5. Add logging for debugging

## License

See LICENSE file in repository root.

## Support

For issues or questions, create an issue on GitHub.
