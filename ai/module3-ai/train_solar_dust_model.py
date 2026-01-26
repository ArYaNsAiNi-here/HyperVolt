"""
Solar Panel Dust Prediction Model for Vesta Energy Orchestrator
Predicts dust accumulation on solar panels using LDR readings and power output
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Tuple, Dict
import json

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib


class SolarDustPredictor:
    """
    Machine Learning model to predict dust accumulation on solar panels
    
    Uses:
    - LDR readings (ambient light)
    - Expected power (based on irradiance)
    - Actual power output
    - Efficiency ratio
    - Time since last cleaning
    
    Predicts:
    - Dust percentage (0-100%)
    - Cleaning recommendation (boolean)
    """
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize the predictor
        
        Args:
            model_type: 'random_forest' or 'gradient_boosting'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.model_path = f'models/solar_dust_{model_type}.pkl'
        self.scaler_path = f'models/solar_dust_scaler.pkl'
        self.config_path = f'models/solar_dust_config.json'
        
        # Ensure models directory exists
        os.makedirs('models', exist_ok=True)
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features for training
        
        Args:
            df: DataFrame with solar panel data
            
        Returns:
            X (features), y (target - dust percentage)
        """
        # Define features for prediction
        self.feature_columns = [
            'solar_irradiance',
            'temperature_c',
            'ldr_lux',
            'expected_power_kw',
            'actual_power_kw',
            'efficiency_ratio',
            'days_since_cleaning',
            'hour'
        ]
        
        # Check if all columns exist
        available_features = [col for col in self.feature_columns if col in df.columns]
        if len(available_features) < len(self.feature_columns):
            print(f"Warning: Some features missing. Using {len(available_features)}/{len(self.feature_columns)}")
            self.feature_columns = available_features
        
        X = df[self.feature_columns].values
        y = df['dust_percentage'].values
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        print(f"Prepared features: X={X.shape}, y={y.shape}")
        return X, y
    
    def build_model(self):
        """Build the machine learning model"""
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        return self.model
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2) -> Dict:
        """
        Train the dust prediction model
        
        Args:
            df: DataFrame with solar panel data
            test_size: Fraction of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        print("=" * 70)
        print("SOLAR DUST PREDICTION - MODEL TRAINING")
        print("=" * 70)
        
        # Prepare data
        print("\nPreparing training data...")
        X, y = self.prepare_features(df)
        
        # Split into train and test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, shuffle=True
        )
        
        print(f"Training set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        
        # Build and train model
        print(f"\nTraining {self.model_type} model...")
        self.build_model()
        self.model.fit(X_train, y_train)
        
        # Make predictions
        print("\nEvaluating model...")
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        # Calculate metrics
        train_mae = mean_absolute_error(y_train, y_pred_train)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        train_r2 = r2_score(y_train, y_pred_train)
        
        test_mae = mean_absolute_error(y_test, y_pred_test)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        test_r2 = r2_score(y_test, y_pred_test)
        
        metrics = {
            'train': {
                'mae': float(train_mae),
                'rmse': float(train_rmse),
                'r2': float(train_r2)
            },
            'test': {
                'mae': float(test_mae),
                'rmse': float(test_rmse),
                'r2': float(test_r2)
            },
            'training_samples': int(X_train.shape[0]),
            'test_samples': int(X_test.shape[0])
        }
        
        print("\n" + "=" * 70)
        print("TRAINING RESULTS")
        print("=" * 70)
        print(f"\nTraining Set:")
        print(f"  MAE:  {train_mae:.2f}% dust")
        print(f"  RMSE: {train_rmse:.2f}%")
        print(f"  R²:   {train_r2:.4f}")
        
        print(f"\nTest Set:")
        print(f"  MAE:  {test_mae:.2f}% dust")
        print(f"  RMSE: {test_rmse:.2f}%")
        print(f"  R²:   {test_r2:.4f}")
        
        # Feature importance (for tree-based models)
        if hasattr(self.model, 'feature_importances_'):
            print(f"\n📊 Feature Importance:")
            importances = self.model.feature_importances_
            for feature, importance in sorted(
                zip(self.feature_columns, importances),
                key=lambda x: x[1],
                reverse=True
            ):
                print(f"  {feature:.<30} {importance:.4f}")
        
        print("=" * 70)
        
        # Save model
        self.save_model()
        
        return metrics
    
    def predict(self, current_data: pd.DataFrame) -> Dict:
        """
        Predict dust accumulation for current conditions
        
        Args:
            current_data: DataFrame with current sensor readings
            
        Returns:
            Dictionary with predictions and recommendations
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded. Train or load model first.")
        
        # Prepare features
        X = current_data[self.feature_columns].values
        X = self.scaler.transform(X)
        
        # Predict
        dust_percentage = self.model.predict(X)[0]
        
        # Generate recommendations
        needs_cleaning = dust_percentage > 40
        urgency = 'High' if dust_percentage > 60 else 'Medium' if dust_percentage > 40 else 'Low'
        
        # Calculate potential savings from cleaning
        efficiency_loss = dust_percentage * 0.007
        if 'expected_power_kw' in current_data.columns:
            expected_power = current_data['expected_power_kw'].values[0]
            potential_gain_kw = expected_power * efficiency_loss
            potential_revenue_gain = potential_gain_kw * 6  # ₹6/kWh
        else:
            potential_gain_kw = 0
            potential_revenue_gain = 0
        
        return {
            'dust_percentage': float(dust_percentage),
            'needs_cleaning': bool(needs_cleaning),
            'urgency': urgency,
            'efficiency_loss_percent': float(efficiency_loss * 100),
            'potential_power_gain_kw': float(potential_gain_kw),
            'potential_revenue_gain_per_hour': float(potential_revenue_gain),
            'recommendation': self._generate_recommendation(dust_percentage, urgency)
        }
    
    def _generate_recommendation(self, dust_percentage: float, urgency: str) -> str:
        """Generate human-readable recommendation"""
        if dust_percentage < 20:
            return "Solar panels are clean. No action needed."
        elif dust_percentage < 40:
            return f"Minor dust detected ({dust_percentage:.1f}%). Monitor for now."
        elif dust_percentage < 60:
            return f"Moderate dust ({dust_percentage:.1f}%). Schedule cleaning within 3-5 days."
        else:
            return f"Heavy dust ({dust_percentage:.1f}%). Clean panels immediately to restore efficiency!"
    
    def save_model(self):
        """Save model, scaler, and configuration"""
        # Save model
        joblib.dump(self.model, self.model_path)
        
        # Save scaler
        joblib.dump(self.scaler, self.scaler_path)
        
        # Save configuration
        config = {
            'model_type': self.model_type,
            'feature_columns': self.feature_columns,
            'trained_date': datetime.now().isoformat()
        }
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✓ Model saved to: {self.model_path}")
        print(f"✓ Scaler saved to: {self.scaler_path}")
        print(f"✓ Config saved to: {self.config_path}")
    
    def load_model(self) -> bool:
        """Load saved model, scaler, and configuration"""
        try:
            # Load model
            self.model = joblib.load(self.model_path)
            
            # Load scaler
            self.scaler = joblib.load(self.scaler_path)
            
            # Load configuration
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            self.model_type = config['model_type']
            self.feature_columns = config['feature_columns']
            
            print(f"✓ Model loaded from: {self.model_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            return False


def main():
    """
    Main function to train the solar dust prediction model
    """
    # Load dataset
    data_path = 'data/raw/solar_dust_data.csv'
    
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        print("Please run 'python module3-ai/generate_solar_dust_data.py' first.")
        return
    
    print("Loading dataset...")
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"Dataset loaded: {len(df)} records")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Train model with Random Forest
    print("\n" + "=" * 70)
    print("Training Random Forest Model")
    print("=" * 70)
    
    predictor = SolarDustPredictor(model_type='random_forest')
    metrics = predictor.train(df, test_size=0.2)
    
    # Test prediction
    print("\n" + "=" * 70)
    print("TESTING PREDICTION")
    print("=" * 70)
    
    # Use last record for testing
    test_sample = df.tail(1)
    prediction = predictor.predict(test_sample)
    
    print("\nCurrent Conditions:")
    print(f"  LDR reading: {test_sample['ldr_lux'].values[0]:.0f} lux")
    print(f"  Expected power: {test_sample['expected_power_kw'].values[0]:.3f} kW")
    print(f"  Actual power: {test_sample['actual_power_kw'].values[0]:.3f} kW")
    print(f"  Efficiency: {test_sample['efficiency_ratio'].values[0]:.2%}")
    print(f"  Days since cleaning: {test_sample['days_since_cleaning'].values[0]:.1f}")
    
    print("\n🔮 Prediction:")
    print(f"  Dust level: {prediction['dust_percentage']:.1f}%")
    print(f"  Needs cleaning: {'Yes' if prediction['needs_cleaning'] else 'No'}")
    print(f"  Urgency: {prediction['urgency']}")
    print(f"  Efficiency loss: {prediction['efficiency_loss_percent']:.1f}%")
    print(f"  Potential gain: {prediction['potential_power_gain_kw']:.3f} kW/hour")
    print(f"  Revenue gain: ₹{prediction['potential_revenue_gain_per_hour']:.2f}/hour")
    
    print(f"\n💡 Recommendation:")
    print(f"  {prediction['recommendation']}")
    
    print("\n" + "=" * 70)
    print("✓ MODEL TRAINING COMPLETE!")
    print("=" * 70)
    print("\nModel files saved in 'models/' directory:")
    print("  - solar_dust_random_forest.pkl (trained model)")
    print("  - solar_dust_scaler.pkl (feature scaler)")
    print("  - solar_dust_config.json (configuration)")
    print("\nYou can now use this model for real-time dust prediction!")


if __name__ == "__main__":
    main()
