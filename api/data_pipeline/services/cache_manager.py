"""
Cache management utilities for the Hot Path.
Implements a sliding window buffer for the latest sensor readings.
"""
import json
import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class SensorBufferManager:
    """
    Manages the in-memory sliding window buffer for sensor readings.
    This is the 'Hot Path' for AI inference.
    """

    def __init__(self):
        self.buffer_size = settings.SENSOR_BUFFER_SIZE
        self.key_prefix = settings.SENSOR_BUFFER_KEY_PREFIX

    def _get_buffer_key(self, sensor_type, sensor_id):
        """Generate cache key for a specific sensor."""
        return f"{self.key_prefix}:{sensor_type}:{sensor_id}"

    def add_reading(self, sensor_type, sensor_id, value, timestamp):
        """
        Add a new reading to the sensor's buffer.
        Maintains a sliding window of the latest N readings.
        
        Args:
            sensor_type: Type of sensor (ldr, current, etc.)
            sensor_id: Unique identifier for the sensor
            value: The sensor reading value
            timestamp: ISO format timestamp
        """
        key = self._get_buffer_key(sensor_type, sensor_id)
        
        # Get existing buffer or create new one
        buffer = cache.get(key, [])
        
        # Add new reading
        reading = {
            'value': value,
            'timestamp': timestamp
        }
        buffer.append(reading)
        
        # Keep only the latest N readings (sliding window)
        if len(buffer) > self.buffer_size:
            buffer = buffer[-self.buffer_size:]
        
        # Save back to cache (expire after 1 hour)
        cache.set(key, buffer, 3600)
        
        logger.debug(f"Added reading to buffer {key}: {reading}")

    def get_latest_readings(self, sensor_type, sensor_id, count=None):
        """
        Get the latest N readings from the buffer.
        
        Args:
            sensor_type: Type of sensor
            sensor_id: Unique identifier for the sensor
            count: Number of readings to retrieve (default: all)
        
        Returns:
            list: List of readings in chronological order
        """
        key = self._get_buffer_key(sensor_type, sensor_id)
        buffer = cache.get(key, [])
        
        if count:
            return buffer[-count:]
        return buffer

    def get_all_buffers(self):
        """
        Get all sensor buffers. Useful for AI inference across multiple sensors.
        
        Returns:
            dict: Dictionary mapping sensor keys to their buffers
        """
        # Note: This is a simplified version. In production, you'd want to
        # maintain a registry of active sensors
        # For now, this returns an empty dict as we need the sensor list
        return {}

    def clear_buffer(self, sensor_type, sensor_id):
        """Clear the buffer for a specific sensor."""
        key = self._get_buffer_key(sensor_type, sensor_id)
        cache.delete(key)
        logger.info(f"Cleared buffer for {key}")

    def get_buffer_stats(self, sensor_type, sensor_id):
        """
        Get statistics about the buffer.
        
        Returns:
            dict: Statistics including count, latest value, etc.
        """
        buffer = self.get_latest_readings(sensor_type, sensor_id)
        
        if not buffer:
            return {
                'count': 0,
                'is_full': False
            }
        
        values = [r['value'] for r in buffer]
        
        return {
            'count': len(buffer),
            'is_full': len(buffer) >= self.buffer_size,
            'latest_value': buffer[-1]['value'],
            'latest_timestamp': buffer[-1]['timestamp'],
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': sum(values) / len(values)
        }
