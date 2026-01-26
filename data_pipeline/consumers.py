"""
WebSocket consumers for real-time sensor data streaming.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class SensorConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for streaming sensor data to frontend clients.
    Clients connect and receive real-time updates when sensors publish data.
    """

    async def connect(self):
        """Called when a WebSocket connection is established."""
        # Join the sensor updates group
        self.group_name = 'sensor_updates'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket client connected: {self.channel_name}")

    async def disconnect(self, close_code):
        """Called when a WebSocket connection is closed."""
        # Leave the sensor updates group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket client disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """
        Called when we receive a message from the WebSocket.
        Currently not used, but could be extended for client commands.
        """
        try:
            data = json.loads(text_data)
            logger.debug(f"Received from client: {data}")
            
            # Echo back for now (can be extended later)
            await self.send(text_data=json.dumps({
                'type': 'echo',
                'message': 'Message received'
            }))
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def sensor_update(self, event):
        """
        Called when a sensor_update message is broadcast to the group.
        Forwards the update to the WebSocket client.
        """
        # Send the sensor data to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'sensor_update',
            'data': event['data']
        }))
