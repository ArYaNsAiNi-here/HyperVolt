from django.contrib import admin
from .models import SensorReading, GridData, UserPreferences, AIDecision, EnergySource, Load, SourceSwitchEvent


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('sensor_type', 'sensor_id', 'value', 'unit', 'location', 'timestamp')
    list_filter = ('sensor_type', 'location', 'timestamp')
    search_fields = ('sensor_id', 'location')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(GridData)
class GridDataAdmin(admin.ModelAdmin):
    list_display = ('data_type', 'value', 'unit', 'zone', 'timestamp')
    list_filter = ('data_type', 'zone', 'timestamp')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('preference_key', 'preference_value', 'updated_at')
    search_fields = ('preference_key', 'description')
    ordering = ('preference_key',)


@admin.register(AIDecision)
class AIDecisionAdmin(admin.ModelAdmin):
    list_display = ('decision_type', 'confidence', 'applied', 'timestamp')
    list_filter = ('decision_type', 'applied', 'timestamp')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(EnergySource)
class EnergySourceAdmin(admin.ModelAdmin):
    list_display = ('source_type', 'is_available', 'current_output', 'priority', 'updated_at')
    list_filter = ('source_type', 'is_available')
    ordering = ('-priority',)


@admin.register(Load)
class LoadAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'priority', 'rated_power', 'is_active', 'current_source')
    list_filter = ('category', 'priority', 'is_active', 'current_source')
    search_fields = ('name', 'location', 'notes')
    ordering = ('-priority', 'name')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'location', 'notes')
        }),
        ('Power Characteristics', {
            'fields': ('rated_power', 'current_power', 'priority')
        }),
        ('Current State', {
            'fields': ('is_active', 'current_source')
        }),
        ('Optimization Settings', {
            'fields': ('can_defer', 'min_runtime')
        }),
    )


@admin.register(SourceSwitchEvent)
class SourceSwitchEventAdmin(admin.ModelAdmin):
    list_display = ('load', 'from_source', 'to_source', 'triggered_by', 'success', 'timestamp')
    list_filter = ('to_source', 'triggered_by', 'success', 'timestamp')
    search_fields = ('load__name', 'reason')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
