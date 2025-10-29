"""
Use case for saving animation data from armature.

Extracts all keyframe data from armature action and saves it.
"""

from typing import Tuple, Optional
import bpy

from ..domain.animation_data_entities import (
    AnimationData,
    BoneAnimationData,
    FCurveData,
    KeyframeData
)
from ..services.animation_data_service import (
    save_animation_data_to_file,
    validate_animation_data
)


def extract_keyframe_data(keyframe_point) -> KeyframeData:
    """
    Extract keyframe data from Blender keyframe point.

    Args:
        keyframe_point: Blender keyframe point

    Returns:
        KeyframeData: Extracted keyframe data
    """
    return KeyframeData(
        frame=keyframe_point.co[0],
        value=keyframe_point.co[1],
        interpolation=keyframe_point.interpolation,
        handle_left=tuple(keyframe_point.handle_left),
        handle_right=tuple(keyframe_point.handle_right),
        handle_left_type=keyframe_point.handle_left_type,
        handle_right_type=keyframe_point.handle_right_type
    )


def extract_fcurve_data(fcurve) -> FCurveData:
    """
    Extract fcurve data from Blender fcurve.

    Args:
        fcurve: Blender fcurve

    Returns:
        FCurveData: Extracted fcurve data
    """
    # Extract keyframes
    keyframes = [extract_keyframe_data(kf) for kf in fcurve.keyframe_points]

    # Extract modifiers (simplified)
    modifiers = []
    for mod in fcurve.modifiers:
        mod_data = {
            'type': mod.type,
            'mute': mod.mute
        }
        modifiers.append(mod_data)

    return FCurveData(
        data_path=fcurve.data_path,
        array_index=fcurve.array_index,
        keyframes=keyframes,
        extrapolation=fcurve.extrapolation,
        modifiers=modifiers
    )


def extract_animation_from_action(action, armature_name: str) -> AnimationData:
    """
    Extract all animation data from a Blender action.

    Args:
        action: Blender action object
        armature_name: Name of source armature

    Returns:
        AnimationData: Extracted animation data
    """
    # Group fcurves by bone
    bone_fcurves = {}

    for fcurve in action.fcurves:
        # Extract bone name from data_path
        # e.g., 'pose.bones["Hips"].location' -> 'Hips'
        data_path = fcurve.data_path

        if 'pose.bones[' in data_path:
            # Extract bone name
            start = data_path.index('pose.bones["') + len('pose.bones["')
            end = data_path.index('"]', start)
            bone_name = data_path[start:end]

            if bone_name not in bone_fcurves:
                bone_fcurves[bone_name] = []

            bone_fcurves[bone_name].append(fcurve)

    # Create bone animation data
    bones = []
    for bone_name, fcurves in bone_fcurves.items():
        fcurve_data_list = [extract_fcurve_data(fc) for fc in fcurves]
        bone_anim = BoneAnimationData(
            bone_name=bone_name,
            fcurves=fcurve_data_list
        )
        bones.append(bone_anim)

    # Get frame range
    frame_start, frame_end = action.frame_range

    # Create animation data
    anim_data = AnimationData(
        name=action.name,
        frame_start=frame_start,
        frame_end=frame_end,
        bones=bones,
        source_armature=armature_name,
        source_action=action.name,
        bone_count=len(bones)
    )

    return anim_data


def save_animation_data(
    armature_obj: bpy.types.Object,
    action_name: str,
    save_name: str,
    description: str = ""
) -> Tuple[bool, str, Optional[str]]:
    """
    Save animation data from armature action.

    Args:
        armature_obj: Blender armature object
        action_name: Name of action to save
        save_name: Name to save animation as
        description: Optional description

    Returns:
        Tuple[bool, str, Optional[str]]: (success, message, filepath)
    """
    # Validate input
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return (False, "Selected object is not an armature", None)

    if not save_name or not save_name.strip():
        return (False, "Animation name cannot be empty", None)

    # Get action
    action = bpy.data.actions.get(action_name)
    if not action:
        return (False, f"Action not found: {action_name}", None)

    try:
        # Extract animation data
        anim_data = extract_animation_from_action(action, armature_obj.name)

        # Override name and description
        anim_data.name = save_name.strip()
        anim_data.description = description.strip()

        # Validate
        valid, validation_message = validate_animation_data(anim_data)
        if not valid:
            return (False, f"Validation failed: {validation_message}", None)

        # Save to file
        success, message = save_animation_data_to_file(anim_data)

        if success:
            from ..services.animation_data_service import get_animation_data_directory, sanitize_filename
            anim_dir = get_animation_data_directory()
            safe_name = sanitize_filename(anim_data.name)
            filepath = str(anim_dir / f"{safe_name}.json")

            info_msg = f"{message}\nBones: {anim_data.bone_count}, Frames: {int(anim_data.frame_start)}-{int(anim_data.frame_end)}"
            return (True, info_msg, filepath)
        else:
            return (False, message, None)

    except Exception as e:
        return (False, f"Failed to save animation: {str(e)}", None)
