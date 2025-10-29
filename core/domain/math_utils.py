"""
Pure mathematical utility functions for animation calculations.

This module contains no Blender dependencies and can be tested independently.
All functions are pure (no side effects) and deterministic.
"""

import math
from mathutils import Vector


def get_axis_vector(forward_axis: str) -> tuple:
    """
    Convert axis string notation to 3D vector.

    Args:
        forward_axis: String like 'X+', 'Y-', 'Z+', etc.

    Returns:
        Tuple of (x, y, z) representing the axis direction

    Examples:
        >>> get_axis_vector('Y+')
        (0, 1, 0)
        >>> get_axis_vector('X-')
        (-1, 0, 0)
    """
    axis_map = {
        'X+': (1, 0, 0),
        'X-': (-1, 0, 0),
        'Y+': (0, 1, 0),
        'Y-': (0, -1, 0),
        'Z+': (0, 0, 1),
        'Z-': (0, 0, -1),
    }
    return axis_map.get(forward_axis, (0, 1, 0))


def rotate_2d_point(x: float, y: float, angle_deg: float) -> tuple:
    """
    Rotate a 2D point around the origin.

    Uses standard 2D rotation matrix:
    x' = x * cos(θ) - y * sin(θ)
    y' = x * sin(θ) + y * cos(θ)

    Args:
        x: X coordinate
        y: Y coordinate
        angle_deg: Rotation angle in degrees (positive = counter-clockwise)

    Returns:
        Tuple of (x_new, y_new) rotated coordinates

    Examples:
        >>> rotate_2d_point(1.0, 0.0, 90.0)
        (0.0, 1.0)
    """
    # Edge case: No rotation needed
    if abs(angle_deg) < 0.001:
        return (x, y)

    # Convert to radians
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Apply rotation matrix
    x_new = x * cos_a - y * sin_a
    y_new = x * sin_a + y * cos_a

    return (x_new, y_new)


def calculate_offset_vector(start_loc: Vector, target_loc: Vector) -> Vector:
    """
    Calculate offset needed to move start_loc to target_loc.

    Args:
        start_loc: Starting location vector
        target_loc: Target location vector

    Returns:
        Offset vector to add to start_loc

    Examples:
        >>> calculate_offset_vector(Vector((1, 2, 3)), Vector((4, 5, 6)))
        Vector((3, 3, 3))
    """
    return target_loc - start_loc


def is_rotation_needed(angle_deg: float, threshold: float = 0.001) -> bool:
    """
    Check if rotation angle is significant enough to apply.

    Args:
        angle_deg: Rotation angle in degrees
        threshold: Minimum angle to consider (default 0.001)

    Returns:
        True if rotation should be applied
    """
    return abs(angle_deg) >= threshold
