# Energy Source Optimization Feature

## Overview

This feature provides intelligent energy source selection and switching recommendations based on availability, weather conditions, sensor data, and load priorities. It's designed to work seamlessly with Module 3 (AI) while providing rule-based fallback logic.

## Key Components

### 1. Energy Source Optimizer Service

**Location**: `data_pipeline/services/energy_optimizer.py`

**Purpose**: Core logic for selecting optimal energy sources based on:
- Grid availability and carbon intensity
- Weather conditions (for solar viability)
- Sensor readings (LDR for light intensity)
- Load priorities (HVAC prioritized over entertainment)
- User preferences

**Key Methods**:
- `gather_context()` - Collects all relevant data for decision-making
- `recommend_source_for_load()` - Main recommendation engine
- `should_switch_source()` - Determines if switching is beneficial
- `get_optimal_source_distribution()` - Load balancing across sources

**Priority Levels**:
- `PRIORITY_CRITICAL = 100` - Security, communication systems
- `PRIORITY_HIGH = 75` - HVAC, refrigeration
- `PRIORITY_MEDIUM = 50` - Lighting, computing
- `PRIORITY_LOW = 25` - Entertainment, decorative

**Source Preferences** (higher is better):
- Solar: 100 (most preferred - free, clean)
- Battery: 75 (stored clean energy)
- Grid: 50 (depends on carbon intensity)
- Generator: 25 (expensive, dirty)

### 2. Database Models

#### Load Model
Tracks electrical loads with their characteristics:

```python
Load(
    name="Living Room HVAC",
    category='hvac',
    priority=75,  # High priority
    rated_power=2000,  # Watts
    is_active=True,
    current_source='grid',
    can_defer=False,
    min_runtime=30  # minutes
)
```

**Fields**:
- `name` - Unique identifier
- `category` - Type (hvac, lighting, appliance, etc.)
- `priority` - 25/50/75/100 (Low/Medium/High/Critical)
- `rated_power` - Power consumption in watts
- `current_source` - Currently used energy source
- `can_defer` - Can be scheduled for off-peak times
- `min_runtime` - Minimum continuous operation time

#### SourceSwitchEvent Model
Audit trail for all switching events:

```python
SourceSwitchEvent(
    load=hvac_load,
    from_source='grid',
    to_source='solar',
    reason='High solar availability',
    triggered_by='ai',  # or 'manual', 'automatic', 'emergency'
    success=True
)
```

## API Endpoints

### Load Management

#### List All Loads
```
GET /api/loads/
```

Response:
```json
[
  {
    "id": 1,
    "name": "Living Room HVAC",
    "category": "hvac",
    "priority": 75,
    "priority_display": "High",
    "rated_power": 2000,
    "is_active": true,
    "current_source": "grid"
  }
]
```

#### Get Active Loads
```
GET /api/loads/active/
```

#### Get High Priority Loads
```
GET /api/loads/high_priority/
```

Returns loads with priority >= 75.

#### Get Source Recommendation for Load
```
POST /api/loads/{id}/recommend_source/
```

Response:
```json
{
  "recommended_source": "solar",
  "load_name": "Living Room HVAC",
  "load_priority": 75,
  "load_power": 2000,
  "reasoning": "Selected solar for Living Room HVAC. Clear weather favors solar High light intensity detected",
  "confidence": 0.7,
  "scores": {
    "solar": 135,
    "battery": 90,
    "grid": 50
  },
  "algorithm": "rule_based",
  "context": {...}
}
```

#### Check if Switch Recommended
```
POST /api/loads/{id}/check_switch/
```

Response:
```json
{
  "should_switch": true,
  "current_source": "grid",
  "recommended_source": "solar",
  "reasoning": "Selected solar for Living Room HVAC...",
  "score_improvement": 85
}
```

### Energy Optimization

#### Get Optimization Context
```
GET /api/optimization/context/
```

Returns all relevant data for decision-making:
```json
{
  "timestamp": "2026-01-26T10:00:00Z",
  "energy_sources": {
    "solar": {
      "available": true,
      "capacity": 5000,
      "current_output": 2000,
      "priority": 100
    },
    "battery": {...},
    "grid": {...}
  },
  "weather": {
    "temperature": 28,
    "cloud_cover": 20,
    "condition": "Clear"
  },
  "carbon_intensity": {
    "value": 450,
    "unit": "gCO2eq/kWh"
  },
  "sensor_data": {
    "ldr": {"value": 750, "unit": "lux"},
    "current": {...}
  }
}
```

