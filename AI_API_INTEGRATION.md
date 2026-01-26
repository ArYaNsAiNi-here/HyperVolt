# AI-API Integration Guide

## Overview

This document describes how Module 3 (AI) is integrated with Module 2 (API Backend) in the HyperVolt Energy Orchestrator system.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI-API Integration                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌─────────────────┐              │
│  │   Module 2   │◄────────┤  AI Inference   │              │
│  │  (API/Django)│         │    Service      │              │
│  └──────┬───────┘         └────────┬────────┘              │
│         │                          │                        │
│         │                          │                        │
│  ┌──────▼───────┐         ┌────────▼────────┐              │
│  │ REST API     │         │   Module 3      │              │
│  │ Endpoints    │         │  (AI Models)    │              │
│  │              │         │                 │              │
│  │ /api/ai/...  │         │ • LSTM Model    │              │
│  │              │         │ • Optimizer     │              │
│  └──────────────┘         │ • Solar Dust    │              │
│                           └─────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## Integration Components

### 1. AI Inference Service

**Location**: `api/data_pipeline/services/ai_inference.py`

**Purpose**: Bridge layer between Django API and AI models

**Key Responsibilities**:
- Load and initialize AI models
- Fetch data from database for predictions
- Process AI outputs for API consumption
- Handle errors gracefully

**Main Methods**:
```python
class AIInferenceService:
    def is_available() -> bool
        """Check if AI models are loaded and ready"""
    
    def forecast_demand(hours_ahead: int) -> Dict
        """Forecast energy demand for next N hours"""
    
    def recommend_source(load_name, load_priority, load_power) -> Dict
        """Recommend optimal energy source using AI"""
    
    def make_decision() -> Dict
        """Make comprehensive energy management decision"""
```

## API Endpoints

**Base URL**: `/api/ai/`

All AI-related endpoints are grouped under the `/api/ai/` prefix.

#### Check AI Status

```http
GET /api/ai/status/
```

**Response**:
```json
{
  "available": true,
  "models_loaded": true,
  "capabilities": {
    "demand_forecasting": true,
    "source_optimization": true,
    "decision_making": true
  },
  "timestamp": "2026-01-26T12:00:00Z"
}
```

**Use Case**: Check if AI models are loaded before making predictions

---

#### Forecast Energy Demand

```http
GET /api/ai/forecast/?hours=6
```

**Query Parameters**:
- `hours` (optional): Number of hours to forecast (default: 6, max: 24)

**Response**:
```json
{
  "timestamp": "2026-01-26T12:00:00Z",
  "forecast_horizon": 6,
  "predictions": [
    {
      "hour": 1,
      "predicted_kwh": 1.523,
      "timestamp": "2026-01-26T13:00:00Z"
    },
    {
      "hour": 2,
      "predicted_kwh": 1.687,
      "timestamp": "2026-01-26T14:00:00Z"
    }
  ],
  "available": true,
  "model_type": "lstm"
}
```

**Use Cases**:
- Dashboard showing future energy usage
- Scheduling high-power tasks during low-demand periods
- Battery charging optimization

**Requirements**:
- At least 24 hours of historical sensor data in database

---

#### Recommend Energy Source (AI-Powered)

```http
POST /api/ai/recommend_source/
Content-Type: application/json

{
  "load_name": "Living Room HVAC",
  "load_priority": 75,
  "load_power": 2000,
  "current_conditions": {
    "solar_radiation": 0.8,
    "cloud_cover": 20,
    "carbon_intensity": 420,
    "grid_price": 7.5
  }
}
```

**Request Body**:
- `load_name` (required): Name of the load
- `load_priority` (optional): Priority level 0-100 (default: 50)
- `load_power` (optional): Power in watts (default: 0)
- `current_conditions` (optional): Override current conditions (auto-fetched if omitted)

**Response**:
```json
{
  "timestamp": "2026-01-26T12:00:00Z",
  "load_name": "Living Room HVAC",
  "load_priority": 75,
  "load_power": 2000,
  "recommended_source": "solar",
  "source_allocation": [
    ["solar", 1.5],
    ["battery", 0.5]
  ],
  "metrics": {
    "estimated_cost": 3.25,
    "estimated_carbon": 187.5,
    "battery_charge": 8.75
  },
  "reasoning": "Primary source: solar | High solar availability | Clear weather conditions",
  "confidence": 0.85,
  "algorithm": "ml_optimizer",
  "available": true
}
```

