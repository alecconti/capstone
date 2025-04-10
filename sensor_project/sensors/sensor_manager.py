"""
Manager class for coordinating sensor readings and providing data to the application
"""
import threading
import time
from queue import Queue
from sensor_project.utils.logger import setup_logger
from sensor_project.config.settings import SENSOR_SETTINGS

# In a real project, you would import actual sensor drivers
# from sensor_project.sensors.sensor_driver_1 import read_sensor_1
# from sensor_project.sensors.sensor_driver_2 import read_sensor_2

# For initial development, we'll simulate sensor data
import random

logger = setup_logger(__name__)

class SensorManager:
    """
    Manages sensor reading in a background thread and provides data through a queue
    """
    def __init__(self, raw_data_queue):
        """
        Initialize the sensor manager
        
        Args:
            raw_data_queue (Queue): Thread-safe queue to receive sensor readings
        """
        self.raw_data_queue = raw_data_queue
        self.running = False
        self.sample_rate = SENSOR_SETTINGS['sample_rate']
        self.thread = None
        self.stop_event = threading.Event()
        
        # Initialize sensor connections
        # In a real implementation, you would set up your sensor hardware here
        logger.info("Initializing sensor connections")
        
    def start(self):
        """Start the sensor reading thread"""
        if self.running:
            logger.warning("Sensor manager is already running")
            return
            
        logger.info("Starting sensor manager")
        self.stop_event.clear()
        self.running = True
        self.thread = threading.Thread(target=self._sensor_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop the sensor reading thread"""
        if not self.running:
            logger.warning("Sensor manager is not running")
            return
            
        logger.info("Stopping sensor manager")
        self.stop_event.set()
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)  # Wait for thread to terminate
            
    def _sensor_loop(self):
        """Main sensor reading loop that runs in a separate thread"""
        logger.info("Sensor loop started")
        
        while not self.stop_event.is_set():
            try:
                # In a real application, read from actual sensors
                # sensor1_value = read_sensor_1()
                # sensor2_value = read_sensor_2()
                
                # For development, simulate sensor data
                sensor1_value = random.uniform(20, 30)  # e.g., temperature
                sensor2_value = random.uniform(40, 60)  # e.g., humidity
                
                timestamp = time.time()
                
                # Create data packet
                data = {
                    'timestamp': timestamp,
                    'sensor1': sensor1_value,
                    'sensor2': sensor2_value
                }
                
                # Try to add to queue, with timeout to prevent blocking
                try:
                    self.raw_data_queue.put(data, block=True, timeout=0.1)
                except:
                    logger.warning("Queue is full, skipping data point")
                
                # Sleep until next reading
                time.sleep(self.sample_rate)
                
            except Exception as e:
                logger.error(f"Error in sensor loop: {str(e)}")
                # Brief pause before retrying
                time.sleep(1.0)