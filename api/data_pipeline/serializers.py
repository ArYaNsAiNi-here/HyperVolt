from rest_framework import serializers
from .models import SensorReading, GridData, UserPreferences, AIDecision, EnergySource


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
