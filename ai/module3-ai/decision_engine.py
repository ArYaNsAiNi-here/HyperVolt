"""
Vesta Decision Engine - Real-time Energy Management
Combines demand forecasting and source optimization for intelligent energy decisions
Supports model retraining on new data
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

# Import our models
import sys
sys.path.append(os.path.dirname(__file__))
from train_demand_model import EnergyDemandForecaster
from optimize_sources import SourceOptimizer, EnergySource


class VestaDecisionEngine:
    """
    The Brain of Vesta Energy Orchestrator
    Coordinates demand forecasting and source optimization
    """
    
    def __init__(self):
        """Initialize the decision engine"""
        self.forecaster = EnergyDemandForecaster(lookback_hours=24, forecast_horizon=6)
        self.optimizer = SourceOptimizer(
            carbon_weight=0.5,
            cost_weight=0.5,
            solar_capacity=3.0,
            battery_capacity=10.0,
            battery_max_discharge=2.0
        )
        self.decision_log = []
        
    def load_models(self) -> bool:
        """Load pre-trained models"""
        print("Loading pre-trained models...")
        success = self.forecaster.load_model()
        if success:
            print("✓ Demand forecasting model loaded")
        else:
            print("✗ No pre-trained forecasting model found")
        return success
    
    def train_models(self, data_path: str = 'data/raw/integrated_dataset.csv'):
        """Train both models from scratch"""
        print("=" * 70)
        print("VESTA DECISION ENGINE - MODEL TRAINING")
        print("=" * 70)
        
        # Load data
        df = pd.read_csv(data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"\nDataset: {len(df)} records")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        # Train forecasting model
        print("\n" + "-" * 70)
        print("PHASE 1: Training Demand Forecasting Model")
        print("-" * 70)
        self.forecaster.train(df, epochs=50, batch_size=32)
        
        # Optimizer doesn't need training (rule-based)
        print("\n" + "-" * 70)
        print("PHASE 2: Source Optimization Algorithm")
        print("-" * 70)
        print("✓ Optimization algorithm initialized (rule-based, no training needed)")
        
        print("\n" + "=" * 70)
        print("✓ ALL MODELS READY!")
        print("=" * 70)
    
    def retrain_on_new_data(self, new_data_path: str):
        """
        Retrain models on newly collected data
        This allows the system to adapt to changing patterns
        """
        print("=" * 70)
        print("RETRAINING MODELS ON NEW DATA")
        print("=" * 70)
        
        # Retrain forecaster
        print("\nRetraining demand forecasting model...")
        self.forecaster.retrain(new_data_path, epochs=20)
        
        print("\n✓ Models updated with new data!")
    
    def make_decision(self, recent_data: pd.DataFrame, current_conditions: Dict) -> Dict:
        """
        Make real-time energy management decision
        
        Args:
            recent_data: Last 24 hours of data for forecasting
            current_conditions: Current conditions for optimization
            
        Returns:
            Decision dictionary with forecast, allocation, and metrics
        """
        # Step 1: Forecast demand for next 6 hours
        forecast = self.forecaster.predict(recent_data)
        
        # Step 2: For the next hour, optimize source selection
        current_power_needed = forecast[0]  # Next hour's predicted demand
        
        allocation, metrics = self.optimizer.optimize_source(
            current_power_needed,
            current_conditions
        )
        
        # Prepare decision
        decision = {
            'timestamp': datetime.now().isoformat(),
            'forecast_6h': forecast.tolist(),
            'current_hour': {
                'predicted_demand': float(current_power_needed),
                'source_allocation': [(s.value, float(p)) for s, p in allocation],
                'cost': float(metrics['cost']),
                'carbon': float(metrics['carbon']),
                'battery_charge': float(metrics['battery_charge'])
            },
            'recommendation': self._generate_recommendation(forecast, allocation, metrics)
        }
        
        # Log decision
        self.decision_log.append(decision)
        
        return decision
    
    def _generate_recommendation(self, forecast: np.ndarray, 
                                 allocation: List[Tuple[EnergySource, float]],
                                 metrics: Dict) -> str:
        """Generate human-readable recommendation"""
        sources = [s.value for s, _ in allocation]
        
        # Build recommendation text
        rec = []
        
        if EnergySource.SOLAR in [s for s, _ in allocation]:
            rec.append("Using solar power (cleanest option)")
        if EnergySource.BATTERY in [s for s, _ in allocation]:
            rec.append("Drawing from battery (cost-effective)")
        if EnergySource.GRID in [s for s, _ in allocation]:
            rec.append("Supplementing with grid power")
        
        # Check if demand will increase
        avg_demand = forecast.mean()
        if forecast[1] > forecast[0] * 1.2:
            rec.append("⚠ Demand will increase significantly in next hour")
        
        # Check battery status
        battery_pct = (metrics['battery_charge'] / self.optimizer.battery_capacity) * 100
        if battery_pct < 20:
            rec.append("⚠ Battery low - consider charging during low-cost hours")
        elif battery_pct > 80:
            rec.append("✓ Battery well charged")
        
        return " | ".join(rec)
    
    def simulate_realtime(self, df: pd.DataFrame, hours: int = 24) -> pd.DataFrame:
        """
        Simulate real-time operation for given hours
        
        Args:
            df: Dataset with all necessary features
            hours: Number of hours to simulate
            
        Returns:
            DataFrame with decisions for each hour
        """
        print("=" * 70)
        print(f"SIMULATING REAL-TIME OPERATION ({hours} hours)")
        print("=" * 70)
        
        decisions = []
        
        for i in range(24, min(24 + hours, len(df))):
            # Get recent data for forecasting (24 hours lookback)
            recent_data = df.iloc[i-24:i].copy()
            
            # Current conditions
            current = df.iloc[i]
            conditions = {
                'solar_radiation': current['solar_radiation_proxy'],
                'cloud_cover': current['cloud_cover'],
                'hour': current['hour'],
                'carbon_intensity': current['carbon_intensity'],
                'grid_price': current['grid_price_per_kwh']
            }
            
            # Make decision
            decision = self.make_decision(recent_data, conditions)
            
            # Add actual values for comparison
            decision['actual_demand'] = float(current['total_energy_kwh'])
            decision['timestamp_hour'] = current['timestamp']
            
            decisions.append(decision)
            
            if (i - 24) % 6 == 0:
                print(f"  Processed hour {i-24}/{hours}")
        
        print("\n✓ Simulation complete!")
        
        # Convert to DataFrame for analysis
        results = []
        for d in decisions:
            results.append({
                'timestamp': d['timestamp_hour'],
                'predicted_demand': d['current_hour']['predicted_demand'],
                'actual_demand': d['actual_demand'],
                'sources': str(d['current_hour']['source_allocation']),
                'cost': d['current_hour']['cost'],
                'carbon': d['current_hour']['carbon'],
                'battery_charge': d['current_hour']['battery_charge'],
                'recommendation': d['recommendation']
            })
        
        return pd.DataFrame(results)
    
    def save_decision_log(self, path: str = 'data/decision_log.json'):
        """Save decision log to file"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.decision_log, f, indent=2)
        print(f"✓ Decision log saved to: {path}")


