# HyperVolt - Quick Reference Card

## 🚀 Start Everything (4 Terminals)

```powershell
# Terminal 1: Redis
redis-server

# Terminal 2: Django Backend
cd D:\Projects\HyperVolt\api
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application

# Terminal 3: Frontend
cd D:\Projects\HyperVolt\website
npm run dev

# Terminal 4: Simulation
cd D:\Projects\HyperVolt
.\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
```

## 🔍 Quick Health Check

```powershell
# Check if Redis is running
redis-cli ping
# Expected: PONG

# Check if Django is running
curl http://localhost:8000/api/ai/status/
# Expected: {"available": true, ...}

# Check if Frontend is running
curl http://localhost:3000
# Expected: HTML response

# Run full diagnostic
.\.venv\Scripts\python.exe scripts\diagnose_system.py
```

## ✅ What Success Looks Like

### Simulation Terminal
```
API Success Rate: 18/18  ← Must be increasing!
AI Decisions: 3          ← Increases every 30 seconds
```

### Frontend Browser (http://localhost:3000)
- 3D room visualization updating
- Energy flow diagram animating
- Charts showing live data
- AI narrator logging decisions

### Browser Console (F12)
```
WebSocket connected
Received sensor data: {...}
```

## ❌ Common Problems & Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `API Success Rate: 0/X` | Django not running | `cd api && daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application` |
| `Connection refused` | Redis not running | `redis-server` |
| `WebSocket failed` | Using `runserver` | Use `daphne` not `runserver` |
| `AI models not available` | Models not trained | `cd ai/module3-ai && python train_demand_model.py` |
| Frontend not updating | WebSocket not connected | Check Django running with `daphne` |

## 🧪 Test Individual Components

```powershell
# Test API only
.\.venv\Scripts\python.exe scripts\test_api.py

# Test full system
.\.venv\Scripts\python.exe scripts\diagnose_system.py

# Check services
.\quickstart.bat
```

## 📊 Monitoring

### Watch Django Logs
Terminal 2 shows:
```
HTTP POST /api/sensor-readings/ 201
HTTP POST /api/predictions/decide/ 200
WebSocket CONNECT /ws/sensors/
```

### Watch Simulation Output
Terminal 4 shows:
```
📊 Sensor Readings:
   LDR: 756, Temperature: 24.2°C
   
🤖 AI Decision:
   Predicted Demand: 1.5 kWh
   Source: Solar + Battery
```

### Watch Browser Console
F12 → Console shows:
```
WebSocket connected
Received sensor data: {sensor_type: "ldr", value: 756, ...}
AI decision received: {...}
```

## 🛠️ First Time Setup

```powershell
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Node dependencies
cd website
npm install
cd ..

# 3. Run database migrations
cd api
python manage.py migrate
cd ..

# 4. Train AI models
cd ai\module3-ai
python train_demand_model.py
cd ..\..

# 5. Start services (see "Start Everything" above)
```

## 📝 Important Files

| File | Purpose |
|------|---------|
| `FIX_SUMMARY.md` | What was fixed and why |
| `TROUBLESHOOTING.md` | Detailed troubleshooting |
| `Simulation_Guidelines.md` | Complete setup guide |
| `scripts/diagnose_system.py` | System health check |
| `scripts/test_api.py` | API quick test |

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Django API | http://localhost:8000/api/ |
| API Status | http://localhost:8000/api/ai/status/ |
| WebSocket | ws://localhost:8000/ws/sensors/ |

## 💡 Pro Tips

1. **Always use `daphne`** for Django (NOT `runserver`)
2. **Redis must be running** for WebSocket to work
3. **Check browser console (F12)** for WebSocket errors
4. **API Success Rate must increase** - if stuck at 0, Django isn't running
5. **AI decisions every 30 seconds** - if stuck at 0, models not loaded

## 🆘 Emergency Reset

If everything is broken:

```powershell
# 1. Stop all services (Ctrl+C in each terminal)

# 2. Delete database (fresh start)
cd D:\Projects\HyperVolt\api
del db.sqlite3

# 3. Recreate database
python manage.py migrate

# 4. Restart all services (see "Start Everything")
```

## 📞 Get Help

1. Run: `.\.venv\Scripts\python.exe scripts\diagnose_system.py`
2. Check: `TROUBLESHOOTING.md`
3. Read: `FIX_SUMMARY.md`

---

**HyperVolt - AI-Driven Energy Orchestrator**
**Built by HyperHawks Team** ⚡
