"""
Smart Rig Service for CrossRig.

Core logic for generating armatures from user-selected landmarks,
mimicking Auto-Rig Pro's Smart function.
"""

import bpy
from mathutils import Vector
import math
import datetime


def log_arm_bone_positions(armature_obj, naming='standard', stage='BEFORE'):
    """
    Log shoulder to hand bone positions for debugging.

    Args:
        armature_obj: The armature object
        naming: Naming convention ('standard' or 'mixamo')
        stage: 'BEFORE' or 'AFTER' T-pose
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*80}")
    print(f"ARM BONE POSITIONS LOG - {stage} T-POSE")
    print(f"Timestamp: {timestamp}")
    print(f"Armature: {armature_obj.name}")
    print(f"Naming: {naming}")
    print(f"{'='*80}\n")

    # Define arm bones to log based on naming convention
    if naming == 'mixamo':
        arm_bones = {
            'LEFT': [
                'mixamorig:LeftShoulder',
                'mixamorig:LeftArm',
                'mixamorig:LeftForeArm',
                'mixamorig:LeftHand'
            ],
            'RIGHT': [
                'mixamorig:RightShoulder',
                'mixamorig:RightArm',
                'mixamorig:RightForeArm',
                'mixamorig:RightHand'
            ]
        }
    else:
        arm_bones = {
            'LEFT': [
                'shoulder.L',
                'upper_arm.L',
                'forearm.L',
                'hand.L'
            ],
            'RIGHT': [
                'shoulder.R',
                'upper_arm.R',
                'forearm.R',
                'hand.R'
            ]
        }

    # Save current mode and switch to edit mode to access roll
    current_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature_obj.data.edit_bones

    # Collect bone data in edit mode
    bone_data = {}
    for side, bone_names in arm_bones.items():
        for bone_name in bone_names:
            if bone_name in edit_bones:
                bone = edit_bones[bone_name]
                bone_data[bone_name] = {
                    'head': bone.head.copy(),
                    'tail': bone.tail.copy(),
                    'roll': bone.roll,
                    'length': bone.length
                }

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Log each side using collected data
    for side, bone_names in arm_bones.items():
        print(f"\n--- {side} ARM ---")

        for bone_name in bone_names:
            if bone_name in bone_data:
                data = bone_data[bone_name]

                # Get world space positions
                head_world = armature_obj.matrix_world @ data['head']
                tail_world = armature_obj.matrix_world @ data['tail']

                # Calculate direction
                direction = (tail_world - head_world).normalized()

                print(f"\n{bone_name}:")
                print(f"  Head (local):  {data['head']}")
                print(f"  Tail (local):  {data['tail']}")
                print(f"  Head (world):  {head_world}")
                print(f"  Tail (world):  {tail_world}")
                print(f"  Length:        {data['length']:.4f}")
                print(f"  Direction:     {direction}")
                print(f"  Roll (deg):    {math.degrees(data['roll']):.2f}")
            else:
                print(f"\n{bone_name}: NOT FOUND")

    # Restore original mode
    if current_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode=current_mode)

    print(f"\n{'='*80}\n")


# Bone naming conventions matching standard armature naming
BONE_NAMING = {
    'standard': {
        'head_top': 'head',
        'head_center': 'head_mid',
        'neck': 'neck',
        'chin': 'jaw',
        'hips': 'hips',
        'spine_bottom': 'spine_01',
        'spine_mid': 'spine_02',
        'spine_top': 'spine_03',
        'shoulder': {'LEFT': 'shoulder.L', 'RIGHT': 'shoulder.R'},
        'elbow': {'LEFT': 'upper_arm.L', 'RIGHT': 'upper_arm.R'},
        'wrist': {'LEFT': 'forearm.L', 'RIGHT': 'forearm.R'},
        'hand': {'LEFT': 'hand.L', 'RIGHT': 'hand.R'},
        'hip': {'LEFT': 'thigh.L', 'RIGHT': 'thigh.R'},
        'knee': {'LEFT': 'shin.L', 'RIGHT': 'shin.R'},
        'ankle': {'LEFT': 'foot.L', 'RIGHT': 'foot.R'},
        'foot': {'LEFT': 'toe.L', 'RIGHT': 'toe.R'},
        'toe': {'LEFT': 'toe_tip.L', 'RIGHT': 'toe_tip.R'},
        # Fingers
        'thumb': {
            'LEFT': ['thumb_01.L', 'thumb_02.L', 'thumb_03.L'],
            'RIGHT': ['thumb_01.R', 'thumb_02.R', 'thumb_03.R']
        },
        'index': {
            'LEFT': ['index_01.L', 'index_02.L', 'index_03.L'],
            'RIGHT': ['index_01.R', 'index_02.R', 'index_03.R']
        },
        'middle': {
            'LEFT': ['middle_01.L', 'middle_02.L', 'middle_03.L'],
            'RIGHT': ['middle_01.R', 'middle_02.R', 'middle_03.R']
        },
        'ring': {
            'LEFT': ['ring_01.L', 'ring_02.L', 'ring_03.L'],
            'RIGHT': ['ring_01.R', 'ring_02.R', 'ring_03.R']
        },
        'pinky': {
            'LEFT': ['pinky_01.L', 'pinky_02.L', 'pinky_03.L'],
            'RIGHT': ['pinky_01.R', 'pinky_02.R', 'pinky_03.R']
        },
    },
    'mixamo': {
        'head_top': 'mixamorig:Head',
        'head_center': 'mixamorig:HeadTop_End',
        'neck': 'mixamorig:Neck',
        'chin': 'mixamorig:Jaw',
        'hips': 'mixamorig:Hips',
        'spine_bottom': 'mixamorig:Spine',
        'spine_mid': 'mixamorig:Spine1',
        'spine_top': 'mixamorig:Spine2',
        'shoulder': {'LEFT': 'mixamorig:LeftShoulder', 'RIGHT': 'mixamorig:RightShoulder'},
        'elbow': {'LEFT': 'mixamorig:LeftArm', 'RIGHT': 'mixamorig:RightArm'},
        'wrist': {'LEFT': 'mixamorig:LeftForeArm', 'RIGHT': 'mixamorig:RightForeArm'},
        'hand': {'LEFT': 'mixamorig:LeftHand', 'RIGHT': 'mixamorig:RightHand'},
        'hip': {'LEFT': 'mixamorig:LeftUpLeg', 'RIGHT': 'mixamorig:RightUpLeg'},
        'knee': {'LEFT': 'mixamorig:LeftLeg', 'RIGHT': 'mixamorig:RightLeg'},
        'ankle': {'LEFT': 'mixamorig:LeftFoot', 'RIGHT': 'mixamorig:RightFoot'},
        'foot': {'LEFT': 'mixamorig:LeftToeBase', 'RIGHT': 'mixamorig:RightToeBase'},
        'toe': {'LEFT': 'mixamorig:LeftToe_End', 'RIGHT': 'mixamorig:RightToe_End'},
        # Fingers (4 bones each for Mixamo Standard)
        'thumb': {
            'LEFT': ['mixamorig:LeftHandThumb1', 'mixamorig:LeftHandThumb2', 'mixamorig:LeftHandThumb3', 'mixamorig:LeftHandThumb4'],
            'RIGHT': ['mixamorig:RightHandThumb1', 'mixamorig:RightHandThumb2', 'mixamorig:RightHandThumb3', 'mixamorig:RightHandThumb4']
        },
        'index': {
            'LEFT': ['mixamorig:LeftHandIndex1', 'mixamorig:LeftHandIndex2', 'mixamorig:LeftHandIndex3', 'mixamorig:LeftHandIndex4'],
            'RIGHT': ['mixamorig:RightHandIndex1', 'mixamorig:RightHandIndex2', 'mixamorig:RightHandIndex3', 'mixamorig:RightHandIndex4']
        },
        'middle': {
            'LEFT': ['mixamorig:LeftHandMiddle1', 'mixamorig:LeftHandMiddle2', 'mixamorig:LeftHandMiddle3', 'mixamorig:LeftHandMiddle4'],
            'RIGHT': ['mixamorig:RightHandMiddle1', 'mixamorig:RightHandMiddle2', 'mixamorig:RightHandMiddle3', 'mixamorig:RightHandMiddle4']
        },
        'ring': {
            'LEFT': ['mixamorig:LeftHandRing1', 'mixamorig:LeftHandRing2', 'mixamorig:LeftHandRing3', 'mixamorig:LeftHandRing4'],
            'RIGHT': ['mixamorig:RightHandRing1', 'mixamorig:RightHandRing2', 'mixamorig:RightHandRing3', 'mixamorig:RightHandRing4']
        },
        'pinky': {
            'LEFT': ['mixamorig:LeftHandPinky1', 'mixamorig:LeftHandPinky2', 'mixamorig:LeftHandPinky3', 'mixamorig:LeftHandPinky4'],
            'RIGHT': ['mixamorig:RightHandPinky1', 'mixamorig:RightHandPinky2', 'mixamorig:RightHandPinky3', 'mixamorig:RightHandPinky4']
        },
    }
}


def get_bone_name(landmark_id, side='CENTER', naming='standard'):
    """Get standardized bone name for a landmark."""
    naming_dict = BONE_NAMING.get(naming, BONE_NAMING['standard'])
    name_def = naming_dict.get(landmark_id)

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

    elif landmark_id == 'spine_bottom':
        hips = get_landmark_position(landmarks, 'hips', 'CENTER')
        neck = get_landmark_position(landmarks, 'neck', 'CENTER')
        if hips and neck:
            # Spine bottom is 33% of the way from hips to neck
            return hips.lerp(neck, 0.33)
        elif hips:
            # If no neck, estimate upward from hips
            return hips + Vector((0, 0, 0.2))

    elif landmark_id == 'spine_mid':
        hips = get_landmark_position(landmarks, 'hips', 'CENTER')
        neck = get_landmark_position(landmarks, 'neck', 'CENTER')
        spine_bottom = get_landmark_position(landmarks, 'spine_bottom', 'CENTER')
        if spine_bottom and neck:
            # Spine mid is halfway between spine_bottom and neck
            return spine_bottom.lerp(neck, 0.5)
        elif hips and neck:
            # Spine mid is 50% of the way from hips to neck
            return hips.lerp(neck, 0.5)

    elif landmark_id == 'spine_top':
        neck = get_landmark_position(landmarks, 'neck', 'CENTER')
        spine_mid = get_landmark_position(landmarks, 'spine_mid', 'CENTER')
        hips = get_landmark_position(landmarks, 'hips', 'CENTER')
        head_top = get_landmark_position(landmarks, 'head_top', 'CENTER')
        if spine_mid and neck:
            # Spine top is 75% of the way from spine_mid to neck
            return spine_mid.lerp(neck, 0.75)
        elif hips and neck:
            # Spine top is 75% of the way from hips to neck
            return hips.lerp(neck, 0.75)
        elif hips and head_top:
            # If no neck, spine top is 80% from hips to head_top
            return hips.lerp(head_top, 0.80)

    elif landmark_id == 'neck':
        # CRITICAL: Auto-generate neck if not manually picked
        spine_top = get_landmark_position(landmarks, 'spine_top', 'CENTER')
        head_top = get_landmark_position(landmarks, 'head_top', 'CENTER')
        hips = get_landmark_position(landmarks, 'hips', 'CENTER')

        if spine_top and head_top:
            # Neck is 20% of the way from spine_top to head_top
            return spine_top.lerp(head_top, 0.2)
        elif hips and head_top:
            # If no spine_top, neck is 85% from hips to head_top
            return hips.lerp(head_top, 0.85)

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
        hips = get_landmark_position(landmarks, 'hips', 'CENTER')
        if hips:
            # Leg hips are offset from center hips
            offset_x = 0.15 if side == 'LEFT' else -0.15
            return hips + Vector((offset_x, 0, -0.05))

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

    # Finger segment interpolation - auto-generate if not manually picked
    elif '_' in landmark_id and any(f in landmark_id for f in ['thumb', 'index', 'middle', 'ring', 'pinky']):
        # Parse finger name and segment (e.g., "thumb_01" -> "thumb", "01")
        parts = landmark_id.split('_')
        if len(parts) != 2:
            return None

        finger_name = parts[0]
        segment = parts[1]

        wrist = get_landmark_position(landmarks, 'wrist', side)
        hand = get_landmark_position(landmarks, 'hand', side)

        if not (wrist and hand):
            return None

        # Calculate finger base direction and width
        hand_dir = (hand - wrist).normalized()
        hand_width = (hand - wrist).length * 0.3

        # Right vector perpendicular to hand direction
        if side == 'LEFT':
            right_vec = Vector((hand_dir.y, -hand_dir.x, 0)).normalized()
        else:
            right_vec = Vector((-hand_dir.y, hand_dir.x, 0)).normalized()

        # Finger offsets and lengths
        finger_data = {
            'thumb': {'offset': -0.4, 'length': 0.25},
            'index': {'offset': -0.2, 'length': 0.35},
            'middle': {'offset': 0.0, 'length': 0.38},
            'ring': {'offset': 0.2, 'length': 0.35},
            'pinky': {'offset': 0.4, 'length': 0.28},
        }

        if finger_name not in finger_data:
            return None

        data = finger_data[finger_name]
        finger_base = hand + (right_vec * hand_width * data['offset'])
        finger_length = (hand - wrist).length * data['length']
        segment_length = finger_length / 3

        # Calculate position based on segment number
        if segment == '01':
            # Base segment - starts at finger base
            return finger_base
        elif segment == '02':
            # Middle segment - one segment forward
            return finger_base + (hand_dir * segment_length)
        elif segment == '03':
            # Tip segment - two segments forward
            return finger_base + (hand_dir * segment_length * 2)

    return None


def calculate_bone_roll(bone_vector, bone_type='spine'):
    """
    Calculate bone roll to match Mixamo standard orientation.

    Mixamo bones use specific roll angles:
    - Spine bones: 0 degrees (pointing forward)
    - Arm bones: X-axis aligned
    - Leg bones: Z-axis aligned
    """
    bone_dir = bone_vector.normalized()

    if bone_type == 'spine' or bone_type == 'neck' or bone_type == 'head':
        # Spine chain: keep roll at 0 for forward-facing
        return 0.0

    elif bone_type == 'arm_left':
        # Left arm: roll so Y-axis points down (hand opens downward)
        # This matches Mixamo's left arm orientation
        return math.radians(0)  # No roll for proper alignment

    elif bone_type == 'arm_right':
        # Right arm: roll so Y-axis points down (hand opens downward)
        return math.radians(0)  # No roll for proper alignment

    elif bone_type == 'leg':
        # Legs: roll so Y-axis points forward (toes forward)
        return math.radians(0)  # No roll for proper alignment

    else:
        # Default: no roll
        return 0.0


def create_bone_chain(edit_bones, bone_name, head_pos, tail_pos, parent=None, roll=0.0, align_roll=True):
    """Create a single bone in edit mode with proper roll alignment."""
    bone = edit_bones.new(bone_name)
    bone.head = head_pos
    bone.tail = tail_pos

    # Set roll
    if align_roll:
        # Auto-calculate roll based on bone name/type
        if 'Spine' in bone_name or 'spine' in bone_name or 'Hips' in bone_name or 'hips' in bone_name:
            bone.roll = 0.0
        elif 'Neck' in bone_name or 'neck' in bone_name or 'Head' in bone_name or 'head' in bone_name:
            bone.roll = 0.0
        elif 'Left' in bone_name or '.L' in bone_name:
            if 'Leg' in bone_name or 'Foot' in bone_name or 'Toe' in bone_name or 'leg' in bone_name or 'foot' in bone_name:
                bone.roll = 0.0
            else:  # Arms
                bone.roll = 0.0
        elif 'Right' in bone_name or '.R' in bone_name:
            if 'Leg' in bone_name or 'Foot' in bone_name or 'Toe' in bone_name or 'leg' in bone_name or 'foot' in bone_name:
                bone.roll = 0.0
            else:  # Arms
                bone.roll = 0.0
        else:
            bone.roll = roll
    else:
        bone.roll = roll

    if parent:
        bone.parent = parent
        # Use connected bones for better deformation
        if 'Spine' in bone_name or 'Neck' in bone_name or 'Head' in bone_name or \
           'spine' in bone_name or 'neck' in bone_name or 'head' in bone_name:
            bone.use_connect = True

    return bone


def set_t_pose(armature_obj, naming='mixamo'):
    """
    Set the armature to T-pose by rotating arm bones.

    This function rotates the arm bones to be horizontal (T-pose) and applies
    the pose as the rest pose. If arms are already horizontal (from generation
    with checkbox enabled), it skips the rotation to avoid double-transformation.

    Args:
        armature_obj: The armature object to pose
        naming: Naming convention ('standard' or 'mixamo')
    """
    import math
    from mathutils import Vector

    # Get naming dictionary
    naming_dict = BONE_NAMING.get(naming, BONE_NAMING['standard'])

    # Get arm bone names for checking
    if naming == 'mixamo':
        left_arm = 'mixamorig:LeftArm'
        right_arm = 'mixamorig:RightArm'
    else:
        left_arm = 'upper_arm.L'
        right_arm = 'upper_arm.R'

    # === CHECK IF ARMS ARE ALREADY HORIZONTAL ===
    # If the rest pose already has horizontal arms (from horizontal correction),
    # we should skip T-pose application to avoid incorrect rotations
    armature_data = armature_obj.data
    arms_already_horizontal = False

    if left_arm in armature_data.bones and right_arm in armature_data.bones:
        left_bone = armature_data.bones[left_arm]
        right_bone = armature_data.bones[right_arm]

        # Calculate bone directions in local space
        left_dir = (left_bone.tail_local - left_bone.head_local).normalized()
        right_dir = (right_bone.tail_local - right_bone.head_local).normalized()

        # Check if arms are already horizontal (Z component near 0)
        # Threshold: abs(z) < 0.1 means horizontal
        left_horizontal = abs(left_dir.z) < 0.1
        right_horizontal = abs(right_dir.z) < 0.1

        if left_horizontal and right_horizontal:
            arms_already_horizontal = True
            print("\n" + "="*80)
            print("INFO: Arms are already in horizontal T-pose position")
            print(f"  Left arm direction:  {left_dir}")
            print(f"  Right arm direction: {right_dir}")
            print("  Skipping T-pose rotation to avoid double-transformation")
            print("="*80 + "\n")
            return  # Skip T-pose application
        else:
            print("\n" + "="*80)
            print("INFO: Arms need T-pose correction")
            print(f"  Left arm direction:  {left_dir} (horizontal: {left_horizontal})")
            print(f"  Right arm direction: {right_dir} (horizontal: {right_horizontal})")
            print("  Proceeding with T-pose rotation...")
            print("="*80 + "\n")

    # Enter pose mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    pose_bones = armature_obj.pose.bones

    # === LOG INITIAL BONE STATE (BEFORE T-POSE) ===
    print("\n" + "="*80)
    print("BONE STATE BEFORE T-POSE APPLICATION")
    print("="*80)

    # Get armature data for accessing bone properties
    armature_data = armature_obj.data

    for bone in pose_bones:
        # Get corresponding data bone for roll access
        data_bone = armature_data.bones[bone.name]

        print(f"\n{bone.name}:")
        print(f"  Location: {bone.location}")
        print(f"  Rotation (Euler): {bone.rotation_euler}")
        print(f"  Rotation (Quat): {bone.rotation_quaternion}")
        print(f"  Scale: {bone.scale}")
        print(f"  Matrix (local): {bone.matrix}")
        print(f"  Matrix (world): {bone.matrix_channel}")
        if data_bone.parent:
            print(f"  Parent: {data_bone.parent.name}")
        else:
            print(f"  Parent: None (root bone)")
        print(f"  Head (local): {data_bone.head_local}")
        print(f"  Tail (local): {data_bone.tail_local}")
        print(f"  Length: {data_bone.length}")
    print("="*80 + "\n")

    # Get arm bone names
    if naming == 'mixamo':
        # Mixamo naming
        left_shoulder = 'mixamorig:LeftShoulder'
        right_shoulder = 'mixamorig:RightShoulder'
        left_arm = 'mixamorig:LeftArm'
        right_arm = 'mixamorig:RightArm'
        left_forearm = 'mixamorig:LeftForeArm'
        right_forearm = 'mixamorig:RightForeArm'
    else:
        # Standard naming
        left_shoulder = 'shoulder.L'
        right_shoulder = 'shoulder.R'
        left_arm = 'upper_arm.L'
        right_arm = 'upper_arm.R'
        left_forearm = 'forearm.L'
        right_forearm = 'forearm.R'

    # Set T-pose rotations - arms completely horizontal (90° from body)
    # Analysis shows bones are pointing UP instead of horizontal
    # Need to rotate DOWN and OUT using X and Y axes

    # Left arm: rotate outward and down to horizontal position
    if left_shoulder in pose_bones:
        pose_bones[left_shoulder].rotation_mode = 'XYZ'
        # Rotate DOWN (negative X) and OUT (positive Z)
        pose_bones[left_shoulder].rotation_euler = (math.radians(-60), 0, math.radians(15))

    if left_arm in pose_bones:
        pose_bones[left_arm].rotation_mode = 'XYZ'
        # Current: pointing UP (Z=0.941), need to rotate DOWN and LEFT
        # Rotate DOWN (negative X) to bring arm horizontal
        pose_bones[left_arm].rotation_euler = (math.radians(-90), 0, 0)

    if left_forearm in pose_bones:
        pose_bones[left_forearm].rotation_mode = 'XYZ'
        # Keep straight
        pose_bones[left_forearm].rotation_euler = (0, 0, 0)

    # Right arm: rotate outward and down to horizontal position
    if right_shoulder in pose_bones:
        pose_bones[right_shoulder].rotation_mode = 'XYZ'
        # Rotate DOWN (negative X) and OUT (negative Z)
        pose_bones[right_shoulder].rotation_euler = (math.radians(-60), 0, math.radians(-15))

    if right_arm in pose_bones:
        pose_bones[right_arm].rotation_mode = 'XYZ'
        # Current: pointing UP (Z=0.914), need to rotate DOWN and RIGHT
        # Rotate DOWN (negative X) to bring arm horizontal
        pose_bones[right_arm].rotation_euler = (math.radians(-90), 0, 0)

    if right_forearm in pose_bones:
        pose_bones[right_forearm].rotation_mode = 'XYZ'
        # Keep straight
        pose_bones[right_forearm].rotation_euler = (0, 0, 0)

    # Force update to ensure rotations are applied
    bpy.context.view_layer.update()

    # === LOG BONE STATE AFTER T-POSE ROTATION ===
    print("\n" + "="*80)
    print("BONE STATE AFTER T-POSE ROTATION (BEFORE APPLY)")
    print("="*80)
    for bone in pose_bones:
        # Get corresponding data bone
        data_bone = armature_data.bones[bone.name]

        print(f"\n{bone.name}:")
        print(f"  Location: {bone.location}")
        print(f"  Rotation (Euler): {bone.rotation_euler}")
        print(f"  Rotation (Degrees): ({math.degrees(bone.rotation_euler.x):.2f}°, {math.degrees(bone.rotation_euler.y):.2f}°, {math.degrees(bone.rotation_euler.z):.2f}°)")
        print(f"  Rotation (Quat): {bone.rotation_quaternion}")
        print(f"  Scale: {bone.scale}")
        print(f"  Matrix (local): {bone.matrix}")
        print(f"  Matrix (world): {bone.matrix_channel}")
        # Calculate world space direction
        tail_world = bone.matrix @ data_bone.tail_local
        head_world = bone.matrix @ data_bone.head_local
        direction = (tail_world - head_world).normalized()
        print(f"  Bone Direction (world): {direction}")
    print("="*80 + "\n")

    # Apply pose as rest pose WITH mesh deformation
    # This ensures the mesh deforms with the bones
    bpy.ops.pose.select_all(action='SELECT')

    # Apply pose as rest pose
    # This changes the armature's rest position to match the current pose
    bpy.ops.pose.armature_apply(selected=False)

    # Switch to object mode to update mesh deformation
    bpy.ops.object.mode_set(mode='OBJECT')

    # === LOG FINAL BONE STATE AFTER APPLY ===
    print("\n" + "="*80)
    print("FINAL BONE STATE AFTER APPLY AS REST POSE")
    print("="*80)
    for bone in pose_bones:
        # Get corresponding data bone
        data_bone = armature_data.bones[bone.name]

        print(f"\n{bone.name}:")
        print(f"  Location: {bone.location}")
        print(f"  Rotation (Euler): {bone.rotation_euler}")
        print(f"  Rotation (Quat): {bone.rotation_quaternion}")
        print(f"  Scale: {bone.scale}")
        print(f"  Head (local): {data_bone.head_local}")
        print(f"  Tail (local): {data_bone.tail_local}")
    print("="*80 + "\n")

    # === SUMMARY: ARM BONES FOR T-POSE ANALYSIS ===
    print("\n" + "="*80)
    print("T-POSE ANALYSIS SUMMARY - ARM BONES ONLY")
    print("="*80)
    print("\nTarget: Arms should be HORIZONTAL (90° from body, perpendicular to torso)")
    print("Expected: Bone direction in world space should be close to (±1, 0, 0) for horizontal\n")

    arm_bone_names = [
        left_shoulder, right_shoulder,
        left_arm, right_arm,
        left_forearm, right_forearm
    ]

    for bone_name in arm_bone_names:
        if bone_name in pose_bones:
            bone = pose_bones[bone_name]
            # Get corresponding data bone
            data_bone = armature_data.bones[bone_name]

            # Calculate world space direction
            tail_world = bone.matrix @ data_bone.tail_local
            head_world = bone.matrix @ data_bone.head_local
            direction = (tail_world - head_world).normalized()

            print(f"\n{bone.name}:")
            print(f"  World Direction: ({direction.x:.3f}, {direction.y:.3f}, {direction.z:.3f})")
            print(f"  Head Position: ({head_world.x:.3f}, {head_world.y:.3f}, {head_world.z:.3f})")
            print(f"  Tail Position: ({tail_world.x:.3f}, {tail_world.y:.3f}, {tail_world.z:.3f})")

            # Analysis
            if 'Arm' in bone_name or 'arm' in bone_name:
                if abs(direction.x) > 0.9:  # Should be horizontal along X-axis
                    print(f"  ✓ CORRECT: Arm is horizontal (X-direction: {direction.x:.3f})")
                else:
                    print(f"  ✗ ISSUE: Arm not horizontal (X-direction: {direction.x:.3f}, should be close to ±1.0)")
                    print(f"     Suggestion: Adjust rotation to align with X-axis")

    print("="*80 + "\n")

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def generate_armature_from_landmarks(landmarks, mesh_obj, auto_skin=True, context=None,
                                    naming='standard', include_fingers=False, include_foot_details=False):
    """
    Generate an armature from user-selected landmarks.

    Smart Mode: Generates complete body skeleton from minimal landmarks.
    - 6 picks generates: Hips (1), spine (3: Spine/Spine1/Spine2), neck, head, HeadTop_End, arms (8), legs (10) = 25 bones
    - Automatically calculates all intermediate bones
    - Optional: fingers (20 bones per hand = 40 total, 4 bones per finger) - picks finger landmarks or auto-generates
    - Optional: detailed foot bones

    Args:
        landmarks: Collection of SmartRigLandmark property groups
        mesh_obj: Target mesh object
        auto_skin: If True, automatically parent and weight paint
        context: Blender context
        naming: Naming convention ('standard' or 'mixamo')
        include_fingers: If True, generate finger bones (manual picks or auto)
        include_foot_details: If True, generate detailed foot bones

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

    # Create armature with appropriate name
    armature_name = "Mixamo" if naming == 'mixamo' else "SmartRig"
    armature_data = bpy.data.armatures.new(armature_name)
    armature_obj = bpy.data.objects.new(armature_name, armature_data)

    # Link to scene
    context.collection.objects.link(armature_obj)
    armature_obj.location = mesh_obj.location

    # Set as active and enter edit mode
    context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    edit_bones = armature_obj.data.edit_bones
    created_bones = {}

    # === Create Spine Chain (4 bones: Hips → Spine → Spine1 → Spine2) ===
    hips = interpolate_landmark(landmarks, 'hips', 'CENTER')
    spine_bottom = interpolate_landmark(landmarks, 'spine_bottom', 'CENTER')
    spine_mid = interpolate_landmark(landmarks, 'spine_mid', 'CENTER')
    spine_top = interpolate_landmark(landmarks, 'spine_top', 'CENTER')
    neck = interpolate_landmark(landmarks, 'neck', 'CENTER')
    head_top = interpolate_landmark(landmarks, 'head_top', 'CENTER')

    # DEBUG: Print landmark positions
    print(f"\n=== LANDMARK POSITIONS ===")
    print(f"hips: {hips}")
    print(f"spine_bottom: {spine_bottom}")
    print(f"spine_mid: {spine_mid}")
    print(f"spine_top: {spine_top}")
    print(f"neck: {neck}")
    print(f"head_top: {head_top}")
    print(f"========================\n")

    # Get naming dictionary
    naming_dict = BONE_NAMING.get(naming, BONE_NAMING['standard'])

    # ALIGN ALL SPINE BONES VERTICALLY - Use hips X,Y for all center bones
    if hips:
        spine_x = hips.x
        spine_y = hips.y

        # Align all spine positions to be directly above hips (straight vertical line)
        if spine_bottom:
            spine_bottom = Vector((spine_x, spine_y, spine_bottom.z))
        if spine_mid:
            spine_mid = Vector((spine_x, spine_y, spine_mid.z))
        if spine_top:
            spine_top = Vector((spine_x, spine_y, spine_top.z))
        if neck:
            neck = Vector((spine_x, spine_y, neck.z))
        if head_top:
            head_top = Vector((spine_x, spine_y, head_top.z))

    # Root bone (Hips)
    if hips:
        # Hips bone pointing to spine_bottom
        hips_name = naming_dict.get('hips', 'hips')

        if spine_bottom:
            # Hips → Spine_bottom
            hips_bone = create_bone_chain(
                edit_bones, hips_name, hips, spine_bottom
            )
        else:
            # If no spine_bottom, point upward
            hips_tail = hips.copy()
            hips_tail.z += 0.2
            hips_bone = create_bone_chain(
                edit_bones, hips_name, hips, hips_tail
            )

        created_bones['hips'] = hips_bone
        current_parent = hips_bone

        # Spine (first spine bone from spine_bottom to spine_mid)
        if spine_bottom:
            spine_01_name = naming_dict.get('spine_bottom', 'spine_01')

            if spine_mid:
                # Spine_bottom → Spine_mid
                spine_01 = create_bone_chain(
                    edit_bones, spine_01_name, spine_bottom, spine_mid, current_parent
                )
            elif spine_top:
                # Spine_bottom → Spine_top (skip mid)
                spine_01 = create_bone_chain(
                    edit_bones, spine_01_name, spine_bottom, spine_top, current_parent
                )
            else:
                # Spine_bottom → upward
                spine_01_tail = spine_bottom.copy()
                spine_01_tail.z += 0.25
                spine_01 = create_bone_chain(
                    edit_bones, spine_01_name, spine_bottom, spine_01_tail, current_parent
                )

            created_bones['spine_01'] = spine_01
            current_parent = spine_01

        # Spine1 (second spine bone from spine_mid to spine_top)
        if spine_mid:
            spine_02_name = naming_dict.get('spine_mid', 'spine_02')

            if spine_top:
                # Spine_mid → Spine_top
                spine_02 = create_bone_chain(
                    edit_bones, spine_02_name, spine_mid, spine_top, current_parent
                )
            elif neck:
                # Spine_mid → Neck (skip top)
                spine_02 = create_bone_chain(
                    edit_bones, spine_02_name, spine_mid, neck, current_parent
                )
            else:
                # Spine_mid → upward
                spine_02_tail = spine_mid.copy()
                spine_02_tail.z += 0.25
                spine_02 = create_bone_chain(
                    edit_bones, spine_02_name, spine_mid, spine_02_tail, current_parent
                )

            created_bones['spine_02'] = spine_02
            current_parent = spine_02

        # Spine2 (third spine bone from spine_top to neck)
        if spine_top:
            spine_03_name = naming_dict.get('spine_top', 'spine_03')

            if neck:
                # Spine_top → Neck
                spine_03 = create_bone_chain(
                    edit_bones, spine_03_name, spine_top, neck, current_parent
                )
            else:
                # Spine_top → upward
                spine_03_tail = spine_top.copy()
                spine_03_tail.z += 0.2
                spine_03 = create_bone_chain(
                    edit_bones, spine_03_name, spine_top, spine_03_tail, current_parent
                )

            created_bones['spine_03'] = spine_03
            current_parent = spine_03

        # Neck (MUST be parented to Spine2/spine_03)
        # NOTE: Spine2 already points to neck position, so Neck bone starts FROM neck position
        if neck and head_top:
            neck_name = naming_dict.get('neck', 'neck')
            # Neck bone: starts at neck position, ends at head_top position
            neck_bone = create_bone_chain(
                edit_bones, neck_name, neck, head_top, current_parent
            )
            created_bones['neck'] = neck_bone
            current_parent = neck_bone
            print(f"DEBUG: Created Neck bone from {neck} to {head_top}")

        # Head (mixamorig:Head) - starts where Neck ends
        # NOTE: Neck goes from neck→head_top, so Head starts at head_top
        head_center = interpolate_landmark(landmarks, 'head_center', 'CENTER')
        if head_top and head_center:
            # Align head_center vertically with spine
            if hips:
                head_center = Vector((spine_x, spine_y, head_center.z))

            head_name = naming_dict.get('head_top', 'head')
            head_bone = create_bone_chain(
                edit_bones, head_name, head_top, head_center, current_parent
            )
            created_bones['head'] = head_bone
            print(f"DEBUG: Created Head bone from {head_top} to {head_center}")

            # HeadTop_End (child of Head)
            head_end_pos = head_center.copy()
            head_end_pos.z += 0.2  # Extend upward
            head_end_name = naming_dict.get('head_center', 'head_top_end')
            head_end_bone = create_bone_chain(
                edit_bones, head_end_name, head_center, head_end_pos, head_bone
            )
            created_bones['head_end'] = head_end_bone
            print(f"DEBUG: Created HeadTop_End bone from {head_center} to {head_end_pos}")

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

        # === CONDITIONAL HORIZONTAL ARM REST POSE ===
        # Check if user wants T-pose applied automatically
        settings = context.scene.crossrig_settings if context and hasattr(context.scene, 'crossrig_settings') else None
        apply_tpose = settings.smart_rig_auto_tpose if settings else False

        # Only force horizontal arms if T-pose will be applied automatically
        if apply_tpose and shoulder:
            shoulder_z = shoulder.z

            # Force elbow to same Z height as shoulder
            if elbow:
                elbow = Vector((elbow.x, elbow.y, shoulder_z))

            # Force wrist to same Z height as shoulder
            if wrist:
                wrist = Vector((wrist.x, wrist.y, shoulder_z))

            # Force hand to same Z height as shoulder
            if hand:
                hand = Vector((hand.x, hand.y, shoulder_z))

            print(f"\n=== {side} ARM HORIZONTAL CORRECTION (T-POSE ENABLED) ===")
            print(f"Shoulder Z: {shoulder.z if shoulder else 'N/A'}")
            print(f"Corrected Elbow: {elbow}")
            print(f"Corrected Wrist: {wrist}")
            print(f"Corrected Hand: {hand}")
            print(f"=========================================================\n")
        else:
            print(f"\n=== {side} ARM LANDMARKS (NATURAL POSITION) ===")
            print(f"Shoulder: {shoulder}")
            print(f"Elbow: {elbow}")
            print(f"Wrist: {wrist}")
            print(f"Hand: {hand}")
            print(f"==============================================\n")

        side_suffix = '.L' if side == 'LEFT' else '.R'
        arm_parent = created_bones.get('spine_03', created_bones.get('root'))

        # Shoulder bone (always create)
        shoulder_name = naming_dict['shoulder'][side]
        shoulder_bone = create_bone_chain(
            edit_bones, shoulder_name,
            shoulder_attach, shoulder, arm_parent
        )
        created_bones[f'shoulder{side_suffix}'] = shoulder_bone

        # Upper arm (always create if elbow exists or can be interpolated)
        if elbow:
            upper_arm_name = naming_dict['elbow'][side]
            upper_arm = create_bone_chain(
                edit_bones, upper_arm_name,
                shoulder, elbow, shoulder_bone
            )
            created_bones[f'upper_arm{side_suffix}'] = upper_arm

            # Forearm (always create if wrist exists or can be interpolated)
            if wrist:
                forearm_name = naming_dict['wrist'][side]
                forearm = create_bone_chain(
                    edit_bones, forearm_name,
                    elbow, wrist, upper_arm
                )
                created_bones[f'forearm{side_suffix}'] = forearm

                # Hand (always create if it exists or can be interpolated)
                if hand:
                    hand_name = naming_dict['hand'][side]
                    hand_bone = create_bone_chain(
                        edit_bones, hand_name,
                        wrist, hand, forearm
                    )
                    created_bones[f'hand{side_suffix}'] = hand_bone

                    # === Fingers (optional) ===
                    if include_fingers and wrist and hand:
                        # Finger names
                        fingers = ['thumb', 'index', 'middle', 'ring', 'pinky']

                        naming_dict = BONE_NAMING.get(naming, BONE_NAMING['standard'])

                        # Calculate finger base direction
                        hand_dir = (hand - wrist).normalized()
                        hand_width = (hand - wrist).length * 0.3

                        # Right vector perpendicular to hand direction
                        if side == 'LEFT':
                            right_vec = Vector((hand_dir.y, -hand_dir.x, 0)).normalized()
                        else:
                            right_vec = Vector((-hand_dir.y, hand_dir.x, 0)).normalized()

                        for finger_name in fingers:
                            # Check if finger segments were manually picked
                            seg_01_manual = get_landmark_position(landmarks, f"{finger_name}_01", side)
                            seg_02_manual = get_landmark_position(landmarks, f"{finger_name}_02", side)
                            seg_03_manual = get_landmark_position(landmarks, f"{finger_name}_03", side)
                            seg_04_manual = get_landmark_position(landmarks, f"{finger_name}_04", side)

                            # If manually picked, use those positions
                            # Only force Z height if T-pose is enabled (arms are horizontal)
                            if seg_01_manual:
                                if apply_tpose:
                                    seg_01 = Vector((seg_01_manual.x, seg_01_manual.y, hand.z))
                                else:
                                    seg_01 = seg_01_manual
                            else:
                                # Auto-generate using corrected hand position
                                finger_data = {
                                    'thumb': {'offset': -0.4, 'length': 0.25},
                                    'index': {'offset': -0.2, 'length': 0.35},
                                    'middle': {'offset': 0.0, 'length': 0.38},
                                    'ring': {'offset': 0.2, 'length': 0.35},
                                    'pinky': {'offset': 0.4, 'length': 0.28},
                                }
                                data = finger_data[finger_name]
                                seg_01 = hand + (right_vec * hand_width * data['offset'])

                            if seg_02_manual:
                                if apply_tpose:
                                    seg_02 = Vector((seg_02_manual.x, seg_02_manual.y, hand.z))
                                else:
                                    seg_02 = seg_02_manual
                            else:
                                # Auto-generate
                                finger_data = {
                                    'thumb': {'offset': -0.4, 'length': 0.25},
                                    'index': {'offset': -0.2, 'length': 0.35},
                                    'middle': {'offset': 0.0, 'length': 0.38},
                                    'ring': {'offset': 0.2, 'length': 0.35},
                                    'pinky': {'offset': 0.4, 'length': 0.28},
                                }
                                data = finger_data[finger_name]
                                finger_base = hand + (right_vec * hand_width * data['offset'])
                                finger_length = (hand - wrist).length * data['length']
                                segment_length = finger_length / 3
                                seg_02 = finger_base + (hand_dir * segment_length)

                            if seg_03_manual:
                                if apply_tpose:
                                    seg_03 = Vector((seg_03_manual.x, seg_03_manual.y, hand.z))
                                else:
                                    seg_03 = seg_03_manual
                            else:
                                # Auto-generate
                                finger_data = {
                                    'thumb': {'offset': -0.4, 'length': 0.25},
                                    'index': {'offset': -0.2, 'length': 0.35},
                                    'middle': {'offset': 0.0, 'length': 0.38},
                                    'ring': {'offset': 0.2, 'length': 0.35},
                                    'pinky': {'offset': 0.4, 'length': 0.28},
                                }
                                data = finger_data[finger_name]
                                finger_base = hand + (right_vec * hand_width * data['offset'])
                                finger_length = (hand - wrist).length * data['length']
                                segment_length = finger_length / 3
                                seg_03 = finger_base + (hand_dir * segment_length * 2)

                            if seg_04_manual:
                                if apply_tpose:
                                    seg_04 = Vector((seg_04_manual.x, seg_04_manual.y, hand.z))
                                else:
                                    seg_04 = seg_04_manual
                            else:
                                seg_04 = None

                            # Skip finger if base segment can't be determined
                            if not seg_01:
                                continue

                            # Get finger bone names from naming dict
                            finger_bones = naming_dict[finger_name][side]
                            finger_parent = hand_bone

                            # Create bone 1 (base segment)
                            if seg_02:
                                bone_1 = create_bone_chain(
                                    edit_bones, finger_bones[0],
                                    seg_01, seg_02, finger_parent
                                )
                                created_bones[finger_bones[0]] = bone_1
                                finger_parent = bone_1

                                # Create bone 2 (middle segment)
                                if seg_03:
                                    bone_2 = create_bone_chain(
                                        edit_bones, finger_bones[1],
                                        seg_02, seg_03, finger_parent
                                    )
                                    created_bones[finger_bones[1]] = bone_2
                                    finger_parent = bone_2

                                    # Create bone 3 (ring segment)
                                    # If seg_04 not picked, auto-calculate tip position
                                    if not seg_04:
                                        tip_dir = (seg_03 - seg_02).normalized()
                                        tip_length = (seg_02 - seg_01).length * 0.8  # Slightly shorter
                                        seg_04 = seg_03 + (tip_dir * tip_length)

                                    bone_3 = create_bone_chain(
                                        edit_bones, finger_bones[2],
                                        seg_03, seg_04, finger_parent
                                    )
                                    created_bones[finger_bones[2]] = bone_3
                                    finger_parent = bone_3

                                    # Create bone 4 (tip segment - end bone)
                                    # Calculate tip end position beyond seg_04
                                    tip_dir = (seg_04 - seg_03).normalized()
                                    tip_length = (seg_04 - seg_03).length * 0.5  # Short end bone
                                    tip_end_pos = seg_04 + (tip_dir * tip_length)

                                    bone_4 = create_bone_chain(
                                        edit_bones, finger_bones[3],
                                        seg_04, tip_end_pos, finger_parent
                                    )
                                    created_bones[finger_bones[3]] = bone_4

    # === Create Legs (ALWAYS generate all leg bones) ===
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
        leg_parent = created_bones.get('hips')

        # Thigh (always create if knee exists or can be interpolated)
        if knee:
            thigh_name = naming_dict['hip'][side]
            thigh = create_bone_chain(
                edit_bones, thigh_name,
                hip, knee, leg_parent
            )
            created_bones[f'thigh{side_suffix}'] = thigh

            # Shin (always create if ankle exists or can be interpolated)
            if ankle:
                shin_name = naming_dict['knee'][side]
                shin = create_bone_chain(
                    edit_bones, shin_name,
                    knee, ankle, thigh
                )
                created_bones[f'shin{side_suffix}'] = shin

                # Foot (always create if it exists or can be interpolated)
                if foot:
                    foot_name = naming_dict['ankle'][side]
                    foot_bone = create_bone_chain(
                        edit_bones, foot_name,
                        ankle, foot, shin
                    )
                    created_bones[f'foot{side_suffix}'] = foot_bone

                    # Toe (always create if it exists or can be interpolated)
                    if toe:
                        toe_name = naming_dict['foot'][side]
                        toe_bone = create_bone_chain(
                            edit_bones, toe_name,
                            foot, toe, foot_bone
                        )
                        created_bones[f'toe{side_suffix}'] = toe_bone

                        # Toe_End (required for Mixamo animations)
                        # Calculate toe end position (extend beyond toe tip)
                        toe_direction = (toe - foot).normalized()
                        toe_end_pos = toe + (toe_direction * (toe - foot).length * 0.5)

                        toe_end_name = naming_dict['toe'][side]
                        toe_end_bone = create_bone_chain(
                            edit_bones, toe_end_name,
                            toe, toe_end_pos, toe_bone
                        )
                        created_bones[f'toe_end{side_suffix}'] = toe_end_bone

    # === CRITICAL: Set bone rolls to match Mixamo standard orientation ===
    # Manual roll assignment based on analysis of perfect Mixamo armature
    bpy.ops.object.mode_set(mode='EDIT')

    import math

    # Roll angles for different bone types (in radians)
    # These values verified by user testing with animations
    MIXAMO_ROLLS = {
        # Spine bones: aligned with Y-forward, Z-up
        'spine': 0.0,

        # Arm bones - VERIFIED VALUES FROM USER TESTING
        'right_shoulder': math.radians(-102),  # -102° verified with animations
        'right_upper_arm': math.radians(90),   # All right hand bones = 90°
        'right_forearm': math.radians(90),     # All right hand bones = 90°
        'right_hand': math.radians(90),        # All right hand bones = 90°

        'left_shoulder': math.radians(102),    # 102° verified with animations
        'left_upper_arm': math.radians(90),    # All left hand bones = 90°
        'left_forearm': math.radians(90),      # All left hand bones = 90°
        'left_hand': math.radians(90),         # All left hand bones = 90°

        # Finger bones - all 90° to match hand bones
        # Right hand fingers
        'right_thumb': math.radians(90),
        'right_index': math.radians(90),
        'right_middle': math.radians(90),
        'right_ring': math.radians(90),
        'right_pinky': math.radians(90),

        # Left hand fingers
        'left_thumb': math.radians(90),
        'left_index': math.radians(90),
        'left_middle': math.radians(90),
        'left_ring': math.radians(90),
        'left_pinky': math.radians(90),

        # Leg bones - ALL 180° VERIFIED BY USER
        'right_thigh': math.radians(180),
        'right_shin': math.radians(180),
        'right_foot': math.radians(180),
        'right_toe': math.radians(180),

        'left_thigh': math.radians(180),
        'left_shin': math.radians(180),
        'left_foot': math.radians(180),
        'left_toe': math.radians(180),
    }

    # Apply rolls to each bone
    for bone in edit_bones:
        bone_name_lower = bone.name.lower()

        # Spine, neck, head
        if any(x in bone_name_lower for x in ['hips', 'spine', 'neck', 'head']):
            bone.roll = MIXAMO_ROLLS['spine']

        # Right arm
        elif 'rightshoulder' in bone_name_lower or 'shoulder.r' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_shoulder']
        elif 'rightarm' in bone_name_lower and 'forearm' not in bone_name_lower or 'upper_arm.r' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_upper_arm']
        elif 'rightforearm' in bone_name_lower or 'forearm.r' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_forearm']
        elif 'righthand' in bone_name_lower and 'thumb' not in bone_name_lower and 'index' not in bone_name_lower and \
             'middle' not in bone_name_lower and 'ring' not in bone_name_lower and 'pinky' not in bone_name_lower or 'hand.r' == bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_hand']

        # Left arm
        elif 'leftshoulder' in bone_name_lower or 'shoulder.l' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_shoulder']
        elif 'leftarm' in bone_name_lower and 'forearm' not in bone_name_lower or 'upper_arm.l' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_upper_arm']
        elif 'leftforearm' in bone_name_lower or 'forearm.l' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_forearm']
        elif 'lefthand' in bone_name_lower and 'thumb' not in bone_name_lower and 'index' not in bone_name_lower and \
             'middle' not in bone_name_lower and 'ring' not in bone_name_lower and 'pinky' not in bone_name_lower or 'hand.l' == bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_hand']

        # Right fingers
        elif 'righthand' in bone_name_lower and 'thumb' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_thumb']
        elif 'righthand' in bone_name_lower and 'index' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_index']
        elif 'righthand' in bone_name_lower and 'middle' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_middle']
        elif 'righthand' in bone_name_lower and 'ring' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_ring']
        elif 'righthand' in bone_name_lower and 'pinky' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_pinky']

        # Left fingers
        elif 'lefthand' in bone_name_lower and 'thumb' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_thumb']
        elif 'lefthand' in bone_name_lower and 'index' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_index']
        elif 'lefthand' in bone_name_lower and 'middle' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_middle']
        elif 'lefthand' in bone_name_lower and 'ring' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_ring']
        elif 'lefthand' in bone_name_lower and 'pinky' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_pinky']

        # Right leg
        elif 'rightupleg' in bone_name_lower or 'thigh.r' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_thigh']
        elif 'rightleg' in bone_name_lower and 'upleg' not in bone_name_lower or 'shin.r' in bone_name_lower or 'calf.r' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_shin']
        elif 'rightfoot' in bone_name_lower and 'toe' not in bone_name_lower or 'foot.r' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_foot']
        elif 'righttoe' in bone_name_lower or 'toe.r' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['right_toe']

        # Left leg
        elif 'leftupleg' in bone_name_lower or 'thigh.l' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_thigh']
        elif 'leftleg' in bone_name_lower and 'upleg' not in bone_name_lower or 'shin.l' in bone_name_lower or 'calf.l' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_shin']
        elif 'leftfoot' in bone_name_lower and 'toe' not in bone_name_lower or 'foot.l' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_foot']
        elif 'lefttoe' in bone_name_lower or 'toe.l' in bone_name_lower:
            bone.roll = MIXAMO_ROLLS['left_toe']

    print("\n" + "="*80)
    print("BONE ROLL CORRECTION APPLIED - Mixamo Standard Orientation")
    print("="*80)
    for bone in edit_bones:
        print(f"{bone.name}: roll = {math.degrees(bone.roll):.2f}°")
    print("="*80 + "\n")

    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # === LOG ARM BONES BEFORE T-POSE ===
    print("\n" + "="*80)
    print("LOGGING ARM BONE POSITIONS - BEFORE T-POSE")
    print("="*80)
    log_arm_bone_positions(armature_obj, naming, stage='BEFORE')

    # === Set T-Pose automatically (if enabled) ===
    # Check if user wants to apply T-pose
    settings = context.scene.crossrig_settings if context and hasattr(context.scene, 'crossrig_settings') else None
    apply_tpose = settings.smart_rig_auto_tpose if settings else False

    if apply_tpose:
        try:
            print("INFO: Applying T-pose to armature...")
            set_t_pose(armature_obj, naming)

            # === LOG ARM BONES AFTER T-POSE ===
            print("\n" + "="*80)
            print("LOGGING ARM BONE POSITIONS - AFTER T-POSE")
            print("="*80)
            log_arm_bone_positions(armature_obj, naming, stage='AFTER')
        except Exception as e:
            print(f"Warning: Failed to set T-pose: {e}")
    else:
        print("INFO: T-pose application disabled - use 'Apply T-Pose' button if needed")

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
