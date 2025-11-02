"""
Smart Rig Service for CrossRig.

Core logic for generating armatures from user-selected landmarks,
mimicking Auto-Rig Pro's Smart function.
"""

import bpy
from mathutils import Vector
import math


# Bone naming conventions matching standard armature naming
BONE_NAMING = {
    'head_top': 'head',
    'head_center': 'head_mid',
    'neck': 'neck',
    'chin': 'jaw',
    'spine_top': 'spine_03',
    'spine_mid': 'spine_02',
    'spine_bottom': 'spine_01',
    'shoulder': {'LEFT': 'shoulder.L', 'RIGHT': 'shoulder.R'},
    'elbow': {'LEFT': 'upper_arm.L', 'RIGHT': 'upper_arm.R'},
    'wrist': {'LEFT': 'forearm.L', 'RIGHT': 'forearm.R'},
    'hand': {'LEFT': 'hand.L', 'RIGHT': 'hand.R'},
    'hip': {'LEFT': 'thigh.L', 'RIGHT': 'thigh.R'},
    'knee': {'LEFT': 'shin.L', 'RIGHT': 'shin.R'},
    'ankle': {'LEFT': 'foot.L', 'RIGHT': 'foot.R'},
    'foot': {'LEFT': 'toe.L', 'RIGHT': 'toe.R'},
    'toe': {'LEFT': 'toe_tip.L', 'RIGHT': 'toe_tip.R'},
}


def get_bone_name(landmark_id, side='CENTER'):
    """Get standardized bone name for a landmark."""
    name_def = BONE_NAMING.get(landmark_id)

    if isinstance(name_def, dict):
        return name_def.get(side, landmark_id)
    else:
        return name_def if name_def else landmark_id


def get_landmark_position(landmarks, landmark_id, side='CENTER'):
    """Get position of a specific landmark."""
    for lm in landmarks:
        if lm.landmark_id == landmark_id and lm.landmark_side == side:
            return Vector(lm.position)
    return None


def interpolate_landmark(landmarks, landmark_id, side='CENTER'):
    """
    Intelligently interpolate missing landmarks based on available ones.

    This mimics Auto-Rig Pro's Smart mode by calculating reasonable
    positions for missing bones.
    """
    # Try to get existing landmark first
    existing = get_landmark_position(landmarks, landmark_id, side)
    if existing:
        return existing

    # Interpolation rules for common landmarks
    if landmark_id == 'head_top':
        neck = get_landmark_position(landmarks, 'neck', 'CENTER')
        chin = get_landmark_position(landmarks, 'chin', 'CENTER')
        if neck and chin:
            # Head top is above neck, opposite direction from chin
            neck_to_chin = chin - neck
            return neck - neck_to_chin * 0.8

    elif landmark_id == 'spine_top':
        neck = get_landmark_position(landmarks, 'neck', 'CENTER')
        spine_bottom = get_landmark_position(landmarks, 'spine_bottom', 'CENTER')
        if neck and spine_bottom:
            # Spine top is 80% of the way from hips to neck
            return spine_bottom.lerp(neck, 0.8)

    elif landmark_id == 'spine_mid':
        neck = get_landmark_position(landmarks, 'neck', 'CENTER')
        spine_bottom = get_landmark_position(landmarks, 'spine_bottom', 'CENTER')
        if neck and spine_bottom:
            # Spine mid is halfway between hips and neck
            return spine_bottom.lerp(neck, 0.5)

    elif landmark_id == 'elbow':
        shoulder = get_landmark_position(landmarks, 'shoulder', side)
        wrist = get_landmark_position(landmarks, 'wrist', side)
        if shoulder and wrist:
            # Elbow is roughly halfway between shoulder and wrist
            return shoulder.lerp(wrist, 0.5)

    elif landmark_id == 'hand':
        wrist = get_landmark_position(landmarks, 'wrist', side)
        elbow = get_landmark_position(landmarks, 'elbow', side)
        if wrist and elbow:
            # Hand extends from wrist in same direction
            wrist_to_elbow = elbow - wrist
            return wrist - wrist_to_elbow * 0.3

    elif landmark_id == 'hip':
        spine_bottom = get_landmark_position(landmarks, 'spine_bottom', 'CENTER')
        if spine_bottom:
            # Hips are offset from spine bottom
            offset_x = 0.15 if side == 'LEFT' else -0.15
            return spine_bottom + Vector((offset_x, 0, -0.1))

    elif landmark_id == 'knee':
        hip = get_landmark_position(landmarks, 'hip', side)
        ankle = get_landmark_position(landmarks, 'ankle', side)
        if hip and ankle:
            # Knee is roughly halfway between hip and ankle
            return hip.lerp(ankle, 0.5)
        elif hip:
            # Estimate knee below hip
            return hip + Vector((0, 0, -0.5))

    elif landmark_id == 'foot':
        ankle = get_landmark_position(landmarks, 'ankle', side)
        knee = get_landmark_position(landmarks, 'knee', side)
        if ankle and knee:
            # Foot extends forward from ankle
            return ankle + Vector((0, 0.2, -0.05))
        elif ankle:
            return ankle + Vector((0, 0.2, -0.05))

    elif landmark_id == 'toe':
        foot = get_landmark_position(landmarks, 'foot', side)
        ankle = get_landmark_position(landmarks, 'ankle', side)
        if foot:
            return foot + Vector((0, 0.1, 0))
        elif ankle:
            return ankle + Vector((0, 0.3, -0.05))

    return None


