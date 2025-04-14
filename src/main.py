"""
Main entry point for the sensor visualization application
"""
import queue

from data_source import DataSource
from gui_app import SensorGUI

def main():
    """Main application entry point"""
    print("Starting sensor visualization application")
    
    try:
        # Create communication queue for data flow
        data_queue = queue.Queue(maxsize=100)
        
        # Initialize the data source
        # Mode can be "hardware" for real sensors or "simulation" for testing
        data_source = DataSource(data_queue, mode="hardware")  # Change to "simulation" for testing
        
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