# HyperVolt Module 2 - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies (1 minute)

```bash
# Install Python packages
pip install -r requirements.txt

# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Install Mosquitto MQTT Broker (Ubuntu/Debian)
sudo apt-get install mosquitto mosquitto-clients
```

### Step 2: Configure Environment (1 minute)

```bash
# Copy example environment file
cp .env.example .env

# Edit if needed (optional for testing)
# nano .env
```

**For quick testing, the defaults work fine!** No API keys needed to start.

### Step 3: Initialize Database (1 minute)

```bash
# Run migrations
python manage.py migrate

# (Optional) Create admin user
python manage.py createsuperuser
```

### Step 4: Start the Services (2 minutes)

Open **4 separate terminal windows**:

**Terminal 1: Redis**
```bash
redis-server
```

**Terminal 2: MQTT Broker**
```bash
mosquitto -v
```

**Terminal 3: Django Server (with WebSocket support)**
```bash
cd /path/to/HyperVolt
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

**Terminal 4: MQTT Listener**
```bash
cd /path/to/HyperVolt
python manage.py mqtt_listener
```

### Step 5: Test It! (30 seconds)

**Terminal 5: Send test data**
```bash
cd /path/to/HyperVolt
python test_mqtt_publisher.py
```

You should see:
- ✅ MQTT Broker receiving messages
- ✅ MQTT Listener processing sensor data
- ✅ Data being saved to database

## 🔍 Verify It's Working

### Check the Admin Interface

1. Go to: http://localhost:8000/admin/
2. Login with your superuser credentials
3. Navigate to: **Data Pipeline > Sensor Readings**
4. You should see sensor data appearing!

### Check the API

```bash
# Get latest sensor readings
curl http://localhost:8000/api/sensor-readings/latest/

# Get recent readings from last hour
curl http://localhost:8000/api/sensor-readings/recent/?hours=1

# Get buffer data for a specific sensor
curl "http://localhost:8000/api/sensor-readings/buffer/?sensor_type=ldr&sensor_id=ldr_1"
```

### Test WebSocket Connection

Create a file `test_websocket.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>HyperVolt WebSocket Test</title>
</head>
<body>
    <h1>HyperVolt Sensor Data (Real-time)</h1>
    <div id="output"></div>
    
    <script>
        const ws = new WebSocket('ws://localhost:8000/ws/sensors/');
        const output = document.getElementById('output');
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            const div = document.createElement('div');
            div.textContent = JSON.stringify(data, null, 2);
            output.prepend(div);
        };
        
        ws.onopen = function() {
            output.innerHTML = '<p style="color:green">Connected!</p>';
        };
    </script>
</body>
</html>
```

Open it in your browser and watch real-time sensor updates!

## 🎯 Optional: Set Up Scheduled Tasks

```bash
# Set up periodic tasks (carbon intensity, weather)
python setup_scheduled_tasks.py

# Start Django-Q worker (Terminal 6)
python manage.py qcluster
```

## 📊 Sample Data Flow

```
1. test_mqtt_publisher.py → Sends sensor data
                             ↓
2. Mosquitto Broker       → Routes message
                             ↓
3. mqtt_listener command  → Receives & processes
                             ↓
4. Database (Cold Path)   → Stores historical data
   Redis Cache (Hot Path) → Stores recent 60 readings
                             ↓
5. WebSocket Broadcast    → Sends to frontend
                             ↓
6. Browser/API clients    → Receive real-time updates
```

## 🐛 Troubleshooting

### "Connection refused" error
- **Redis**: Check if running: `redis-cli ping` (should return PONG)
- **Mosquitto**: Check if running: `sudo systemctl status mosquitto`

### "Module not found" error
```bash
pip install -r requirements.txt
```

### WebSocket not connecting
- Use `daphne` instead of `python manage.py runserver`
- Check if port 8000 is available

### No data in API
- Check if MQTT listener is running
- Check if test publisher is sending data
- Look at Django logs for errors

## 🎓 Next Steps

1. **Explore the API**: Try all endpoints in MODULE2_README.md
2. **Modify sensor simulator**: Edit `test_mqtt_publisher.py` to send different data
3. **Check the Admin**: Explore all models in Django admin
4. **Read the code**: Start with `models.py`, then `views.py`

## 📚 Documentation

- **Full Module 2 docs**: [MODULE2_README.md](MODULE2_README.md)
- **Project overview**: [README.md](../README.md)
- **API Reference**: See MODULE2_README.md

## ✨ You're Ready!

The data pipeline is now running! Next:
- Build the AI inference engine (Module 3)
- Create the frontend dashboard (Module 4)
- Connect real Raspberry Pi sensors (Module 1)

**Happy Hacking! 🚀**
