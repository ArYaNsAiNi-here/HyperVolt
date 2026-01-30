#!/usr/bin/env python3
"""
HyperVolt Simulation Script - WITH Hardware Sensors
=====================================================

This script runs a complete simulation of the HyperVolt energy management system
by interconnecting ALL 4 Modules:
- Module 1: Hardware Sensors (Raspberry Pi / ESP32)
- Module 2: Backend (Django API)
- Module 3: AI (Decision Engine)
- Module 4: Frontend (Digital Twin)

This script reads REAL sensor data from hardware via MQTT and processes it through
the full pipeline for real-time visualization on the website.

Usage:
    python scripts/run_simulation_with_sensors.py

Requirements:
    - Raspberry Pi / ESP32 with sensors connected and publishing to MQTT
    - MQTT Broker (Mosquitto) running
    - Redis server running
    - Django backend running
    - Optional: Frontend running

Hardware Setup:
    - LDR (Light sensor) on analog pin
    - ACS712 (Current sensor) on analog pin
    - DHT22 (Temperature/Humidity) on digital pin
    - Publish to MQTT topic: HyperVolt/sensors/{location}/{sensor_type}

Author: HyperVolt Team
Date: 2026
"""

import os
import sys
import json
import time
import signal
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import argparse

# Add project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_PATH = os.path.join(PROJECT_ROOT, 'api')
AI_PATH = os.path.join(PROJECT_ROOT, 'ai', 'module3-ai')

sys.path.insert(0, API_PATH)
sys.path.insert(0, AI_PATH)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hypervolt_backend.settings')

try:
    import django
    django.setup()
    DJANGO_AVAILABLE = True
except Exception as e:
    print(f"Warning: Django not available: {e}")
    DJANGO_AVAILABLE = False

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    print("Warning: paho-mqtt not installed. Run: pip install paho-mqtt")
    MQTT_AVAILABLE = False

import requests

# Configuration
MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST', 'localhost')
MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT', 1883))
MQTT_TOPIC_PREFIX = os.environ.get('MQTT_TOPIC_PREFIX', 'HyperVolt/sensors')
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')
DECISION_INTERVAL_SECONDS = int(os.environ.get('DECISION_INTERVAL', 30))

# Global flag for graceful shutdown
shutdown_flag = threading.Event()


class SensorDataProcessor:
    """
    Processes real sensor data received via MQTT.
    Stores readings and calculates derived values.
    """
    
    def __init__(self):
        self.latest_readings = {}
        self.reading_history = []
        self.lock = threading.Lock()
        
    def add_reading(self, sensor_type: str, value: float, 
                    sensor_id: str = None, unit: str = None, location: str = None):
        """Add a new sensor reading."""
        with self.lock:
            reading = {
                'timestamp': datetime.now().isoformat(),
                'sensor_type': sensor_type,
                'sensor_id': sensor_id or f'{sensor_type}_1',
                'value': value,
                'unit': unit or 'unit',
                'location': location or 'living_room',
            }
            
            self.latest_readings[sensor_type] = reading
            self.reading_history.append(reading)
            
            # Keep only last 1000 readings
            if len(self.reading_history) > 1000:
                self.reading_history = self.reading_history[-1000:]
            
            return reading
    
    def get_latest(self, sensor_type: str = None) -> Dict:
        """Get latest reading(s)."""
        with self.lock:
            if sensor_type:
                return self.latest_readings.get(sensor_type)
            return self.latest_readings.copy()
    
    def get_current_conditions(self) -> Dict:
        """Get current conditions for AI inference."""
        with self.lock:
            conditions = {
                'hour': datetime.now().hour,
                'temperature': 25.0,
                'shortwave_radiation': 500.0,
                'cloud_cover': 30.0,
                'carbon_intensity': 450.0,
                'grid_price': 6.0,
            }
            
            # Override with actual sensor values
            if 'temperature' in self.latest_readings:
                conditions['temperature'] = self.latest_readings['temperature']['value']
            
            if 'ldr' in self.latest_readings:
                # Map LDR (0-4095) to solar radiation (0-1000 W/m2)
                ldr_value = self.latest_readings['ldr']['value']
                conditions['shortwave_radiation'] = (ldr_value / 4095.0) * 1000.0
            
            return conditions


