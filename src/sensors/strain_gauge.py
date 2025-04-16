# src/sensors/strain_gauge.py
import random
import math
from src.sensors.sensor_base import SensorBase

class StrainGaugeSensor(SensorBase):
    """Reads torque data from strain gauge"""
    
    def __init__(self, port=None, update_rate=0.1):
        super().__init__(name="Strain Gauge", update_rate=update_rate)
        self.port = port
        # Add specific strain gauge configuration here
        
    def _read_sensor(self):
        """Read torque from strain gauge"""
        # Replace with actual strain gauge reading code
        # For testing, use simulated data
        if not hasattr(self, '_angle'):
            self._angle = 0
        self._angle = (self._angle + 1) % 360
        
        base_torque = 50 + 30 * math.sin(math.radians(self._angle))
        noise = random.uniform(-1, 1)
        return base_torque + noise