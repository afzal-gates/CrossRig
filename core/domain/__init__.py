"""
Domain layer - Pure business entities and value objects.

No dependencies on Blender or any external frameworks.
"""

from .entities import ActionItem, AnimationSettings, ExportSettings
from .preset_entities import AnimationPreset, PresetActionItem
from .math_utils import (
    get_axis_vector,
    rotate_2d_point,
    calculate_offset_vector,
    is_rotation_needed
)

__all__ = [
    'ActionItem',
    'AnimationSettings',
    'ExportSettings',
    'AnimationPreset',
    'PresetActionItem',
    'get_axis_vector',
    'rotate_2d_point',
    'calculate_offset_vector',
    'is_rotation_needed',
]
