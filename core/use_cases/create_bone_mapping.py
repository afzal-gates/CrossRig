"""
Use case for creating bone mapping between two armatures.

Extracts bone lists from source and target armatures and creates
an empty bone mapping preset ready for manual or auto-mapping.
"""

from typing import Tuple, List
import bpy

from ..domain.bone_mapping_entities import BoneMappingPreset


def get_armature_bone_names(armature_obj) -> List[str]:
    """
    Get list of bone names from armature object.

    Args:
        armature_obj: Blender armature object

    Returns:
        List[str]: List of bone names
    """
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return []

    # Get bones from armature data (not pose bones)
    # This ensures we get all bones regardless of pose
    return [bone.name for bone in armature_obj.data.bones]


def create_bone_mapping_from_armatures(
    source_armature,
    target_armature,
    preset_name: str = "",
    description: str = ""
) -> Tuple[bool, str, BoneMappingPreset]:
    """
    Create bone mapping preset from two armatures.

    Creates an empty mapping with metadata about both armatures.
    Mappings can then be added manually or via auto-mapping.

    Args:
        source_armature: Source armature object
        target_armature: Target armature object
        preset_name: Name for the mapping preset
        description: Optional description

    Returns:
        Tuple[bool, str, BoneMappingPreset]: (success, message, mapping_preset)
    """
    try:
        # Validate armatures
        if not source_armature or source_armature.type != 'ARMATURE':
            return (False, "Invalid source armature", None)

        if not target_armature or target_armature.type != 'ARMATURE':
            return (False, "Invalid target armature", None)

        # Get bone names
        source_bones = get_armature_bone_names(source_armature)
        target_bones = get_armature_bone_names(target_armature)

        if not source_bones:
            return (False, "Source armature has no bones", None)

        if not target_bones:
            return (False, "Target armature has no bones", None)

        # Generate preset name if not provided
        if not preset_name or not preset_name.strip():
            preset_name = f"{source_armature.name}_to_{target_armature.name}"

        # Create mapping preset
        mapping_preset = BoneMappingPreset(
            name=preset_name,
            source_armature_name=source_armature.name,
            target_armature_name=target_armature.name,
            description=description,
            source_bone_count=len(source_bones),
            target_bone_count=len(target_bones),
            mapped_count=0,
            auto_mapped_count=0
        )

        message = (
            f"Created bone mapping: {preset_name}\n"
            f"Source bones: {len(source_bones)}\n"
            f"Target bones: {len(target_bones)}"
        )

        return (True, message, mapping_preset)

    except Exception as e:
        return (False, f"Failed to create bone mapping: {str(e)}", None)


def get_source_bones_for_mapping(source_armature) -> Tuple[bool, str, List[str]]:
    """
    Get list of source bone names for mapping UI.

    Args:
        source_armature: Source armature object

    Returns:
        Tuple[bool, str, List[str]]: (success, message, bone_names)
    """
    try:
        if not source_armature or source_armature.type != 'ARMATURE':
            return (False, "Invalid source armature", [])

        bone_names = get_armature_bone_names(source_armature)

        if not bone_names:
            return (False, "Source armature has no bones", [])

        return (True, f"Found {len(bone_names)} bones", bone_names)

    except Exception as e:
        return (False, f"Failed to get source bones: {str(e)}", [])


def get_target_bones_for_mapping(target_armature) -> Tuple[bool, str, List[str]]:
    """
    Get list of target bone names for mapping UI.

    Args:
        target_armature: Target armature object

    Returns:
        Tuple[bool, str, List[str]]: (success, message, bone_names)
    """
    try:
        if not target_armature or target_armature.type != 'ARMATURE':
            return (False, "Invalid target armature", [])

        bone_names = get_armature_bone_names(target_armature)

        if not bone_names:
            return (False, "Target armature has no bones", [])

        return (True, f"Found {len(bone_names)} bones", bone_names)

    except Exception as e:
        return (False, f"Failed to get target bones: {str(e)}", [])
