# 🔍 DEBUG MODE ENABLED - Find Why AI Decisions = 0

## What I Just Did

I added **comprehensive debug logging** to both Django and the simulation script to see EXACTLY what's happening with AI decisions.

## Debug Logs Added

### In Django (`api/data_pipeline/views.py`)

The `/api/ai/decide/` endpoint now prints:
```
🔍 [DEBUG] AI decide endpoint called
🔍 [DEBUG] AI decision result: {...}
🔍 [DEBUG] Available flag: True/False
✅ [DEBUG] Decision is available, recording to database
OR
❌ [DEBUG] Decision not available - will not be counted
❌ [DEBUG] AI returned error: [error message]
```

### In Simulation (`scripts/run_simulation_without_sensors.py`)

The simulation now prints at EVERY iteration:
```
🔍 [DEBUG] Iteration 6: Checking AI decision trigger...
🔍 [DEBUG] ENABLE_AI_DECISIONS: True
🔍 [DEBUG] iteration_num % 6: 0
✅ [DEBUG] Triggering AI decision at iteration 6...
🔍 [DEBUG] Calling AI decision endpoint: http://localhost:8000/api/ai/decide/
🔍 [DEBUG] Response status: 200
🔍 [DEBUG] Decision received: {...}
🔍 [DEBUG] Available flag: True/False
✅ [DEBUG] Valid AI decision received!
✅ [DEBUG] Incrementing AI decisions count!
✅ [DEBUG] AI Decisions: 1
```

---

## How to Use Debug Mode

### Step 1: Restart Django

```powershell
# Terminal 2: Kill existing Django
cd D:\Projects\HyperVolt
.\kill_django.bat

# Start Django with debug logging
cd api
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

### Step 2: Run Simulation

```powershell
# Terminal 4
cd D:\Projects\HyperVolt
.\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
```

### Step 3: Watch Iteration 6 Carefully

At iteration 6 (~75 seconds), you'll see A LOT of debug output in BOTH terminals.

---

## What to Look For

### Scenario 1: AI Decision Works ✅

**Terminal 4 (Simulation) shows:**
```
🔍 [DEBUG] Iteration 6: Checking AI decision trigger...
✅ [DEBUG] Triggering AI decision at iteration 6...
🔍 [DEBUG] Response status: 200
🔍 [DEBUG] Available flag: True
✅ [DEBUG] Valid AI decision received!
✅ [DEBUG] Incrementing AI decisions count!
✅ [DEBUG] AI Decisions: 1

  🤖 AI Decision:
     Predicted Demand: 0.125 kWh
     ...
     
  AI Decisions: 1  ← WORKING!
```

**Terminal 2 (Django) shows:**
```
🔍 [DEBUG] AI decide endpoint called
🔍 [DEBUG] Available flag: True
✅ [DEBUG] Decision is available, recording to database
HTTP POST /api/ai/decide/ 200
```

### Scenario 2: AI Returns Error ❌

**Terminal 4 (Simulation) shows:**
```
🔍 [DEBUG] Iteration 6: Checking AI decision trigger...
✅ [DEBUG] Triggering AI decision at iteration 6...
🔍 [DEBUG] Response status: 200
🔍 [DEBUG] Available flag: False  ← PROBLEM!
❌ [DEBUG] Decision not available! Error: Insufficient historical data
❌ [DEBUG] Decision available=False, not counting!

  AI Decisions: 0  ← STUCK AT 0
```

**Terminal 2 (Django) shows:**
```
🔍 [DEBUG] AI decide endpoint called
Error fetching historical data: Insufficient data
🔍 [DEBUG] Available flag: False
❌ [DEBUG] Decision not available - will not be counted
HTTP POST /api/ai/decide/ 200
```

**Root Cause:** Not enough historical sensor data in database

### Scenario 3: Iteration Check Failing ❌

**Terminal 4 shows at iteration 6:**
```
🔍 [DEBUG] Iteration 6: Checking AI decision trigger...
🔍 [DEBUG] ENABLE_AI_DECISIONS: True
🔍 [DEBUG] iteration_num % 6: 0
⏭️ [DEBUG] Skipping - not a trigger iteration  ← PROBLEM!
```

**Root Cause:** Logic error in iteration counting

### Scenario 4: Endpoint Not Being Called ❌

**Terminal 4 shows at iteration 6:**
```
🔍 [DEBUG] Iteration 6: Checking AI decision trigger...
⚠️ [DEBUG] AI decisions disabled
```

**Root Cause:** `ENABLE_AI_DECISIONS = False`

---

## Common Issues & Solutions

### Issue 1: "Insufficient historical data"

**Cause:** Database doesn't have 24 hours of sensor readings

**Solution:** Generate fake historical data

```powershell
cd D:\Projects\HyperVolt\api
..\.venv\Scripts\python.exe manage.py shell
```

In the shell:
```python
from data_pipeline.models import SensorReading
from django.utils import timezone
from datetime import timedelta
import random

# Create 24 hours of fake historical data
now = timezone.now()
for i in range(24):
    timestamp = now - timedelta(hours=24-i)
    
    # Temperature
    SensorReading.objects.create(
        sensor_type='temperature',
        sensor_id='temp_1',
        value=25.0 + random.uniform(-2, 2),
        unit='celsius',
        timestamp=timestamp
    )
    
    # LDR
    SensorReading.objects.create(
        sensor_type='ldr',
        sensor_id='ldr_1',
        value=500 + random.uniform(-200, 200),
        unit='raw',
        timestamp=timestamp
    )
    
    # Current
    SensorReading.objects.create(
        sensor_type='current',
        sensor_id='current_1',
        value=0.5 + random.uniform(-0.2, 0.3),
        unit='amperes',
        timestamp=timestamp
    )
    
    # Humidity (if needed)
    SensorReading.objects.create(
        sensor_type='humidity',
        sensor_id='humidity_1',
        value=60.0 + random.uniform(-10, 10),
        unit='percent',
        timestamp=timestamp
    )

print(f"Created {24*4} historical sensor readings!")
exit()
```

Then restart simulation.

### Issue 2: Pandas 'H' frequency error still showing

**Cause:** Django not restarted after code fix

**Solution:** 
```powershell
.\kill_django.bat
cd api
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

### Issue 3: Available=False every time

**Check Django logs for the actual error:**
- "Insufficient historical data"
- "Error fetching historical data: [error]"
- "Forecasting failed: [error]"

Then fix the specific issue shown.

---

## What to Send Me

After running with debug mode, please share:

1. **From Terminal 4 (Simulation):** The complete output from iteration 6, including all 🔍 debug lines

2. **From Terminal 2 (Django):** The output when `/api/ai/decide/` is called at iteration 6

3. **Any errors** you see in either terminal

This will tell us EXACTLY why AI Decisions = 0!

---

## Quick Test

To quickly test if AI endpoint works at all:

```powershell
# Call the endpoint directly
curl -X POST http://localhost:8000/api/ai/decide/
```

Should return JSON like:
```json
{
  "timestamp": "...",
  "available": true,
  "forecast": [...],
  "current_decision": {...}
}
```

OR
```json
{
  "error": "Insufficient historical data",
  "available": false
}
```

---

## Files Changed

- ✅ `api/data_pipeline/views.py` - Added debug logging to decide endpoint
- ✅ `scripts/run_simulation_without_sensors.py` - Added debug logging to trigger logic

## Next Steps

1. Restart Django
2. Run simulation
3. Watch iteration 6 output in BOTH terminals
4. Share the debug output with me

**The debug logs will reveal EXACTLY what's blocking AI decisions!** 🔍
