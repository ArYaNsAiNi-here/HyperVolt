from django.db import models
from django.utils import timezone


class SensorReading(models.Model):
    """
    Time-series model for sensor data from the Raspberry Pi.
    Stores readings from LDR (light sensor) and Current sensor.
    """
    SENSOR_TYPE_CHOICES = [
        ('ldr', 'Light Dependent Resistor'),
        ('current', 'Current Sensor'),
        ('temperature', 'Temperature Sensor'),
        ('humidity', 'Humidity Sensor'),
        ('voltage', 'Voltage Sensor'),
    ]

    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPE_CHOICES, db_index=True)
    sensor_id = models.CharField(max_length=50, db_index=True, help_text="Unique identifier for the sensor")
    value = models.FloatField(help_text="Sensor reading value")
    unit = models.CharField(max_length=20, default='raw', help_text="Unit of measurement")
    location = models.CharField(max_length=100, blank=True, help_text="Location of the sensor (e.g., living_room)")
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor_type', '-timestamp']),
            models.Index(fields=['sensor_id', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.sensor_type} ({self.sensor_id}): {self.value} at {self.timestamp}"


class GridData(models.Model):
    """
    Model for storing external API data like carbon intensity and weather.
    This data provides context for AI decision-making.
    """
    DATA_TYPE_CHOICES = [
        ('carbon_intensity', 'Grid Carbon Intensity'),
        ('weather', 'Weather Data'),
        ('electricity_price', 'Electricity Price'),
    ]

    data_type = models.CharField(max_length=30, choices=DATA_TYPE_CHOICES, db_index=True)
    value = models.FloatField(help_text="Primary value (e.g., carbon intensity in gCO2/kWh)")
    unit = models.CharField(max_length=20, help_text="Unit of measurement")
    zone = models.CharField(max_length=20, default='IN-KA', help_text="Grid zone identifier")
    metadata = models.JSONField(default=dict, help_text="Additional data in JSON format")
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['data_type', '-timestamp']),
            models.Index(fields=['zone', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.data_type}: {self.value} {self.unit} at {self.timestamp}"


class UserPreferences(models.Model):
    """
    Model for storing user-configurable preferences.
    These control how the system operates (e.g., brightness thresholds).
    """
    preference_key = models.CharField(max_length=100, unique=True, db_index=True)
    preference_value = models.JSONField(help_text="Preference value in JSON format")
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "User Preferences"

    def __str__(self):
        return f"{self.preference_key}: {self.preference_value}"


class AIDecision(models.Model):
    """
    Model for storing AI recommendations and decisions.
    This creates an audit trail of what the AI decided and when.
    """
    DECISION_TYPE_CHOICES = [
        ('power_source', 'Power Source Selection'),
        ('light_dim', 'Light Dimming'),
        ('load_shift', 'Load Shifting'),
        ('general', 'General Recommendation'),
    ]

    decision_type = models.CharField(max_length=30, choices=DECISION_TYPE_CHOICES, db_index=True)
    decision = models.JSONField(help_text="The AI's decision in JSON format")
    confidence = models.FloatField(default=1.0, help_text="Confidence score (0-1)")
    reasoning = models.TextField(blank=True, help_text="Explanation of the decision")
    applied = models.BooleanField(default=False, help_text="Whether the decision was applied")
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['decision_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.decision_type} decision at {self.timestamp}"


class EnergySource(models.Model):
    """
    Model for tracking available energy sources and their status.
    """
    SOURCE_TYPE_CHOICES = [
        ('grid', 'Grid Power'),
        ('solar', 'Solar Power'),
        ('battery', 'Battery Power'),
        ('generator', 'Generator'),
    ]

    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, unique=True)
    is_available = models.BooleanField(default=True)
    capacity = models.FloatField(help_text="Capacity in watts", null=True, blank=True)
    current_output = models.FloatField(help_text="Current output in watts", default=0)
    priority = models.IntegerField(default=0, help_text="Priority level (higher is better)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority']

    def __str__(self):
        return f"{self.source_type} ({'Available' if self.is_available else 'Unavailable'})"


class Load(models.Model):
    """
    Model for tracking electrical loads and their characteristics.
    Used by the energy optimizer to make informed switching decisions.
    """
    PRIORITY_CHOICES = [
        (100, 'Critical'),    # Security, communication, medical
        (75, 'High'),         # HVAC, refrigeration, water pump
        (50, 'Medium'),       # Lighting, computing, cooking
        (25, 'Low'),          # Entertainment, decorative, optional
    ]
    
    CATEGORY_CHOICES = [
        ('hvac', 'HVAC System'),
        ('lighting', 'Lighting'),
        ('appliance', 'Appliance'),
        ('computing', 'Computing'),
        ('entertainment', 'Entertainment'),
        ('security', 'Security System'),
        ('communication', 'Communication'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True, help_text="Load identifier (e.g., 'Living Room HVAC')")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=50, help_text="Load priority level")
    rated_power = models.FloatField(help_text="Rated power consumption in watts")
    current_power = models.FloatField(default=0, help_text="Current power consumption in watts")
    
    # Current state
    is_active = models.BooleanField(default=False, help_text="Whether the load is currently active")
    current_source = models.CharField(
        max_length=20, 
        choices=EnergySource.SOURCE_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Current energy source powering this load"
    )
    
    # Optimization hints
    can_defer = models.BooleanField(default=False, help_text="Can this load be deferred to off-peak times?")
    min_runtime = models.IntegerField(default=0, help_text="Minimum continuous runtime in minutes")
    
    location = models.CharField(max_length=100, blank=True, help_text="Physical location of the load")
    notes = models.TextField(blank=True, help_text="Additional notes about this load")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_priority_display()}, {self.rated_power}W)"


class SourceSwitchEvent(models.Model):
    """
    Model for tracking energy source switching events.
    Provides audit trail and analytics for optimization decisions.
    """
    load = models.ForeignKey(Load, on_delete=models.CASCADE, related_name='switch_events')
    from_source = models.CharField(
        max_length=20,
        choices=EnergySource.SOURCE_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Previous energy source"
    )
    to_source = models.CharField(
        max_length=20,
        choices=EnergySource.SOURCE_TYPE_CHOICES,
        help_text="New energy source"
    )
    
    reason = models.TextField(help_text="Reason for the switch")
    triggered_by = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Manual'),
            ('automatic', 'Automatic'),
            ('ai', 'AI Decision'),
            ('emergency', 'Emergency'),
        ],
        default='automatic'
    )
    
    # Performance metrics
    expected_savings = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Expected cost/carbon savings"
    )
    actual_savings = models.FloatField(
        null=True,
        blank=True,
        help_text="Actual savings (filled in later)"
    )
    
    success = models.BooleanField(default=True, help_text="Whether the switch was successful")
    error_message = models.TextField(blank=True, help_text="Error details if switch failed")
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['load', '-timestamp']),
            models.Index(fields=['to_source', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.load.name}: {self.from_source or 'None'} → {self.to_source} at {self.timestamp}"