#### Get Source Recommendation
```
POST /api/optimization/recommend/

Body:
{
  "load_name": "HVAC Living Room",
  "load_priority": 75,
  "load_power": 2000
}
```

Response: Same as load-specific recommendation above.

#### Get Load Distribution
```
GET /api/optimization/distribution/
```

Returns optimal distribution of loads across sources:
```json
{
  "timestamp": "2026-01-26T10:00:00Z",
  "available_sources": ["solar", "battery", "grid"],
  "recommendations": [
    {
      "load_category": "HVAC",
      "priority": 75,
      "recommended_source": "solar",
      "fallback_source": "battery"
    },
    {
      "load_category": "Lighting",
      "priority": 50,
      "recommended_source": "grid",
      "fallback_source": "solar"
    }
  ]
}
```

#### Execute Source Switch
```
POST /api/optimization/execute_switch/

Body:
{
  "load_id": 1,
  "to_source": "solar",
  "reason": "High solar availability",
  "triggered_by": "ai"
}
```

Response:
```json
{
  "message": "Switch recorded successfully",
  "switch_event": {
    "id": 1,
    "load": 1,
    "from_source": "grid",
    "to_source": "solar",
    "reason": "High solar availability",
    "triggered_by": "ai",
    "timestamp": "2026-01-26T10:00:00Z"
  },
  "mqtt_command": {
    "topic": "HyperVolt/commands/load_1",
    "payload": {
      "command": "switch_source",
      "load_id": 1,
      "load_name": "Living Room HVAC",
      "to_source": "solar",
      "timestamp": "2026-01-26T10:00:00Z"
    }
  },
  "note": "Module 1 (Hardware) should subscribe to MQTT commands and execute the physical switch"
}
```

### Switch Event History

#### List Switch Events
```
GET /api/switch-events/
```

#### Recent Switch Events
```
GET /api/switch-events/recent/?hours=24
```

#### Events by Load
```
GET /api/switch-events/by_load/?load_id=1
```

## Decision Logic

### Rule-Based Algorithm (Current)

The system uses a scoring algorithm:

1. **Base Score**: Each source has a preference score
   - Solar: 100
   - Battery: 75
   - Grid: 50
   - Generator: 25

2. **Weather Adjustments**:
   - Clear weather (cloud cover < 30%): +20 for solar
   - Partly cloudy (30-60%): +10 for solar

3. **Sensor Adjustments**:
   - High LDR reading (> 500 lux): +15 for solar

4. **Carbon Intensity**:
   - High carbon (> 500 gCO2/kWh): -30 for grid
   - Low carbon (< 300 gCO2/kWh): +20 for grid

5. **Load Priority**:
   - High priority loads: +15 for battery

6. **Selection**: Source with highest score wins

### Module 3 (AI) Integration Points

The system is designed for easy AI enhancement:

1. **Override `recommend_source_for_load()`**: Module 3 can implement ML-based recommendations
2. **Use `gather_context()`**: Provides all necessary input features
3. **Enhance `get_optimal_source_distribution()`**: Implement sophisticated load balancing
4. **Record Decisions**: All decisions stored in `AIDecision` model for training

## Usage Examples

### Example 1: Set Up Loads

```python
from data_pipeline.models import Load

# Create HVAC load
hvac = Load.objects.create(
    name='Living Room HVAC',
    category='hvac',
    priority=75,  # High priority
    rated_power=2000,
    is_active=True,
    current_source='grid'
)

# Create lighting load
lights = Load.objects.create(
    name='Living Room Lights',
    category='lighting',
    priority=50,  # Medium priority
    rated_power=200,
    is_active=True,
    current_source='grid',
    can_defer=True
)
```

### Example 2: Get Recommendations

```python
from data_pipeline.services import EnergySourceOptimizer

optimizer = EnergySourceOptimizer()

# For HVAC
recommendation = optimizer.recommend_source_for_load(
    load_name='Living Room HVAC',
    load_priority=75,
    load_power=2000
)

print(f"Recommended: {recommendation['recommended_source']}")
print(f"Reasoning: {recommendation['reasoning']}")
```

