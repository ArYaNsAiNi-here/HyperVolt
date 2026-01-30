"""
Simple AI Service for HyperVolt Energy Management System
This is a lightweight, rule-based AI that works without TensorFlow
Provides energy demand forecasting and source optimization
"""

import os
import json
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.utils import timezone

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class SimpleEnergyForecaster:
    """
    Simple energy demand forecaster using statistical patterns
    Uses time-of-day patterns and weather to predict demand
    """
    
    # Hourly demand patterns (kWh) - typical household
    HOURLY_PATTERNS = {
        0: 0.4, 1: 0.3, 2: 0.3, 3: 0.3, 4: 0.3, 5: 0.4,
        6: 0.8, 7: 1.2, 8: 1.5, 9: 1.2, 10: 1.0, 11: 1.1,
        12: 1.3, 13: 1.2, 14: 1.1, 15: 1.0, 16: 1.2, 17: 1.5,
        18: 2.0, 19: 2.2, 20: 2.0, 21: 1.5, 22: 1.0, 23: 0.6
    }
    
    # Peak hours definition
    PEAK_HOURS = [7, 8, 9, 17, 18, 19, 20]
    
    def __init__(self):
        self.model_ready = True
    
    def forecast(self, hours_ahead: int = 6) -> List[Dict]:
        """
        Forecast energy demand for next N hours
        Returns list of predictions with timestamps
        """
        predictions = []
        now = timezone.now()
        
        for i in range(hours_ahead):
            future_time = now + timedelta(hours=i + 1)
            hour = future_time.hour
            
            # Base demand from pattern
            base_demand = self.HOURLY_PATTERNS.get(hour, 1.0)
            
            # Add some variation (±15%) - deterministic based on time
            random.seed(int(future_time.timestamp()) % 100)
            variation = random.uniform(0.85, 1.15)
            
            predicted_kwh = round(base_demand * variation, 3)
            is_peak = hour in self.PEAK_HOURS
            
            predictions.append({
                'hour': i + 1,
                'predicted_kwh': predicted_kwh,
                'timestamp': future_time.isoformat(),
                'hour_of_day': hour,
                'is_peak_hour': is_peak,
                'demand_level': 'high' if predicted_kwh > 1.5 else ('medium' if predicted_kwh > 0.8 else 'low')
            })
        
        return predictions
    
    def identify_peak_hours(self, hours_ahead: int = 24) -> Dict:
        """
        Identify upcoming peak hours in the forecast period
        """
        forecast = self.forecast(hours_ahead)
        
        peak_hours = [p for p in forecast if p['is_peak_hour']]
        high_demand_hours = [p for p in forecast if p['predicted_kwh'] > 1.5]
        
        return {
            'peak_hours': peak_hours,
            'high_demand_periods': high_demand_hours,
            'next_peak': peak_hours[0] if peak_hours else None,
            'total_peak_hours': len(peak_hours),
            'recommendation': self._get_peak_recommendation(peak_hours)
        }
    
    def _get_peak_recommendation(self, peak_hours: List[Dict]) -> str:
        if not peak_hours:
            return "No peak hours in forecast period. Good time for high-energy tasks."
        
        next_peak = peak_hours[0]
        return f"Peak hour coming at {next_peak['hour_of_day']}:00. Consider deferring heavy loads or switching to battery/solar."


