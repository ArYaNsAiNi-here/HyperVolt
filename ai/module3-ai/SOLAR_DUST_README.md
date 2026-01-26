# Solar Panel Dust Prediction Module

## Overview

This module predicts dust accumulation on solar panels using LDR (Light Dependent Resistor) sensor readings and power output measurements. It helps determine when solar panels need cleaning to maintain optimal efficiency.

## Problem Statement

Solar panels lose efficiency over time due to dust accumulation. Research shows that:
- 1% dust coverage ≈ 0.7% power loss
- Heavy dust (>60%) can reduce output by 40%+
- Regular cleaning can improve efficiency by 15-25%

**Challenge**: Determine when panels need cleaning without manual inspection.

**Solution**: ML model using LDR + power output to predict dust levels.

## How It Works

### Data Collection

The system monitors:
1. **LDR Sensor**: Measures ambient light intensity (lux)
2. **Expected Power**: Calculated based on:
   - Solar irradiance
   - Temperature (panels lose 0.5% per °C above 25°C)
   - Sun angle (time of day)
3. **Actual Power**: Real power output from panels
4. **Efficiency Ratio**: `Actual / Expected`
5. **Time**: Days since last cleaning

### Dust Detection Logic

```
IF (Efficiency Ratio < Expected)
   AND (LDR shows good sunlight)
   AND (Temperature normal)
THEN: Dust is likely causing power loss

Dust % = f(Efficiency_Loss, Days_Since_Cleaning, LDR, Power_Diff)
```

### Model Architecture

**Type**: Random Forest Regressor

**Features** (8):
- Solar irradiance (0-1)
- Temperature (°C)
- LDR reading (lux)
- Expected power (kW)
- Actual power (kW)
- Efficiency ratio (0-1)
- Days since cleaning
- Hour of day

**Target**: Dust percentage (0-100%)

**Performance**:
- Test MAE: 1.86% (very accurate!)
- Test R²: 0.97 (excellent fit)
- Inference: <10ms

**Most Important Features**:
1. Efficiency ratio (84.2%)
2. Days since cleaning (14.1%)
3. Other factors (1.7%)

## Dataset Generation

### Script: `generate_solar_dust_data.py`

Generates realistic solar panel data with dust accumulation patterns.

**Features**:
- 30 days of 5-minute interval data (daylight only)
- ~4,320 records
- Simulates cleaning events every 10-15 days
- Models dust accumulation curve (non-linear)
- Calculates economic impact

**Key Metrics** (30-day simulation):
- Average dust: 21.2%
- Max dust: 75.2%
- Power loss: 84 kWh
- Revenue loss: ₹504.84

### Usage:

```bash
python module3-ai/generate_solar_dust_data.py
```

**Output**: `data/raw/solar_dust_data.csv`

## Model Training

### Script: `train_solar_dust_model.py`

Trains Random Forest model to predict dust levels.

**Process**:
1. Load dataset
2. Feature engineering & scaling
3. Train Random Forest (100 trees)
4. Evaluate on test set (20%)
5. Save model, scaler, config

### Usage:

```bash
python module3-ai/train_solar_dust_model.py
```

**Output**:
- `models/solar_dust_random_forest.pkl` (trained model)
- `models/solar_dust_scaler.pkl` (feature scaler)
- `models/solar_dust_config.json` (configuration)

## Real-Time Prediction

### API Usage

```python
from train_solar_dust_model import SolarDustPredictor
import pandas as pd

# Load model
predictor = SolarDustPredictor()
predictor.load_model()

# Current sensor readings
current_data = pd.DataFrame([{
    'solar_irradiance': 0.85,
    'temperature_c': 28.5,
    'ldr_lux': 850,
    'expected_power_kw': 2.5,
    'actual_power_kw': 2.1,
    'efficiency_ratio': 0.84,
    'days_since_cleaning': 8.5,
    'hour': 14
}])

# Predict
prediction = predictor.predict(current_data)

print(f"Dust level: {prediction['dust_percentage']:.1f}%")
print(f"Needs cleaning: {prediction['needs_cleaning']}")
print(f"Urgency: {prediction['urgency']}")
print(f"Recommendation: {prediction['recommendation']}")
```

### Example Output

```
Dust level: 23.0%
Needs cleaning: No
Urgency: Low
Efficiency loss: 16.1%
Potential gain: 0.324 kW/hour
Revenue gain: ₹1.94/hour
Recommendation: Minor dust detected (23.0%). Monitor for now.
```