### Example 3: Check if Switch Needed

```python
# Check if we should switch HVAC from grid to solar
switch_check = optimizer.should_switch_source(
    current_source='grid',
    load_name='Living Room HVAC',
    load_priority=75
)

if switch_check['should_switch']:
    print(f"Switch to {switch_check['recommended_source']}")
    print(f"Improvement: {switch_check['score_improvement']}")
```

### Example 4: Via API

```bash
# Get context
curl http://localhost:8000/api/optimization/context/

# Get recommendation
curl -X POST http://localhost:8000/api/optimization/recommend/ \
  -H "Content-Type: application/json" \
  -d '{
    "load_name": "HVAC",
    "load_priority": 75,
    "load_power": 2000
  }'

# Execute switch
curl -X POST http://localhost:8000/api/optimization/execute_switch/ \
  -H "Content-Type: application/json" \
  -d '{
    "load_id": 1,
    "to_source": "solar",
    "reason": "High solar availability",
    "triggered_by": "manual"
  }'
```

## Integration with Other Modules

### Module 1 (Hardware)

**Subscribe to MQTT Commands**:
```python
# Topic: HyperVolt/commands/load_{id}
# Payload:
{
  "command": "switch_source",
  "load_id": 1,
  "load_name": "Living Room HVAC",
  "to_source": "solar",
  "timestamp": "2026-01-26T10:00:00Z"
}
```

Module 1 should:
1. Subscribe to `HyperVolt/commands/#`
2. Execute physical relay switching
3. Publish confirmation back to API

### Module 3 (AI)

**Enhanced Decision Making**:
```python
from data_pipeline.services import EnergySourceOptimizer
from your_ml_model import predict_optimal_source

class AIEnergyOptimizer(EnergySourceOptimizer):
    def recommend_source_for_load(self, load_name, load_priority, load_power):
        # Gather context using parent method
        context = self.gather_context()
        
        # Use ML model for prediction
        features = self._prepare_features(context, load_priority, load_power)
        ml_recommendation = predict_optimal_source(features)
        
        # Return with higher confidence
        return {
            'recommended_source': ml_recommendation,
            'confidence': 0.95,
            'algorithm': 'ml',
            'context': context
        }
```

### Module 4 (Frontend)

**Real-time Monitoring**:
- Connect to WebSocket for live updates
- Display current source for each load
- Show optimization recommendations
- Visualize energy flow

## Configuration

### Energy Source Setup

```python
from data_pipeline.models import EnergySource

# Configure available sources
EnergySource.objects.create(
    source_type='solar',
    is_available=True,
    capacity=5000,  # 5kW system
    priority=100
)

EnergySource.objects.create(
    source_type='battery',
    is_available=True,
    capacity=3000,  # 3kWh battery
    priority=75
)
```

### User Preferences

```python
from data_pipeline.models import UserPreferences

UserPreferences.objects.create(
    preference_key='comfort_level',
    preference_value={'min_temp': 22, 'max_temp': 26}
)

UserPreferences.objects.create(
    preference_key='cost_optimization',
    preference_value={'priority': 'balanced'}  # 'cost', 'comfort', 'balanced'
)
```

## Testing

Run validation tests:
```bash
python validate_module2.py
```

Test optimization service:
```bash
python manage.py shell
>>> from data_pipeline.services import EnergySourceOptimizer
>>> optimizer = EnergySourceOptimizer()
>>> context = optimizer.gather_context()
>>> print(context.keys())
```

## Notes for Module 3 (AI)

**Ready-to-Use Features**:
- ✅ Context gathering (all sensor + API data)
- ✅ Decision recording (for training data)
- ✅ Load priority system
- ✅ Source preference framework
- ✅ API endpoints for integration

**What to Enhance**:
- Replace rule-based scoring with ML model
- Implement sophisticated load balancing
- Add demand forecasting
- Optimize for cost, carbon, or user-defined goals
- Learn from historical switch events

**Entry Points**:
- Override `EnergySourceOptimizer.recommend_source_for_load()`
- Use `gather_context()` for feature engineering
- Access historical data via models
- Store ML decisions in `AIDecision` model

---

**Status**: ✅ Complete and ready for Module 3 integration  
**Tested**: All models, services, and API endpoints validated  
**Documentation**: Full API reference and usage examples provided