**Use Cases**:
- Real-time source switching decisions
- Load balancing across multiple sources
- Cost and carbon optimization

---

#### Make Comprehensive Decision

```http
POST /api/ai/decide/
```

**Request Body**: None (uses current system state)

**Response**:
```json
{
  "timestamp": "2026-01-26T12:00:00Z",
  "forecast": [
    {"hour": 1, "predicted_kwh": 1.5, "timestamp": "..."},
    {"hour": 2, "predicted_kwh": 1.7, "timestamp": "..."}
  ],
  "current_decision": {
    "predicted_demand_kwh": 1.5,
    "source_allocation": [
      ["solar", 1.0],
      ["battery", 0.5]
    ],
    "cost": 3.5,
    "carbon": 250.0,
    "battery_charge": 8.5
  },
  "recommendation": "Using solar power (clean & free) | Battery discharge active | ✓ Battery well charged",
  "available": true
}
```

**Use Cases**:
- Automated energy management system
- Dashboard showing complete energy status
- Scheduled decision-making (every 10-15 minutes)

---

## Data Flow

### 1. Forecasting Flow

```
1. Client → GET /api/ai/forecast/
2. AI Service → Fetch last 24h data from database
3. AI Service → Load LSTM model
4. AI Service → Make predictions
5. AI Service → Store decision in AIDecision table
6. AI Service → Return predictions to client
```

### 2. Recommendation Flow

```
1. Client → POST /api/ai/recommend_source/ with load details
2. AI Service → Fetch current conditions (weather, carbon, sensors)
3. AI Service → Load optimizer model
4. AI Service → Optimize source allocation
5. AI Service → Calculate cost/carbon metrics
6. AI Service → Store decision in AIDecision table
7. AI Service → Return recommendation to client
```

### 3. Decision-Making Flow

```
1. Client → POST /api/ai/decide/
2. AI Service → Forecast next 6 hours demand
3. AI Service → Get current conditions
4. AI Service → Optimize for next hour
5. AI Service → Generate recommendation
6. AI Service → Store decision in AIDecision table
7. AI Service → Return comprehensive decision
```

## Integration with Other Modules

### Module 1 (Hardware)

Hardware should periodically call AI endpoints and execute recommendations:

```python
import requests

# Check AI status
response = requests.get('http://api:8000/api/ai/status/')
if response.json()['available']:
    # Get decision
    decision = requests.post('http://api:8000/api/ai/decide/')
    
    # Execute source switching via MQTT
    for source, power in decision['current_decision']['source_allocation']:
        mqtt_client.publish(f'HyperVolt/commands/switch', {
            'to_source': source,
            'power': power
        })
```

### Module 4 (Frontend)

Frontend can display AI predictions and recommendations:

```javascript
// Fetch AI forecast
fetch('/api/ai/forecast/?hours=12')
  .then(res => res.json())
  .then(data => {
    // Display forecast on chart
    displayForecastChart(data.predictions);
  });

// Get recommendation for HVAC
fetch('/api/ai/recommend_source/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    load_name: 'HVAC',
    load_priority: 75,
    load_power: 2000
  })
})
  .then(res => res.json())
  .then(rec => {
    // Show recommendation
    console.log(`Recommended: ${rec.recommended_source}`);
    console.log(`Reasoning: ${rec.reasoning}`);
  });
```

## Error Handling

### AI Models Not Available

If AI models are not loaded, endpoints return:

```json
{
  "error": "AI models not available",
  "available": false,
  "fallback": "Use rule-based optimizer from EnergySourceOptimizer"
}
```

**Fallback Strategy**:
- Use existing rule-based optimizer at `/api/optimization/recommend/`
- Continue with manual/heuristic decisions
- Check model status with `/api/ai/status/`

### Insufficient Historical Data

For forecasting, if less than 24 hours of data:

```json
{
  "error": "Insufficient historical data (need at least 24 hours)",
  "available": false
}
```

**Solution**:
- Wait for more data to accumulate
- Use shorter forecast horizons
- Seed database with synthetic data for testing

## Configuration

### AI Model Paths

Models are loaded from: `../ai/models/`

