"""
Domain entities for bone mapping system.

This module defines pure Python data structures for representing
bone mappings between different armature types.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


@dataclass
class BoneMapping:
    """
    Represents a single bone-to-bone mapping.

    Maps a source bone name to a target bone name with optional
    confidence score for auto-generated mappings.
    """
    source_bone: str
    target_bone: str
    confidence: float = 1.0  # 0.0-1.0, where 1.0 = manually confirmed or exact match

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'source_bone': self.source_bone,
            'target_bone': self.target_bone,
            'confidence': self.confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoneMapping':
        """Create from dictionary."""
        return cls(
            source_bone=data['source_bone'],
            target_bone=data['target_bone'],
            confidence=data.get('confidence', 1.0)
        )


@dataclass
class BoneMappingPreset:
    """
    Represents a complete bone mapping configuration between two armature types.

    Contains all bone mappings and metadata needed to transfer animations
    between different armature structures (e.g., Mixamo → AccuRig).
    """
    name: str
    source_armature_name: str
    target_armature_name: str
    mappings: List[BoneMapping] = field(default_factory=list)
    description: str = ""

    # Metadata
    created_date: str = ""
    modified_date: str = ""
    source_bone_count: int = 0
    target_bone_count: int = 0
    mapped_count: int = 0
    auto_mapped_count: int = 0

    # Version for forward compatibility
    version: str = "1.0"

    def __post_init__(self):
        """Initialize dates if not provided."""
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.modified_date:
            self.modified_date = self.created_date

    def update_metadata(self):
        """Update metadata based on current mappings."""
        self.mapped_count = len(self.mappings)
        self.auto_mapped_count = sum(1 for m in self.mappings if m.confidence < 1.0)
        self.modified_date = datetime.now().isoformat()

    def get_mapping_dict(self) -> Dict[str, str]:
        """
        Get a simple dictionary mapping source bone names to target bone names.

        Returns:
            Dict mapping source_bone → target_bone
        """
        return {m.source_bone: m.target_bone for m in self.mappings}

    def get_reverse_mapping_dict(self) -> Dict[str, str]:
        """
        Get a reverse dictionary mapping target bone names to source bone names.

        Returns:
            Dict mapping target_bone → source_bone
        """
        return {m.target_bone: m.source_bone for m in self.mappings}

    def find_target_bone(self, source_bone: str) -> Optional[str]:
        """
        Find the target bone name for a given source bone.

        Args:
            source_bone: Source bone name

        Returns:
            Target bone name or None if not found
        """
        for mapping in self.mappings:
            if mapping.source_bone == source_bone:
                return mapping.target_bone
        return None

    def find_source_bone(self, target_bone: str) -> Optional[str]:
        """
        Find the source bone name for a given target bone.

        Args:
            target_bone: Target bone name

        Returns:
            Source bone name or None if not found
        """
        for mapping in self.mappings:
            if mapping.target_bone == target_bone:
                return mapping.source_bone
        return None

    def add_mapping(self, source_bone: str, target_bone: str, confidence: float = 1.0):
        """
        Add a new bone mapping.

        Args:
            source_bone: Source bone name
            target_bone: Target bone name
            confidence: Confidence score (0.0-1.0)
        """
        # Check if mapping already exists
        for i, mapping in enumerate(self.mappings):
            if mapping.source_bone == source_bone:
                # Update existing mapping
                self.mappings[i] = BoneMapping(source_bone, target_bone, confidence)
                self.update_metadata()
                return

        # Add new mapping
        self.mappings.append(BoneMapping(source_bone, target_bone, confidence))
        self.update_metadata()

    def remove_mapping(self, source_bone: str):
        """
        Remove a bone mapping by source bone name.

        Args:
            source_bone: Source bone name to remove
        """
        self.mappings = [m for m in self.mappings if m.source_bone != source_bone]
        self.update_metadata()

    def get_unmapped_source_bones(self, all_source_bones: List[str]) -> List[str]:
        """
        Get list of source bones that don't have mappings.

        Args:
            all_source_bones: Complete list of source bone names

        Returns:
            List of unmapped source bone names
        """
        mapped_sources = {m.source_bone for m in self.mappings}
        return [bone for bone in all_source_bones if bone not in mapped_sources]

    def get_unmapped_target_bones(self, all_target_bones: List[str]) -> List[str]:
        """
        Get list of target bones that aren't mapped to.

        Args:
            all_target_bones: Complete list of target bone names

        Returns:
            List of unmapped target bone names
        """
        mapped_targets = {m.target_bone for m in self.mappings}
        return [bone for bone in all_target_bones if bone not in mapped_targets]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'source_armature_name': self.source_armature_name,
            'target_armature_name': self.target_armature_name,
            'description': self.description,
            'mappings': [m.to_dict() for m in self.mappings],
            'metadata': {
                'created_date': self.created_date,
                'modified_date': self.modified_date,
                'source_bone_count': self.source_bone_count,
                'target_bone_count': self.target_bone_count,
                'mapped_count': self.mapped_count,
                'auto_mapped_count': self.auto_mapped_count
            },
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoneMappingPreset':
        """Create from dictionary."""
        mappings = [BoneMapping.from_dict(m) for m in data.get('mappings', [])]
        metadata = data.get('metadata', {})

        return cls(
            name=data['name'],
            source_armature_name=data['source_armature_name'],
            target_armature_name=data['target_armature_name'],
            description=data.get('description', ''),
            mappings=mappings,
            created_date=metadata.get('created_date', ''),
            modified_date=metadata.get('modified_date', ''),
            source_bone_count=metadata.get('source_bone_count', 0),
            target_bone_count=metadata.get('target_bone_count', 0),
            mapped_count=metadata.get('mapped_count', 0),
            auto_mapped_count=metadata.get('auto_mapped_count', 0),
            version=data.get('version', '1.0')
        )

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'BoneMappingPreset':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