class MQTTSensorListener:
    """
    Listens for sensor data from hardware via MQTT.
    Parses incoming messages and forwards to the data processor.
    """
    
    def __init__(self, processor: SensorDataProcessor, broker_host: str = MQTT_BROKER_HOST,
                 broker_port: int = MQTT_BROKER_PORT):
        self.processor = processor
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = None
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker."""
        if rc == 0:
            print(f"  ✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.connected = True
            
            # Subscribe to sensor topics
            topic = f"{MQTT_TOPIC_PREFIX}/#"
            client.subscribe(topic)
            print(f"  📡 Subscribed to: {topic}")
        else:
            print(f"  ❌ Failed to connect to MQTT broker (code: {rc})")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker."""
        print(f"  ⚠ Disconnected from MQTT broker (code: {rc})")
        self.connected = False
    
    def on_message(self, client, userdata, msg):
        """Callback when a message is received."""
        try:
            # Parse topic: HyperVolt/sensors/{location}/{sensor_type}
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 4:
                location = topic_parts[2]
                sensor_type = topic_parts[3]
            else:
                print(f"  ⚠ Invalid topic format: {msg.topic}")
                return

            # Parse payload
            try:
                payload = json.loads(msg.payload.decode())
            except json.JSONDecodeError:
                # Try parsing as simple value
                payload = {'value': float(msg.payload.decode())}

            # Extract values
            value = payload.get('value', 0)
            sensor_id = payload.get('sensor_id', f'{sensor_type}_1')
            unit = payload.get('unit', 'unit')

            # Add to processor
            reading = self.processor.add_reading(
                sensor_type=sensor_type,
                value=value,
                sensor_id=sensor_id,
                unit=unit,
                location=location
            )
            
            print(f"  📥 Received: {sensor_type} = {value:.2f} {unit} from {location}")
            
        except Exception as e:
            print(f"  ⚠ Error processing message: {e}")
    
    def start(self):
        """Start the MQTT listener."""
        if not MQTT_AVAILABLE:
            print("  ❌ MQTT client not available!")
            return False
        
        try:
            self.client = mqtt.Client(client_id='hypervolt_sim_listener')
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            
            print(f"\n  Connecting to MQTT broker at {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            
            # Wait for connection
            time.sleep(2)
            return self.connected
            
        except Exception as e:
            print(f"  ❌ Failed to connect to MQTT: {e}")
            return False
    
    def stop(self):
        """Stop the MQTT listener."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            print("  MQTT listener stopped.")


class RealSensorSimulationRunner:
    """
    Main simulation runner that coordinates real sensor data,
    API calls, AI decision making, and frontend updates.
    """
    
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.processor = SensorDataProcessor()
        self.mqtt_listener = MQTTSensorListener(self.processor)
        self.decision_history = []
        self.stats = {
            'total_iterations': 0,
            'sensor_readings_received': 0,
            'successful_api_calls': 0,
            'ai_decisions_made': 0,
            'total_cost': 0.0,
            'total_carbon': 0.0,
        }
        self.last_decision_time = 0
    
    def check_api_health(self) -> bool:
        """Check if the API is available."""
        try:
            response = requests.get(f"{self.api_url}/api/ai/status/", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def check_mqtt_broker(self) -> bool:
        """Check if MQTT broker is available."""
        return self.mqtt_listener.start()
    
    def update_simulation_file(self, conditions: Dict):
        """Update the simulation sensor file (set to real sensor mode)."""
        csv_path = os.path.join(API_PATH, 'data', 'simulation_sensors.csv')
        
        csv_content = "timestamp,sensor_type,value\n"
        timestamp = datetime.now().isoformat()
        
        latest = self.processor.get_latest()
        for sensor_type, reading in latest.items():
            csv_content += f"{timestamp},{sensor_type},{reading['value']}\n"
        
        try:
            with open(csv_path, 'w') as f:
                f.write(csv_content)
            return True
        except Exception as e:
            print(f"  ⚠ Failed to update simulation file: {e}")
            return False
    
    def post_sensor_reading(self, reading: Dict) -> bool:
        """Post a sensor reading to the API."""
        try:
            response = requests.post(
                f"{self.api_url}/api/sensor-readings/",
                json=reading,
                timeout=5
            )
            return response.status_code in [200, 201]
        except requests.exceptions.RequestException:
            return False
    
    def trigger_ai_decision(self) -> Dict:
        """Trigger the AI to make an energy management decision."""
        try:
            response = requests.post(
                f"{self.api_url}/api/ai/decide/",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def send_command_to_hardware(self, decision: Dict):
        """Send control command back to hardware via MQTT."""
        if not self.mqtt_listener.client or not self.mqtt_listener.connected:
            return
        
        try:
            current_decision = decision.get('current_decision', {})
            allocation = current_decision.get('source_allocation', [])
            
            if not allocation:
                return
            
            # Determine primary source
            primary_source = allocation[0][0] if allocation else 'grid'
            
            command = {
                'command': 'switch_source',
                'source': primary_source,
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'predicted_demand': current_decision.get('predicted_demand_kwh', 0),
                    'allocation': allocation,
                    'cost': current_decision.get('cost', 0),
                    'carbon': current_decision.get('carbon', 0),
                }
            }
            
            topic = "HyperVolt/commands/control"
            payload = json.dumps(command)
            
            self.mqtt_listener.client.publish(topic, payload)
            print(f"  📤 Sent command to hardware: switch to {primary_source}")
            
        except Exception as e:
            print(f"  ⚠ Failed to send command to hardware: {e}")
    
    def run_iteration(self) -> Dict:
        """Run a single simulation iteration."""
        result = {
            'timestamp': datetime.now().isoformat(),
            'latest_readings': self.processor.get_latest(),
            'conditions': self.processor.get_current_conditions(),
            'api_success': True,
            'decision': None,
        }
        
        # Update simulation file with latest readings
        self.update_simulation_file(result['conditions'])
        
        # Post latest readings to API
        for sensor_type, reading in result['latest_readings'].items():
            success = self.post_sensor_reading(reading)
            if success:
                self.stats['successful_api_calls'] += 1
        
        # Check if it's time for an AI decision
        current_time = time.time()
        decision_interval = getattr(self, 'decision_interval', DECISION_INTERVAL_SECONDS)
        if current_time - self.last_decision_time >= decision_interval:
            decision = self.trigger_ai_decision()
            if decision and decision.get('available'):
                result['decision'] = decision
                self.stats['ai_decisions_made'] += 1
                self.decision_history.append(decision)
                
                # Update stats
                current_decision = decision.get('current_decision', {})
                self.stats['total_cost'] += current_decision.get('cost', 0)
                self.stats['total_carbon'] += current_decision.get('carbon', 0)
                
                # Send command to hardware
                self.send_command_to_hardware(decision)
                
                self.last_decision_time = current_time
        
        self.stats['total_iterations'] += 1
        self.stats['sensor_readings_received'] = len(self.processor.reading_history)
        
        return result
    
    def print_status(self, result: Dict):
        """Print the current simulation status."""
        readings = result.get('latest_readings', {})
        conditions = result.get('conditions', {})
        decision = result.get('decision')
        
        print(f"\n{'='*60}")
        print(f"  Real-Time Sensor Simulation - {datetime.now().strftime('%H:%M:%S')}")
        print(f"  MQTT Connected: {'✅' if self.mqtt_listener.connected else '❌'}")
        print(f"  Iteration: {self.stats['total_iterations']}")
        print(f"{'='*60}")
        
        if readings:
            print(f"\n  📊 Latest Sensor Readings:")
            for sensor_type, reading in readings.items():
                print(f"     {sensor_type}: {reading['value']:.2f} {reading['unit']} ({reading['location']})")
        else:
            print(f"\n  ⚠ No sensor readings received yet.")
            print(f"     Waiting for data from hardware...")
        
        print(f"\n  🌍 Current Conditions (for AI):")
        print(f"     Hour: {conditions.get('hour', 0)}")
        print(f"     Temperature: {conditions.get('temperature', 0):.1f}°C")
        print(f"     Solar Radiation: {conditions.get('shortwave_radiation', 0):.0f} W/m²")
        
        if decision and decision.get('available'):
            current = decision.get('current_decision', {})
            allocation = current.get('source_allocation', [])
            
            print(f"\n  🤖 AI Decision:")
            print(f"     Predicted Demand: {current.get('predicted_demand_kwh', 0):.3f} kWh")
            print(f"     Source Allocation:")
            for source, power in allocation:
                print(f"       - {source}: {power:.3f} kW")
            print(f"     Cost: ₹{current.get('cost', 0):.2f}")
            print(f"     Carbon: {current.get('carbon', 0):.0f} gCO2eq")
            print(f"     Recommendation: {decision.get('recommendation', 'N/A')[:50]}...")
        
        print(f"\n  📈 Cumulative Stats:")
        print(f"     Total Sensor Readings: {self.stats['sensor_readings_received']}")
        print(f"     Successful API Calls: {self.stats['successful_api_calls']}")
        print(f"     AI Decisions: {self.stats['ai_decisions_made']}")
        print(f"     Total Cost: ₹{self.stats['total_cost']:.2f}")
        print(f"     Total Carbon: {self.stats['total_carbon']/1000:.2f} kg CO2")
    
    def run(self, duration_minutes: int = 60, interval_seconds: int = 5, 
            decision_interval: int = DECISION_INTERVAL_SECONDS):
        """
        Run the simulation with real sensor data.
        
        Args:
            duration_minutes: How long to run the simulation
            interval_seconds: Time between status updates
            decision_interval: Time between AI decisions in seconds
        """
        # Store decision interval for use in run_iteration
        self.decision_interval = decision_interval
        print("\n" + "="*60)
        print("  HYPERVOLT SIMULATION - WITH REAL SENSORS")
        print("  Interconnecting ALL 4 Modules")
        print("  Module 1: Hardware Sensors (MQTT)")
        print("  Module 2: Backend (Django API)")
        print("  Module 3: AI (Decision Engine)")
        print("  Module 4: Frontend (Digital Twin)")
        print("="*60)
        
        # Check API health
        print("\n  Checking API health...")
        if not self.check_api_health():
            print("  ❌ API is not available! Please start the Django backend:")
            print("     cd api && python manage.py runserver")
            return
        print("  ✅ API is available!")
        
        # Check MQTT broker
        print("\n  Checking MQTT broker...")
        if not self.check_mqtt_broker():
            print("  ❌ MQTT broker is not available!")
            print("     Please start Mosquitto: mosquitto -v")
            return
        
        # Get AI status
        print("\n  Checking AI models...")
        try:
            response = requests.get(f"{self.api_url}/api/ai/status/", timeout=5)
            ai_status = response.json()
            if ai_status.get('available'):
                print("  ✅ AI models loaded and ready!")
            else:
                print("  ⚠ AI models not available. Using rule-based optimization.")
        except Exception:
            print("  ⚠ Could not check AI status.")
        
        print(f"\n  Starting simulation:")
        print(f"    Duration: {duration_minutes} minutes")
        print(f"    Update interval: {interval_seconds} seconds")
        print(f"    AI decision interval: {decision_interval} seconds")
        print(f"\n  Waiting for sensor data from hardware...")
        print(f"  Make sure your Raspberry Pi / ESP32 is publishing to MQTT.")
        print(f"  Press Ctrl+C to stop\n")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time and not shutdown_flag.is_set():
                # Run iteration
                result = self.run_iteration()
                
                # Print status
                self.print_status(result)
                
                # Wait for next iteration
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\n  Simulation stopped by user.")
        finally:
            self.mqtt_listener.stop()
        
        # Print final summary
        self.print_summary()
    
    def print_summary(self):
        """Print final simulation summary."""
        print("\n" + "="*60)
        print("  SIMULATION SUMMARY")
        print("="*60)
        print(f"\n  Total Iterations: {self.stats['total_iterations']}")
        print(f"  Sensor Readings Received: {self.stats['sensor_readings_received']}")
        print(f"  Successful API Calls: {self.stats['successful_api_calls']}")
        print(f"  AI Decisions Made: {self.stats['ai_decisions_made']}")
        print(f"  Total Cost: ₹{self.stats['total_cost']:.2f}")
        print(f"  Total Carbon: {self.stats['total_carbon']/1000:.2f} kg CO2")
        
        if self.decision_history:
            print(f"\n  Last AI Decision:")
            last_decision = self.decision_history[-1]
            current = last_decision.get('current_decision', {})
            print(f"    Allocation: {current.get('source_allocation', [])}")
            print(f"    Recommendation: {last_decision.get('recommendation', 'N/A')}")
        
        print("\n" + "="*60)
        print("  Simulation complete!")
        print("  Check the HyperVolt dashboard: http://localhost:3000")
        print("="*60 + "\n")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n  Received shutdown signal...")
    shutdown_flag.set()


def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(
        description='HyperVolt Simulation - With Real Sensors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_simulation_with_sensors.py
  python run_simulation_with_sensors.py --duration 30 --interval 10
  python run_simulation_with_sensors.py --mqtt-host 192.168.1.100
  
Hardware Setup:
  1. Connect sensors to Raspberry Pi / ESP32
  2. Install MQTT library on hardware
  3. Publish sensor data to topics:
     - HyperVolt/sensors/living_room/ldr
     - HyperVolt/sensors/living_room/temperature
     - HyperVolt/sensors/living_room/humidity
     - HyperVolt/sensors/living_room/current
  
  Payload format (JSON):
  {
    "sensor_type": "ldr",
    "sensor_id": "ldr_1",
    "value": 2500,
    "unit": "raw",
    "location": "living_room",
    "timestamp": "2026-01-28T12:00:00Z"
  }
        """
    )
    parser.add_argument('--duration', type=int, default=60,
                        help='Simulation duration in minutes (default: 60)')
    parser.add_argument('--interval', type=int, default=5,
                        help='Status update interval in seconds (default: 5)')
    parser.add_argument('--mqtt-host', type=str, default=MQTT_BROKER_HOST,
                        help=f'MQTT broker host (default: {MQTT_BROKER_HOST})')
    parser.add_argument('--mqtt-port', type=int, default=MQTT_BROKER_PORT,
                        help=f'MQTT broker port (default: {MQTT_BROKER_PORT})')
    parser.add_argument('--api-url', type=str, default=API_BASE_URL,
                        help=f'Backend API URL (default: {API_BASE_URL})')
    parser.add_argument('--decision-interval', type=int, default=DECISION_INTERVAL_SECONDS,
                        help=f'AI decision interval in seconds (default: {DECISION_INTERVAL_SECONDS})')
    
    args = parser.parse_args()
    
    # Create and run simulation
    runner = RealSensorSimulationRunner(api_url=args.api_url)
    runner.mqtt_listener.broker_host = args.mqtt_host
    runner.mqtt_listener.broker_port = args.mqtt_port
    
    runner.run(
        duration_minutes=args.duration,
        interval_seconds=args.interval,
        decision_interval=args.decision_interval
    )


if __name__ == '__main__':
    main()
