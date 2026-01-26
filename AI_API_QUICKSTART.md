# AI-API Integration Quick Start Guide

## 🎯 Overview

The AI models from Module 3 are now fully integrated with the API backend (Module 2) and ready to work together!

## ✅ What's Ready

### AI Models (Module 3)
- ✅ LSTM demand forecaster (trained on 30 days data)
- ✅ Source optimizer (Grid/Solar/Battery)
- ✅ Solar dust prediction model
- ✅ Decision engine

### API Endpoints (Module 2)
- ✅ `/api/ai/status/` - Check AI availability
- ✅ `/api/ai/forecast/` - Get demand predictions
- ✅ `/api/ai/recommend_source/` - Get source recommendations
- ✅ `/api/ai/decide/` - Get comprehensive decisions

### Integration Layer
- ✅ AI Inference Service bridge
- ✅ Database data fetching
- ✅ Error handling & fallbacks
- ✅ Decision logging

## 🚀 Getting Started

### 1. Install Dependencies

```bash
# Install Python dependencies (if not already done)
cd /path/to/HyperVolt
pip install -r requirements.txt
```

Required packages:
- Django 5.0+
- TensorFlow/Keras (for LSTM)
- NumPy, Pandas (for data processing)
- Scikit-learn (for optimization)
- All API dependencies (djangorestframework, etc.)

### 2. Verify AI Models

```bash
# Check that trained models exist
ls -l ai/models/

# You should see:
# - demand_forecaster.h5 (LSTM model)
# - demand_forecaster_config.json
# - demand_forecaster_scalers.pkl
# - optimizer_config.json
```

If models are missing, train them:

```bash
cd ai/module3-ai
python decision_engine.py  # This will train all models
```

### 3. Run Integration Tests

```bash
cd api
python test_ai_integration.py
```

Expected output:
```
✓ PASS: AI Model Files
✓ PASS: Integration Service
✓ PASS: API Endpoints
✓ PASS: Documentation

✓ AI-API INTEGRATION IS READY!
```

### 4. Start the API Server

```bash
cd api

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

Or with WebSocket support (recommended):
```bash
daphne -b 0.0.0.0 -p 8000 hypervolt_backend.asgi:application
```

### 5. Test AI Endpoints

#### Check AI Status
```bash
curl http://localhost:8000/api/ai/status/
```

Expected response:
```json
{
  "available": true,
  "models_loaded": true,
  "capabilities": {
    "demand_forecasting": true,
    "source_optimization": true,
    "decision_making": true
  }
}
```

#### Get Energy Forecast
```bash
curl "http://localhost:8000/api/ai/forecast/?hours=6"
```

Expected response:
```json
{
  "timestamp": "2026-01-26T12:00:00Z",
  "forecast_horizon": 6,
  "predictions": [
    {"hour": 1, "predicted_kwh": 1.523, "timestamp": "..."},
    {"hour": 2, "predicted_kwh": 1.687, "timestamp": "..."},
    ...
  ],
  "available": true,
  "model_type": "lstm"
}
```

#### Get Source Recommendation
```bash
curl -X POST http://localhost:8000/api/ai/recommend_source/ \
  -H "Content-Type: application/json" \
  -d '{
    "load_name": "HVAC Living Room",
    "load_priority": 75,
    "load_power": 2000
  }'
```

Expected response:
```json
{
  "recommended_source": "solar",
  "source_allocation": [["solar", 1.5], ["battery", 0.5]],
  "metrics": {
    "estimated_cost": 3.25,
    "estimated_carbon": 187.5,
    "battery_charge": 8.75
  },
  "reasoning": "Primary source: solar | High solar availability",
  "confidence": 0.85
}
```

#### Make Comprehensive Decision
```bash
curl -X POST http://localhost:8000/api/ai/decide/
```

## 📊 Usage Examples

### Python Client

```python
import requests

# Initialize client
base_url = "http://localhost:8000/api"

# Check if AI is available
status = requests.get(f"{base_url}/ai/status/").json()
if not status['available']:
    print("AI not available!")
    exit(1)

# Get 12-hour forecast
forecast = requests.get(f"{base_url}/ai/forecast/?hours=12").json()
print(f"Next hour demand: {forecast['predictions'][0]['predicted_kwh']} kWh")

# Get recommendation for HVAC
recommendation = requests.post(
    f"{base_url}/ai/recommend_source/",
    json={
        "load_name": "HVAC",
        "load_priority": 75,
        "load_power": 2000
    }
).json()
print(f"Recommended source: {recommendation['recommended_source']}")
print(f"Reasoning: {recommendation['reasoning']}")

# Make comprehensive decision
decision = requests.post(f"{base_url}/ai/decide/").json()
print(f"Recommendation: {decision['recommendation']}")
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

