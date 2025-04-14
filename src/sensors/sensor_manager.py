# src/sensors/sensor_manager.py
import time
import threading
import queue

from .encoder import EncoderSensor
from .strain_gauge import StrainGaugeSensor
from .load_cell import LoadCellSensor

class SensorManager:
    """
    Manages and synchronizes data from multiple sensors
    """
    
    def __init__(self, data_queue, sync_threshold=0.1):
        """
        Initialize the sensor manager
        
        Args:
            data_queue: Queue to send synchronized data
            sync_threshold: Maximum time difference (in seconds) allowed between readings
        """
        self.data_queue = data_queue
        self.sync_threshold = sync_threshold
        self.running = False
        self.thread = None
        self.stop_event = threading.Event()
        
        # Create sensor instances
        self.encoder = EncoderSensor()
        self.strain_gauge = StrainGaugeSensor()
        self.load_cell = LoadCellSensor()
        
        # List of all sensors for easier management
        self.sensors = [self.encoder, self.strain_gauge, self.load_cell]
        
        # Last synchronized timestamp
        self.last_sync_time = 0
        
    # ... rest of the class implementation stays the same ...
        
    def start(self):
        """Start all sensors and the synchronization thread"""
        if self.running:
            print("Sensor manager is already running")
            return
            
        print("Starting sensor manager")
        
        # Start all sensors
        for sensor in self.sensors:
            sensor.start()
        
        # Start synchronization thread
        self.stop_event.clear()
        self.running = True
        self.thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop all sensors and the synchronization thread"""
        if not self.running:
            return
            
        print("Stopping sensor manager")
        self.stop_event.set()
        self.running = False
        
        # Stop synchronization thread
        if self.thread:
            self.thread.join(timeout=2.0)
        
        # Stop all sensors
        for sensor in self.sensors:
            sensor.stop()
    
    def _sync_loop(self):
        """Main synchronization loop"""
        print("Sensor synchronization loop started")
        
        # Give sensors a moment to start collecting data
        time.sleep(0.5)
        
        while not self.stop_event.is_set():
            try:
                # Attempt to collect synchronized data
                sync_data = self._get_synchronized_data()
                
                if sync_data:
                    try:
                        # Add synchronized data to queue with timeout
                        self.data_queue.put(sync_data, block=True, timeout=0.1)
                    except queue.Full:
                        print("Queue is full, skipping synchronized data point")
                
                # Sleep a short time before next sync attempt
                time.sleep(0.02)  # 20ms sleep allows for up to 50Hz sync rate
                
            except Exception as e:
                print(f"Error in sensor synchronization: {str(e)}")
                time.sleep(0.5)
    
    def _get_synchronized_data(self):
        """
        Get synchronized data from all sensors
        
        Returns:
            Dictionary with synchronized data or None if cannot synchronize
        """
        # Get current readings from all sensors
        encoder_data = self.encoder.get_reading()
        strain_data = self.strain_gauge.get_reading()
        load_cell_data = self.load_cell.get_reading()
        
        # Ensure all sensors have data
        if not encoder_data or not strain_data or not load_cell_data:
            return None
        
        # Check if timestamps are within threshold
        timestamps = [
            encoder_data['timestamp'],
            strain_data['timestamp'],
            load_cell_data['timestamp']
        ]
        
        max_diff = max(timestamps) - min(timestamps)
        if max_diff > self.sync_threshold:
            # Data is not synchronized enough
            return None
        
        # Data is synchronized, create data packet
        now = time.time()
        
        # Only send if this is newer than our last sync
        if now - self.last_sync_time < 0.01:  # Prevent too frequent updates
            return None
            
        self.last_sync_time = now
        
        return {
            'timestamp': now,
            'angle': encoder_data['value'],
            'torque': strain_data['value'],
            'preload': load_cell_data['value']
        }