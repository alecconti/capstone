"""
Main entry point for the sensor visualization application
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
import threading
import queue

from data_source import DataSource
from gui_app import SensorGUI

def main():
    """Main application entry point"""
    print("Starting sensor visualization application")
    
    try:
        # Create communication queue for data flow
        data_queue = queue.Queue(maxsize=100)
        
        # Initialize the data source (simulated for now)
        data_source = DataSource(data_queue)
        
        # Create and run the GUI
        app = SensorGUI(data_queue)
        
        # Start data source in background thread
        data_source.start()
        
        # Start GUI (blocks until window is closed)
        app.run()
        
        # Clean up when GUI is closed
        data_source.stop()
        print("Application closed successfully")
        
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()