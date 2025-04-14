# data_source.py
import threading
import time
import queue

from sensor_manager import SensorManager

class DataSource:
    """
    Provides data for the visualization application
    Handles data acquisition from multiple hardware sensors
    """
    
    def __init__(self, data_queue, mode="hardware"):
        """
        Initialize the data source
        
        Args:
            data_queue: Queue to send data to the GUI
            mode: Data source mode (hardware, simulation, file)
        """
        self.data_queue = data_queue
        self.mode = mode
        self.running = False
        self.thread = None
        self.stop_event = threading.Event()
        
        # Create sensor manager if using hardware
        self.sensor_manager = None
        if self.mode == "hardware":
            self.sensor_manager = SensorManager(data_queue)
        
    def start(self):
        """Start the data source"""
        if self.running:
            print("Data source is already running")
            return
            
        print(f"Starting data source (mode: {self.mode})")
        self.stop_event.clear()
        self.running = True
        
        if self.mode == "hardware":
            # Start sensor manager for hardware mode
            self.sensor_manager.start()
        else:
            # Start simulation thread for other modes
            self.thread = threading.Thread(target=self._data_loop, daemon=True)
            self.thread.start()
        
    def stop(self):
        """Stop the data source"""
        if not self.running:
            print("Data source is not running")
            return
            
        print("Stopping data source")
        self.stop_event.set()
        self.running = False
        
        if self.mode == "hardware":
            # Stop sensor manager
            if self.sensor_manager:
                self.sensor_manager.stop()
        else:
            # Stop simulation thread
            if self.thread:
                self.thread.join(timeout=2.0)
        
    def _data_loop(self):
        """Main data generation loop (for simulation mode)"""
        print("Data source loop started")
        
        # Import the simulation code here to avoid imports when using hardware
        import random
        import math
        
        # Simulation parameters
        update_rate = 0.05  # seconds between readings
        angle = 0           # starting angle
        angle_increment = 1 # degrees per update
        
        while not self.stop_event.is_set():
            try:
                if self.mode == "simulation":
                    # Update angle
                    angle += angle_increment
                    if angle > 360:
                        angle = 0
                    
                    # Generate torque with some noise
                    base_torque = 50 + 30 * math.sin(math.radians(angle))
                    noise = random.uniform(-2, 2)
                    torque = base_torque + noise
                    
                    # Generate preload with some noise
                    base_preload = 200 + 0.5 * angle + 50 * math.sin(math.radians(angle * 2))
                    noise = random.uniform(-10, 10)
                    preload = base_preload + noise
                    
                    data = {
                        'timestamp': time.time(),
                        'angle': angle,
                        'torque': torque,
                        'preload': preload
                    }
                elif self.mode == "file":
                    data = self._read_data_from_file()
                else:
                    data = None
                
                if data:
                    try:
                        # Add data to queue with timeout
                        self.data_queue.put(data, block=True, timeout=0.1)
                    except queue.Full:
                        print("Queue is full, skipping data point")
                
                # Sleep until next reading
                time.sleep(update_rate)
                
            except Exception as e:
                print(f"Error in data source: {str(e)}")
                time.sleep(1.0)
    
    def _read_data_from_file(self):
        """Read data from a file (placeholder)"""
        # Implementation would depend on file format
        return None