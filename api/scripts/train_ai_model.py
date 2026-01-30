#!/usr/bin/env python3
"""
HyperVolt AI Model Training Script
Trains and exports a simple ML model for peak hour prediction
Provides manual querying interface for demonstrations
"""

import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'generated')
MODEL_DIR = os.path.join(SCRIPT_DIR, '..', 'models', 'trained')

os.makedirs(MODEL_DIR, exist_ok=True)


class HyperVoltEnergyModel:
    """
    AI Model for predicting peak hours based on day of week and other features
    Input: day_of_week (0-6), hour (0-23), is_weekend (bool)
    Output: is_peak_hour (bool), predicted_power_mw (float)
    """
    
    def __init__(self):
        self.peak_classifier = None
        self.power_model = None
        self.is_trained = False
        self.training_date = None
        self.accuracy = 0.0
    
    def load_dataset(self, csv_path: str = None) -> pd.DataFrame:
        """Load the generated dataset"""
        if csv_path is None:
            csv_path = os.path.join(DATA_DIR, 'energy_forecast_dataset.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ Dataset not found: {csv_path}")
            print("   Run generate_dataset.py first!")
            return None
        
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded dataset: {len(df)} records")
        return df
    
    def prepare_features(self, df: pd.DataFrame):
        """Prepare features for training"""
        # Features for peak hour prediction
        X = df[['day_of_week', 'hour', 'is_weekend']].copy()
        X['is_weekend'] = X['is_weekend'].astype(int)
        
        # Add cyclical features for hour
        X['hour_sin'] = np.sin(2 * np.pi * X['hour'] / 24)
        X['hour_cos'] = np.cos(2 * np.pi * X['hour'] / 24)
        
        # Target: is_peak_hour
        y_peak = df['is_peak_hour'].astype(int)
        
        # Target: power consumption
        y_power = df['power_consumption_mw']
        
        return X, y_peak, y_power
    
    def train(self, df: pd.DataFrame = None):
        """Train the model on dataset"""
        if df is None:
            df = self.load_dataset()
            if df is None:
                return False
        
        print("\n🧠 Training AI Model...")
        
        X, y_peak, y_power = self.prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_peak, test_size=0.2, random_state=42
        )
        
        # Train peak hour classifier
        self.peak_classifier = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42
        )
        self.peak_classifier.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.peak_classifier.predict(X_test)
        self.accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📊 Model Performance:")
        print(f"   Accuracy: {self.accuracy * 100:.2f}%")
        print("\n   Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Normal', 'Peak']))
        
        self.is_trained = True
        self.training_date = datetime.now().isoformat()
        
        return True
    
    def predict_peak_hours(self, day_of_week: int) -> dict:
        """
        Predict peak hours for a given day of the week
        
        Args:
            day_of_week: 0=Monday, 1=Tuesday, ..., 6=Sunday
        
        Returns:
            dict with predicted peak hours and power levels
        """
        if not self.is_trained:
            print("❌ Model not trained! Call train() first.")
            return None
        
        is_weekend = 1 if day_of_week >= 5 else 0
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        results = {
            'day_of_week': day_of_week,
            'day_name': day_names[day_of_week],
            'is_weekend': bool(is_weekend),
            'predictions': [],
            'peak_hours': [],
            'normal_hours': []
        }
        
        for hour in range(24):
            # Prepare input
            X = pd.DataFrame([{
                'day_of_week': day_of_week,
                'hour': hour,
                'is_weekend': is_weekend,
                'hour_sin': np.sin(2 * np.pi * hour / 24),
                'hour_cos': np.cos(2 * np.pi * hour / 24)
            }])
            
            # Predict
            is_peak = bool(self.peak_classifier.predict(X)[0])
            confidence = float(self.peak_classifier.predict_proba(X)[0][1])
            
            # Estimate power based on peak status
            if hour <= 6:
                est_power = 400  # Night
            elif is_peak:
                est_power = 2100  # Peak
            else:
                est_power = 1100  # Normal
            
            prediction = {
                'hour': hour,
                'time': f'{hour:02d}:00',
                'is_peak': is_peak,
                'confidence': round(confidence, 3),
                'estimated_power_mw': est_power
            }
            
            results['predictions'].append(prediction)
            
            if is_peak:
                results['peak_hours'].append(hour)
            else:
                results['normal_hours'].append(hour)
        
        return results
    
    def save_model(self, path: str = None):
        """Save trained model to disk"""
        if not self.is_trained:
            print("❌ Model not trained!")
            return False
        
        if path is None:
            path = os.path.join(MODEL_DIR, 'hypervolt_energy_model.pkl')
        
        model_data = {
            'peak_classifier': self.peak_classifier,
            'is_trained': self.is_trained,
            'training_date': self.training_date,
            'accuracy': self.accuracy
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✓ Model saved: {path}")
        return True
    
    def load_model(self, path: str = None):
        """Load trained model from disk"""
        if path is None:
            path = os.path.join(MODEL_DIR, 'hypervolt_energy_model.pkl')
        
        if not os.path.exists(path):
            print(f"❌ Model not found: {path}")
            return False
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.peak_classifier = model_data['peak_classifier']
        self.is_trained = model_data['is_trained']
        self.training_date = model_data['training_date']
        self.accuracy = model_data['accuracy']
        
        print(f"✓ Model loaded (trained: {self.training_date}, accuracy: {self.accuracy*100:.2f}%)")
        return True
    
    def get_status(self) -> dict:
        """Get model status for API"""
        return {
            'is_trained': self.is_trained,
            'training_date': self.training_date,
            'accuracy': self.accuracy,
            'model_type': 'RandomForestClassifier',
            'features': ['day_of_week', 'hour', 'is_weekend', 'hour_sin', 'hour_cos']
        }


def interactive_query():
    """Interactive query mode for demonstrations"""
    print("\n" + "=" * 60)
    print("HyperVolt AI Model - Interactive Query Mode")
    print("=" * 60)
    
    model = HyperVoltEnergyModel()
    
    # Try to load existing model
    if not model.load_model():
        print("\nNo trained model found. Training new model...")
        model.train()
        model.save_model()
    
    print("\n📋 Enter day of week (0=Monday, 6=Sunday) or 'q' to quit")
    
    while True:
        try:
            user_input = input("\n🔍 Day of week (0-6): ").strip()
            
            if user_input.lower() == 'q':
                print("Goodbye!")
                break
            
            day = int(user_input)
            if not 0 <= day <= 6:
                print("Invalid! Enter 0-6")
                continue
            
            result = model.predict_peak_hours(day)
            
            print(f"\n{'='*50}")
            print(f"📅 Predictions for {result['day_name']}:")
            print(f"   Type: {'Weekend' if result['is_weekend'] else 'Weekday'}")
            print(f"\n🔴 Peak Hours: {[f'{h:02d}:00' for h in result['peak_hours']]}")
            print(f"🟢 Normal Hours: {len(result['normal_hours'])} hours")
            
            print("\n📊 Hourly Breakdown:")
            for pred in result['predictions']:
                status = "🔴 PEAK" if pred['is_peak'] else "🟢 Normal"
                print(f"   {pred['time']} - {status} ({pred['confidence']*100:.1f}% conf) - {pred['estimated_power_mw']} mW")
            
        except ValueError:
            print("Invalid input! Enter a number 0-6 or 'q' to quit")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


def main():
    """Main training and export function"""
    print("=" * 60)
    print("HyperVolt AI Model Training")
    print("=" * 60)
    
    model = HyperVoltEnergyModel()
    
    # Train model
    success = model.train()
    
    if success:
        # Save model
        model.save_model()
        
        # Demo prediction
        print("\n📋 Demo Prediction for Monday:")
        result = model.predict_peak_hours(0)
        print(f"   Peak hours: {result['peak_hours']}")
        
        print("\n📋 Demo Prediction for Saturday:")
        result = model.predict_peak_hours(5)
        print(f"   Peak hours: {result['peak_hours']}")
        
        print("\n✅ Training complete! Model exported.")
        print(f"   Model path: {os.path.join(MODEL_DIR, 'hypervolt_energy_model.pkl')}")
        print("\n💡 Run with --query flag for interactive mode:")
        print("   python train_ai_model.py --query")
    
    return model


if __name__ == '__main__':
    import sys
    if '--query' in sys.argv:
        interactive_query()
    else:
        main()
