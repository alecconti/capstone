    """
    Data source for the sensor visualization application
    Can be configured to read from simulated data, file, or real sensors
    """
    import threading
    import time
    import random
    import queue
    import math

    class DataSource:
        """
        Provides data for the visualization application
        Currently simulates data, but can be extended to read from real sensors
        """
        
        def __init__(self, data_queue, mode="simulation"):
            """
            Initialize the data source
            
            Args:
                data_queue: Queue to send data to the GUI
                mode: Data source mode (simulation, file, sensors)
            """
            self.data_queue = data_queue
            self.mode = mode
            self.running = False
            self.thread = None
            self.stop_event = threading.Event()
            
            # Simulation parameters
            self.update_rate = 0.05  # seconds between readings
            self.angle = 0           # starting angle
            self.angle_increment = 1 # degrees per update
            
        def start(self):
            """Start the data source thread"""
            if self.running:
                print("Data source is already running")
                return
                
            print("Starting data source")
            self.stop_event.clear()
            self.running = True
            self.thread = threading.Thread(target=self._data_loop, daemon=True)
            self.thread.start()
            
        def stop(self):
            """Stop the data source thread"""
            if not self.running:
                print("Data source is not running")
                return
                
            print("Stopping data source")
            self.stop_event.set()
            self.running = False
            if self.thread:
                self.thread.join(timeout=2.0)
        
        def _data_loop(self):
            """Main data generation loop"""
            print("Data source loop started")
            
            while not self.stop_event.is_set():
                try:
                    if self.mode == "simulation":
                        data = self._generate_simulated_data()
                    elif self.mode == "file":
                        data = self._read_data_from_file()
                    elif self.mode == "sensors":
                        data = self._read_from_sensors()
                    else:
                        data = None
                    
                    if data:
                        try:
                            # Add data to queue with timeout
                            self.data_queue.put(data, block=True, timeout=0.1)
                        except queue.Full:
                            print("Queue is full, skipping data point")
                    
                    # Sleep until next reading
                    time.sleep(self.update_rate)
                    
                except Exception as e:
                    print(f"Error in data source: {str(e)}")
                    time.sleep(1.0)
        
        def _generate_simulated_data(self):
            """Generate simulated sensor data"""
            # Update angle
            self.angle += self.angle_increment
            if self.angle > 360:
                self.angle = 0
            
            # Generate torque with some noise
            # Torque follows a sinusoidal pattern with noise
            base_torque = 50 + 30 * math.sin(math.radians(self.angle))
            noise = random.uniform(-2, 2)
            torque = base_torque + noise
            
            # Generate preload with some noise and correlation to torque
            # Preload increases with angle but has different characteristics
            base_preload = 200 + 0.5 * self.angle + 50 * math.sin(math.radians(self.angle * 2))
            noise = random.uniform(-10, 10)
            preload = base_preload + noise
            
            return {
                'timestamp': time.time(),
                'angle': self.angle,
                'torque': torque,
                'preload': preload
            }
        
        def _read_data_from_file(self):
            """Read data from a file (placeholder)"""
            # Implementation would depend on file format
            # For now, just return None
            return None
        
        def _read_from_sensors(self):
            """Read data from actual sensors (placeholder)"""
            # Implementation would connect to and read from hardware
            # For now, just return None
            return None