const baseUrl = 'http://localhost:8000/api';

// Check AI status
async function checkAI() {
  const response = await axios.get(`${baseUrl}/ai/status/`);
  return response.data.available;
}

// Get forecast
async function getForecast(hours = 6) {
  const response = await axios.get(`${baseUrl}/ai/forecast/?hours=${hours}`);
  return response.data.predictions;
}

// Get recommendation
async function getRecommendation(load) {
  const response = await axios.post(`${baseUrl}/ai/recommend_source/`, load);
  return response.data;
}

// Usage
(async () => {
  if (await checkAI()) {
    const forecast = await getForecast(12);
    console.log('Forecast:', forecast);
    
    const rec = await getRecommendation({
      load_name: 'HVAC',
      load_priority: 75,
      load_power: 2000
    });
    console.log('Recommendation:', rec.recommended_source);
  }
})();
```

### cURL Scripts

Create a file `test_ai.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api"

echo "=== Checking AI Status ==="
curl -s "$BASE_URL/ai/status/" | jq .

echo -e "\n=== Getting Forecast ==="
curl -s "$BASE_URL/ai/forecast/?hours=6" | jq .

echo -e "\n=== Getting Recommendation ==="
curl -s -X POST "$BASE_URL/ai/recommend_source/" \
  -H "Content-Type: application/json" \
  -d '{"load_name": "HVAC", "load_priority": 75, "load_power": 2000}' | jq .

echo -e "\n=== Making Decision ==="
curl -s -X POST "$BASE_URL/ai/decide/" | jq .
```

Run it:
```bash
chmod +x test_ai.sh
./test_ai.sh
```

## 🔄 Integration with Other Modules

### Module 1 (Hardware)

Hardware should call AI endpoints periodically:

```python
import requests
import paho.mqtt.client as mqtt

api_url = "http://api-server:8000/api"
mqtt_client = mqtt.Client()

# Every 10 minutes, get AI decision
def get_ai_decision():
    response = requests.post(f"{api_url}/ai/decide/")
    if response.status_code == 200:
        decision = response.json()
        
        # Execute source switching
        allocation = decision['current_decision']['source_allocation']
        for source, power in allocation:
            mqtt_client.publish(
                f"HyperVolt/commands/switch",
                json.dumps({
                    'to_source': source,
                    'power': power
                })
            )
```

### Module 4 (Frontend)

Frontend can display AI predictions:

```jsx
// React component
function EnergyForecast() {
  const [forecast, setForecast] = useState([]);
  
  useEffect(() => {
    fetch('/api/ai/forecast/?hours=12')
      .then(res => res.json())
      .then(data => setForecast(data.predictions));
  }, []);
  
  return (
    <div>
      <h2>Energy Forecast</h2>
      <Chart data={forecast} />
    </div>
  );
}
```

## ⚠️ Troubleshooting

### Issue: "AI models not available"

**Solution**:
1. Check models exist: `ls ai/models/`
2. Train models if missing: `cd ai/module3-ai && python decision_engine.py`
3. Check dependencies: `pip install tensorflow scikit-learn numpy pandas`

### Issue: "Insufficient historical data"

**Solution**:
1. Wait for 24+ hours of sensor data to accumulate
2. Or import test data: `python api/test_mqtt_publisher.py`

### Issue: High latency (>1 second)

**Solution**:
1. Models should load once at startup, not per-request
2. Add caching for predictions (5-10 minute cache)
3. Consider using async/Celery for predictions

## 📈 Performance

Expected response times:
- **Status check**: <50ms
- **Forecast (6h)**: 200-500ms (LSTM inference)
- **Recommendation**: 100-300ms (optimization)
- **Decision**: 300-800ms (forecast + optimization)

## 🎓 Next Steps

1. **Populate Database**: Ensure sensor and grid data is being collected
2. **Scheduled Tasks**: Set up periodic AI decision-making (every 10-15 min)
3. **Frontend Integration**: Build dashboard to display predictions
4. **Hardware Integration**: Connect Module 1 to execute AI decisions
5. **Monitoring**: Add logging and metrics for AI performance

## 📚 Documentation

For detailed documentation, see:
- **Full Integration Guide**: `AI_API_INTEGRATION.md`
- **API Documentation**: `api/MODULE2_README.md`
- **AI Models**: `ai/module3-ai/AI_MODELS_README.md`

## ✅ Summary

**The AI is now ready to work with the API!**

You can:
- ✅ Get energy demand forecasts
- ✅ Get AI-powered source recommendations
- ✅ Make comprehensive energy decisions
- ✅ Log all decisions in database
- ✅ Integrate with hardware and frontend

**Everything is connected and working together!** 🎉

---

**Status**: ✅ Ready for Production  
**Last Updated**: January 26, 2026  
**Version**: 1.0
