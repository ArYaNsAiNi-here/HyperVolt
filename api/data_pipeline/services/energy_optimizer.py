"""
Energy source optimization service.
Provides logic for selecting optimal energy sources based on availability,
weather conditions, sensor data, and load priorities.

This service prepares the groundwork for Module 3 (AI) by:
- Defining the decision framework
- Providing context gathering methods
- Implementing basic fallback logic
- Offering hooks for AI-based optimization
"""
import logging
from django.utils import timezone
from django.db.models import Q

from data_pipeline.models import (
    EnergySource, 
    SensorReading, 
    GridData, 
    AIDecision,
    UserPreferences
)

logger = logging.getLogger(__name__)


class EnergySourceOptimizer:
    """
    Service for optimizing energy source selection.
    
    This class provides:
    1. Context gathering from sensors and APIs
    2. Basic rule-based optimization (fallback)
    3. Hooks for AI-based decision making (Module 3)
    4. Decision recording and execution
    """
    
    # Load priority levels
    PRIORITY_CRITICAL = 100  # Critical loads (security, communication)
    PRIORITY_HIGH = 75       # High priority (HVAC, refrigeration)
    PRIORITY_MEDIUM = 50     # Medium priority (lighting, entertainment)
    PRIORITY_LOW = 25        # Low priority (decorative, optional)
    
    # Energy source preference order (higher is better)
    SOURCE_PREFERENCES = {
        'solar': 100,      # Most preferred (free, clean)
        'battery': 75,     # Second choice (stored clean energy)
        'generator': 25,   # Fallback (expensive, dirty)
        'grid': 50,        # Middle ground (depends on carbon intensity)
    }
    
    def __init__(self):
        self.context = {}
    
    def gather_context(self):
        """
        Gather all relevant context for energy optimization decision.
        
        Returns:
            dict: Context including sensor data, weather, carbon intensity, etc.
        """
        context = {
            'timestamp': timezone.now().isoformat(),
            'energy_sources': self._get_energy_source_status(),
            'weather': self._get_weather_context(),
            'carbon_intensity': self._get_carbon_intensity(),
            'sensor_data': self._get_sensor_data(),
            'user_preferences': self._get_user_preferences(),
        }
        
        self.context = context
        return context
    
    def _get_energy_source_status(self):
        """Get current status of all energy sources."""
        sources = {}
        for source in EnergySource.objects.all():
            sources[source.source_type] = {
                'available': source.is_available,
                'capacity': source.capacity,
                'current_output': source.current_output,
                'priority': source.priority,
            }
        return sources
    
    def _get_weather_context(self):
        """Get weather context (for solar availability prediction)."""
        try:
            latest_weather = GridData.objects.filter(
                data_type='weather'
            ).order_by('-timestamp').first()
            
            if latest_weather:
                return {
                    'temperature': latest_weather.value,
                    'cloud_cover': latest_weather.metadata.get('cloud_cover', 0),
                    'condition': latest_weather.metadata.get('weather_condition', 'Unknown'),
                    'timestamp': latest_weather.timestamp.isoformat(),
                }
        except Exception as e:
            logger.error(f"Error getting weather context: {e}")
        
        return None
    
    def _get_carbon_intensity(self):
        """Get current grid carbon intensity."""
        try:
            latest_carbon = GridData.objects.filter(
                data_type='carbon_intensity'
            ).order_by('-timestamp').first()
            
            if latest_carbon:
                return {
                    'value': latest_carbon.value,
                    'unit': latest_carbon.unit,
                    'timestamp': latest_carbon.timestamp.isoformat(),
                }
        except Exception as e:
            logger.error(f"Error getting carbon intensity: {e}")
        
        return None
    
    def _get_sensor_data(self):
        """Get recent sensor readings."""
        sensors = {}
        
        # Get latest reading for each sensor type
        sensor_types = ['ldr', 'current', 'temperature', 'humidity']
        for sensor_type in sensor_types:
            try:
                latest = SensorReading.objects.filter(
                    sensor_type=sensor_type
                ).order_by('-timestamp').first()
                
                if latest:
                    sensors[sensor_type] = {
                        'value': latest.value,
                        'unit': latest.unit,
                        'timestamp': latest.timestamp.isoformat(),
                    }
            except Exception as e:
                logger.error(f"Error getting {sensor_type} data: {e}")
        
        return sensors
    
    def _get_user_preferences(self):
        """Get user preferences for energy optimization."""
        prefs = {}
        try:
            # Get comfort preferences
            comfort_pref = UserPreferences.objects.filter(
                preference_key='comfort_level'
            ).first()
            if comfort_pref:
                prefs['comfort_level'] = comfort_pref.preference_value
            
            # Get cost preferences
            cost_pref = UserPreferences.objects.filter(
                preference_key='cost_optimization'
            ).first()
            if cost_pref:
                prefs['cost_optimization'] = cost_pref.preference_value
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
        
        return prefs
    
    def recommend_source_for_load(self, load_name, load_priority=PRIORITY_MEDIUM, load_power=0):
        """
        Recommend optimal energy source for a specific load.
        
        This is the main method that Module 3 (AI) can override or enhance.
        Currently implements basic rule-based logic as a fallback.
        
        Args:
            load_name (str): Name of the load (e.g., "HVAC", "Lighting")
            load_priority (int): Priority level of the load
            load_power (float): Power requirement in watts
        
        Returns:
            dict: Recommendation with source, reasoning, and confidence
        """
        # Gather latest context
        context = self.gather_context()
        
        # Get available sources
        available_sources = [
            source for source, status in context['energy_sources'].items()
            if status['available'] and status['capacity'] and status['current_output'] + load_power <= status['capacity']
        ]
        
        if not available_sources:
            return {
                'recommended_source': None,
                'reasoning': 'No energy sources available with sufficient capacity',
                'confidence': 1.0,
                'fallback_to_grid': True,
                'context': context,
            }
        
        # Rule-based optimization (Module 3 AI will enhance this)
        recommendation = self._rule_based_optimization(
            available_sources, 
            load_name, 
            load_priority, 
            load_power,
            context
        )
        
        # Record decision
        self._record_decision(recommendation)
        
        return recommendation
    
    def _rule_based_optimization(self, available_sources, load_name, load_priority, load_power, context):
        """
        Basic rule-based optimization logic.
        Module 3 (AI) will replace or enhance this with ML-based decisions.
        
        Rules:
        1. If solar available and sunny, prefer solar
        2. If grid down, prefer battery for high-priority loads
        3. If grid carbon high, prefer clean sources
        4. Otherwise, use source preference order
        """
        reasoning_parts = []
        scores = {}
        
        # Score each available source
        for source in available_sources:
            score = self.SOURCE_PREFERENCES.get(source, 0)
            
            # Adjust score based on context
            
            # Solar bonus if sunny
            if source == 'solar':
                weather = context.get('weather')
                if weather:
                    cloud_cover = weather.get('cloud_cover', 100)
                    if cloud_cover < 30:
                        score += 20
                        reasoning_parts.append("Clear weather favors solar")
                    elif cloud_cover < 60:
                        score += 10
                        reasoning_parts.append("Partly cloudy, solar still viable")
                
                # Check LDR sensor
                ldr_data = context.get('sensor_data', {}).get('ldr')
                if ldr_data and ldr_data['value'] > 500:
                    score += 15
                    reasoning_parts.append("High light intensity detected")
            
            # Grid penalty if high carbon intensity
            if source == 'grid':
                carbon = context.get('carbon_intensity')
                if carbon and carbon['value'] > 500:  # High carbon
                    score -= 30
                    reasoning_parts.append("High grid carbon intensity")
                elif carbon and carbon['value'] < 300:  # Low carbon
                    score += 20
                    reasoning_parts.append("Low grid carbon intensity")
            
            # Battery consideration for high-priority loads
            if source == 'battery' and load_priority >= self.PRIORITY_HIGH:
                score += 15
                reasoning_parts.append("Battery prioritized for critical loads")
            
            scores[source] = score
        
        # Select best source
        recommended_source = max(scores, key=scores.get)
        
        # Build reasoning
        reasoning = f"Selected {recommended_source} for {load_name}. "
        reasoning += " ".join(reasoning_parts[:3])  # Top 3 reasons
        
        return {
            'recommended_source': recommended_source,
            'load_name': load_name,
            'load_priority': load_priority,
            'load_power': load_power,
            'reasoning': reasoning,
            'confidence': 0.7,  # Rule-based has moderate confidence
            'scores': scores,
            'context': context,
            'algorithm': 'rule_based',  # Module 3 will set this to 'ml' or 'hybrid'
        }
    
    def _record_decision(self, recommendation):
        """Record the energy optimization decision."""
        try:
            AIDecision.objects.create(
                decision_type='power_source',
                decision={
                    'recommended_source': recommendation['recommended_source'],
                    'load_name': recommendation.get('load_name'),
                    'load_priority': recommendation.get('load_priority'),
                    'load_power': recommendation.get('load_power'),
                    'scores': recommendation.get('scores', {}),
                    'algorithm': recommendation.get('algorithm', 'rule_based'),
                },
                confidence=recommendation.get('confidence', 0.5),
                reasoning=recommendation['reasoning'],
                applied=False,  # Module 1 (Hardware) will set this to True when applied
            )
        except Exception as e:
            logger.error(f"Error recording decision: {e}")
    
    def get_optimal_source_distribution(self):
        """
        Get optimal distribution of loads across available sources.
        
        This is a placeholder for Module 3 (AI) to implement more sophisticated
        load balancing and optimization algorithms.
        
        Returns:
            dict: Distribution plan with sources and assigned loads
        """
        context = self.gather_context()
        
        # For now, return simple recommendations
        # Module 3 will implement sophisticated optimization here
        
        distribution = {
            'timestamp': context['timestamp'],
            'available_sources': list(context['energy_sources'].keys()),
            'recommendations': [
                {
                    'load_category': 'HVAC',
                    'priority': self.PRIORITY_HIGH,
                    'recommended_source': 'solar',
                    'fallback_source': 'battery',
                },
                {
                    'load_category': 'Lighting',
                    'priority': self.PRIORITY_MEDIUM,
                    'recommended_source': 'grid',
                    'fallback_source': 'solar',
                },
                {
                    'load_category': 'Entertainment',
                    'priority': self.PRIORITY_LOW,
                    'recommended_source': 'grid',
                    'fallback_source': 'battery',
                },
            ],
            'note': 'Basic rule-based distribution. Module 3 will enhance with ML optimization.',
        }
        
        return distribution
    
    def should_switch_source(self, current_source, load_name, load_priority):
        """
        Determine if switching from current source is recommended.
        
        Args:
            current_source (str): Currently used source
            load_name (str): Name of the load
            load_priority (int): Priority of the load
        
        Returns:
            dict: Switch recommendation with reasoning
        """
        recommendation = self.recommend_source_for_load(load_name, load_priority)
        
        recommended = recommendation['recommended_source']
        
        if recommended == current_source:
            return {
                'should_switch': False,
                'current_source': current_source,
                'reasoning': 'Current source is optimal',
            }
        
        # Check if switch is beneficial enough
        current_score = self.SOURCE_PREFERENCES.get(current_source, 0)
        recommended_score = recommendation.get('scores', {}).get(recommended, 0)
        
        # Require significant improvement to switch (avoid frequent switching)
        threshold = 20
        if recommended_score - current_score > threshold:
            return {
                'should_switch': True,
                'current_source': current_source,
                'recommended_source': recommended,
                'reasoning': recommendation['reasoning'],
                'score_improvement': recommended_score - current_score,
            }
        
        return {
            'should_switch': False,
            'current_source': current_source,
            'reasoning': 'Improvement not significant enough to justify switching',
            'score_difference': recommended_score - current_score,
        }
