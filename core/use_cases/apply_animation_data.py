"""
Use case for applying saved animation data to armature.

Transfers animation keyframes to target armature.
"""

from typing import Tuple, Optional, List
import bpy

from ..domain.animation_data_entities import AnimationData, BoneAnimationData, FCurveData, KeyframeData
from ..services.animation_data_service import load_animation_data_from_file


def create_action_for_armature(armature_obj: bpy.types.Object, action_name: str) -> bpy.types.Action:
    """
    Create unique action for armature.

    Args:
        armature_obj: Target armature
        action_name: Base name for the action

    Returns:
        bpy.types.Action: Created unique action
    """
    # Create unique action name by appending armature name
    # This ensures each armature gets its own action instance
    # Example: "Walk" + "Armature" = "Walk_Armature"
    # Example: "Walk" + "Armature.001" = "Walk_Armature.001"
    unique_action_name = f"{action_name}_{armature_obj.name}"

    # Always create a new unique action or get existing one for re-application
    action = bpy.data.actions.get(unique_action_name)

    if not action:
        # Create new unique action
        action = bpy.data.actions.new(name=unique_action_name)
        print(f"  Created new action: {unique_action_name}")
    else:
        # Action exists - this is a re-application to same armature
        print(f"  Reusing existing action: {unique_action_name}")

    # Assign to armature
    if not armature_obj.animation_data:
        armature_obj.animation_data_create()

    armature_obj.animation_data.action = action

    return action


def apply_keyframe_to_fcurve(fcurve, keyframe_data: KeyframeData):
    """
    Apply keyframe data to fcurve.

    Args:
        fcurve: Blender fcurve
        keyframe_data: Keyframe data to apply
    """
    # Insert keyframe
    kf = fcurve.keyframe_points.insert(
        frame=keyframe_data.frame,
        value=keyframe_data.value
    )

    # Set interpolation
    kf.interpolation = keyframe_data.interpolation

    # Set handles
    kf.handle_left = keyframe_data.handle_left
    kf.handle_right = keyframe_data.handle_right
    kf.handle_left_type = keyframe_data.handle_left_type
    kf.handle_right_type = keyframe_data.handle_right_type


def apply_fcurve_to_action(action, fcurve_data: FCurveData, bone_name: str, target_armature: bpy.types.Object) -> Optional[str]:
    """
    Apply fcurve data to action.

    Args:
        action: Target action
        fcurve_data: FCurve data to apply
        bone_name: Name of bone in target armature
        target_armature: Target armature object

    Returns:
        Optional[str]: Error message if failed, None if success
    """
    # Check if bone exists in target armature
    if bone_name not in target_armature.pose.bones:
        return f"Bone not found: {bone_name}"

    # Create data_path for target armature
    data_path = fcurve_data.data_path

    # Create or get fcurve
    fcurve = action.fcurves.find(data_path, index=fcurve_data.array_index)

    if not fcurve:
        fcurve = action.fcurves.new(data_path, index=fcurve_data.array_index)
        print(f"    Created fcurve: {data_path}[{fcurve_data.array_index}]")

    # Clear existing keyframes
    fcurve.keyframe_points.clear()

    # Apply all keyframes
    keyframe_count = 0
    for keyframe_data in fcurve_data.keyframes:
        apply_keyframe_to_fcurve(fcurve, keyframe_data)
        keyframe_count += 1

    print(f"    Added {keyframe_count} keyframes to {data_path}[{fcurve_data.array_index}]")

    # Set extrapolation
    fcurve.extrapolation = fcurve_data.extrapolation

    # Update fcurve
    fcurve.update()

    return None


