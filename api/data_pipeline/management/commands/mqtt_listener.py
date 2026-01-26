"""
Django management command to run the MQTT listener.
This is the core of the data ingestion pipeline.

Usage:
    python manage.py mqtt_listener
"""
import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import paho.mqtt.client as mqtt

from data_pipeline.models import SensorReading
from data_pipeline.services.cache_manager import SensorBufferManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Runs the MQTT listener to receive sensor data from Raspberry Pi'

    def __init__(self):
        super().__init__()
        self.buffer_manager = SensorBufferManager()
        self.channel_layer = get_channel_layer()
        self.mqtt_client = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--topics',
            type=str,
            default=None,
            help='Comma-separated list of MQTT topics to subscribe to'
        )

    def handle(self, *args, **options):
        """Main entry point for the command."""
        self.stdout.write(self.style.SUCCESS('Starting MQTT Listener...'))

        # Set up MQTT client
        self.mqtt_client = mqtt.Client(
            client_id=settings.MQTT_CLIENT_ID,
            protocol=mqtt.MQTTv5
        )

        # Set callbacks
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect

        # Set authentication if provided
        if settings.MQTT_USERNAME:
            self.mqtt_client.username_pw_set(
                settings.MQTT_USERNAME,
                settings.MQTT_PASSWORD
            )

        try:
            # Connect to broker
            self.stdout.write(
                f'Connecting to MQTT broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}'
            )
            self.mqtt_client.connect(
                settings.MQTT_BROKER_HOST,
                settings.MQTT_BROKER_PORT,
                keepalive=60
            )

            # Start the network loop
            self.mqtt_client.loop_forever()

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nShutting down MQTT listener...'))
            self.mqtt_client.disconnect()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            logger.error(f'MQTT Listener error: {e}')
            raise

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback when connected to MQTT broker."""
        if rc == 0:
            self.stdout.write(self.style.SUCCESS('Connected to MQTT broker'))
            
            # Subscribe to topics
            topic_pattern = f"{settings.MQTT_TOPIC_PREFIX}/sensors/#"
            client.subscribe(topic_pattern)
            self.stdout.write(self.style.SUCCESS(f'Subscribed to: {topic_pattern}'))
            
            # Also subscribe to commands response topic
            commands_topic = f"{settings.MQTT_TOPIC_PREFIX}/commands/response"
            client.subscribe(commands_topic)
            
        else:
            self.stdout.write(self.style.ERROR(f'Connection failed with code {rc}'))
            logger.error(f'MQTT connection failed: {rc}')

    def on_disconnect(self, client, userdata, rc, properties=None):
        """Callback when disconnected from MQTT broker."""
        if rc != 0:
            self.stdout.write(self.style.WARNING(f'Unexpected disconnection (rc={rc})'))
            logger.warning(f'MQTT disconnected: {rc}')

    def on_message(self, client, userdata, msg):
        """
        Callback when a message is received.
        
        Expected message format (JSON):
        {
            "sensor_type": "ldr",
            "sensor_id": "ldr_1",
            "value": 750,
            "unit": "lux",
            "location": "living_room",
            "timestamp": "2026-01-26T08:00:00Z"
        }
        """
        try:
            # Parse the message
            payload = json.loads(msg.payload.decode('utf-8'))
            
            self.stdout.write(
                self.style.SUCCESS(f'Received on {msg.topic}: {payload}')
            )

            # Validate required fields
            required_fields = ['sensor_type', 'sensor_id', 'value']
            if not all(field in payload for field in required_fields):
                logger.warning(f'Invalid message format: {payload}')
                return

            # Extract data
            sensor_type = payload.get('sensor_type')
            sensor_id = payload.get('sensor_id')
            value = float(payload.get('value'))
            unit = payload.get('unit', 'raw')
            location = payload.get('location', '')
            timestamp = payload.get('timestamp')

            if timestamp:
                timestamp = timezone.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                timestamp = timezone.now()

            # Save to database (Cold Path)
            sensor_reading = SensorReading.objects.create(
                sensor_type=sensor_type,
                sensor_id=sensor_id,
                value=value,
                unit=unit,
                location=location,
                timestamp=timestamp
            )

            # Add to in-memory buffer (Hot Path)
            self.buffer_manager.add_reading(
                sensor_type=sensor_type,
                sensor_id=sensor_id,
                value=value,
                timestamp=timestamp.isoformat()
            )

            # Broadcast to WebSocket clients
            self.broadcast_sensor_data(sensor_reading)

            logger.info(f'Processed sensor reading: {sensor_reading}')

        except json.JSONDecodeError as e:
            logger.error(f'Failed to decode JSON: {e}')
        except Exception as e:
            logger.error(f'Error processing message: {e}')

    def broadcast_sensor_data(self, sensor_reading):
        """
        Broadcast sensor data to WebSocket clients via Django Channels.
        """
        try:
            message = {
                'type': 'sensor_update',
                'data': {
                    'sensor_type': sensor_reading.sensor_type,
                    'sensor_id': sensor_reading.sensor_id,
                    'value': sensor_reading.value,
                    'unit': sensor_reading.unit,
                    'location': sensor_reading.location,
                    'timestamp': sensor_reading.timestamp.isoformat(),
                }
            }

            async_to_sync(self.channel_layer.group_send)(
                'sensor_updates',
                message
            )

        except Exception as e:
            logger.error(f'Failed to broadcast sensor data: {e}')
