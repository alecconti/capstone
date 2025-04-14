# src/sensors/sensor_base.py
import threading
import time
import abc

class SensorBase(abc.ABC):
    """Base class for all sensor implementations"""
    
    def __init__(self, name, update_rate=0.05):
        self.name = name
        self.update_rate = update_rate
        self.running = False
        self.thread = None
        self.stop_event = threading.Event()
        self.last_reading = None
        self.last_timestamp = None
        self.error_count = 0
        self.max_errors = 5
        
    def start(self):
        """Start the sensor reading thread"""
        if self.running:
            print(f"{self.name} is already running")
            return
            
        print(f"Starting {self.name}")
        self.stop_event.clear()
        self.running = True
        self.thread = threading.Thread(target=self._reading_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop the sensor reading thread"""
        if not self.running:
            return
            
        print(f"Stopping {self.name}")
        self.stop_event.set()
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def _reading_loop(self):
        """Main sensor reading loop"""
        while not self.stop_event.is_set():
            try:
                reading = self._read_sensor()
                if reading is not None:
                    self.last_reading = reading
                    self.last_timestamp = time.time()
                    self.error_count = 0
                time.sleep(self.update_rate)
            except Exception as e:
                print(f"Error reading from {self.name}: {str(e)}")
                self.error_count += 1
                if self.error_count > self.max_errors:
                    print(f"Too many errors from {self.name}, stopping sensor")
                    self.running = False
                    break
                time.sleep(1.0)  # Wait longer after error
    
    def get_reading(self):
        """Get the latest reading with timestamp"""
        if self.last_reading is None:
            return None
        return {
            'value': self.last_reading,
            'timestamp': self.last_timestamp
        }
    
    @abc.abstractmethod
    def _read_sensor(self):
        """Implement in subclass to read from the actual sensor"""
        pass