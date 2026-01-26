from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import SensorReading, GridData, UserPreferences, AIDecision, EnergySource
from .serializers import (
    SensorReadingSerializer,
    GridDataSerializer,
    UserPreferencesSerializer,
    AIDecisionSerializer,
    EnergySourceSerializer
)
from .services.cache_manager import SensorBufferManager


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
