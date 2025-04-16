# src/alerts/alert_manager.py
import tkinter as tk
from tkinter import ttk
import threading
import time

from .buzzer import Buzzer

class AlertManager:
    """Manages the visual and audio alerts for the application"""
    
    def __init__(self, root=None):
        """
        Initialize the alert manager
        
        Args:
            root: Tkinter root window (optional, for visual alerts)
        """
        self.root = root
        self.buzzer = Buzzer()
        self.popup_window = None
        self.alert_active = {}  # Track active alerts by type
        self.alert_cooldown = 5.0  # Seconds between repeated alerts
        self.last_alert_time = {}  # Track when alerts were last triggered
    
    def alert(self, alert_type, message, sound=True, popup=True):
        """
        Trigger an alert
        
        Args:
            alert_type: String identifier for the alert type
            message: Alert message to display
            sound: Whether to sound the buzzer
            popup: Whether to show a popup
        """
        # Check cooldown for this alert type
        current_time = time.time()
        if alert_type in self.last_alert_time:
            time_since_last = current_time - self.last_alert_time[alert_type]
            if time_since_last < self.alert_cooldown:
                return  # Skip this alert - cooldown period
        
        # Update last alert time
        self.last_alert_time[alert_type] = current_time
        
        # Already have an active alert of this type?
        if alert_type in self.alert_active and self.alert_active[alert_type]:
            return
            
        self.alert_active[alert_type] = True
        
        # Trigger sound alert in a separate thread
        if sound:
            try:
                self.buzzer.beep(count=3)
            except Exception as e:
                print(f"Error triggering buzzer: {str(e)}")
        
        # Show popup if requested and we have a root window
        if popup and self.root:
            # Run popup in the main thread to avoid Tkinter threading issues
            self.root.after(0, lambda: self._show_popup(alert_type, message))
    
    def dismiss_alert(self, alert_type):
        """Dismiss an active alert"""
        self.alert_active[alert_type] = False
        
        # Close popup if it exists and belongs to this alert type
        if self.popup_window and hasattr(self.popup_window, 'alert_type') and \
           self.popup_window.alert_type == alert_type:
            try:
                self.popup_window.destroy()
                self.popup_window = None
            except:
                pass
    
    def _show_popup(self, alert_type, message):
        """Show an alert popup window"""
        # Close any existing popup
        if self.popup_window:
            try:
                self.popup_window.destroy()
            except:
                pass
        
        # Create new popup window
        self.popup_window = tk.Toplevel(self.root)
        self.popup_window.alert_type = alert_type
        self.popup_window.title("Alert")
        self.popup_window.geometry("400x150")
        
        # Keep it on top
        self.popup_window.attributes('-topmost', True)
        
        # Add red border
        self.popup_window.configure(bg='red')
        
        # Inner frame with padding
        frame = ttk.Frame(self.popup_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Warning icon (Unicode character)
        warning_label = ttk.Label(frame, text="⚠️", font=("Arial", 24))
        warning_label.pack(pady=(10, 5))
        
        # Message
        msg_label = ttk.Label(frame, text=message, font=("Arial", 12))
        msg_label.pack(pady=5)
        
        # Dismiss button
        dismiss_btn = ttk.Button(
            frame, 
            text="Dismiss", 
            command=lambda: self.dismiss_alert(alert_type)
        )
        dismiss_btn.pack(pady=10)
    
    def cleanup(self):
        """Clean up resources"""
        self.buzzer.cleanup()
        
        # Close any open popup
        if self.popup_window:
            try:
                self.popup_window.destroy()
            except:
                pass