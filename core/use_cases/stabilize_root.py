"""
Use case: Stabilize root bone for in-place animations.
"""

from ..services.action_service import stabilize_root_bone_axes


def stabilize_root_animation(armature, root_bone: str) -> tuple:
    """
    Remove horizontal movement from root bone, keeping character in place.

    Args:
        armature: Blender Armature object
        root_bone: Name of the root bone

    Returns:
        Tuple of (success: bool, message: str, keyframe_count: int)
    """
    # Validate animation data exists
    if not armature.animation_data:
        return (False, "No animation data found", 0)

    # Check if NLA tracks exist but no action
    if armature.animation_data.nla_tracks and not armature.animation_data.action:
        return (False, "NLA tracks found. Please use 'Bake Action' first to create a single action", 0)

    # Check if action exists
    if not armature.animation_data.action:
        return (False, "No active action found. Create or bake an animation first", 0)

    action = armature.animation_data.action

    # Validate root bone exists in armature
    if root_bone not in armature.pose.bones:
        return (False, f"Root bone '{root_bone}' not found in armature", 0)

    # Find location fcurves for root bone
    data_path = f'pose.bones["{root_bone}"].location'
    has_fcurves = any(fc.data_path == data_path for fc in action.fcurves)

    if not has_fcurves:
        return (False, f"No location animation found for root bone '{root_bone}'", 0)

    # Disable NLA influence to work on action directly
    nla_was_enabled = armature.animation_data.use_nla
    armature.animation_data.use_nla = False

    # Stabilize X and Y axes (keep Z for vertical movement like jumps)
    keyframe_count = stabilize_root_bone_axes(action, root_bone, axes=[0, 1])

    # Restore NLA state
    armature.animation_data.use_nla = nla_was_enabled

    if keyframe_count > 0:
        message = f"Root stabilized on X, Y axes ({keyframe_count} keyframes → origin). Action: {action.name}"
        success = True
    else:
        message = "No axes were stabilized"
        success = False

    return (success, message, keyframe_count)
