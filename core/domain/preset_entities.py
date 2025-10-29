"""
Preset entities for saving and loading animation sequences.

These are pure data structures for animation presets.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import json


@dataclass
class PresetActionItem:
    """
    Individual action in a preset.

    Attributes:
        action_name: Name of the animation action
        use_action: Whether this action is enabled
        repeat_count: Number of times to repeat
        angle: Rotation angle in degrees
    """
    action_name: str
    use_action: bool = True
    repeat_count: int = 1
    angle: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'action_name': self.action_name,
            'use_action': self.use_action,
            'repeat_count': self.repeat_count,
            'angle': self.angle
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PresetActionItem':
        """Create from dictionary."""
        return cls(
            action_name=data['action_name'],
            use_action=data.get('use_action', True),
            repeat_count=data.get('repeat_count', 1),
            angle=data.get('angle', 0)
        )


@dataclass
class AnimationPreset:
    """
    Complete animation sequence preset.

    Attributes:
        name: Preset name
        description: Optional description
        root_bone: Root bone name
        overlap_frames: Overlap frames for blending
        forward_axis: Character forward direction
        actions: List of actions in sequence
        version: Preset format version
    """
    name: str
    actions: List[PresetActionItem] = field(default_factory=list)
    description: str = ""
    root_bone: str = "mixamorig:Hips"
    overlap_frames: int = 3
    forward_axis: str = 'Y+'
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'root_bone': self.root_bone,
            'overlap_frames': self.overlap_frames,
            'forward_axis': self.forward_axis,
            'actions': [action.to_dict() for action in self.actions],
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnimationPreset':
        """Create from dictionary."""
        actions = [
            PresetActionItem.from_dict(action_data)
            for action_data in data.get('actions', [])
        ]

        return cls(
            name=data['name'],
            description=data.get('description', ''),
            root_bone=data.get('root_bone', 'mixamorig:Hips'),
            overlap_frames=data.get('overlap_frames', 3),
            forward_axis=data.get('forward_axis', 'Y+'),
            actions=actions,
            version=data.get('version', '1.0')
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'AnimationPreset':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
