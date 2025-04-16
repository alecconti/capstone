# src/alerts/buzzer.py
import RPi.GPIO as GPIO
import time
import threading
import platform

class Buzzer:
    """Controls a GPIO buzzer for audio alerts"""
    
    def __init__(self, pin=17):
        self.pin = pin
        self.is_simulation = platform.system() != "Linux"
        
        if not self.is_simulation:
            # Only setup GPIO on Raspberry Pi
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
    
    def beep(self, count=3, on_time=0.1, off_time=0.2):
        """Sound the buzzer with the specified pattern"""
        # Run in a separate thread to avoid blocking the GUI
        thread = threading.Thread(target=self._beep_thread, 
                                  args=(count, on_time, off_time),
                                  daemon=True)
        thread.start()
    
    def _beep_thread(self, count, on_time, off_time):
        """Thread function to control the buzzer"""
        if self.is_simulation:
            print(f"BUZZER: {count} beeps (simulation mode)")
            return
            
        try:
            for _ in range(count):
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(on_time)
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(off_time)
        except Exception as e:
            print(f"Buzzer error: {str(e)}")
        finally:
            # Don't cleanup here - it would reset all GPIO
            pass
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if not self.is_simulation:
            try:
                GPIO.cleanup(self.pin)
            except:
                pass