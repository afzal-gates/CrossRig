"""
Use case for applying animation data to armature using bone mapping.

Transfers animation keyframes between different armature types by
remapping bone names according to a bone mapping preset.
"""

from typing import Tuple, Optional, List, Dict
import bpy
import re

from ..domain.animation_data_entities import AnimationData, BoneAnimationData, FCurveData, KeyframeData
from ..domain.bone_mapping_entities import BoneMappingPreset
from ..services.animation_data_service import load_animation_data_from_file
from .apply_animation_data import create_action_for_armature, apply_keyframe_to_fcurve


def remap_bone_name_in_datapath(data_path: str, source_bone: str, target_bone: str) -> str:
    """
    Remap bone name in fcurve data_path.

    Replaces source bone name with target bone name in data paths like:
    'pose.bones["SourceBone"].location' → 'pose.bones["TargetBone"].location'

    Args:
        data_path: Original fcurve data path
        source_bone: Source bone name to replace
        target_bone: Target bone name

    Returns:
        str: Remapped data path
    """
    # Pattern to match pose.bones["BoneName"] or pose.bones['BoneName']
    # Using regex to handle both single and double quotes
    pattern = r'pose\.bones\[(["\'])' + re.escape(source_bone) + r'\1\]'
    replacement = f'pose.bones["{target_bone}"]'

    remapped_path = re.sub(pattern, replacement, data_path)
    return remapped_path


def apply_fcurve_with_mapping(
    action,
    fcurve_data: FCurveData,
    source_bone: str,
    target_bone: str,
    target_armature: bpy.types.Object
) -> Optional[str]:
    """
    Apply fcurve data to action with bone name remapping.

    Args:
        action: Target action
        fcurve_data: FCurve data to apply
        source_bone: Original bone name in animation
        target_bone: Target bone name in armature
        target_armature: Target armature object

    Returns:
        Optional[str]: Error message if failed, None if success
    """
    # Check if target bone exists in target armature
    if target_bone not in target_armature.pose.bones:
        return f"Target bone not found: {target_bone}"

    # Remap data path
    original_data_path = fcurve_data.data_path
    remapped_data_path = remap_bone_name_in_datapath(original_data_path, source_bone, target_bone)

    # Create or get fcurve
    fcurve = action.fcurves.find(remapped_data_path, index=fcurve_data.array_index)

    if not fcurve:
        fcurve = action.fcurves.new(remapped_data_path, index=fcurve_data.array_index)
        print(f"    Created fcurve: {remapped_data_path}[{fcurve_data.array_index}]")

    # Clear existing keyframes
    fcurve.keyframe_points.clear()

    # Apply all keyframes
    keyframe_count = 0
    for keyframe_data in fcurve_data.keyframes:
        apply_keyframe_to_fcurve(fcurve, keyframe_data)
        keyframe_count += 1

    print(f"    Added {keyframe_count} keyframes to {remapped_data_path}[{fcurve_data.array_index}]")

    # Set extrapolation
    fcurve.extrapolation = fcurve_data.extrapolation

    # Update fcurve
    fcurve.update()

    return None


