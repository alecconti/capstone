"""
Main entry point for the sensor visualization application
"""
import queue
from sensor_project.sensors.sensor_manager import SensorManager
from sensor_project.data.processor import DataProcessor
from sensor_project.gui.app import Application
from sensor_project.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Main application entry point"""
    logger.info("Starting sensor visualization application")
    
    try:
        # Create communication queues
        raw_data_queue = queue.Queue(maxsize=100)  # From sensors to processor
        processed_data_queue = queue.Queue(maxsize=100)  # From processor to GUI
        
        # Initialize components
        sensor_manager = SensorManager(raw_data_queue)
        data_processor = DataProcessor(raw_data_queue, processed_data_queue)
        app = Application(processed_data_queue)
        
        # Start background components
        logger.info("Starting sensor manager")
        sensor_manager.start()
        
        logger.info("Starting data processor")
        data_processor.start()
        
        # Start GUI (this will block until GUI is closed)
        logger.info("Starting GUI")
        app.run()
        
        # Clean up when GUI is closed
        logger.info("Application closing, performing cleanup")
        data_processor.stop()
        sensor_manager.stop()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    
    logger.info("Application terminated")

if __name__ == "__main__":
    main()