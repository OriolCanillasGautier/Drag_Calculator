# simulation.py

def calculate_drag(density, velocity, frontal_area, drag_coefficient):
    """
    Calculate drag force using: F_d = 0.5 * density * velocity^2 * area * drag_coefficient
    """
    return 0.5 * density * (velocity ** 2) * frontal_area * drag_coefficient

def calculate_power(drag_force, velocity):
    """
    Calculate the power required to overcome drag.
    """
    return drag_force * velocity
