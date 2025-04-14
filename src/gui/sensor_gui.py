# src/gui/sensor_gui.py
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import queue
import threading
import time

class SensorGUI:
    """Main GUI for sensor visualization application"""
    
    def __init__(self, data_queue, max_points=500):
        """
        Initialize the GUI
        
        Args:
            data_queue: Queue containing sensor data
            max_points: Maximum number of data points to display
        """
        self.data_queue = data_queue
        self.max_points = max_points
        
        # Data storage
        self.angles = []
        self.torques = []
        self.preloads = []
        self.timestamps = []
        
        # Statistics
        self.max_torque = 0
        self.max_preload = 0
        self.update_count = 0
        
        # GUI update frequency (in ms)
        self.update_interval = 50
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("SensorViz - Real-time Sensor Visualization")
        self.root.geometry("1200x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set app icon (optional)
        # self.root.iconbitmap("path/to/icon.ico")
        
        # Configure the grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=0)  # Header
        self.root.rowconfigure(1, weight=1)  # Plots
        self.root.rowconfigure(2, weight=0)  # Controls
        self.root.rowconfigure(3, weight=0)  # Status
        
        # Initialize GUI components
        self._create_header()
        self._create_plots()
        self._create_controls()
        self._create_status_bar()
        
        # Animation state
        self.running = False
        self.animation_thread = None
        self.stop_event = threading.Event()
    
    def _create_header(self):
        """Create the header section"""
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        title_label = ttk.Label(
            header_frame, 
            text="Sensor Visualization Dashboard", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Add app description
        desc_label = ttk.Label(
            header_frame,
            text="Real-time monitoring of angle, torque, and preload sensors",
            font=("Arial", 10)
        )
        desc_label.pack(side=tk.LEFT, padx=10)
    
    def _create_plots(self):
        """Create the plot area with two plots"""
        # Main plot frame
        plot_frame = ttk.Frame(self.root)
        plot_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        # Create a figure with two subplots
        self.fig = Figure(figsize=(12, 6), dpi=100)
        
        # Torque vs Angle plot (left)
        self.ax1 = self.fig.add_subplot(121)
        self.ax1.set_title("Torque vs Angle")
        self.ax1.set_xlabel("Angle (degrees)")
        self.ax1.set_ylabel("Torque (Nm)")
        self.ax1.grid(True)
        
        # Initial empty line for torque plot
        self.torque_line, = self.ax1.plot([], [], 'b-', label="Torque")
        self.ax1.legend()
        
        # Preload vs Angle plot (right)
        self.ax2 = self.fig.add_subplot(122)
        self.ax2.set_title("Preload vs Angle")
        self.ax2.set_xlabel("Angle (degrees)")
        self.ax2.set_ylabel("Preload (N)")
        self.ax2.grid(True)
        
        # Initial empty line for preload plot
        self.preload_line, = self.ax2.plot([], [], 'r-', label="Preload")
        self.ax2.legend()
        
        # Set tight layout for better spacing
        self.fig.tight_layout()
        
        # Create a canvas to display the figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar with pan, zoom, etc.
        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.pack(fill=tk.X)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
    
    def _create_controls(self):
        """Create the control panel"""
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Data source control
        source_frame = ttk.Frame(control_frame)
        source_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(source_frame, text="Data Source:").pack(side=tk.LEFT)
        
        # Data source selector
        self.source_var = tk.StringVar(value="hardware")
        source_combo = ttk.Combobox(
            source_frame, 
            textvariable=self.source_var,
            values=["hardware", "simulation", "file"],
            state="readonly",
            width=10
        )
        source_combo.pack(side=tk.LEFT, padx=5)
        
        # Start/Stop buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT, padx=20)
        
        self.start_btn = ttk.Button(
            btn_frame, 
            text="Start", 
            command=self.start_visualization,
            width=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            btn_frame, 
            text="Stop", 
            command=self.stop_visualization,
            width=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_btn = ttk.Button(
            btn_frame,
            text="Clear",
            command=self.clear_data,
            width=10
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Export data button
        self.export_btn = ttk.Button(
            btn_frame,
            text="Export Data",
            command=self.export_data,
            width=10
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Display options
        display_frame = ttk.Frame(control_frame)
        display_frame.pack(side=tk.RIGHT, padx=10)
        
        # Points shown slider
        ttk.Label(display_frame, text="Points:").pack(side=tk.LEFT)
        self.points_var = tk.IntVar(value=self.max_points)
        points_slider = ttk.Scale(
            display_frame,
            from_=50,
            to=1000,
            variable=self.points_var,
            orient=tk.HORIZONTAL,
            length=100,
            command=lambda v: self.points_var.set(int(float(v)))
        )
        points_slider.pack(side=tk.LEFT, padx=5)
        
        # Display for points value
        self.points_label = ttk.Label(display_frame, text="500")
        self.points_label.pack(side=tk.LEFT, padx=2)
        
        # Update when points value changes
        self.points_var.trace_add("write", lambda *args: 
            self.points_label.config(text=str(self.points_var.get())))
    
    def _create_status_bar(self):
        """Create the status bar with max values display"""
        status_frame = ttk.Frame(self.root, padding="5")
        status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Max values display
        stats_frame = ttk.LabelFrame(status_frame, text="Statistics", padding="5")
        stats_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Max torque
        torque_frame = ttk.Frame(stats_frame)
        torque_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(torque_frame, text="Max Torque:").pack(side=tk.LEFT)
        self.max_torque_var = tk.StringVar(value="0.0 Nm")
        ttk.Label(torque_frame, textvariable=self.max_torque_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Max preload
        preload_frame = ttk.Frame(stats_frame)
        preload_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(preload_frame, text="Max Preload:").pack(side=tk.LEFT)
        self.max_preload_var = tk.StringVar(value="0.0 N")
        ttk.Label(preload_frame, textvariable=self.max_preload_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Current values
        current_frame = ttk.Frame(stats_frame)
        current_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(current_frame, text="Current Angle:").pack(side=tk.LEFT)
        self.current_angle_var = tk.StringVar(value="0.0°")
        ttk.Label(current_frame, textvariable=self.current_angle_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Status message
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT, padx=10)
    
    def start_visualization(self):
        """Start data acquisition and visualization"""
        if self.running:
            return
        
        self.running = True
        self.status_var.set("Running")
        
        # Update button states
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Start the animation thread
        self.stop_event.clear()
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
        
        # Schedule regular GUI updates
        self._schedule_update()
    
    def stop_visualization(self):
        """Stop data acquisition and visualization"""
        if not self.running:
            return
        
        self.running = False
        self.status_var.set("Stopped")
        
        # Update button states
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Stop the animation thread
        self.stop_event.set()
        if self.animation_thread:
            self.animation_thread.join(timeout=1.0)
    
    def clear_data(self):
        """Clear all stored data"""
        self.angles = []
        self.torques = []
        self.preloads = []
        self.timestamps = []
        self.max_torque = 0
        self.max_preload = 0
        self.update_count = 0
        
        # Update plots with empty data
        self.torque_line.set_data([], [])
        self.preload_line.set_data([], [])
        self.canvas.draw_idle()
        
        # Reset statistics
        self.max_torque_var.set("0.0 Nm")
        self.max_preload_var.set("0.0 N")
        self.current_angle_var.set("0.0°")
        
        self.status_var.set("Data cleared")
    
    def export_data(self):
        """Export data to CSV file"""
        # This is a placeholder - implement actual file export
        self.status_var.set("Export functionality not yet implemented")
        # TODO: Implement data export to CSV
    
    def on_closing(self):
        """Handle window close event"""
        self.stop_visualization()
        self.root.destroy()
    
    def _animation_loop(self):
        """Background thread for processing data"""
        while not self.stop_event.is_set():
            try:
                # Try to get data from queue with timeout
                try:
                    data = self.data_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Process the data (store for next UI update)
                if data:
                    angle = data.get('angle', 0)
                    torque = data.get('torque', 0)
                    preload = data.get('preload', 0)
                    timestamp = data.get('timestamp', time.time())
                    
                    # Add data to lists
                    self.angles.append(angle)
                    self.torques.append(torque)
                    self.preloads.append(preload)
                    self.timestamps.append(timestamp)
                    
                    # Limit data points
                    max_points = self.points_var.get()
                    if len(self.angles) > max_points:
                        self.angles = self.angles[-max_points:]
                        self.torques = self.torques[-max_points:]
                        self.preloads = self.preloads[-max_points:]
                        self.timestamps = self.timestamps[-max_points:]
                    
                    # Update statistics
                    if torque > self.max_torque:
                        self.max_torque = torque
                    if preload > self.max_preload:
                        self.max_preload = preload
                
            except Exception as e:
                print(f"Error in animation loop: {str(e)}")
                time.sleep(0.5)
    
    def _update_plots(self):
        """Update the plots with new data"""
        if not self.angles:
            return
            
        # Update torque plot
        self.torque_line.set_data(self.angles, self.torques)
        self.ax1.relim()
        self.ax1.autoscale_view()
        
        # Update preload plot
        self.preload_line.set_data(self.angles, self.preloads)
        self.ax2.relim()
        self.ax2.autoscale_view()
        
        # Redraw the canvas
        self.canvas.draw_idle()
        
        # Update statistics display
        self.max_torque_var.set(f"{self.max_torque:.1f} Nm")
        self.max_preload_var.set(f"{self.max_preload:.1f} N")
        
        # Update current angle (most recent)
        if self.angles:
            self.current_angle_var.set(f"{self.angles[-1]:.1f}°")
        
        # Update count for debugging
        self.update_count += 1
    
    def _schedule_update(self):
        """Schedule the next UI update if still running"""
        if self.running:
            # Update the plots
            self._update_plots()
            
            # Schedule next update
            self.root.after(self.update_interval, self._schedule_update)
    
    def run(self):
        """Run the main application loop"""
        self.root.mainloop()