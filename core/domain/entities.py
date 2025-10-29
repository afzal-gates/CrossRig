"""
Domain entities for Mixanimo Lite.

These are pure data structures with no Blender dependencies.
They represent core business concepts.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ActionItem:
    """
    Represents an animation action to be sequenced.

    Attributes:
        action_name: Name of the Blender action
        armature_name: Name of the armature object
        use_action: Whether this action is enabled
        repeat_count: Number of times to repeat
        angle: Rotation angle for trajectory (degrees)
    """
    action_name: str
    armature_name: str = ""
    use_action: bool = True
    repeat_count: int = 1
    angle: int = 0


@dataclass
class AnimationSettings:
    """
    Settings for animation sequencing.

    Attributes:
        root_bone: Name of the root bone (e.g., "mixamorig:Hips")
        overlap_frames: Frames for blending between actions
        forward_axis: Character's forward direction
        order_confirmed: Whether action order is confirmed
    """
    root_bone: str = "mixamorig:Hips"
    overlap_frames: int = 3
    forward_axis: str = 'Y+'
    order_confirmed: bool = False


@dataclass
class ExportSettings:
    """
    Settings for FBX export.

    Attributes:
        filepath: Full path to output file
        include_mesh: Whether to export mesh with armature
        action_name: Name of action being exported
    """
    filepath: str
    include_mesh: bool = True
    action_name: Optional[str] = None
