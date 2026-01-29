# HyperVolt Troubleshooting Guide - Frontend Not Updating & AI Not Responding

## Current Issue

Your simulation is running but:
- **API Success Rate: 0/18** - Sensor data is NOT being posted successfully to the API
- **AI Decisions: 0** - AI is not making any decisions
- **Frontend not updating** - No data reaches the frontend via WebSocket

## Root Cause Analysis

Based on the symptoms, one or more of these issues is present:

1. **Django Backend NOT Running** - Most likely cause
2. **Django running on wrong port** - Check if it's on 8000
3. **Django using `runserver` instead of `daphne`** - WebSocket won't work
4. **Redis NOT running** - WebSocket channels won't work
5. **Database migrations not run** - API will fail
6. **AI models not loaded** - Decisions won't work

## Step-by-Step Fix

### Step 1: Check if Django is Running

Open a terminal and run:

```powershell
curl http://localhost:8000/api/ai/status/
```

**If you get "Connection refused" or "Unable to connect":**
- Django is NOT running!
- Continue to Step 2

**If you get a JSON response:**
- Django IS running
- Skip to Step 3

### Step 2: Start Django Backend (WITH WebSocket Support)

**IMPORTANT:** You MUST use `daphne`, not `runserver`, for WebSocket support!

```powershell
# Terminal 1: Start Redis (required for WebSocket)
redis-server

# Terminal 2: Start Django with WebSocket support
cd D:\Projects\HyperVolt\api
..\. venv\Scripts\activate
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

You should see output like:
```
INFO     Starting server at tcp:port=8000:interface=0.0.0.0
INFO     HTTP/2 support not enabled (install the http2 and tls Twisted extras)
INFO     Configuring endpoint tcp:port=8000:interface=0.0.0.0
INFO     Listening on TCP address 0.0.0.0:8000
```

### Step 3: Run Database Migrations (First Time Only)

If this is your first time running the API:

```powershell
cd D:\Projects\HyperVolt\api
..\.venv\Scripts\python.exe manage.py migrate
```

### Step 4: Test the API

```powershell
cd D:\Projects\HyperVolt
..\.venv\Scripts\python.exe scripts\test_api.py
```

You should see:
```
✅ API is running!
✅ Sensor POST works!
✅ GET works!
✅ AI Decision works! (or ⚠️ AI models not available)
```

### Step 5: Check AI Models

If AI says "models not available":

```powershell
cd D:\Projects\HyperVolt\ai\module3-ai
..\..\. venv\Scripts\python.exe train_demand_model.py
```

This will train and save the AI models to `ai/models/`

### Step 6: Restart Django

After training models, restart Django (Ctrl+C in Terminal 2, then run daphne again)

### Step 7: Start the Frontend

```powershell
cd D:\Projects\HyperVolt\website
npm run dev
```

Open http://localhost:3000 in your browser

### Step 8: Run the Simulation (With Better Error Messages)

```powershell
cd D:\Projects\HyperVolt
..\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
```

Now you'll see detailed error messages if something fails!

## Quick Diagnostic Commands

### Check if Redis is Running

```powershell
redis-cli ping
```

Expected output: `PONG`

If not: `redis-server`

### Check if Django is Running

```powershell
curl http://localhost:8000/api/ai/status/
```

Expected: JSON response

If not: Start Django with `daphne`

### Check if Frontend is Running

Open browser: http://localhost:3000

Expected: HyperVolt dashboard

If not: `cd website && npm run dev`

### List All Running Processes

```powershell
# Check if Redis is running
Get-Process redis-server -ErrorAction SilentlyContinue

# Check if Python (Django) is running
Get-Process python -ErrorAction SilentlyContinue

# Check if Node (Frontend) is running
Get-Process node -ErrorAction SilentlyContinue
```

## Complete Startup Sequence

Run these in **separate terminal windows**:

```powershell
# Terminal 1: Redis
redis-server

# Terminal 2: Django Backend (WITH WebSocket)
cd D:\Projects\HyperVolt\api
..\.venv\Scripts\activate
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application

# Terminal 3: Frontend
cd D:\Projects\HyperVolt\website
npm run dev

# Terminal 4: Simulation
cd D:\Projects\HyperVolt
..\.venv\Scripts\python.exe scripts\run_simulation_without_sensors.py
```

## What Each Terminal Should Show

### Terminal 1 (Redis)
```
[xxxxx] Ready to accept connections
```

### Terminal 2 (Django)
```
INFO     Starting server at tcp:port=8000:interface=0.0.0.0
INFO     Listening on TCP address 0.0.0.0:8000
```

### Terminal 3 (Frontend)
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- info  Loaded env from D:\Projects\HyperVolt\website\.env.local
```

### Terminal 4 (Simulation)
```
API Success Rate: 5/5  ← Should be increasing!
AI Decisions: 1         ← Should increase every 30 seconds
```

## Verification Checklist

- [ ] Redis is running (`redis-cli ping` returns `PONG`)
- [ ] Django is running (`curl http://localhost:8000/api/ai/status/` works)
- [ ] Django using `daphne` (NOT `runserver`)
- [ ] Frontend is running (http://localhost:3000 loads)
- [ ] API Success Rate is increasing (not 0)
- [ ] AI Decisions count is increasing
- [ ] Frontend shows live data updates

## Common Mistakes

### ❌ Using `python manage.py runserver`
**Problem:** WebSocket won't work!
**Solution:** Use `daphne` instead

### ❌ Forgetting to start Redis
**Problem:** WebSocket channels won't work
**Solution:** `redis-server` in a separate terminal

### ❌ Not activating virtual environment
**Problem:** Wrong Python packages
**Solution:** `..\. venv\Scripts\activate` before running Python commands

### ❌ Wrong directory
**Problem:** Commands fail with "file not found"
**Solution:** Check you're in the right directory with `pwd`

## Still Not Working?

Run the full diagnostic:

```powershell
cd D:\Projects\HyperVolt
..\.venv\Scripts\python.exe scripts\diagnose_system.py
```

This will check **everything** and tell you exactly what's wrong.

## Expected Behavior

When everything is working correctly:

1. **Simulation Terminal** shows:
   - `API Success Rate: X/X` (all successful, not 0)
   - `AI Decisions: N` (increasing every 30 seconds)
   - No error messages

2. **Django Terminal** shows:
   - `HTTP GET /api/sensor-readings/` requests
   - `HTTP POST /api/predictions/decide/` requests
   - `WebSocket CONNECT /ws/sensors/` connections

3. **Frontend Browser** shows:
   - 3D room with changing light
   - Energy flow diagram updating
   - Charts showing live data
   - AI Strategy Narrator logging decisions

4. **Browser Console** (F12) shows:
   - `WebSocket connected`
   - `Received sensor data: {…}`
   - No error messages

## Need More Help?

1. Check `Simulation_Guidelines.md` for full setup instructions
2. Check `api/MODULE2_README.md` for Django API details
3. Check `ai/MODULE3_SUMMARY.md` for AI module details
4. Run `python scripts/diagnose_system.py` for automated diagnosis

---

**Built with ❤️ by HyperHawks Team**
