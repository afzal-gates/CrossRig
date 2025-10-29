"""
Domain entities for armature template system.

This module defines pure Python data structures for representing
armature bone structures independent of Blender.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import json


@dataclass
class BoneData:
    """
    Represents a single bone's data in the armature.

    Stores all information needed to recreate a bone including
    hierarchy, position, rotation, and properties.
    """
    name: str
    parent_name: Optional[str] = None

    # Edit mode bone positions (relative to armature origin)
    head: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    tail: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    roll: float = 0.0

    # Bone properties
    use_connect: bool = False
    use_inherit_rotation: bool = True
    inherit_scale: str = 'FULL'
    use_local_location: bool = True
    use_deform: bool = True

    # Bone layers (which layers bone is visible on)
    layers: List[bool] = field(default_factory=lambda: [True] + [False] * 31)

    # Custom properties
    custom_properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert bone data to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'parent_name': self.parent_name,
            'head': list(self.head),
            'tail': list(self.tail),
            'roll': self.roll,
            'use_connect': self.use_connect,
            'use_inherit_rotation': self.use_inherit_rotation,
            'inherit_scale': self.inherit_scale,
            'use_local_location': self.use_local_location,
            'use_deform': self.use_deform,
            'layers': self.layers,
            'custom_properties': self.custom_properties
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoneData':
        """Create BoneData instance from dictionary."""
        return cls(
            name=data['name'],
            parent_name=data.get('parent_name'),
            head=tuple(data.get('head', [0.0, 0.0, 0.0])),
            tail=tuple(data.get('tail', [0.0, 1.0, 0.0])),
            roll=data.get('roll', 0.0),
            use_connect=data.get('use_connect', False),
            use_inherit_rotation=data.get('use_inherit_rotation', True),
            inherit_scale=data.get('inherit_scale', 'FULL'),
            use_local_location=data.get('use_local_location', True),
            use_deform=data.get('use_deform', True),
            layers=data.get('layers', [True] + [False] * 31),
            custom_properties=data.get('custom_properties', {})
        )


@dataclass
class ArmatureTemplate:
    """
    Represents a complete armature structure template.

    Contains all bones and armature properties needed to
    recreate the armature from scratch.
    """
    name: str
    bones: List[BoneData] = field(default_factory=list)
    description: str = ""

    # Armature display properties
    display_type: str = 'OCTAHEDRAL'
    show_names: bool = False
    show_axes: bool = False
    show_in_front: bool = False

    # Version for forward compatibility
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert armature template to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'display_type': self.display_type,
            'show_names': self.show_names,
            'show_axes': self.show_axes,
            'show_in_front': self.show_in_front,
            'bones': [bone.to_dict() for bone in self.bones],
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArmatureTemplate':
        """Create ArmatureTemplate instance from dictionary."""
        bones = [BoneData.from_dict(bone_data) for bone_data in data.get('bones', [])]

        return cls(
            name=data['name'],
            description=data.get('description', ''),
            display_type=data.get('display_type', 'OCTAHEDRAL'),
            show_names=data.get('show_names', False),
            show_axes=data.get('show_axes', False),
            show_in_front=data.get('show_in_front', False),
            bones=bones,
            version=data.get('version', '1.0')
        )

    def to_json(self) -> str:
        """Serialize template to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'ArmatureTemplate':
        """Deserialize template from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