class SimpleSourceOptimizer:
    """
    Simple energy source optimizer
    Decides between Solar, Battery, and Grid based on conditions
    """
    
    def __init__(self, 
                 solar_capacity: float = 3.0,
                 battery_capacity: float = 10.0,
                 battery_max_discharge: float = 2.0):
        self.solar_capacity = solar_capacity
        self.battery_capacity = battery_capacity
        self.battery_max_discharge = battery_max_discharge
        self.battery_charge = battery_capacity * 0.7  # Start at 70%
        
        # Cost per kWh
        self.costs = {
            'solar': 0.05,   # Nearly free (maintenance only)
            'battery': 0.10, # Battery degradation cost
            'grid': 6.00     # Grid electricity price
        }
        
        # Carbon intensity (gCO2/kWh)
        self.carbon = {
            'solar': 50,     # Manufacturing amortized
            'battery': 100,  # Depends on charging source
            'grid': 500      # Average grid carbon
        }
    
    def calculate_solar_available(self, ldr_value: float, hour: int) -> float:
        """
        Calculate available solar power based on LDR sensor and time
        LDR values: 0-4095 (higher = more light)
        """
        # Night time - no solar
        if hour < 6 or hour >= 18:
            return 0.0
        
        # Convert LDR (0-4095) to solar fraction (0-1)
        solar_fraction = min(1.0, max(0.0, ldr_value / 4095.0))
        
        # Apply time-of-day factor (peak at noon)
        hour_factor = 1.0 - abs(hour - 12) / 6.0
        
        return self.solar_capacity * solar_fraction * hour_factor
    
    def optimize_source(self, 
                       power_needed: float,
                       conditions: Dict) -> Tuple[List[Tuple[str, float]], Dict]:
        """
        Optimize energy source selection
        
        Args:
            power_needed: Power required in kW
            conditions: Dict with hour, ldr, temperature, etc.
        
        Returns:
            (source_allocation, metrics)
        """
        hour = conditions.get('hour', timezone.now().hour)
        ldr = conditions.get('ldr', 0)
        carbon_intensity = conditions.get('carbon_intensity', 500)
        grid_price = conditions.get('grid_price', 6.0)
        
        # Calculate available power from each source
        solar_available = self.calculate_solar_available(ldr, hour)
        battery_available = min(self.battery_max_discharge, self.battery_charge * 0.8)
        
        allocation = []
        remaining = power_needed
        total_cost = 0
        total_carbon = 0
        
        # Priority 1: Use solar (cleanest and cheapest)
        if solar_available > 0 and remaining > 0:
            solar_used = min(solar_available, remaining)
            allocation.append(('solar', round(solar_used, 3)))
            remaining -= solar_used
            total_cost += solar_used * self.costs['solar']
            total_carbon += solar_used * self.carbon['solar']
        
        # Priority 2: Use battery if grid carbon is high
        if remaining > 0 and battery_available > 0:
            # Use battery if grid carbon is high or during peak hours
            if carbon_intensity > 400 or hour in [17, 18, 19, 20]:
                battery_used = min(battery_available, remaining)
                allocation.append(('battery', round(battery_used, 3)))
                remaining -= battery_used
                # Ensure battery charge never goes below zero
                self.battery_charge = max(0, self.battery_charge - battery_used)
                total_cost += battery_used * self.costs['battery']
                total_carbon += battery_used * self.carbon['battery']
        
        # Priority 3: Use grid for remaining
        if remaining > 0:
            allocation.append(('grid', round(remaining, 3)))
            total_cost += remaining * grid_price
            total_carbon += remaining * carbon_intensity
        
        # Recharge battery from excess solar
        if solar_available > power_needed:
            excess = solar_available - power_needed
            charge_amount = min(excess, self.battery_capacity - self.battery_charge)
            # Ensure battery charge never exceeds capacity
            self.battery_charge = min(self.battery_capacity, self.battery_charge + charge_amount)
        
        metrics = {
            'total_power': power_needed,
            'solar_available': round(solar_available, 3),
            'battery_available': round(battery_available, 3),
            'battery_charge': round(self.battery_charge, 2),
            'battery_percentage': round((self.battery_charge / self.battery_capacity) * 100, 1),
            'cost': round(total_cost, 2),
            'carbon': round(total_carbon, 1),
            'primary_source': allocation[0][0] if allocation else 'grid'
        }
        
        return allocation, metrics
    
    def get_recommendation(self, allocation: List[Tuple[str, float]], 
                          metrics: Dict, conditions: Dict) -> str:
        """Generate human-readable recommendation"""
        parts = []
        
        primary = metrics.get('primary_source', 'grid')
        
        if primary == 'solar':
            parts.append("☀️ Using solar power (cleanest option)")
        elif primary == 'battery':
            parts.append("🔋 Using battery power (avoiding grid)")
        else:
            parts.append("⚡ Using grid power")
        
        battery_pct = metrics.get('battery_percentage', 0)
        if battery_pct < 20:
            parts.append("⚠️ Battery low - consider charging")
        elif battery_pct > 80:
            parts.append("✓ Battery well charged")
        
        hour = conditions.get('hour', 12)
        if hour in [17, 18, 19, 20]:
            parts.append("📈 Peak hour - optimize consumption")
        
        return " | ".join(parts)


