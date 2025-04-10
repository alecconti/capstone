"""
Centralized configuration settings for the sensor visualization project
"""

# Sensor settings
SENSOR_SETTINGS = {
    'sample_rate': 0.1,  # seconds between readings
    'max_history': 1000  # maximum data points to store
}

# GUI settings
GUI_SETTINGS = {
    'update_interval': 50,  # milliseconds between GUI updates
    'graph_points': 100,    # data points to display on graphs
    'window_title': 'Sensor Data Visualization',
    'window_size': '800x600'
}

# Logging settings
LOG_SETTINGS = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'sensor_app.log'
}