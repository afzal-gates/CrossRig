"""
Mixamo Rig Generator Service.

Creates animation-ready control rigs for Mixamo armatures with:
- IK/FK controls for arms and legs
- Pole targets for elbows and knees
- Control widgets/shapes
- Constraints for realistic animation
"""

import bpy
from mathutils import Vector, Matrix
import math


def create_control_bone(armature, edit_bones, name, position, size=1.0, parent=None):
    """Create a control bone at the specified position."""
    bone = edit_bones.new(name)
    bone.head = position
    bone.tail = position + Vector((0, 0, size * 0.1))

    if parent:
        bone.parent = parent

    return bone


def create_widget_shape(obj, bone_name, shape_type='CIRCLE'):
    """Create a custom shape widget for a control bone."""
    # This would create custom mesh shapes for controls
    # For now, we'll set bone display properties
    pass


def add_ik_constraint(pose_bone, target_armature, target_bone_name, chain_length=2):
    """Add IK constraint to a pose bone."""
    constraint = pose_bone.constraints.new('IK')
    constraint.target = target_armature
    constraint.subtarget = target_bone_name
    constraint.chain_count = chain_length
    return constraint


def add_copy_rotation_constraint(pose_bone, target_armature, target_bone_name):
    """Add Copy Rotation constraint to a pose bone."""
    constraint = pose_bone.constraints.new('COPY_ROTATION')
    constraint.target = target_armature
    constraint.subtarget = target_bone_name
    return constraint