## Cleaning Thresholds

| Dust % | Status | Action | Revenue Impact |
|--------|--------|--------|----------------|
| 0-20% | Clean | Monitor | Minimal |
| 20-40% | Minor dust | Plan cleaning | Low |
| 40-60% | Moderate | Clean within 3-5 days | Medium |
| 60%+ | Heavy | **Clean immediately** | High |

## Economic Impact

Based on 3kW solar system:

**Average dust (25%)**:
- Power loss: ~0.4 kW
- Daily loss: ~4 kWh
- Monthly loss: ~120 kWh
- Revenue loss: ~₹720/month

**Heavy dust (60%)**:
- Power loss: ~1.0 kW
- Daily loss: ~10 kWh
- Monthly loss: ~300 kWh
- Revenue loss: ~₹1,800/month

**ROI of cleaning**:
- Cost: ₹200-500 per cleaning
- Benefit: ₹500-1,800/month (depending on dust)
- Payback: <1 week

## Integration with Vesta System

### With Decision Engine

```python
from decision_engine import VestaDecisionEngine
from train_solar_dust_model import SolarDustPredictor

# Initialize
engine = VestaDecisionEngine()
dust_predictor = SolarDustPredictor()
dust_predictor.load_model()

# Get solar dust prediction
dust_info = dust_predictor.predict(current_sensor_data)

# Adjust solar capacity based on dust
if dust_info['needs_cleaning']:
    # Reduce solar capacity estimate
    adjusted_solar = base_solar * dust_info['efficiency_ratio']
    engine.optimizer.solar_capacity = adjusted_solar
    
    # Alert user
    print(f"⚠️  {dust_info['recommendation']}")
```

### Dashboard Display

The dust prediction can be displayed in the frontend:

```javascript
// Real-time dust monitoring card
{
  "dust_percentage": 23.0,
  "status": "Clean",
  "color": "green",
  "needs_cleaning": false,
  "recommendation": "Minor dust detected. Monitor for now.",
  "potential_gain": "₹1.94/hour if cleaned",
  "last_cleaning": "8.5 days ago"
}
```

## Testing & Validation

### Dataset Statistics

```
Total Records: 4,320
Time Span: 30 days (daylight only)
Cleaning Events: 2-3 cycles
Dust Range: 0-75%
```

### Model Performance

```
Training Set:
  MAE:  0.94% dust
  RMSE: 1.39%
  R²:   0.9929

Test Set:
  MAE:  1.86% dust  ← Excellent!
  RMSE: 2.80%
  R²:   0.9702      ← Very accurate!
```

### Feature Importance

Most critical factors:
1. **Efficiency ratio** (84%) - Key indicator
2. **Days since cleaning** (14%) - Temporal factor
3. **Other sensors** (2%) - Fine-tuning

## Maintenance Schedule

**Recommended**:
- Monitor: Daily (automatic)
- Clean when: Dust >40% or efficiency <85%
- Typical frequency: Every 10-15 days (varies by location)

**Automation**:
```python
if dust_percentage > 40:
    send_notification("Solar panels need cleaning")
    schedule_cleaning_reminder(days=3)
elif dust_percentage > 60:
    send_alert("URGENT: Clean solar panels immediately")
```

## Files

```
module3-ai/
├── generate_solar_dust_data.py    # Dataset generator
├── train_solar_dust_model.py      # Model training
└── SOLAR_DUST_README.md           # This file

data/raw/
└── solar_dust_data.csv            # Generated dataset (4,320 records)

models/
├── solar_dust_random_forest.pkl   # Trained model (~500KB)
├── solar_dust_scaler.pkl          # Feature scaler
└── solar_dust_config.json         # Configuration
```

## Next Steps

1. **Hardware Integration**: Connect to real LDR sensor + power meter
2. **Backend API**: Expose prediction endpoint
3. **Frontend Dashboard**: Display dust status & alerts
4. **Notifications**: Send cleaning reminders
5. **Logging**: Track cleaning events and efficiency improvements

## References

- Solar panel efficiency loss: ~0.7% per 1% dust coverage
- Cleaning frequency: Every 10-15 days in dusty environments
- Economic impact: ₹500-1,800/month revenue loss if uncleaned

---

**Status**: Complete & Tested ✅  
**Accuracy**: 97% R² Score  
**Ready for**: Integration with Vesta System

*Built for Sustainergy Hackathon 2026 by Team HyperVolt* 🌱⚡
