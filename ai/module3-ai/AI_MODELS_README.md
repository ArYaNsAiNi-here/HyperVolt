# Module 3 - Phase 2: AI Model Training

## Overview

This phase implements the AI "brain" for the Vesta Energy Orchestrator with:
1. **LSTM Demand Forecasting** - Predicts energy consumption 6 hours ahead
2. **Source Optimization** - Decides Grid vs Solar vs Battery
3. **Decision Engine** - Combines both for real-time intelligent decisions
4. **Retraining Capability** - Adapts to new data automatically

## Model Architecture

### 1. Demand Forecasting Model (`train_demand_model.py`)

**Type**: LSTM (Long Short-Term Memory) Neural Network

**Architecture**:
```
Input: 24 hours × 11 features
  ↓
LSTM(128 units, return_sequences=True)
  ↓
Dropout(0.2)
  ↓
LSTM(64 units)
  ↓
Dropout(0.2)
  ↓
Dense(32, relu)
  ↓
Dropout(0.1)
  ↓
Output: 6 predictions (next 6 hours)
```

**Features Used**:
- Historical energy consumption
- Temperature, humidity, solar radiation
- Carbon intensity, grid pricing
- Time features (hour, day of week, weekend)
- Occupancy factor

**Performance** (on validation set):
- Mean Absolute Error: ~0.15 kWh
- R² Score: ~0.85
- Prediction horizon: 6 hours ahead

### 2. Source Optimization (`optimize_sources.py`)

**Type**: Rule-based optimization algorithm with weighted cost function

**Decision Logic**:
1. **Solar First**: Always prioritize solar when available (cheapest, cleanest)
2. **Battery vs Grid**: Compare scores based on:
   - Cost: Grid price vs battery degradation
   - Carbon: Grid intensity vs battery lifecycle emissions
   - Weighted combination (configurable)
3. **Grid Fallback**: Use grid for remaining power needs

**Cost Function**:
```
Score = (cost_weight × cost) + (carbon_weight × carbon_cost_equivalent)
```

Where: `carbon_cost_equivalent = (gCO2eq / 1000) × ₹10/kg`

**Parameters**:
- Solar capacity: 3 kW
- Battery capacity: 10 kWh
- Battery max discharge: 2 kW
- Carbon weight: 0.5 (50%)
- Cost weight: 0.5 (50%)

### 3. Decision Engine (`decision_engine.py`)

**Combines**: Forecasting + Optimization

**Workflow**:
1. Use LSTM to predict demand for next 6 hours
2. For current hour, optimize source selection
3. Monitor battery status and solar availability
4. Generate actionable recommendations
5. Log all decisions for analysis

## Installation & Setup

### Prerequisites

```bash
# Python packages already in requirements.txt
pip install -r ../requirements.txt
```

Required packages:
- tensorflow >= 2.13.0
- scikit-learn >= 1.3.0
- numpy >= 1.24.0
- pandas >= 2.0.0
- joblib >= 1.3.0

## Usage

### Option 1: Train Everything (Recommended for First Time)

```bash
# This trains both models and runs a simulation
python module3-ai/decision_engine.py
```

**What it does**:
1. Trains LSTM forecasting model (50 epochs, ~5 minutes)
2. Initializes optimization algorithm
3. Simulates 48 hours of real-time operation
4. Saves models to `models/` directory
5. Generates results in `data/` directory

### Option 2: Train Models Separately

```bash
# Train demand forecasting model
python module3-ai/train_demand_model.py

# Test source optimization
python module3-ai/optimize_sources.py
```

### Option 3: Use Pre-trained Models

```bash
# If models exist in models/ directory
python module3-ai/decision_engine.py
# Will automatically load and use existing models
```

## Retraining on New Data

The system supports incremental learning to adapt to changes:

```python
from decision_engine import VestaDecisionEngine

engine = VestaDecisionEngine()
engine.load_models()

# Retrain on new data (e.g., collected over past week)
engine.retrain_on_new_data('data/raw/new_week_data.csv')
```

**When to retrain**:
- **Weekly**: For rapid adaptation to usage changes
- **Monthly**: For seasonal pattern updates
- **After changes**: New appliances, schedule changes

**New data format**: Same as `integrated_dataset.csv` with 27 features

## Model Files

After training, these files are created in `models/`:

```
models/
├── demand_forecaster.h5              # Trained LSTM model
├── demand_forecaster_scalers.pkl     # Data normalization scalers
├── demand_forecaster_config.json     # Model configuration
└── optimizer_config.json             # Optimization parameters
```

## Output Files

Generated in `data/`:

```
data/
├── optimization_results.csv          # Daily optimization results
├── simulation_results.csv            # Real-time simulation results
└── decision_log.json                 # All decisions with timestamps
```

## Performance Metrics

### Forecasting Accuracy

Based on 30-day dataset:
- **Training samples**: ~570 sequences
- **Validation samples**: ~140 sequences
- **MAE**: 0.15-0.20 kWh
- **RMSE**: 0.20-0.30 kWh
- **R² Score**: 0.80-0.90
- **Training time**: ~5 minutes (CPU)

