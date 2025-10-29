"""
Domain entities for animation data transfer system.

This module defines pure Python data structures for representing
animation keyframe data independent of Blender.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import json


@dataclass
class KeyframeData:
    """
    Represents a single keyframe on an animation curve.
    """
    frame: float
    value: float
    interpolation: str = 'BEZIER'
    handle_left: Tuple[float, float] = (0.0, 0.0)
    handle_right: Tuple[float, float] = (0.0, 0.0)
    handle_left_type: str = 'AUTO'
    handle_right_type: str = 'AUTO'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'frame': self.frame,
            'value': self.value,
            'interpolation': self.interpolation,
            'handle_left': list(self.handle_left),
            'handle_right': list(self.handle_right),
            'handle_left_type': self.handle_left_type,
            'handle_right_type': self.handle_right_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyframeData':
        """Create from dictionary."""
        return cls(
            frame=data['frame'],
            value=data['value'],
            interpolation=data.get('interpolation', 'BEZIER'),
            handle_left=tuple(data.get('handle_left', [0.0, 0.0])),
            handle_right=tuple(data.get('handle_right', [0.0, 0.0])),
            handle_left_type=data.get('handle_left_type', 'AUTO'),
            handle_right_type=data.get('handle_right_type', 'AUTO')
        )


@dataclass
class FCurveData:
    """
    Represents an animation curve (fcurve) with all keyframes.
    """
    data_path: str  # e.g., 'pose.bones["Hips"].location'
    array_index: int  # 0=X, 1=Y, 2=Z for location/rotation/scale
    keyframes: List[KeyframeData] = field(default_factory=list)

    # Extrapolation
    extrapolation: str = 'CONSTANT'

    # Modifiers (if any)
    modifiers: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'data_path': self.data_path,
            'array_index': self.array_index,
            'keyframes': [kf.to_dict() for kf in self.keyframes],
            'extrapolation': self.extrapolation,
            'modifiers': self.modifiers
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FCurveData':
        """Create from dictionary."""
        keyframes = [KeyframeData.from_dict(kf) for kf in data.get('keyframes', [])]
        return cls(
            data_path=data['data_path'],
            array_index=data['array_index'],
            keyframes=keyframes,
            extrapolation=data.get('extrapolation', 'CONSTANT'),
            modifiers=data.get('modifiers', [])
        )


@dataclass
class BoneAnimationData:
    """
    Represents animation data for a single bone.
    """
    bone_name: str
    fcurves: List[FCurveData] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'bone_name': self.bone_name,
            'fcurves': [fc.to_dict() for fc in self.fcurves]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoneAnimationData':
        """Create from dictionary."""
        fcurves = [FCurveData.from_dict(fc) for fc in data.get('fcurves', [])]
        return cls(
            bone_name=data['bone_name'],
            fcurves=fcurves
        )


@dataclass
class AnimationData:
    """
    Represents complete animation data from an armature action.

    Contains all fcurves, keyframes, and metadata needed to
    transfer animation between armatures.
    """
    name: str
    description: str = ""

    # Frame range
    frame_start: float = 1.0
    frame_end: float = 250.0

    # Bone animations
    bones: List[BoneAnimationData] = field(default_factory=list)

    # Metadata
    source_armature: str = ""
    source_action: str = ""
    bone_count: int = 0

    # Version for forward compatibility
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'frame_start': self.frame_start,
            'frame_end': self.frame_end,
            'bones': [bone.to_dict() for bone in self.bones],
            'source_armature': self.source_armature,
            'source_action': self.source_action,
            'bone_count': self.bone_count,
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnimationData':
        """Create from dictionary."""
        bones = [BoneAnimationData.from_dict(b) for b in data.get('bones', [])]
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            frame_start=data.get('frame_start', 1.0),
            frame_end=data.get('frame_end', 250.0),
            bones=bones,
            source_armature=data.get('source_armature', ''),
            source_action=data.get('source_action', ''),
            bone_count=data.get('bone_count', 0),
            version=data.get('version', '1.0')
        )

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'AnimationData':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
