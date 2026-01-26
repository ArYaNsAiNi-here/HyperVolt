from rest_framework import serializers
from .models import SensorReading, GridData, UserPreferences, AIDecision, EnergySource, Load, SourceSwitchEvent


class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = '__all__'
        read_only_fields = ('created_at',)


class GridDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GridData
        fields = '__all__'
        read_only_fields = ('created_at',)


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AIDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIDecision
        fields = '__all__'
        read_only_fields = ('created_at',)


class EnergySourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergySource
        fields = '__all__'
        read_only_fields = ('updated_at',)


class LoadSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Load
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class SourceSwitchEventSerializer(serializers.ModelSerializer):
    load_name = serializers.CharField(source='load.name', read_only=True)
    triggered_by_display = serializers.CharField(source='get_triggered_by_display', read_only=True)
    
    class Meta:
        model = SourceSwitchEvent
        fields = '__all__'
        read_only_fields = ('timestamp',)
