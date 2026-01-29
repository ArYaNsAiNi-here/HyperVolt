# HyperVolt System - Complete Fix Summary

## What Was the Problem?

Your simulation showed:
- **API Success Rate: 0/18** ❌
- **AI Decisions: 0** ❌  
- **Frontend not updating** ❌

This meant sensor data wasn't reaching the backend API.

## What Did I Fix?

### 1. Added WebSocket Broadcasting (views.py)

**Problem:** When sensor data was posted to the API, it wasn't being broadcast to WebSocket clients (the frontend).

**Fix:** Added a `create()` method in `SensorReadingViewSet` that:
- Saves the sensor reading to database
- Broadcasts it to all WebSocket clients via channels

```python
def create(self, request, *args, **kwargs):
    # Save to database
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    
    # Broadcast to WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'sensor_updates',
        {
            'type': 'sensor_update',
            'data': serializer.data
        }
    )
    
    return Response(serializer.data, status=201)
```

### 2. Improved Error Logging (run_simulation_without_sensors.py)

**Problem:** The simulation script was silently failing - no error messages shown.

**Fix:** Added detailed error messages:
- Connection errors now show: "❌ Connection Error: Cannot reach http://localhost:8000"
- API errors show the status code and response
- Timeout errors are clearly identified

### 3. Created Diagnostic Tools

Created several helper scripts:

- **scripts/diagnose_system.py** - Complete system health check
- **scripts/test_api.py** - Quick API functionality test
- **quickstart.bat** - Windows batch file to check services
- **TROUBLESHOOTING.md** - Complete troubleshooting guide

## How to Fix Your Current Issue

### The Most Likely Problem

Based on your output showing `API Success Rate: 0/18`, **Django is either:**
1. Not running at all
2. Running but can't save to database (migrations not run)
3. Running on the wrong port

### The Solution

Run these commands in **separate terminal windows**:

#### Terminal 1: Start Redis
```powershell
redis-server
```

Expected output: `Ready to accept connections`

#### Terminal 2: Start Django (WITH WebSocket support)
```powershell
cd D:\Projects\HyperVolt\api
..\.venv\Scripts\activate
python manage.py migrate  # First time only!
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

Expected output: `Listening on TCP address 0.0.0.0:8000`

**IMPORTANT:** Use `daphne`, NOT `python manage.py runserver`!

#### Terminal 3: Start Frontend
```powershell
cd D:\Projects\HyperVolt\website
npm run dev
```

Expected output: `ready started server on 0.0.0.0:3000`

#### Terminal 4: Run Simulation (With Better Errors!)
```powershell
cd D:\Projects\HyperVolt
..\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
```

Now you'll see detailed error messages if something fails!

### What You Should See Now

With the improved error logging, if Django is not running, you'll see:

```
❌ Connection Error: Cannot reach http://localhost:8000
   Make sure Django is running!
```

If Django is running but has issues, you'll see the actual error:

```
⚠ API Error [temperature]: Status 400
   Response: {"sensor_type": ["This field is required"]}
```

## Verification Steps

### Step 1: Test API Directly

```powershell
cd D:\Projects\HyperVolt
..\.venv\Scripts\python.exe scripts\test_api.py
```

You should see:
```
✅ API is running!
✅ Sensor POST works!
✅ AI Decision works!
```

### Step 2: Run Simulation

```powershell
..\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
```

You should see:
```
API Success Rate: 5/5  ← Increasing, not 0!
AI Decisions: 1        ← Increases every 30 seconds
```

### Step 3: Check Frontend

Open http://localhost:3000

You should see:
- 3D room visualization updating
- Energy flow diagram showing power routing
- Charts with live data
- AI Strategy Narrator logging decisions

## Complete Startup Checklist

- [ ] Redis running (`redis-server`)
- [ ] Django running with `daphne` (NOT `runserver`)
- [ ] Database migrated (`python manage.py migrate`)
- [ ] Frontend running (`npm run dev`)
- [ ] Simulation shows increasing API success rate
- [ ] Frontend updates in real-time
- [ ] Browser console (F12) shows WebSocket connected

## File Changes Made

### Modified Files

1. **api/data_pipeline/views.py**
   - Added imports: `get_channel_layer`, `async_to_sync`
   - Added `create()` method to `SensorReadingViewSet`
   - Now broadcasts sensor data to WebSocket

2. **scripts/run_simulation_without_sensors.py**
   - Improved `post_sensor_reading()` error logging
   - Improved `trigger_ai_decision()` error logging
   - Now shows detailed error messages

### New Files Created

1. **scripts/diagnose_system.py** - Full system diagnostic
2. **scripts/test_api.py** - Quick API test
3. **TROUBLESHOOTING.md** - Complete troubleshooting guide
4. **quickstart.bat** - Windows service checker

## Why Was This Happening?

The original code had two issues:

### Issue 1: No WebSocket Broadcasting

The `SensorReadingViewSet` used Django REST Framework's default `ModelViewSet`, which only saves to the database. It didn't know about WebSocket broadcasting.

**Fix:** Override the `create()` method to also broadcast.

### Issue 2: Silent Failures

When the API wasn't running, the simulation script just showed `API Success Rate: 0/X` with no explanation.

**Fix:** Added detailed error logging to show exactly what's wrong.

## Architecture Flow (After Fix)

```
Simulation Script
      ↓
   POST /api/sensor-readings/
      ↓
