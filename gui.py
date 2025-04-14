"""
GUI application for sensor visualization
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")  # Use TkAgg backend for better performance
import numpy as np
import time
from queue import Empty

class SensorGUI:
    """Main application GUI class for sensor visualization"""
    
    def __init__(self, data_queue):
        """
        Initialize the GUI application
        
        Args:
            data_queue: Queue containing incoming sensor data
        """
        self.data_queue = data_queue
        self.update_interval = 100  # milliseconds between GUI updates
        
        # Initialize data storage
        self.angles = []
        self.torques = []
        self.preloads = []
    
    def run(self):
        """Create and run the GUI application"""
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Sensor Visualization")
        self.root.geometry("1200x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create graphs
        self._create_graphs()
        
        # Schedule first update
        self._schedule_update()
        
        # Start the main event loop
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing event"""
        print("Closing application")
        self.root.destroy()
    
    def _create_graphs(self):
        """Create the two graphs for data visualization"""
        # Create frame for graphs
        graphs_frame = ttk.Frame(self.main_frame)
        graphs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left graph (Torque vs Angle)
        left_frame = ttk.LabelFrame(graphs_frame, text="Torque vs Angle")
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.fig_torque = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax_torque = self.fig_torque.add_subplot(111)
        self.ax_torque.set_xlabel("Angle (degrees)")
        self.ax_torque.set_ylabel("Torque (Nm)")
        self.ax_torque.grid(True)
        
        self.torque_canvas = FigureCanvasTkAgg(self.fig_torque, master=left_frame)
        self.torque_canvas.draw()
        self.torque_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create right graph (Preload vs Angle)
        right_frame = ttk.LabelFrame(graphs_frame, text="Preload vs Angle")
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.fig_preload = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax_preload = self.fig_preload.add_subplot(111)
        self.ax_preload.set_xlabel("Angle (degrees)")
        self.ax_preload.set_ylabel("Preload (N)")
        self.ax_preload.grid(True)
        
        self.preload_canvas = FigureCanvasTkAgg(self.fig_preload, master=right_frame)
        self.preload_canvas.draw()
        self.preload_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for resizing
        graphs_frame.columnconfigure(0, weight=1)
        graphs_frame.columnconfigure(1, weight=1)
        graphs_frame.rowconfigure(0, weight=1)
    
    def _schedule_update(self):
        """Schedule the next GUI update"""
        self.root.after(self.update_interval, self._update_gui)
    
    def _update_gui(self):
        """Update GUI with latest data"""
        try:
            # Process all available data from queue
            data_updated = False
            while True:
                try:
                    # Get data from queue (non-blocking)
                    data = self.data_queue.get(block=False)
                    
                    # Process the data
                    self.angles.append(data['angle'])
                    self.torques.append(data['torque'])
                    self.preloads.append(data['preload'])
                    
                    # Mark as processed
                    self.data_queue.task_done()
                    data_updated = True
                except Empty:
                    # No more data in queue
                    break
            
            # Update plots if new data was received
            if data_updated:
                self._update_plots()
                
        except Exception as e:
            print(f"Error updating GUI: {str(e)}")
        
        # Schedule next update
        self._schedule_update()
    
    def _update_plots(self):
        """Update the plots with latest data"""
        # Clear previous plots
        self.ax_torque.clear()
        self.ax_preload.clear()
        
        # Plot Torque vs Angle
        self.ax_torque.plot(self.angles, self.torques, 'r-')
        self.ax_torque.set_xlabel("Angle (degrees)")
        self.ax_torque.set_ylabel("Torque (Nm)")
        self.ax_torque.grid(True)
        self.ax_torque.set_title("Torque vs Angle")
        
        # Plot Preload vs Angle
        self.ax_preload.plot(self.angles, self.preloads, 'b-')
        self.ax_preload.set_xlabel("Angle (degrees)")
        self.ax_preload.set_ylabel("Preload (N)")
        self.ax_preload.grid(True)
        self.ax_preload.set_title("Preload vs Angle")
        
        # Update the canvases
        self.fig_torque.tight_layout()
        self.torque_canvas.draw()
        
        self.fig_preload.tight_layout()
        self.preload_canvas.draw()