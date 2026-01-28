# AI Inference Service Integration Guide

## Overview

This guide explains the enhanced AI inference service in HyperVolt, including dynamic user preferences, sensor data switching, MQTT integration, and model retraining capabilities.

## Key Features

### 1. Dynamic User Preference Weights

The AI optimizer now reads user preferences from the database to adjust optimization priorities.

**Database Configuration:**
```python
from api.data_pipeline.models import UserPreferences

# Set cost priority (0-100)
UserPreferences.objects.create(
    preference_key='cost_priority',
    preference_value=70  # 70% cost, 30% carbon
)
```

### 2. Sensor Data Switching

Switch between simulation mode (for testing) and real hardware mode (for production).

**Simulation Mode File:** `api/data/simulation_sensors.csv`

**LDR Value Guide:**
- 4000+: Bright sunny day → AI recommends Solar
- 2000-4000: Cloudy day → AI may recommend Hybrid
- 0-500: Nighttime → AI recommends Grid or Battery

**Switch to Real Mode:** In `ai_inference.py` set `USE_SIMULATION_FILE = False`

### 3. MQTT Integration

**Topic:** `HyperVolt/commands/control`

The AI automatically publishes decisions for hardware actuation.

### 4. Model Retraining

**Endpoint:** `POST /api/predictions/retrain/`

Retrains models with recent database data.

## API Endpoints

- `GET /api/predictions/status/` - Check AI availability
- `GET /api/predictions/forecast/?hours=6` - Forecast demand
- `POST /api/predictions/recommend_source/` - Get source recommendation
- `POST /api/predictions/decide/` - Make decision and publish to MQTT
- `POST /api/predictions/retrain/` - Retrain models

## Testing Workflow

1. Edit `api/data/simulation_sensors.csv` with test values
2. Start Django server
3. Call API endpoints
4. Verify recommendations change based on LDR values
5. Switch to real sensors when hardware is ready

For detailed information, see README.md