Django views.py create()
      ↓
   ├─→ Save to Database
   └─→ Broadcast to WebSocket
            ↓
      WebSocket Consumer
            ↓
       Frontend Client
```

## Testing the Fix

### Test 1: API Connection
```powershell
curl http://localhost:8000/api/ai/status/
```

Expected: JSON response with `"available": true/false`

### Test 2: Sensor POST
```powershell
# In PowerShell
$body = @{
    sensor_type = "temperature"
    sensor_id = "test_1"
    value = 25.5
    unit = "celsius"
    location = "test_room"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/sensor-readings/" -Method Post -Body $body -ContentType "application/json"
```

Expected: JSON response with created sensor reading

### Test 3: WebSocket Connection
Open browser console (F12) and run:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/sensors/');
ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));
ws.onopen = () => console.log('Connected!');
```

Expected: `Connected!` then live sensor data messages

## Common Issues and Solutions

### "Connection refused"
**Cause:** Django not running
**Fix:** `cd api && daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application`

### "WebSocket connection failed"
**Cause:** Using `runserver` instead of `daphne`
**Fix:** Use `daphne` command above

### "Redis connection refused"
**Cause:** Redis not running
**Fix:** `redis-server`

### "AI models not available"
**Cause:** Models not trained
**Fix:** `cd ai/module3-ai && python train_demand_model.py`

### Still showing "API Success Rate: 0/X"
**Causes:**
1. Django not running → Start with `daphne`
2. Database not migrated → Run `python manage.py migrate`
3. Wrong port → Check Django is on port 8000
4. Firewall blocking → Disable or allow Python

## Next Steps

1. **Run quickstart check:**
   ```powershell
   .\quickstart.bat
   ```

2. **If services missing, start them:**
   ```powershell
   # Terminal 1
   redis-server
   
   # Terminal 2
   cd api
   daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
   
   # Terminal 3
   cd website
   npm run dev
   ```

3. **Test API:**
   ```powershell
   .\.venv\Scripts\python.exe scripts\test_api.py
   ```

4. **Run simulation:**
   ```powershell
   .\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
   ```

5. **Open dashboard:**
   http://localhost:3000

## Expected Behavior (When Working)

### Simulation Terminal
```
API Success Rate: 18/18  ✅
AI Decisions: 3          ✅
Total Cost: ₹12.50
Total Carbon: 4.32 kg CO2
```

### Django Terminal
```
HTTP POST /api/sensor-readings/ 201
HTTP POST /api/predictions/decide/ 200
WebSocket CONNECT /ws/sensors/
```

### Frontend Browser
- 3D room updates lighting
- Energy flow shows power routing
- Charts display live data
- AI narrator logs decisions

### Browser Console (F12)
```
WebSocket connected
Received sensor data: {sensor_type: "temperature", value: 25.5, ...}
Received sensor data: {sensor_type: "humidity", value: 58.6, ...}
```

## Support

For more help:
- **TROUBLESHOOTING.md** - Detailed troubleshooting
- **Simulation_Guidelines.md** - Complete setup guide
- **api/MODULE2_README.md** - Backend API documentation

---

**Fix implemented on January 28, 2026 by GitHub Copilot**
**Built with ❤️ by HyperHawks Team**
