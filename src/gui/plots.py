# src/gui/plots.py
"""
Specialized plotting functions for sensor visualization
"""
from matplotlib.figure import Figure

def create_sensor_figure(fig_size=(12, 6), dpi=100):
    """
    Create a standard figure with two subplots for sensor visualization
    
    Args:
        fig_size: Figure size as (width, height) tuple
        dpi: Dots per inch for figure resolution
        
    Returns:
        fig: Figure object
        ax1: Torque vs Angle axes
        ax2: Preload vs Angle axes
    """
    fig = Figure(figsize=fig_size, dpi=dpi)
    
    # Torque vs Angle plot (left)
    ax1 = fig.add_subplot(121)
    ax1.set_title("Torque vs Angle")
    ax1.set_xlabel("Angle (degrees)")
    ax1.set_ylabel("Torque (Nm)")
    ax1.grid(True)
    
    # Preload vs Angle plot (right)
    ax2 = fig.add_subplot(122)
    ax2.set_title("Preload vs Angle")
    ax2.set_xlabel("Angle (degrees)")
    ax2.set_ylabel("Preload (N)")
    ax2.grid(True)
    
    # Set tight layout for better spacing
    fig.tight_layout()
    
    return fig, ax1, ax2

def create_polar_plot(fig_size=(6, 6), dpi=100):
    """
    Create a polar plot for directional sensor data visualization
    
    Args:
        fig_size: Figure size as (width, height) tuple
        dpi: Dots per inch for figure resolution
        
    Returns:
        fig: Figure object
        ax: Polar axes
    """
    fig = Figure(figsize=fig_size, dpi=dpi)
    
    ax = fig.add_subplot(111, polar=True)
    ax.set_title("Polar Representation")
    ax.set_theta_zero_location("N")  # 0 degrees at the top
    ax.set_theta_direction(-1)       # Clockwise
    ax.grid(True)
    
    return fig, ax

def update_torque_angle_plot(ax, angles, torques, line=None):
    """
    Update the Torque vs Angle plot
    
    Args:
        ax: Matplotlib axes
        angles: List of angle values
        torques: List of torque values
        line: Line to update (optional)
        
    Returns:
        line: The updated line
    """
    if line is None:
        line, = ax.plot(angles, torques, 'b-', label="Torque")
        ax.legend()
    else:
        line.set_data(angles, torques)
    
    ax.relim()
    ax.autoscale_view()
    
    return line

def update_preload_angle_plot(ax, angles, preloads, line=None):
    """
    Update the Preload vs Angle plot
    
    Args:
        ax: Matplotlib axes
        angles: List of angle values
        preloads: List of preload values
        line: Line to update (optional)
        
    Returns:
        line: The updated line
    """
    if line is None:
        line, = ax.plot(angles, preloads, 'r-', label="Preload")
        ax.legend()
    else:
        line.set_data(angles, preloads)
    
    ax.relim()
    ax.autoscale_view()
    
    return line

def plot_to_image(fig):
    """
    Convert a matplotlib figure to a PNG image
    
    Args:
        fig: Matplotlib figure
        
    Returns:
        bytes: PNG image data
    """
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    return buf.getvalue()