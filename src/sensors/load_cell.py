# src/sensors/load_cell.py
import random
import math
from src.sensors.sensor_base import SensorBase

class LoadCellSensor(SensorBase):
    """Reads preload force data from load cells"""
    
    def __init__(self, port=None, update_rate=0.1):
        super().__init__(name="Load Cell", update_rate=update_rate)
        self.port = port
        # Add specific load cell configuration here
        
    def _read_sensor(self):
        """Read preload from load cell"""
        # Replace with actual load cell reading code
        # For testing, use simulated data
        if not hasattr(self, '_angle'):
            self._angle = 0
        self._angle = (self._angle + 1) % 360
        
        base_preload = 200 + 0.5 * self._angle + 50 * math.sin(math.radians(self._angle * 2))
        noise = random.uniform(-1, 1)
        return base_preload + noise