def apply_animation_to_armature(
    armature_obj: bpy.types.Object,
    anim_data: AnimationData,
    create_new_action: bool = True,
    action_name_override: Optional[str] = None
) -> Tuple[bool, str, List[str]]:
    """
    Apply animation data to target armature.

    Args:
        armature_obj: Target armature object
        anim_data: Animation data to apply
        create_new_action: Whether to create new action or modify existing
        action_name_override: Optional custom name for created action

    Returns:
        Tuple[bool, str, List[str]]: (success, message, warnings)
    """
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return (False, "Target object is not an armature", [])

    warnings = []
    bones_applied = 0
    bones_skipped = 0
    fcurves_created = 0

    try:
        print(f"\n=== APPLYING ANIMATION ===")
        print(f"Animation: {anim_data.name}")
        print(f"Target Armature: {armature_obj.name}")
        print(f"Bones in animation: {len(anim_data.bones)}")

        # Create or get action
        if create_new_action:
            action_name = action_name_override or anim_data.name
            action = create_action_for_armature(armature_obj, action_name)
            print(f"Action assigned: {action.name}")
        else:
            if not armature_obj.animation_data or not armature_obj.animation_data.action:
                return (False, "No active action on armature", [])
            action = armature_obj.animation_data.action
            print(f"Using existing action: {action.name}")

        # Clear existing fcurves in action
        action.fcurves.clear()
        print("Cleared existing fcurves")

        # Set frame range
        action.frame_start = anim_data.frame_start
        action.frame_end = anim_data.frame_end
        print(f"Frame range: {int(anim_data.frame_start)} - {int(anim_data.frame_end)}")

        # Apply animation for each bone
        for bone_anim in anim_data.bones:
            bone_name = bone_anim.bone_name

            # Check if bone exists
            if bone_name not in armature_obj.pose.bones:
                warnings.append(f"Bone not found in target: {bone_name}")
                bones_skipped += 1
                print(f"  ❌ Bone not found: {bone_name}")
                continue

            # Apply all fcurves for this bone
            for fcurve_data in bone_anim.fcurves:
                error = apply_fcurve_to_action(action, fcurve_data, bone_name, armature_obj)
                if error:
                    warnings.append(error)
                else:
                    fcurves_created += 1

            bones_applied += 1
            print(f"  ✅ Applied animation to bone: {bone_name} ({len(bone_anim.fcurves)} fcurves)")

        print(f"\nTotal fcurves created: {fcurves_created}")
        print(f"Bones applied: {bones_applied}/{anim_data.bone_count}")

        # IMPORTANT: Ensure action is assigned to armature
        if not armature_obj.animation_data:
            armature_obj.animation_data_create()
        armature_obj.animation_data.action = action
        print(f"Action '{action.name}' assigned to armature")

        # Set scene frame range to match animation
        bpy.context.scene.frame_start = int(anim_data.frame_start)
        bpy.context.scene.frame_end = int(anim_data.frame_end)
        bpy.context.scene.frame_current = int(anim_data.frame_start)
        print(f"Scene frame range updated: {int(anim_data.frame_start)} - {int(anim_data.frame_end)}")

        # Update scene and viewport
        bpy.context.view_layer.update()

        # Force viewport refresh
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        print("=== APPLICATION COMPLETE ===\n")

        # Build result message
        message = f"Animation '{anim_data.name}' applied to '{armature_obj.name}'\n"
        message += f"FCurves created: {fcurves_created}\n"
        message += f"Bones animated: {bones_applied}/{anim_data.bone_count}\n"
        message += f"Frame range: {int(anim_data.frame_start)}-{int(anim_data.frame_end)}"

        if bones_skipped > 0:
            message += f"\nWarning: {bones_skipped} bones skipped (not found in target)"

        if fcurves_created == 0:
            return (False, "No fcurves were created - animation may not have been saved correctly", warnings)

        return (True, message, warnings)

    except Exception as e:
        return (False, f"Failed to apply animation: {str(e)}", warnings)


def load_and_apply_animation(
    filepath: str,
    armature_obj: bpy.types.Object,
    action_name_override: Optional[str] = None
) -> Tuple[bool, str, List[str]]:
    """
    Load animation data from file and apply to armature.

    Args:
        filepath: Path to animation data file
        armature_obj: Target armature object
        action_name_override: Optional custom name for created action

    Returns:
        Tuple[bool, str, List[str]]: (success, message, warnings)
    """
    # Load animation data
    success, message, anim_data = load_animation_data_from_file(filepath)

    if not success or not anim_data:
        return (False, message, [])

    # Apply to armature
    return apply_animation_to_armature(
        armature_obj,
        anim_data,
        create_new_action=True,
        action_name_override=action_name_override
    )
