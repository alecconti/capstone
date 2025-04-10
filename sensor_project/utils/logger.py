"""
Logging utility for the sensor visualization project
"""
import logging
import sys
from sensor_project.config.settings import LOG_SETTINGS

def setup_logger(name):
    """
    Set up and return a logger with the given name
    
    Args:
        name (str): Name of the logger, typically __name__
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_SETTINGS['level']))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_SETTINGS['level']))
    
    # Create formatter
    formatter = logging.Formatter(LOG_SETTINGS['format'])
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if LOG_SETTINGS.get('file'):
        file_handler = logging.FileHandler(LOG_SETTINGS['file'])
        file_handler.setLevel(getattr(logging, LOG_SETTINGS['level']))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger