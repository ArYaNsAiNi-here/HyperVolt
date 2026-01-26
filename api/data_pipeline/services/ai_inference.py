"""
AI Inference Service - Integration Layer between Module 2 (API) and Module 3 (AI)

This service provides an interface for the API to call AI models for:
- Energy demand forecasting
- Energy source optimization
- Real-time decision making
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from django.conf import settings
from django.utils import timezone

# Add AI module to path
AI_MODULE_PATH = os.path.join(settings.BASE_DIR, '..', 'ai', 'module3-ai')
sys.path.insert(0, AI_MODULE_PATH)

# Import AI components
try:
    from train_demand_model import EnergyDemandForecaster
    from optimize_sources import SourceOptimizer, EnergySource
    AI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI modules not available: {e}")
    AI_AVAILABLE = False


class AIInferenceService:
    """
    Service layer for AI model inference
    
    Provides methods to:
    1. Forecast energy demand
    2. Recommend energy sources
    3. Make real-time decisions
    """
    
    def __init__(self):
        """Initialize AI inference service"""
        self.forecaster = None
        self.optimizer = None
        self.models_loaded = False
        
        if AI_AVAILABLE:
            self._initialize_models()
    
    def _initialize_models(self):
        """Initialize and load AI models"""
        try:
            # Initialize forecaster
            self.forecaster = EnergyDemandForecaster(
                lookback_hours=24,
                forecast_horizon=6
            )
            
            # Try to load pre-trained model
            model_path = os.path.join(settings.BASE_DIR, '..', 'ai', 'models')
            if os.path.exists(model_path):
                self.forecaster.load_model()
                self.models_loaded = True
            
            # Initialize optimizer
            self.optimizer = SourceOptimizer(
                carbon_weight=0.5,
                cost_weight=0.5,
                solar_capacity=3.0,
                battery_capacity=10.0,
                battery_max_discharge=2.0
            )
            
            print("✓ AI models initialized successfully")
            
        except Exception as e:
            print(f"Warning: Could not initialize AI models: {e}")
            self.models_loaded = False
    
    def is_available(self) -> bool:
        """Check if AI inference is available"""
        return AI_AVAILABLE and self.models_loaded
    
    def forecast_demand(self, hours_ahead: int = 6) -> Dict:
        """
        Forecast energy demand for the next N hours
        
        Args:
            hours_ahead: Number of hours to forecast (default: 6)
            
        Returns:
            Dictionary with forecast results
        """
        if not self.is_available():
            return {
                'error': 'AI models not available',
                'available': False
            }
        
        try:
            # Get recent data from database
            recent_data = self._get_recent_data_for_forecasting()
            
            if recent_data is None or len(recent_data) < 24:
                return {
                    'error': 'Insufficient historical data (need at least 24 hours)',
                    'available': False
                }
            
            # Make prediction
            forecast = self.forecaster.predict(recent_data)
            
            # Prepare response
            return {
                'timestamp': timezone.now().isoformat(),
                'forecast_horizon': hours_ahead,
                'predictions': [
                    {
                        'hour': i + 1,
                        'predicted_kwh': float(forecast[i]),
                        'timestamp': (timezone.now() + timedelta(hours=i+1)).isoformat()
                    }
                    for i in range(min(hours_ahead, len(forecast)))
                ],
                'available': True,
                'model_type': 'lstm'
            }
            
        except Exception as e:
            return {
                'error': f'Forecasting failed: {str(e)}',
                'available': False
            }
    
    def recommend_source(self, load_name: str, load_priority: int, 
                        load_power: float, current_conditions: Optional[Dict] = None) -> Dict:
        """
        Recommend optimal energy source for a load
        
        Args:
            load_name: Name of the load
            load_priority: Priority level (25-100)
            load_power: Power requirement in watts
            current_conditions: Optional current conditions (fetched if not provided)
            
        Returns:
            Dictionary with recommendation
        """
        if not self.is_available():
            return {
                'error': 'AI models not available',
                'available': False,
                'fallback': 'Use rule-based optimizer from EnergySourceOptimizer'
            }
        
        try:
            # Get current conditions if not provided
            if current_conditions is None:
                current_conditions = self._get_current_conditions()
            
            # Convert power to kW
            power_kw = load_power / 1000.0
            
            # Use optimizer to recommend source
            allocation, metrics = self.optimizer.optimize_source(
                power_kw,
                current_conditions
            )
            
            # Extract primary source
            primary_source = allocation[0][0].value if allocation else 'grid'
            
            # Build reasoning
            reasoning = self._build_reasoning(allocation, current_conditions, load_name)
            
            return {
                'timestamp': timezone.now().isoformat(),
                'load_name': load_name,
                'load_priority': load_priority,
                'load_power': load_power,
                'recommended_source': primary_source,
                'source_allocation': [(s.value, float(p)) for s, p in allocation],
                'metrics': {
                    'estimated_cost': float(metrics['cost']),
                    'estimated_carbon': float(metrics['carbon']),
                    'battery_charge': float(metrics['battery_charge'])
                },
                'reasoning': reasoning,
                'confidence': 0.85,
                'algorithm': 'ml_optimizer',
                'available': True
            }
            
        except Exception as e:
            return {
                'error': f'Source recommendation failed: {str(e)}',
                'available': False
            }
    
    def make_decision(self) -> Dict:
        """
        Make a comprehensive energy management decision
        Combines forecasting and optimization
        
        Returns:
            Decision dictionary with forecast and recommendations
        """
        if not self.is_available():
            return {
                'error': 'AI models not available',
                'available': False
            }
        
        try:
            # Get forecast
            forecast_result = self.forecast_demand()
            
            if not forecast_result.get('available'):
                return forecast_result
            
            # Get current conditions
            conditions = self._get_current_conditions()
            
            # Get predicted demand for next hour
            next_hour_demand = forecast_result['predictions'][0]['predicted_kwh']
            
            # Optimize source allocation
            allocation, metrics = self.optimizer.optimize_source(
                next_hour_demand,
                conditions
            )
            
            # Build comprehensive decision
            return {
                'timestamp': timezone.now().isoformat(),
                'forecast': forecast_result['predictions'],
                'current_decision': {
                    'predicted_demand_kwh': float(next_hour_demand),
                    'source_allocation': [(s.value, float(p)) for s, p in allocation],
                    'cost': float(metrics['cost']),
                    'carbon': float(metrics['carbon']),
                    'battery_charge': float(metrics['battery_charge'])
                },
                'recommendation': self._generate_recommendation(
                    forecast_result['predictions'],
                    allocation,
                    metrics
                ),
                'available': True
            }
            
        except Exception as e:
            return {
                'error': f'Decision making failed: {str(e)}',
                'available': False
            }
    
    def _get_recent_data_for_forecasting(self) -> Optional[pd.DataFrame]:
        """
        Fetch recent 24 hours of data from database for forecasting
        
        Returns:
            DataFrame with required features or None
        """
        try:
            from ..models import SensorReading, GridData
            
            # Get timestamp range
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=24)
            
            # Fetch sensor data
            sensor_readings = SensorReading.objects.filter(
                timestamp__gte=start_time,
                timestamp__lte=end_time
            ).order_by('timestamp')
            
            # Fetch grid data
            grid_data = GridData.objects.filter(
                timestamp__gte=start_time,
                timestamp__lte=end_time
            ).order_by('timestamp')
            
            if not sensor_readings.exists() or not grid_data.exists():
                return None
            
            # Convert to DataFrame
            # This is a simplified version - in production, you'd merge all data properly
            data = []
            for reading in sensor_readings[:24]:  # Get hourly samples
                data.append({
                    'timestamp': reading.timestamp,
                    'hour': reading.timestamp.hour,
                    'day_of_week': reading.timestamp.weekday(),
                    'is_weekend': reading.timestamp.weekday() >= 5,
                    'total_energy_kwh': reading.value / 1000.0 if reading.sensor_type == 'current' else 1.0,
                })
            
            df = pd.DataFrame(data)
            
            # Add required features with default values
            df['temperature'] = 25.0
            df['cloud_cover'] = 30.0
            df['solar_radiation_proxy'] = 0.5
            df['carbon_intensity'] = 450.0
            df['grid_price_per_kwh'] = 6.0
            
            return df if len(df) >= 24 else None
            
        except Exception as e:
            print(f"Error fetching recent data: {e}")
            return None
    
    def _get_current_conditions(self) -> Dict:
        """
        Get current environmental and grid conditions
        
        Returns:
            Dictionary with current conditions
        """
        try:
            from ..models import GridData, SensorReading
            
            # Get latest grid data
            carbon_data = GridData.objects.filter(
                data_type='carbon_intensity'
            ).order_by('-timestamp').first()
            
            weather_data = GridData.objects.filter(
                data_type='weather'
            ).order_by('-timestamp').first()
            
            # Get latest sensor readings
            ldr_reading = SensorReading.objects.filter(
                sensor_type='ldr'
            ).order_by('-timestamp').first()
            
            current_hour = timezone.now().hour
            
            # Build conditions dict
            conditions = {
                'hour': current_hour,
                'solar_radiation': 0.7 if 8 <= current_hour <= 17 else 0.0,
                'cloud_cover': 30.0,
                'carbon_intensity': 450.0,
                'grid_price': 6.0
            }
            
            # Update with actual data if available
            if weather_data and weather_data.data:
                conditions['cloud_cover'] = weather_data.data.get('cloud_cover', 30.0)
                
            if carbon_data and carbon_data.data:
                conditions['carbon_intensity'] = carbon_data.data.get('carbon_intensity', 450.0)
                conditions['grid_price'] = carbon_data.data.get('grid_price', 6.0)
            
            return conditions
            
        except Exception as e:
            print(f"Error fetching current conditions: {e}")
            # Return default conditions
            return {
                'hour': timezone.now().hour,
                'solar_radiation': 0.5,
                'cloud_cover': 30.0,
                'carbon_intensity': 450.0,
                'grid_price': 6.0
            }
    
    def _build_reasoning(self, allocation: List[Tuple], conditions: Dict, load_name: str) -> str:
        """Build human-readable reasoning for recommendation"""
        reasons = []
        
        # Primary source
        if allocation:
            primary_source = allocation[0][0].value
            reasons.append(f"Primary source: {primary_source}")
            
            # Solar reasoning
            if primary_source == 'solar':
                if conditions.get('solar_radiation', 0) > 0.5:
                    reasons.append("High solar availability")
                if conditions.get('cloud_cover', 100) < 40:
                    reasons.append("Clear weather conditions")
            
            # Grid reasoning
            if primary_source == 'grid':
                carbon = conditions.get('carbon_intensity', 0)
                if carbon < 400:
                    reasons.append("Low grid carbon intensity")
                elif carbon > 600:
                    reasons.append("High grid carbon but necessary")
        
        return " | ".join(reasons) if reasons else f"Optimized for {load_name}"
    
    def _generate_recommendation(self, forecast: List[Dict], 
                                 allocation: List[Tuple], metrics: Dict) -> str:
        """Generate human-readable recommendation"""
        recommendations = []
        
        # Source recommendation
        sources_used = [s.value for s, _ in allocation]
        if 'solar' in sources_used:
            recommendations.append("Using solar power (clean & free)")
        if 'battery' in sources_used:
            recommendations.append("Battery discharge active")
        if 'grid' in sources_used:
            recommendations.append("Grid power as backup")
        
        # Battery status
        battery_pct = (metrics['battery_charge'] / 10.0) * 100  # Assuming 10kWh capacity
        if battery_pct < 20:
            recommendations.append("⚠ Battery low - schedule charging")
        elif battery_pct > 80:
            recommendations.append("✓ Battery well charged")
        
        # Demand trend
        if len(forecast) >= 2:
            if forecast[1]['predicted_kwh'] > forecast[0]['predicted_kwh'] * 1.2:
                recommendations.append("⚠ Demand increasing - prepare for higher load")
        
        return " | ".join(recommendations)
