# src/sensors/encoder.py
from src.sensors.sensor_base import SensorBase

class EncoderSensor(SensorBase):
    """Reads angle data from a hardware encoder"""
    
    def __init__(self, port=None, update_rate=0.01):
        super().__init__(name="Encoder", update_rate=update_rate)
        self.port = port
        # Add specific encoder configuration here
        
    def _read_sensor(self):
        """Read angle from hardware encoder"""
        # Replace with actual encoder reading code
        # For testing, can keep the simulation code:
        if not hasattr(self, '_angle'):
            self._angle = 0
        self._angle = (self._angle + 1) % 360
        return self._angle