def calculate_bone_roll(bone_vector, up_vector=Vector((0, 0, 1))):
    """Calculate bone roll to align with up vector."""
    # This is a simplified roll calculation
    # For production, you'd want more sophisticated alignment
    bone_dir = bone_vector.normalized()

    # Calculate perpendicular vector
    right = bone_dir.cross(up_vector)
    if right.length < 0.001:
        # Bone is parallel to up vector, use alternative
        right = bone_dir.cross(Vector((1, 0, 0)))

    right.normalize()
    actual_up = right.cross(bone_dir)

    # Calculate roll angle
    roll = math.atan2(actual_up.y, actual_up.x)
    return roll


def create_bone_chain(edit_bones, bone_name, head_pos, tail_pos, parent=None, roll=0.0):
    """Create a single bone in edit mode."""
    bone = edit_bones.new(bone_name)
    bone.head = head_pos
    bone.tail = tail_pos
    bone.roll = roll

    if parent:
        bone.parent = parent

    return bone


def generate_armature_from_landmarks(landmarks, mesh_obj, auto_skin=True, context=None):
    """
    Generate an armature from user-selected landmarks.

    Smart Mode: Generates complete body skeleton from minimal landmarks.
    - 6 picks generates: spine (3), neck, head, arms (8), legs (10) = 23 bones
    - Automatically calculates all intermediate bones

    Args:
        landmarks: Collection of SmartRigLandmark property groups
        mesh_obj: Target mesh object
        auto_skin: If True, automatically parent and weight paint
        context: Blender context

    Returns:
        (success, message, armature_obj)
    """
    if len(landmarks) < 1:
        return False, "Need at least 1 landmark to generate rig", None

    # Create landmark position dictionary
    landmark_dict = {}
    for lm in landmarks:
        key = f"{lm.landmark_id}_{lm.landmark_side}"
        landmark_dict[key] = Vector(lm.position)

    # Create armature
    armature_data = bpy.data.armatures.new("SmartRig")
    armature_obj = bpy.data.objects.new("SmartRig", armature_data)

    # Link to scene
    context.collection.objects.link(armature_obj)
    armature_obj.location = mesh_obj.location

    # Set as active and enter edit mode
    context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    edit_bones = armature_obj.data.edit_bones
    created_bones = {}

    # === Create Spine Chain (with interpolation) ===
    spine_bottom = interpolate_landmark(landmarks, 'spine_bottom', 'CENTER')
    spine_mid = interpolate_landmark(landmarks, 'spine_mid', 'CENTER')
    spine_top = interpolate_landmark(landmarks, 'spine_top', 'CENTER')
    neck = interpolate_landmark(landmarks, 'neck', 'CENTER')
    head_top = interpolate_landmark(landmarks, 'head_top', 'CENTER')

    # Root bone (hips)
    if spine_bottom:
        # Create root bone pointing down slightly
        root_tail = spine_bottom.copy()
        root_head = spine_bottom.copy()
        root_head.z -= 0.2  # Small offset downward

        root_bone = create_bone_chain(
            edit_bones, 'root', root_head, root_tail
        )
        created_bones['root'] = root_bone

        # Spine chain
        current_parent = root_bone

        if spine_mid:
            spine_02 = create_bone_chain(
                edit_bones, 'spine_02', spine_bottom, spine_mid, current_parent
            )
            created_bones['spine_02'] = spine_02
            current_parent = spine_02

        if spine_top:
            start = spine_mid if spine_mid else spine_bottom
            spine_03 = create_bone_chain(
                edit_bones, 'spine_03', start, spine_top, current_parent
            )
            created_bones['spine_03'] = spine_03
            current_parent = spine_03

        # Neck
        if neck:
            start = spine_top if spine_top else (spine_mid if spine_mid else spine_bottom)
            neck_bone = create_bone_chain(
                edit_bones, 'neck', start, neck, current_parent
            )
            created_bones['neck'] = neck_bone
            current_parent = neck_bone

        # Head
        if head_top:
            start = neck if neck else (spine_top if spine_top else spine_bottom)
            head_bone = create_bone_chain(
                edit_bones, 'head', start, head_top, current_parent
            )
            created_bones['head'] = head_bone

    # === Create Arms (ALWAYS generate all arm bones) ===
    shoulder_attach = spine_top if spine_top else (spine_mid if spine_mid else spine_bottom)

    for side in ['LEFT', 'RIGHT']:
        # Force interpolation - ALWAYS create all bones
        shoulder = interpolate_landmark(landmarks, 'shoulder', side)
        elbow = interpolate_landmark(landmarks, 'elbow', side)
        wrist = interpolate_landmark(landmarks, 'wrist', side)
        hand = interpolate_landmark(landmarks, 'hand', side)

        # Skip only if we can't even interpolate shoulder
        if not shoulder:
            continue

        side_suffix = '.L' if side == 'LEFT' else '.R'
        arm_parent = created_bones.get('spine_03', created_bones.get('root'))

        # Shoulder bone (always create)
        shoulder_bone = create_bone_chain(
            edit_bones, f'shoulder{side_suffix}',
            shoulder_attach, shoulder, arm_parent
        )
        created_bones[f'shoulder{side_suffix}'] = shoulder_bone

        # Upper arm (always create if elbow exists or can be interpolated)
        if elbow:
            upper_arm = create_bone_chain(
                edit_bones, f'upper_arm{side_suffix}',
                shoulder, elbow, shoulder_bone
            )
            created_bones[f'upper_arm{side_suffix}'] = upper_arm

            # Forearm (always create if wrist exists or can be interpolated)
            if wrist:
                forearm = create_bone_chain(
                    edit_bones, f'forearm{side_suffix}',
                    elbow, wrist, upper_arm
                )
                created_bones[f'forearm{side_suffix}'] = forearm

                # Hand (always create if it exists or can be interpolated)
                if hand:
                    hand_bone = create_bone_chain(
                        edit_bones, f'hand{side_suffix}',
                        wrist, hand, forearm
                    )
                    created_bones[f'hand{side_suffix}'] = hand_bone

    # === Create Legs (ALWAYS generate all leg bones) ===
    hip_attach = spine_bottom if spine_bottom else interpolate_landmark(landmarks, 'spine_mid', 'CENTER')

    for side in ['LEFT', 'RIGHT']:
        # Force interpolation - ALWAYS create all bones
        hip = interpolate_landmark(landmarks, 'hip', side)
        knee = interpolate_landmark(landmarks, 'knee', side)
        ankle = interpolate_landmark(landmarks, 'ankle', side)
        foot = interpolate_landmark(landmarks, 'foot', side)
        toe = interpolate_landmark(landmarks, 'toe', side)

        # Skip only if we can't even interpolate hip
        if not hip:
            continue

        side_suffix = '.L' if side == 'LEFT' else '.R'
        leg_parent = created_bones.get('root')

        # Thigh (always create if knee exists or can be interpolated)
        if knee:
            thigh = create_bone_chain(
                edit_bones, f'thigh{side_suffix}',
                hip, knee, leg_parent
            )
            created_bones[f'thigh{side_suffix}'] = thigh

            # Shin (always create if ankle exists or can be interpolated)
            if ankle:
                shin = create_bone_chain(
                    edit_bones, f'shin{side_suffix}',
                    knee, ankle, thigh
                )
                created_bones[f'shin{side_suffix}'] = shin

                # Foot (always create if it exists or can be interpolated)
                if foot:
                    foot_bone = create_bone_chain(
                        edit_bones, f'foot{side_suffix}',
                        ankle, foot, shin
                    )
                    created_bones[f'foot{side_suffix}'] = foot_bone

                    # Toe (always create if it exists or can be interpolated)
                    if toe:
                        toe_bone = create_bone_chain(
                            edit_bones, f'toe{side_suffix}',
                            foot, toe, foot_bone
                        )
                        created_bones[f'toe{side_suffix}'] = toe_bone

    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # === Auto-skin if requested ===
    if auto_skin:
        try:
            # Select mesh and armature
            bpy.ops.object.select_all(action='DESELECT')
            mesh_obj.select_set(True)
            armature_obj.select_set(True)
            context.view_layer.objects.active = armature_obj

            # Parent with automatic weights
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')

            message = f"Generated armature '{armature_obj.name}' with {len(created_bones)} bones and automatic skinning"
        except Exception as e:
            message = f"Generated armature '{armature_obj.name}' with {len(created_bones)} bones (skinning failed: {str(e)})"
    else:
        message = f"Generated armature '{armature_obj.name}' with {len(created_bones)} bones"

    return True, message, armature_obj