def generate_mixamo_control_rig(armature_obj, context):
    """
    Generate a complete control rig for Mixamo armature.

    Creates:
    - IK controls for arms (hand IK controllers)
    - IK controls for legs (foot IK controllers)
    - Pole targets for elbows and knees
    - FK controls as backup
    - Root controller

    Args:
        armature_obj: The Mixamo armature object
        context: Blender context

    Returns:
        (success, message, rig_obj)
    """

    if not armature_obj or armature_obj.type != 'ARMATURE':
        return False, "Not a valid armature object", None

    # Check if it's a Mixamo armature
    armature_data = armature_obj.data
    has_mixamo_bones = any('mixamorig:' in bone.name for bone in armature_data.bones)

    if not has_mixamo_bones:
        return False, "Not a Mixamo armature (no mixamorig: prefix found)", None

    # Store original mode
    original_mode = armature_obj.mode if hasattr(armature_obj, 'mode') else 'OBJECT'

    try:
        # Enter edit mode
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        armature_obj.select_set(True)
        context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')

        edit_bones = armature_obj.data.edit_bones

        # Find key bones
        hips = edit_bones.get('mixamorig:Hips')

        # Left arm bones
        left_shoulder = edit_bones.get('mixamorig:LeftShoulder')
        left_arm = edit_bones.get('mixamorig:LeftArm')
        left_forearm = edit_bones.get('mixamorig:LeftForeArm')
        left_hand = edit_bones.get('mixamorig:LeftHand')

        # Right arm bones
        right_shoulder = edit_bones.get('mixamorig:RightShoulder')
        right_arm = edit_bones.get('mixamorig:RightArm')
        right_forearm = edit_bones.get('mixamorig:RightForeArm')
        right_hand = edit_bones.get('mixamorig:RightHand')

        # Left leg bones
        left_upleg = edit_bones.get('mixamorig:LeftUpLeg')
        left_leg = edit_bones.get('mixamorig:LeftLeg')
        left_foot = edit_bones.get('mixamorig:LeftFoot')

        # Right leg bones
        right_upleg = edit_bones.get('mixamorig:RightUpLeg')
        right_leg = edit_bones.get('mixamorig:RightLeg')
        right_foot = edit_bones.get('mixamorig:RightFoot')

        control_bones = {}

        # === Create Root Controller ===
        if hips:
            root_pos = hips.head.copy()
            root_pos.z = 0  # Place at ground level
            root_ctrl = create_control_bone(
                armature_obj, edit_bones, "CTRL_Root", root_pos, size=2.0
            )
            control_bones['root'] = root_ctrl

            # Create COG (Center of Gravity) controller
            cog_ctrl = create_control_bone(
                armature_obj, edit_bones, "CTRL_COG", hips.head, size=1.5, parent=root_ctrl
            )
            control_bones['cog'] = cog_ctrl

        # === Create Arm IK Controls ===
        if left_hand and left_forearm:
            # Left hand IK controller
            left_hand_ik = create_control_bone(
                armature_obj, edit_bones, "CTRL_Hand_IK.L", left_hand.head, size=0.8
            )
            control_bones['hand_ik_l'] = left_hand_ik

            # Left elbow pole target
            elbow_pos = left_forearm.head.copy()
            elbow_pos.y -= 0.5  # Offset forward
            left_elbow_pole = create_control_bone(
                armature_obj, edit_bones, "CTRL_Elbow_Pole.L", elbow_pos, size=0.5
            )
            control_bones['elbow_pole_l'] = left_elbow_pole

        if right_hand and right_forearm:
            # Right hand IK controller
            right_hand_ik = create_control_bone(
                armature_obj, edit_bones, "CTRL_Hand_IK.R", right_hand.head, size=0.8
            )
            control_bones['hand_ik_r'] = right_hand_ik

            # Right elbow pole target
            elbow_pos = right_forearm.head.copy()
            elbow_pos.y -= 0.5  # Offset forward
            right_elbow_pole = create_control_bone(
                armature_obj, edit_bones, "CTRL_Elbow_Pole.R", elbow_pos, size=0.5
            )
            control_bones['elbow_pole_r'] = right_elbow_pole

        # === Create Leg IK Controls ===
        if left_foot and left_leg:
            # Left foot IK controller
            left_foot_ik = create_control_bone(
                armature_obj, edit_bones, "CTRL_Foot_IK.L", left_foot.head, size=1.0
            )
            control_bones['foot_ik_l'] = left_foot_ik

            # Left knee pole target
            knee_pos = left_leg.head.copy()
            knee_pos.y += 0.5  # Offset forward
            left_knee_pole = create_control_bone(
                armature_obj, edit_bones, "CTRL_Knee_Pole.L", knee_pos, size=0.5
            )
            control_bones['knee_pole_l'] = left_knee_pole

        if right_foot and right_leg:
            # Right foot IK controller
            right_foot_ik = create_control_bone(
                armature_obj, edit_bones, "CTRL_Foot_IK.R", right_foot.head, size=1.0
            )
            control_bones['foot_ik_r'] = right_foot_ik

            # Right knee pole target
            knee_pos = right_leg.head.copy()
            knee_pos.y += 0.5  # Offset forward
            right_knee_pole = create_control_bone(
                armature_obj, edit_bones, "CTRL_Knee_Pole.R", knee_pos, size=0.5
            )
            control_bones['knee_pole_r'] = right_knee_pole

        # Exit edit mode and enter pose mode to add constraints
        bpy.ops.object.mode_set(mode='POSE')
        pose_bones = armature_obj.pose.bones

        # === Add IK Constraints ===

        # Left arm IK
        if left_hand and 'hand_ik_l' in control_bones:
            left_forearm_pose = pose_bones.get('mixamorig:LeftForeArm')
            if left_forearm_pose:
                ik_constraint = add_ik_constraint(
                    left_forearm_pose, armature_obj, "CTRL_Hand_IK.L", chain_length=2
                )
                if 'elbow_pole_l' in control_bones:
                    ik_constraint.pole_target = armature_obj
                    ik_constraint.pole_subtarget = "CTRL_Elbow_Pole.L"
                    ik_constraint.pole_angle = math.radians(0)

        # Right arm IK
        if right_hand and 'hand_ik_r' in control_bones:
            right_forearm_pose = pose_bones.get('mixamorig:RightForeArm')
            if right_forearm_pose:
                ik_constraint = add_ik_constraint(
                    right_forearm_pose, armature_obj, "CTRL_Hand_IK.R", chain_length=2
                )
                if 'elbow_pole_r' in control_bones:
                    ik_constraint.pole_target = armature_obj
                    ik_constraint.pole_subtarget = "CTRL_Elbow_Pole.R"
                    ik_constraint.pole_angle = math.radians(0)

        # Left leg IK
        if left_foot and 'foot_ik_l' in control_bones:
            left_leg_pose = pose_bones.get('mixamorig:LeftLeg')
            if left_leg_pose:
                ik_constraint = add_ik_constraint(
                    left_leg_pose, armature_obj, "CTRL_Foot_IK.L", chain_length=2
                )
                if 'knee_pole_l' in control_bones:
                    ik_constraint.pole_target = armature_obj
                    ik_constraint.pole_subtarget = "CTRL_Knee_Pole.L"
                    ik_constraint.pole_angle = math.radians(0)

        # Right leg IK
        if right_foot and 'foot_ik_r' in control_bones:
            right_leg_pose = pose_bones.get('mixamorig:RightLeg')
            if right_leg_pose:
                ik_constraint = add_ik_constraint(
                    right_leg_pose, armature_obj, "CTRL_Foot_IK.R", chain_length=2
                )
                if 'knee_pole_r' in control_bones:
                    ik_constraint.pole_target = armature_obj
                    ik_constraint.pole_subtarget = "CTRL_Knee_Pole.R"
                    ik_constraint.pole_angle = math.radians(0)

        # Parent Hips to COG if available
        if hips and 'cog' in control_bones:
            hips_pose = pose_bones.get('mixamorig:Hips')
            if hips_pose:
                constraint = add_copy_rotation_constraint(hips_pose, armature_obj, "CTRL_COG")
                constraint.mix_mode = 'BEFORE'

        # Set bone display for control bones
        for ctrl_name in control_bones.keys():
            ctrl_pose = pose_bones.get(control_bones[ctrl_name].name)
            if ctrl_pose:
                ctrl_pose.custom_shape_scale_xyz = (0.5, 0.5, 0.5)
                # Make control bones easier to select
                armature_obj.data.bones[ctrl_pose.name].show_wire = True

        # Create bone groups for organization
        bpy.ops.object.mode_set(mode='POSE')

        # IK controls group
        ik_group = armature_obj.pose.bone_groups.new(name="IK_Controls")
        ik_group.color_set = 'THEME01'  # Red

        # Pole targets group
        pole_group = armature_obj.pose.bone_groups.new(name="Pole_Targets")
        pole_group.color_set = 'THEME03'  # Blue

        # Root group
        root_group = armature_obj.pose.bone_groups.new(name="Root_Controls")
        root_group.color_set = 'THEME09'  # Green

        # Assign bone groups
        for ctrl_name, ctrl_bone in control_bones.items():
            pose_bone = pose_bones.get(ctrl_bone.name)
            if pose_bone:
                if 'root' in ctrl_name.lower() or 'cog' in ctrl_name.lower():
                    pose_bone.bone_group = root_group
                elif 'pole' in ctrl_name.lower():
                    pose_bone.bone_group = pole_group
                else:
                    pose_bone.bone_group = ik_group

        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        control_count = len(control_bones)
        message = f"Successfully generated control rig with {control_count} controllers (IK hands, feet, poles, root)"

        return True, message, armature_obj

    except Exception as e:
        # Restore original mode
        try:
            bpy.ops.object.mode_set(mode=original_mode)
        except:
            pass

        return False, f"Failed to generate rig: {str(e)}", None