class SimpleAIService:
    """
    Main AI Service combining forecasting and optimization
    """
    
    def __init__(self):
        self.forecaster = SimpleEnergyForecaster()
        self.optimizer = SimpleSourceOptimizer()
        self.models_loaded = True  # Always ready
    
    def is_available(self) -> bool:
        return True
    
    def get_conditions(self) -> Dict:
        """Get current conditions from database"""
        return self._read_from_database()
    
    def _read_from_database(self) -> Dict:
        """Read conditions from Django database"""
        from ..models import SensorReading, GridData
        
        conditions = self._get_defaults()
        conditions['source'] = 'database'
        
        try:
            # Get latest sensor readings
            for sensor_type in ['temperature', 'humidity', 'ldr', 'current', 'voltage']:
                reading = SensorReading.objects.filter(
                    sensor_type=sensor_type
                ).order_by('-timestamp').first()
                if reading:
                    conditions[sensor_type] = float(reading.value)
            
            # Get latest carbon intensity
            carbon = GridData.objects.filter(
                data_type='carbon_intensity'
            ).order_by('-timestamp').first()
            if carbon:
                conditions['carbon_intensity'] = float(carbon.value)
        except Exception as e:
            print(f"Database read error: {e}")
        
        return conditions
    
    def _get_defaults(self) -> Dict:
        """Default conditions when all else fails"""
        return {
            'hour': timezone.now().hour,
            'temperature': 25.0,
            'humidity': 50.0,
            'ldr': 2000,
            'current': 1.0,
            'voltage': 230.0,
            'carbon_intensity': 450,
            'grid_price': 6.0,
            'source': 'defaults'
        }
    
    def forecast_demand(self, hours_ahead: int = 6) -> Dict:
        """Forecast energy demand"""
        predictions = self.forecaster.forecast(hours_ahead)
        peak_info = self.forecaster.identify_peak_hours(hours_ahead)
        
        return {
            'timestamp': timezone.now().isoformat(),
            'forecast_horizon': hours_ahead,
            'predictions': predictions,
            'peak_hours': peak_info['peak_hours'],
            'next_peak': peak_info['next_peak'],
            'recommendation': peak_info['recommendation'],
            'available': True,
            'model_type': 'statistical_pattern'
        }
    
    def recommend_source(self, load_name: str = "Default Load",
                        load_priority: int = 50,
                        load_power: float = 1000) -> Dict:
        """Recommend energy source for a load"""
        conditions = self.get_conditions()
        power_kw = load_power / 1000.0
        
        allocation, metrics = self.optimizer.optimize_source(power_kw, conditions)
        recommendation = self.optimizer.get_recommendation(allocation, metrics, conditions)
        
        return {
            'timestamp': timezone.now().isoformat(),
            'load_name': load_name,
            'load_priority': load_priority,
            'load_power': load_power,
            'recommended_source': metrics['primary_source'],
            'source_allocation': allocation,
            'metrics': {
                'estimated_cost': metrics['cost'],
                'estimated_carbon': metrics['carbon'],
                'battery_charge': metrics['battery_charge'],
                'battery_percentage': metrics['battery_percentage'],
                'solar_available': metrics['solar_available']
            },
            'conditions': conditions,
            'reasoning': recommendation,
            'confidence': 0.85,
            'algorithm': 'rule_based_optimizer',
            'available': True
        }
    
    def make_decision(self) -> Dict:
        """Make comprehensive energy management decision"""
        # Get forecast
        forecast_result = self.forecast_demand(6)
        
        # Get current conditions
        conditions = self.get_conditions()
        
        # Get predicted demand for next hour
        next_hour_demand = forecast_result['predictions'][0]['predicted_kwh']
        
        # Optimize source allocation
        allocation, metrics = self.optimizer.optimize_source(next_hour_demand, conditions)
        recommendation = self.optimizer.get_recommendation(allocation, metrics, conditions)
        
        # Build decision
        decision = {
            'timestamp': timezone.now().isoformat(),
            'forecast': forecast_result['predictions'],
            'peak_hours': forecast_result['peak_hours'],
            'current_conditions': conditions,
            'current_decision': {
                'predicted_demand_kwh': next_hour_demand,
                'source_allocation': allocation,
                'cost': metrics['cost'],
                'carbon': metrics['carbon'],
                'battery_charge': metrics['battery_charge'],
                'battery_percentage': metrics['battery_percentage'],
                'solar_available': metrics['solar_available'],
                'primary_source': metrics['primary_source']
            },
            'recommendation': recommendation,
            'available': True
        }
        
        # Publish to MQTT if possible
        self._publish_decision(decision)
        
        return decision
    
    def _publish_decision(self, decision: Dict):
        """Publish decision to MQTT for hardware"""
        try:
            import paho.mqtt.publish as publish
            
            payload = {
                'command': 'switch_source',
                'source': decision['current_decision']['primary_source'],
                'details': decision['current_decision'],
                'timestamp': decision['timestamp']
            }
            
            publish.single(
                "HyperVolt/commands/control",
                payload=json.dumps(payload),
                hostname="localhost",
                port=1883
            )
            print(f"✓ Published AI decision to MQTT: {payload['source']}")
        except Exception as e:
            print(f"MQTT publish failed (expected if broker not running): {e}")
    
    def get_status(self) -> Dict:
        """Get AI service status"""
        conditions = self.get_conditions()
        
        return {
            'available': True,
            'models_loaded': True,
            'capabilities': {
                'demand_forecasting': True,
                'source_optimization': True,
                'peak_detection': True,
                'decision_making': True
            },
            'current_conditions': conditions,
            'battery_status': {
                'charge_kwh': self.optimizer.battery_charge,
                'percentage': (self.optimizer.battery_charge / self.optimizer.battery_capacity) * 100,
                'capacity': self.optimizer.battery_capacity
            },
            'solar_capacity': self.optimizer.solar_capacity,
            'timestamp': timezone.now().isoformat()
        }