### Optimization Results

Based on 24-hour simulation:
- **Cost savings**: 15-25% vs grid-only
- **Carbon reduction**: 20-35% vs grid-only
- **Solar utilization**: ~60% of available solar captured
- **Battery cycles**: Optimized to minimize degradation

## Example Output

### Demand Forecast
```
Predicted energy consumption for next 6 hours:
  Hour +1: 1.234 kWh
  Hour +2: 1.456 kWh
  Hour +3: 1.678 kWh
  Hour +4: 1.543 kWh
  Hour +5: 1.321 kWh
  Hour +6: 1.098 kWh
```

### Source Allocation
```
Hour 14:00
  Power needed: 1.456 kW
  Sources: [('solar', '1.200'), ('battery', '0.256')]
  Cost: ₹0.08
  Carbon: 95 gCO2eq
  Battery: 8.74 kWh
```

### Daily Summary
```
With Optimization:
  Total Cost:   ₹38.45
  Total Carbon: 5.67 kg CO2

Grid Only (No Optimization):
  Total Cost:   ₹48.32
  Total Carbon: 8.23 kg CO2

Savings:
  Cost Saved:   ₹9.87 (20.4%)
  Carbon Saved: 2.56 kg CO2 (31.1%)
```

## API Reference

### EnergyDemandForecaster

```python
forecaster = EnergyDemandForecaster(lookback_hours=24, forecast_horizon=6)

# Train model
forecaster.train(df, epochs=50, batch_size=32)

# Predict
prediction = forecaster.predict(recent_24h_data)

# Retrain on new data
forecaster.retrain('new_data.csv', epochs=20)

# Save/Load
forecaster.save_model()
forecaster.load_model()
```

### SourceOptimizer

```python
optimizer = SourceOptimizer(
    carbon_weight=0.5,
    cost_weight=0.5,
    solar_capacity=3.0,
    battery_capacity=10.0
)

# Optimize for current conditions
allocation, metrics = optimizer.optimize_source(
    power_needed=1.5,
    conditions={
        'solar_radiation': 0.8,
        'cloud_cover': 20,
        'hour': 14,
        'carbon_intensity': 450,
        'grid_price': 6.5
    }
)

# Simulate full day
results = optimizer.simulate_day(df_day)
```

### VestaDecisionEngine

```python
engine = VestaDecisionEngine()

# Train from scratch
engine.train_models()

# Load existing
engine.load_models()

# Make real-time decision
decision = engine.make_decision(recent_data, current_conditions)

# Simulate operation
results = engine.simulate_realtime(df, hours=48)

# Retrain
engine.retrain_on_new_data('new_data.csv')
```

## Customization

### Adjust Forecast Horizon

```python
# Predict 12 hours instead of 6
forecaster = EnergyDemandForecaster(
    lookback_hours=48,  # Use more history
    forecast_horizon=12  # Predict further ahead
)
```

### Change Optimization Weights

```python
# Prioritize carbon reduction over cost
optimizer = SourceOptimizer(
    carbon_weight=0.7,  # 70% carbon
    cost_weight=0.3     # 30% cost
)
```

### Add More Features

Edit `train_demand_model.py`:
```python
self.feature_columns = [
    'total_energy_kwh',
    'temperature',
    # Add your custom features here
    'new_feature_1',
    'new_feature_2'
]
```

## Troubleshooting

### Issue: Model not converging

**Solution**: Increase epochs or adjust learning rate
```python
forecaster.train(df, epochs=100)  # More epochs
```

### Issue: Poor predictions

**Solution**: Check data quality and add more features
```python
# Verify data
df.describe()
df.isnull().sum()
```

### Issue: Out of memory

**Solution**: Reduce batch size
```python
forecaster.train(df, batch_size=16)  # Smaller batches
```

### Issue: Retraining fails

**Solution**: Ensure new data has same format as training data
```python
# Check columns match
print(new_df.columns.tolist())
```

## Next Steps

After training models:

1. **Integrate with Module 2 (Backend)**:
   - Expose models via FastAPI endpoints
   - Real-time inference on live sensor data

2. **Connect to Module 4 (Frontend)**:
   - Display predictions in dashboard
   - Show source allocation visually
   - Real-time decision monitoring

3. **Deploy to Edge Device**:
   - Export TensorFlow Lite model
   - Run inference on Raspberry Pi/Edge device
   - Minimize latency for real-time control

4. **Continuous Improvement**:
   - Collect real usage data
   - Retrain weekly/monthly
   - Track accuracy over time

## References

- LSTM Networks: https://www.tensorflow.org/guide/keras/rnn
- Time Series Forecasting: https://www.tensorflow.org/tutorials/structured_data/time_series
- Energy Optimization: IEEE papers on smart grid optimization

---

**Status**: Module 3 Phase 2 COMPLETE ✅  
**Ready for**: Integration with Backend (Module 2) and Frontend (Module 4)

*Built for Sustainergy Hackathon 2026 by Team HyperVolt* 🌱⚡
