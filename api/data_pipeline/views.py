from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import SensorReading, GridData, UserPreferences, AIDecision, EnergySource, Load, SourceSwitchEvent
from .serializers import (
    SensorReadingSerializer,
    GridDataSerializer,
    UserPreferencesSerializer,
    AIDecisionSerializer,
    EnergySourceSerializer,
    LoadSerializer,
    SourceSwitchEventSerializer
)
from .services.cache_manager import SensorBufferManager
from .services.energy_optimizer import EnergySourceOptimizer
# Use simple AI service that works without TensorFlow
from .services.simple_ai import SimpleAIService


class SensorReadingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SensorReading model.
    Provides CRUD operations and additional custom endpoints.
    """
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    filterset_fields = ['sensor_type', 'sensor_id', 'location']
    ordering_fields = ['timestamp', 'created_at']

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest reading for each sensor."""
        sensor_type = request.query_params.get('sensor_type')
        sensor_id = request.query_params.get('sensor_id')
        
        queryset = self.queryset
        if sensor_type:
            queryset = queryset.filter(sensor_type=sensor_type)
        if sensor_id:
            queryset = queryset.filter(sensor_id=sensor_id)
        
        # Get distinct sensor IDs and their latest readings
        latest_readings = []
        seen = set()
        
        for reading in queryset:
            key = (reading.sensor_type, reading.sensor_id)
            if key not in seen:
                latest_readings.append(reading)
                seen.add(key)
        
        serializer = self.get_serializer(latest_readings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def all_latest(self, request):
        """Get all sensor readings as a single consolidated object."""
        sensor_data = {
            'temperature': 25.0,
            'humidity': 50.0,
            'ldr': 2000,
            'current': 1.0,
            'voltage': 230.0,
        }
        last_updated = None
        
        for sensor_type in sensor_data.keys():
            reading = self.queryset.filter(
                sensor_type=sensor_type
            ).order_by('-timestamp').first()
            
            if reading:
                sensor_data[sensor_type] = float(reading.value)
                if not last_updated or reading.timestamp > last_updated:
                    last_updated = reading.timestamp
        
        return Response({
            'timestamp': timezone.now().isoformat(),
            'last_sensor_update': last_updated.isoformat() if last_updated else None,
            'sensors': sensor_data,
            'source': 'database'
        })

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent readings within a time window."""
        hours = int(request.query_params.get('hours', 1))
        sensor_type = request.query_params.get('sensor_type')
        sensor_id = request.query_params.get('sensor_id')
        
        start_time = timezone.now() - timedelta(hours=hours)
        queryset = self.queryset.filter(timestamp__gte=start_time)
        
        if sensor_type:
            queryset = queryset.filter(sensor_type=sensor_type)
        if sensor_id:
            queryset = queryset.filter(sensor_id=sensor_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def buffer(self, request):
        """Get readings from the hot path buffer (in-memory cache)."""
        sensor_type = request.query_params.get('sensor_type')
        sensor_id = request.query_params.get('sensor_id')
        
        if not sensor_type or not sensor_id:
            return Response(
                {'error': 'sensor_type and sensor_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        buffer_manager = SensorBufferManager()
        readings = buffer_manager.get_latest_readings(sensor_type, sensor_id)
        stats = buffer_manager.get_buffer_stats(sensor_type, sensor_id)
        
        return Response({
            'readings': readings,
            'stats': stats
        })


class GridDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for GridData model.
    Provides access to external API data (carbon intensity, weather).
    """
    queryset = GridData.objects.all()
    serializer_class = GridDataSerializer
    filterset_fields = ['data_type', 'zone']
    ordering_fields = ['timestamp', 'created_at']

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest data for each data type."""
        data_type = request.query_params.get('data_type')
        
        queryset = self.queryset
        if data_type:
            queryset = queryset.filter(data_type=data_type)
        
        # Get latest for each data type
        latest_data = []
        seen_types = set()
        
        for data in queryset:
            if data.data_type not in seen_types:
                latest_data.append(data)
                seen_types.add(data.data_type)
        
        serializer = self.get_serializer(latest_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def carbon_intensity(self, request):
        """Get recent carbon intensity readings."""
        hours = int(request.query_params.get('hours', 24))
        start_time = timezone.now() - timedelta(hours=hours)
        
        queryset = self.queryset.filter(
            data_type='carbon_intensity',
            timestamp__gte=start_time
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def weather(self, request):
        """Get recent weather data."""
        hours = int(request.query_params.get('hours', 24))
        start_time = timezone.now() - timedelta(hours=hours)
        
        queryset = self.queryset.filter(
            data_type='weather',
            timestamp__gte=start_time
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserPreferences model.
    Allows users to configure system behavior.
    """
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    lookup_field = 'preference_key'

    @action(detail=False, methods=['get'])
    def get_preference(self, request):
        """Get a specific preference by key."""
        key = request.query_params.get('key')
        if not key:
            return Response(
                {'error': 'key parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            preference = self.queryset.get(preference_key=key)
            serializer = self.get_serializer(preference)
            return Response(serializer.data)
        except UserPreferences.DoesNotExist:
            return Response(
                {'error': 'Preference not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class AIDecisionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AIDecision model.
    Tracks AI recommendations and decisions.
    """
    queryset = AIDecision.objects.all()
    serializer_class = AIDecisionSerializer
    filterset_fields = ['decision_type', 'applied']
    ordering_fields = ['timestamp', 'created_at', 'confidence']

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent AI decisions."""
        hours = int(request.query_params.get('hours', 24))
        decision_type = request.query_params.get('decision_type')
        
        start_time = timezone.now() - timedelta(hours=hours)
        queryset = self.queryset.filter(timestamp__gte=start_time)
        
        if decision_type:
            queryset = queryset.filter(decision_type=decision_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the most recent AI decision."""
        decision_type = request.query_params.get('decision_type')
        
        queryset = self.queryset
        if decision_type:
            queryset = queryset.filter(decision_type=decision_type)
        
        latest = queryset.order_by('-timestamp').first()
        
        if latest:
            serializer = self.get_serializer(latest)
            return Response(serializer.data)
        
        return Response({'message': 'No decisions found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get a list of recent AI decisions with summary data for display."""
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)  # Cap at 50
        
        decisions = self.queryset.order_by('-timestamp')[:limit]
        
        result = []
        for decision in decisions:
            decision_data = decision.decision or {}
            current_decision = decision_data.get('current_decision', {})
            
            result.append({
                'id': decision.id,
                'timestamp': decision.timestamp.isoformat(),
                'decision_type': decision.decision_type,
                'reasoning': decision.reasoning,
                'confidence': decision.confidence,
                'applied': decision.applied,
                'primary_source': current_decision.get('primary_source', 'unknown'),
                'predicted_demand_kwh': current_decision.get('predicted_demand_kwh', 0),
                'battery_percentage': current_decision.get('battery_percentage', 0),
                'solar_available': current_decision.get('solar_available', 0),
                'cost': current_decision.get('cost', 0),
                'carbon': current_decision.get('carbon', 0),
            })
        
        return Response({
            'count': len(result),
            'decisions': result
        })


class EnergySourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for EnergySource model.
    Manages available energy sources and their status.
    """
    queryset = EnergySource.objects.all()
    serializer_class = EnergySourceSerializer

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available energy sources."""
        queryset = self.queryset.filter(is_available=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LoadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Load model.
    Manages electrical loads and their characteristics.
    """
    queryset = Load.objects.all()
    serializer_class = LoadSerializer
    filterset_fields = ['category', 'priority', 'is_active']
    ordering_fields = ['priority', 'rated_power', 'name']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all currently active loads."""
        queryset = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_priority(self, request):
        """Get all high and critical priority loads."""
        queryset = self.queryset.filter(priority__gte=75)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def recommend_source(self, request, pk=None):
        """
        Get energy source recommendation for this specific load.
        
        This endpoint allows Module 3 (AI) to override with ML-based recommendations.
        """
        load = self.get_object()
        optimizer = EnergySourceOptimizer()
        
        recommendation = optimizer.recommend_source_for_load(
            load_name=load.name,
            load_priority=load.priority,
            load_power=load.rated_power
        )
        
        return Response(recommendation)
    
    @action(detail=True, methods=['post'])
    def check_switch(self, request, pk=None):
        """
        Check if switching energy source is recommended for this load.
        """
        load = self.get_object()
        
        if not load.current_source:
            return Response({
                'error': 'Load has no current source assigned'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        optimizer = EnergySourceOptimizer()
        switch_recommendation = optimizer.should_switch_source(
            current_source=load.current_source,
            load_name=load.name,
            load_priority=load.priority
        )
        
        return Response(switch_recommendation)


class SourceSwitchEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SourceSwitchEvent model.
    Tracks energy source switching history and analytics.
    """
    queryset = SourceSwitchEvent.objects.all()
    serializer_class = SourceSwitchEventSerializer
    filterset_fields = ['load', 'to_source', 'triggered_by', 'success']
    ordering_fields = ['timestamp']
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent switch events."""
        hours = int(request.query_params.get('hours', 24))
        start_time = timezone.now() - timedelta(hours=hours)
        
        queryset = self.queryset.filter(timestamp__gte=start_time)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_load(self, request):
        """Get switch events grouped by load."""
        load_id = request.query_params.get('load_id')
        
        if not load_id:
            return Response({
                'error': 'load_id parameter required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.queryset.filter(load_id=load_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EnergyOptimizationViewSet(viewsets.ViewSet):
    """
    ViewSet for energy optimization operations.
    Provides recommendations and analytics for energy source selection.
    
    This is the main interface for Module 3 (AI) integration.
    """
    
    @action(detail=False, methods=['post'])
    def recommend(self, request):
        """
        Get energy source recommendation for a load.
        
        Request body:
        {
            "load_name": "HVAC Living Room",
            "load_priority": 75,
            "load_power": 2000
        }
        """
        load_name = request.data.get('load_name')
        load_priority = request.data.get('load_priority', 50)
        load_power = request.data.get('load_power', 0)
        
        if not load_name:
            return Response({
                'error': 'load_name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        optimizer = EnergySourceOptimizer()
        recommendation = optimizer.recommend_source_for_load(
            load_name=load_name,
            load_priority=load_priority,
            load_power=load_power
        )
        
        return Response(recommendation)
    
    @action(detail=False, methods=['get'])
    def context(self, request):
        """
        Get current context for energy optimization.
        
        Returns all relevant data: sensors, weather, carbon, energy sources.
        Module 3 (AI) can use this to make informed decisions.
        """
        optimizer = EnergySourceOptimizer()
        context = optimizer.gather_context()
        
        return Response(context)
    
    @action(detail=False, methods=['get'])
    def distribution(self, request):
        """
        Get optimal distribution of loads across energy sources.
        
        This is a placeholder for Module 3 (AI) to implement sophisticated
        load balancing algorithms.
        """
        optimizer = EnergySourceOptimizer()
        distribution = optimizer.get_optimal_source_distribution()
        
        return Response(distribution)
    
    @action(detail=False, methods=['post'])
    def execute_switch(self, request):
        """
        Execute an energy source switch for a load.
        
        Request body:
        {
            "load_id": 1,
            "to_source": "solar",
            "reason": "High solar availability",
            "triggered_by": "ai"
        }
        
        This endpoint records the switch event. Module 1 (Hardware) will
        actually perform the physical switching via MQTT commands.
        """
        load_id = request.data.get('load_id')
        to_source = request.data.get('to_source')
        reason = request.data.get('reason', 'Automatic optimization')
        triggered_by = request.data.get('triggered_by', 'automatic')
        
        if not load_id or not to_source:
            return Response({
                'error': 'load_id and to_source are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            load = Load.objects.get(id=load_id)
        except Load.DoesNotExist:
            return Response({
                'error': 'Load not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Record the switch event
        switch_event = SourceSwitchEvent.objects.create(
            load=load,
            from_source=load.current_source,
            to_source=to_source,
            reason=reason,
            triggered_by=triggered_by,
        )
        
        # Update load's current source
        load.current_source = to_source
        load.save()
        
        serializer = SourceSwitchEventSerializer(switch_event)
        
        return Response({
            'message': 'Switch recorded successfully',
            'switch_event': serializer.data,
            'mqtt_command': {
                'topic': f'HyperVolt/commands/load_{load.id}',
                'payload': {
                    'command': 'switch_source',
                    'load_id': load.id,
                    'load_name': load.name,
                    'to_source': to_source,
                    'timestamp': timezone.now().isoformat(),
                }
            },
            'note': 'Module 1 (Hardware) should subscribe to MQTT commands and execute the physical switch'
        }, status=status.HTTP_201_CREATED)


class AIPredictionViewSet(viewsets.ViewSet):
    """
    ViewSet for AI model predictions and inference.
    
    This is the main interface for AI integration with the API.
    Provides endpoints for:
    - Energy demand forecasting with peak hour detection
    - Energy source recommendations
    - Real-time decision making
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai_service = SimpleAIService()
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Check AI service status and availability.
        
        Returns information about loaded models and capabilities.
        """
        status = self.ai_service.get_status()
        return Response(status)
    
    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """
        Forecast energy demand for the next N hours.
        
        Query params:
        - hours: Number of hours to forecast (default: 6, max: 24)
        
        Returns:
        {
            "timestamp": "2026-01-26T12:00:00Z",
            "forecast_horizon": 6,
            "predictions": [
                {"hour": 1, "predicted_kwh": 1.5, "is_peak_hour": true, ...},
                ...
            ],
            "peak_hours": [...],
            "recommendation": "...",
            "available": true
        }
        """
        try:
            hours = int(request.query_params.get('hours', 6))
        except (ValueError, TypeError):
            hours = 6
        hours = max(1, min(hours, 24))  # Clamp between 1 and 24 hours
        
        result = self.ai_service.forecast_demand(hours_ahead=hours)
        
        # Record the prediction
        try:
            AIDecision.objects.create(
                decision_type='general',
                timestamp=timezone.now(),
                decision=result,
                confidence=0.85,
                applied=False,
                reasoning=result.get('recommendation', 'Energy demand forecast')
            )
        except Exception as e:
            print(f"Warning: Could not record forecast: {e}")
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def peak_hours(self, request):
        """
        Get predicted peak hours for energy planning.
        
        Returns upcoming peak hours and high-demand periods.
        """
        try:
            hours = int(request.query_params.get('hours', 24))
        except (ValueError, TypeError):
            hours = 24
        hours = max(1, min(hours, 48))  # Clamp between 1 and 48 hours
        
        result = self.ai_service.forecast_demand(hours_ahead=hours)
        
        return Response({
            'timestamp': result['timestamp'],
            'peak_hours': result['peak_hours'],
            'next_peak': result['next_peak'],
            'total_predictions': len(result['predictions']),
            'recommendation': result['recommendation']
        })
    
    @action(detail=False, methods=['post'])
    def recommend_source(self, request):
        """
        Get energy source recommendation using AI optimization.
        
        Request body:
        {
            "load_name": "HVAC Living Room",
            "load_priority": 75,
            "load_power": 2000
        }
        """
        load_name = request.data.get('load_name', 'Default Load')
        load_priority = request.data.get('load_priority', 50)
        load_power = request.data.get('load_power', 1000)
        
        result = self.ai_service.recommend_source(
            load_name=load_name,
            load_priority=load_priority,
            load_power=load_power
        )
        
        # Record the recommendation
        try:
            AIDecision.objects.create(
                decision_type='power_source',
                timestamp=timezone.now(),
                decision=result,
                confidence=result.get('confidence', 0.85),
                applied=False,
                reasoning=result.get('reasoning', '')
            )
        except Exception as e:
            print(f"Warning: Could not record recommendation: {e}")
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def decide(self, request):
        """
        Make a comprehensive energy management decision.
        
        Combines demand forecasting, peak detection, and source optimization.
        
        Returns:
        {
            "timestamp": "2026-01-26T12:00:00Z",
            "forecast": [...],
            "peak_hours": [...],
            "current_conditions": {...},
            "current_decision": {
                "predicted_demand_kwh": 1.5,
                "source_allocation": [["solar", 1.0], ["battery", 0.5]],
                "cost": 3.5,
                "carbon": 250.0,
                "battery_charge": 8.5,
                "primary_source": "solar"
            },
            "recommendation": "...",
            "available": true
        }
        """
        result = self.ai_service.make_decision()
        
        # Record the decision
        try:
            AIDecision.objects.create(
                decision_type='general',
                timestamp=timezone.now(),
                decision=result,
                confidence=0.85,
                applied=True,
                reasoning=result.get('recommendation', '')
            )
        except Exception as e:
            print(f"Warning: Could not record decision: {e}")
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def conditions(self, request):
        """
        Get current sensor conditions being used by AI.
        
        Useful for debugging and monitoring.
        """
        conditions = self.ai_service.get_conditions()
        return Response({
            'timestamp': timezone.now().isoformat(),
            'conditions': conditions,
            'source': conditions.get('source', 'unknown')
        })