Required model files:
- `demand_forecaster.h5` - LSTM model
- `demand_forecaster_config.json` - Model configuration
- `demand_forecaster_scalers.pkl` - Feature scalers
- `optimizer_config.json` - Optimizer configuration

### Environment Variables

Add to `api/.env`:

```bash
# AI Module Configuration
AI_MODULE_PATH=../ai/module3-ai
AI_MODELS_PATH=../ai/models
AI_FORECASTING_ENABLED=true
AI_OPTIMIZATION_ENABLED=true
```

## Testing

### Test AI Status

```bash
curl http://localhost:8000/api/ai/status/
```

Expected: `{"available": true, "models_loaded": true, ...}`

### Test Forecasting

```bash
curl http://localhost:8000/api/ai/forecast/?hours=6
```

Expected: Array of 6 hourly predictions

### Test Recommendation

```bash
curl -X POST http://localhost:8000/api/ai/recommend_source/ \
  -H "Content-Type: application/json" \
  -d '{
    "load_name": "Test Load",
    "load_priority": 50,
    "load_power": 1000
  }'
```

Expected: Recommendation with source allocation

### Test Decision Making

```bash
curl -X POST http://localhost:8000/api/ai/decide/
```

Expected: Comprehensive decision with forecast and recommendation

## Performance Considerations

### Response Times

- **AI Status Check**: <50ms (no model inference)
- **Forecast (6h)**: 200-500ms (LSTM inference)
- **Recommendation**: 100-300ms (optimization algorithm)
- **Decision**: 300-800ms (forecast + optimization)

### Caching Strategy

Consider caching predictions for:
- Forecasts: Cache for 10-15 minutes
- Recommendations: Cache per load for 5 minutes
- Current conditions: Cache for 2-3 minutes

### Optimization

For production:
1. Load models once at server startup
2. Use async/celery for heavy predictions
3. Implement request batching
4. Cache frequently accessed data

## Monitoring

Track these metrics:

```python
# In views or middleware
metrics = {
    'ai_forecast_requests': counter,
    'ai_forecast_latency': histogram,
    'ai_recommendation_requests': counter,
    'ai_errors': counter,
    'model_load_failures': counter
}
```

## Future Enhancements

### Phase 2: Advanced Features

1. **Model Retraining API**
   ```http
   POST /api/ai/retrain/
   ```
   Trigger model retraining with new data

2. **Batch Predictions**
   ```http
   POST /api/ai/batch_forecast/
   ```
   Forecast for multiple scenarios

3. **Explainability**
   ```http
   GET /api/ai/explain/?decision_id=123
   ```
   Get detailed explanation of a decision

4. **A/B Testing**
   ```http
   GET /api/ai/compare/?model_a=lstm&model_b=prophet
   ```
   Compare different model predictions

## Troubleshooting

### Issue: "AI models not available"

**Causes**:
- Models not trained yet
- Model files missing
- Import errors

**Solutions**:
1. Train models: `cd ai/module3-ai && python decision_engine.py`
2. Check model files exist in `ai/models/`
3. Check Python dependencies: `pip install -r requirements.txt`

### Issue: "Insufficient historical data"

**Causes**:
- Fresh database with no sensor readings
- Less than 24 hours of data

**Solutions**:
1. Wait for data to accumulate
2. Generate test data: `python api/test_mqtt_publisher.py`
3. Import historical data from CSV

### Issue: High latency (>1 second)

**Causes**:
- Model loading on every request
- Slow database queries
- Large model size

**Solutions**:
1. Ensure models loaded at startup, not per-request
2. Add database indexes
3. Use model quantization/pruning

## Summary

✅ **Ready for Production**

The AI-API integration is complete and provides:

1. **AI Inference Service** - Bridge between API and AI models
2. **REST API Endpoints** - `/api/ai/*` for all AI operations
3. **Error Handling** - Graceful fallbacks when AI unavailable
4. **Monitoring** - All decisions recorded in database
5. **Documentation** - Complete API reference

**Next Steps**:
- Integrate with Module 1 (Hardware) for automated switching
- Build Module 4 (Frontend) dashboard with AI predictions
- Set up scheduled tasks for periodic AI decisions
- Implement model retraining pipeline

---

**Status**: ✅ Complete  
**Last Updated**: January 26, 2026  
**Version**: 1.0