def main():
    """
    Main function demonstrating the decision engine
    """
    # Initialize engine
    engine = VestaDecisionEngine()
    
    # Try to load existing models
    if not engine.load_models():
        print("\nNo pre-trained models found. Training new models...")
        engine.train_models()
    
    # Load data for simulation
    data_path = 'data/raw/integrated_dataset.csv'
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Simulate 48 hours of real-time operation
    print("\n" + "=" * 70)
    print("REAL-TIME SIMULATION")
    print("=" * 70)
    
    results = engine.simulate_realtime(df, hours=48)
    
    # Analyze results
    print("\n" + "=" * 70)
    print("SIMULATION RESULTS")
    print("=" * 70)
    
    print(f"\nForecast Accuracy:")
    mae = np.abs(results['predicted_demand'] - results['actual_demand']).mean()
    mape = (np.abs(results['predicted_demand'] - results['actual_demand']) / results['actual_demand']).mean() * 100
    print(f"  Mean Absolute Error: {mae:.3f} kWh")
    print(f"  Mean Absolute % Error: {mape:.1f}%")
    
    print(f"\nCost & Carbon:")
    print(f"  Total Cost: ₹{results['cost'].sum():.2f}")
    print(f"  Total Carbon: {results['carbon'].sum()/1000:.2f} kg CO2")
    print(f"  Average Cost per hour: ₹{results['cost'].mean():.2f}")
    
    print(f"\nBattery Usage:")
    print(f"  Initial charge: {results['battery_charge'].iloc[0]:.2f} kWh")
    print(f"  Final charge: {results['battery_charge'].iloc[-1]:.2f} kWh")
    print(f"  Min charge: {results['battery_charge'].min():.2f} kWh")
    print(f"  Max charge: {results['battery_charge'].max():.2f} kWh")
    
    # Save results
    output_path = 'data/simulation_results.csv'
    results.to_csv(output_path, index=False)
    print(f"\n✓ Simulation results saved to: {output_path}")
    
    engine.save_decision_log()
    
    print("\n" + "=" * 70)
    print("✓ VESTA DECISION ENGINE READY FOR DEPLOYMENT!")
    print("=" * 70)
    print("\nThe engine can now:")
    print("  1. Predict energy demand 6 hours ahead")
    print("  2. Optimize source selection (Grid/Solar/Battery)")
    print("  3. Minimize both cost and carbon footprint")
    print("  4. Adapt to new data through retraining")
    
    # Demo: Show how to retrain on new data
    print("\n" + "-" * 70)
    print("RETRAINING CAPABILITY")
    print("-" * 70)
    print("\nTo retrain the model on new data:")
    print("  1. Collect new data (e.g., next 7 days)")
    print("  2. Save to CSV with same format as training data")
    print("  3. Run: engine.retrain_on_new_data('path/to/new_data.csv')")
    print("\nThis allows the system to adapt to:")
    print("  - Seasonal changes")
    print("  - New usage patterns")
    print("  - Updated appliances")
    print("  - Grid conditions")


if __name__ == "__main__":
    main()
