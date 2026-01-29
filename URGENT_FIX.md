# URGENT FIX - Voltage Sensor Type & API Endpoint Errors

## Problems Identified

From your simulation output, there were **2 critical errors**:

### Error 1: Voltage Sensor Not Allowed
```
⚠ API Error [voltage]: Status 400
Response: {"sensor_type":["\"voltage\" is not a valid choice."]}
```

**Cause:** The `SensorReading` model only allowed `['ldr', 'current', 'temperature', 'humidity']` but the simulation was sending `'voltage'`.

### Error 2: Wrong API Endpoint
```
⚠ AI Decision Error: Status 404
Response: Page not found at /api/predictions/decide/
```

**Cause:** The simulation was calling `/api/predictions/decide/` but the correct endpoint is `/api/ai/decide/`.

## Fixes Applied

### ✅ Fix 1: Added 'voltage' to Sensor Types

**File:** `api/data_pipeline/models.py`

```python
SENSOR_TYPE_CHOICES = [
    ('ldr', 'Light Dependent Resistor'),
    ('current', 'Current Sensor'),
    ('temperature', 'Temperature Sensor'),
    ('humidity', 'Humidity Sensor'),
    ('voltage', 'Voltage Sensor'),  # ← ADDED THIS
]
```

### ✅ Fix 2: Fixed API Endpoint URLs

**File:** `scripts/run_simulation_without_sensors.py`

Changed:
- ❌ `/api/predictions/decide/` → ✅ `/api/ai/decide/`
- ❌ `/api/predictions/forecast/` → ✅ `/api/ai/forecast/`

## IMPORTANT: You Must Run Database Migration!

Since we changed the model, Django needs to update the database:

### Option 1: Use the Helper Script (Easiest)

```powershell
cd D:\Projects\HyperVolt
.\.venv\Scripts\python.exe scripts\update_database.py
```

### Option 2: Manual Migration

```powershell
cd D:\Projects\HyperVolt\api
..\.venv\Scripts\python.exe manage.py makemigrations
..\.venv\Scripts\python.exe manage.py migrate
```

You should see:
```
Migrations for 'data_pipeline':
  data_pipeline\migrations\0002_auto_XXXXX.py
    - Alter field sensor_type on sensorreading
Running migrations:
  Applying data_pipeline.0002_auto_XXXXX... OK
```

## After Migration: Restart Django

**IMPORTANT:** You must restart Django for the changes to take effect!

1. **Stop Django** (Ctrl+C in Terminal 2)
2. **Restart with daphne:**
   ```powershell
   cd D:\Projects\HyperVolt\api
   daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
   ```

## Then Run Simulation Again

```powershell
cd D:\Projects\HyperVolt
.\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
```

## Expected Output (After Fix)

### ✅ Success Indicators:

```
API Success Rate: 5/5  ← All 5 sensors (ldr, temp, humidity, current, voltage) posting successfully!
AI Decisions: 1        ← AI making decisions every 30 seconds
```

### ✅ No More Errors:

- ❌ No more "voltage is not a valid choice"
- ❌ No more "Page not found at /api/predictions/decide/"
- ✅ Clean sensor posts
- ✅ AI decisions working

## Quick Verification

After restarting Django and running migration, test with:

```powershell
.\.venv\Scripts\python.exe scripts\test_api.py
```

Expected output:
```
✅ API is running!
✅ Sensor POST works!
✅ GET works!
✅ AI Decision works! (or ⚠️ AI models not available)
```

## Complete Startup Sequence

Run these in order:

### Step 1: Run Migration
```powershell
cd D:\Projects\HyperVolt
.\.venv\Scripts\python.exe scripts\update_database.py
```

### Step 2: Restart Services

```powershell
# Terminal 1: Redis (if not running)
redis-server

# Terminal 2: Django (RESTART IT!)
cd D:\Projects\HyperVolt\api
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application

# Terminal 3: Frontend
cd D:\Projects\HyperVolt\website
npm run dev

# Terminal 4: Simulation
cd D:\Projects\HyperVolt
.\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
```

## Summary of All Changes

| File | What Changed | Why |
|------|--------------|-----|
| `api/data_pipeline/models.py` | Added 'voltage' to SENSOR_TYPE_CHOICES | Allow voltage sensor readings |
| `scripts/run_simulation_without_sensors.py` | Fixed `/api/predictions/*` → `/api/ai/*` | Correct API endpoints |
| `scripts/test_api.py` | Fixed API endpoint | Match new URL structure |
| `scripts/update_database.py` | **NEW FILE** | Helper to run migrations |

## Troubleshooting

### If you still see "voltage is not a valid choice":
→ You forgot to run the migration! Run `scripts/update_database.py`

### If you still see "404 Page not found":
→ Check the Django terminal - is it showing any errors?
→ Make sure you restarted Django after the code changes

### If API Success Rate is still 0/X:
→ Django might not be running
→ Run: `curl http://localhost:8000/api/ai/status/`

### If AI Decisions is still 0:
→ This is expected - it shows "⚠ AI models not available"
→ To fix: Train models with `cd ai/module3-ai && python train_demand_model.py`

## What Should Work Now

### ✅ All 5 Sensors Posting Successfully:
- LDR (Light Dependent Resistor)
- Temperature
- Humidity  
- Current
- Voltage ← **NOW WORKS!**

### ✅ AI Endpoints Working:
- `/api/ai/status/` - Check AI availability
- `/api/ai/decide/` - Make AI decision ← **NOW WORKS!**
- `/api/ai/forecast/` - Get forecast ← **NOW WORKS!**

### ✅ Frontend Receiving Data:
- WebSocket broadcasting sensor data
- Real-time updates in dashboard
- Charts updating live

## Next Steps

1. **Run migration** - `python scripts/update_database.py`
2. **Restart Django** - Stop and start with `daphne`
3. **Test API** - `python scripts/test_api.py`
4. **Run simulation** - `python scripts/run_simulation_without_sensors.py`
5. **Watch frontend** - Open http://localhost:3000

You should now see **API Success Rate** increasing instead of staying at 0!

---

**Fix applied on January 28, 2026**
**All errors should now be resolved! 🎉**
