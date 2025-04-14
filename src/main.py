"""
Main entry point for the sensor visualization application
"""
import queue

from src.data.data_source import DataSource
from src.gui.sensor_gui import SensorGUI

def main():
    """Main application entry point"""
    print("Starting sensor visualization application")
    
    try:
        # Create communication queue for data flow
        data_queue = queue.Queue(maxsize=100)
        
        # Initialize the data source
        # Mode can be "hardware" for real sensors or "simulation" for testing
        data_source = DataSource(data_queue, mode="simulation")  # Using simulation mode for testing
        
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