def apply_animation_with_bone_mapping(
    armature_obj: bpy.types.Object,
    anim_data: AnimationData,
    bone_mapping: BoneMappingPreset,
    create_new_action: bool = True,
    action_name_override: Optional[str] = None
) -> Tuple[bool, str, List[str]]:
    """
    Apply animation data to target armature using bone mapping.

    Remaps bone names from animation to target armature according to
    the provided bone mapping preset.

    Args:
        armature_obj: Target armature object
        anim_data: Animation data to apply
        bone_mapping: Bone mapping preset for remapping
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
    bones_unmapped = 0
    fcurves_created = 0

    try:
        print(f"\n=== APPLYING ANIMATION WITH BONE MAPPING ===")
        print(f"Animation: {anim_data.name}")
        print(f"Target Armature: {armature_obj.name}")
        print(f"Bone Mapping: {bone_mapping.name}")
        print(f"Bones in animation: {len(anim_data.bones)}")
        print(f"Mappings available: {bone_mapping.mapped_count}")

        # Create or get action
        if create_new_action:
            # Include mapping name in action for traceability
            if action_name_override:
                action_name = action_name_override
            else:
                action_name = f"{anim_data.name}_{bone_mapping.name}"

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

        # Apply animation for each bone with mapping
        for bone_anim in anim_data.bones:
            source_bone = bone_anim.bone_name

            # Find target bone using mapping
            target_bone = bone_mapping.find_target_bone(source_bone)

            if not target_bone:
                warnings.append(f"No mapping for source bone: {source_bone}")
                bones_unmapped += 1
                print(f"  ⚠️  Unmapped bone: {source_bone}")
                continue

            # Check if target bone exists in armature
            if target_bone not in armature_obj.pose.bones:
                warnings.append(f"Target bone not found in armature: {target_bone} (mapped from {source_bone})")
                bones_skipped += 1
                print(f"  ❌ Target bone not found: {target_bone}")
                continue

            # Apply all fcurves for this bone with remapping
            print(f"  Mapping: {source_bone} → {target_bone}")
            for fcurve_data in bone_anim.fcurves:
                error = apply_fcurve_with_mapping(
                    action,
                    fcurve_data,
                    source_bone,
                    target_bone,
                    armature_obj
                )
                if error:
                    warnings.append(error)
                else:
                    fcurves_created += 1

            bones_applied += 1
            print(f"  ✅ Applied animation: {source_bone} → {target_bone} ({len(bone_anim.fcurves)} fcurves)")

        print(f"\nTotal fcurves created: {fcurves_created}")
        print(f"Bones applied: {bones_applied}")
        print(f"Bones unmapped: {bones_unmapped}")
        print(f"Bones skipped: {bones_skipped}")

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
        message = f"Animation '{anim_data.name}' applied to '{armature_obj.name}' using mapping '{bone_mapping.name}'\n"
        message += f"FCurves created: {fcurves_created}\n"
        message += f"Bones animated: {bones_applied}\n"
        message += f"Bones unmapped: {bones_unmapped}\n"
        message += f"Bones skipped: {bones_skipped}\n"
        message += f"Frame range: {int(anim_data.frame_start)}-{int(anim_data.frame_end)}"

        if bones_unmapped > 0:
            message += f"\n\nWarning: {bones_unmapped} bones have no mapping defined"

        if bones_skipped > 0:
            message += f"\nWarning: {bones_skipped} target bones not found in armature"

        if fcurves_created == 0:
            return (False, "No fcurves were created - check bone mapping and animation data", warnings)

        return (True, message, warnings)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return (False, f"Failed to apply animation with mapping: {str(e)}", warnings)


def load_and_apply_animation_with_mapping(
    animation_filepath: str,
    armature_obj: bpy.types.Object,
    bone_mapping: BoneMappingPreset,
    action_name_override: Optional[str] = None
) -> Tuple[bool, str, List[str]]:
    """
    Load animation data from file and apply to armature using bone mapping.

    Args:
        animation_filepath: Path to animation data file
        armature_obj: Target armature object
        bone_mapping: Bone mapping preset for remapping
        action_name_override: Optional custom name for created action

    Returns:
        Tuple[bool, str, List[str]]: (success, message, warnings)
    """
    # Load animation data
    success, message, anim_data = load_animation_data_from_file(animation_filepath)

    if not success or not anim_data:
        return (False, message, [])

    # Apply to armature with mapping
    return apply_animation_with_bone_mapping(
        armature_obj,
        anim_data,
        bone_mapping,
        create_new_action=True,
        action_name_override=action_name_override
    )


def validate_bone_mapping_for_animation(
    anim_data: AnimationData,
    bone_mapping: BoneMappingPreset,
    target_armature: bpy.types.Object
) -> Tuple[bool, str, Dict[str, List[str]]]:
    """
    Validate bone mapping against animation data and target armature.

    Checks for unmapped bones, missing target bones, and mapping coverage.

    Args:
        anim_data: Animation data to validate
        bone_mapping: Bone mapping preset
        target_armature: Target armature object

    Returns:
        Tuple[bool, str, Dict]: (is_valid, message, validation_details)
    """
    validation = {
        'unmapped_bones': [],
        'missing_target_bones': [],
        'valid_mappings': [],
        'total_bones': len(anim_data.bones),
        'coverage_percentage': 0.0
    }

    # Check each bone in animation
    for bone_anim in anim_data.bones:
        source_bone = bone_anim.bone_name

        # Check if mapped
        target_bone = bone_mapping.find_target_bone(source_bone)

        if not target_bone:
            validation['unmapped_bones'].append(source_bone)
            continue

        # Check if target exists in armature
        if target_bone not in target_armature.pose.bones:
            validation['missing_target_bones'].append(f"{source_bone} → {target_bone}")
        else:
            validation['valid_mappings'].append(f"{source_bone} → {target_bone}")

    # Calculate coverage
    valid_count = len(validation['valid_mappings'])
    total_count = validation['total_bones']
    validation['coverage_percentage'] = (valid_count / total_count * 100) if total_count > 0 else 0.0

    # Determine if valid
    is_valid = (
        len(validation['unmapped_bones']) == 0 and
        len(validation['missing_target_bones']) == 0
    )

    # Build message
    if is_valid:
        message = f"✅ Bone mapping is valid\nCoverage: {validation['coverage_percentage']:.1f}% ({valid_count}/{total_count} bones)"
    else:
        message = f"⚠️ Bone mapping validation issues:\n"
        message += f"Coverage: {validation['coverage_percentage']:.1f}% ({valid_count}/{total_count} bones)\n"

        if validation['unmapped_bones']:
            message += f"Unmapped bones: {len(validation['unmapped_bones'])}\n"

        if validation['missing_target_bones']:
            message += f"Missing target bones: {len(validation['missing_target_bones'])}\n"

    return (is_valid, message, validation)
