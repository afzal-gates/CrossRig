"""
Bone Repositioning Operators for CrossRig.

Allows repositioning existing armature bones by clicking on mesh surfaces.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from mathutils import Vector
from bpy_extras import view3d_utils


def group_bones_by_category(bone_names):
    """
    Group bones into logical categories based on naming patterns.

    Supports multiple naming conventions:
    - Mixamo (mixamorig:BoneName)
    - Rigify (DEF-, MCH-, ORG- prefixes)
    - Standard humanoid naming
    - UE4/UE5 naming

    Returns dict of {category_name: [bone_names]}
    """
    groups = {
        'Spine & Torso': [],
        'Head & Neck': [],
        'Left Arm': [],
        'Right Arm': [],
        'Left Hand': [],
        'Right Hand': [],
        'Left Leg': [],
        'Right Leg': [],
        'Left Foot': [],
        'Right Foot': [],
        'Other': []
    }

    for bone_name in bone_names:
        bone_lower = bone_name.lower()

        # Remove common prefixes for matching
        clean_name = bone_name
        for prefix in ['mixamorig:', 'def-', 'mch-', 'org-', 'ik-', 'fk-']:
            if bone_lower.startswith(prefix.lower()):
                clean_name = bone_name[len(prefix):]
                break

        clean_lower = clean_name.lower()

        # Spine & Torso
        if any(keyword in clean_lower for keyword in ['spine', 'pelvis', 'hips', 'chest', 'torso', 'root']):
            groups['Spine & Torso'].append(bone_name)

        # Head & Neck
        elif any(keyword in clean_lower for keyword in ['head', 'neck', 'jaw', 'chin', 'eye', 'face']):
            groups['Head & Neck'].append(bone_name)

        # Left Arm (upper arm, shoulder, clavicle)
        elif any(keyword in clean_lower for keyword in ['leftshoulder', 'leftarm', 'leftforearm', 'leftelbow', 'leftclavicle', 'l_shoulder', 'l_upperarm', 'l_forearm', 'shoulder.l', 'upper_arm.l', 'forearm.l', 'arm.l']):
            groups['Left Arm'].append(bone_name)

        # Right Arm
        elif any(keyword in clean_lower for keyword in ['rightshoulder', 'rightarm', 'rightforearm', 'rightelbow', 'rightclavicle', 'r_shoulder', 'r_upperarm', 'r_forearm', 'shoulder.r', 'upper_arm.r', 'forearm.r', 'arm.r']):
            groups['Right Arm'].append(bone_name)

        # Left Hand (hand + fingers)
        elif any(keyword in clean_lower for keyword in ['lefthand', 'l_hand', 'hand.l']) or \
             (('left' in clean_lower or 'l_' in clean_lower or '.l' in clean_lower) and
              any(finger in clean_lower for finger in ['thumb', 'index', 'middle', 'ring', 'pinky', 'finger'])):
            groups['Left Hand'].append(bone_name)

        # Right Hand (hand + fingers)
        elif any(keyword in clean_lower for keyword in ['righthand', 'r_hand', 'hand.r']) or \
             (('right' in clean_lower or 'r_' in clean_lower or '.r' in clean_lower) and
              any(finger in clean_lower for finger in ['thumb', 'index', 'middle', 'ring', 'pinky', 'finger'])):
            groups['Right Hand'].append(bone_name)

        # Left Leg (thigh, shin, knee)
        elif any(keyword in clean_lower for keyword in ['leftupleg', 'leftleg', 'leftthigh', 'leftshin', 'leftknee', 'l_thigh', 'l_leg', 'l_shin', 'thigh.l', 'shin.l', 'leg.l']):
            groups['Left Leg'].append(bone_name)

        # Right Leg
        elif any(keyword in clean_lower for keyword in ['rightupleg', 'rightleg', 'rightthigh', 'rightshin', 'rightknee', 'r_thigh', 'r_leg', 'r_shin', 'thigh.r', 'shin.r', 'leg.r']):
            groups['Right Leg'].append(bone_name)

        # Left Foot (foot, ankle, toes)
        elif any(keyword in clean_lower for keyword in ['leftfoot', 'leftankle', 'lefttoe', 'l_foot', 'l_ankle', 'l_toe', 'foot.l', 'ankle.l', 'toe.l']):
            groups['Left Foot'].append(bone_name)

        # Right Foot
        elif any(keyword in clean_lower for keyword in ['rightfoot', 'rightankle', 'righttoe', 'r_foot', 'r_ankle', 'r_toe', 'foot.r', 'ankle.r', 'toe.r']):
            groups['Right Foot'].append(bone_name)

        # Everything else
        else:
            groups['Other'].append(bone_name)

    # Remove empty groups
    return {k: sorted(v) for k, v in groups.items() if v}


def get_group_icon(group_name):
    """Get appropriate Blender icon for bone group."""
    icons = {
        'Spine & Torso': 'BONE_DATA',
        'Head & Neck': 'USER',
        'Left Arm': 'FORWARD',
        'Right Arm': 'BACK',
        'Left Hand': 'HAND',
        'Right Hand': 'HAND',
        'Left Leg': 'PROP_ON',
        'Right Leg': 'PROP_ON',
        'Left Foot': 'TRACKING',
        'Right Foot': 'TRACKING',
        'Other': 'QUESTION'
    }
    return icons.get(group_name, 'DOT')


def get_mirrored_bone_name(bone_name):
    """
    Get the mirrored bone name (Left ↔ Right).

    Supports multiple naming conventions:
    - Mixamo: LeftHand ↔ RightHand
    - Rigify: hand.L ↔ hand.R
    - Standard: l_hand ↔ r_hand, hand_L ↔ hand_R

    Returns mirrored bone name or None if no mirror pattern detected.
    """
    # Mixamo style: Left/Right prefix
    if 'Left' in bone_name:
        return bone_name.replace('Left', 'Right')
    elif 'Right' in bone_name:
        return bone_name.replace('Right', 'Left')

    # Case-insensitive versions
    elif 'left' in bone_name.lower():
        # Find exact casing
        if 'left' in bone_name:
            return bone_name.replace('left', 'right')
        elif 'LEFT' in bone_name:
            return bone_name.replace('LEFT', 'RIGHT')
    elif 'right' in bone_name.lower():
        if 'right' in bone_name:
            return bone_name.replace('right', 'left')
        elif 'RIGHT' in bone_name:
            return bone_name.replace('RIGHT', 'LEFT')

    # Rigify style: .L ↔ .R suffix
    elif bone_name.endswith('.L'):
        return bone_name[:-2] + '.R'
    elif bone_name.endswith('.R'):
        return bone_name[:-2] + '.L'

    # Underscore style: _L ↔ _R, _l ↔ _r
    elif bone_name.endswith('_L'):
        return bone_name[:-2] + '_R'
    elif bone_name.endswith('_R'):
        return bone_name[:-2] + '_L'
    elif bone_name.endswith('_l'):
        return bone_name[:-2] + '_r'
    elif bone_name.endswith('_r'):
        return bone_name[:-2] + '_l'

    # Prefix style: L_ ↔ R_, l_ ↔ r_
    elif bone_name.startswith('L_'):
        return 'R_' + bone_name[2:]
    elif bone_name.startswith('R_'):
        return 'L_' + bone_name[2:]
    elif bone_name.startswith('l_'):
        return 'r_' + bone_name[2:]
    elif bone_name.startswith('r_'):
        return 'l_' + bone_name[2:]

    # No mirror pattern found
    return None


def detect_hand_finger_hierarchy(armature_obj, side='LEFT'):
    """
    Detect hand and finger bones hierarchy similar to Mixamo/AccuRig.

    Returns dict with structure:
    {
        'hand': 'bone_name',
        'fingers': {
            'thumb': ['thumb1', 'thumb2', 'thumb3'],
            'index': ['index1', 'index2', 'index3'],
            'middle': ['middle1', 'middle2', 'middle3'],
            'ring': ['ring1', 'ring2', 'ring3'],
            'pinky': ['pinky1', 'pinky2', 'pinky3']
        }
    }
    """
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return None

    result = {'hand': None, 'fingers': {}}
    side_lower = side.lower()

    # Side keywords
    side_keywords = {
        'LEFT': ['left', 'l_', '.l', '_l'],
        'RIGHT': ['right', 'r_', '.r', '_r']
    }[side]

    # Find hand bone
    for bone in armature_obj.data.bones:
        bone_lower = bone.name.lower()

        # Check if it's a hand bone for the correct side
        if any(kw in bone_lower for kw in side_keywords):
            if 'hand' in bone_lower and not any(finger in bone_lower for finger in ['thumb', 'index', 'middle', 'ring', 'pinky']):
                result['hand'] = bone.name
                break

    if not result['hand']:
        return None

    # Find finger bones (children and descendants of hand)
    hand_bone = armature_obj.data.bones[result['hand']]

    finger_names = {
        'thumb': [],
        'index': [],
        'middle': [],
        'ring': [],
        'pinky': []
    }

    # Collect all descendants of hand bone
    def collect_descendants(bone):
        descendants = []
        for child in bone.children:
            descendants.append(child)
            descendants.extend(collect_descendants(child))
        return descendants

    all_descendants = collect_descendants(hand_bone)

    # Categorize by finger type and sort by hierarchy level
    for bone in all_descendants:
        bone_lower = bone.name.lower()

        # Detect finger type
        finger_type = None
        if 'thumb' in bone_lower:
            finger_type = 'thumb'
        elif 'index' in bone_lower:
            finger_type = 'index'
        elif 'middle' in bone_lower:
            finger_type = 'middle'
        elif 'ring' in bone_lower:
            finger_type = 'ring'
        elif 'pinky' in bone_lower or 'little' in bone_lower:
            finger_type = 'pinky'

        if finger_type:
            finger_names[finger_type].append(bone.name)

    # Sort finger bones by hierarchy (parent to child)
    for finger_type in finger_names:
        if finger_names[finger_type]:
            # Sort by getting bone hierarchy depth
            def get_hierarchy_depth(bone_name):
                bone = armature_obj.data.bones[bone_name]
                depth = 0
                current = bone
                while current.parent and current.parent.name in [result['hand']] + finger_names[finger_type]:
                    depth += 1
                    current = current.parent
                return depth

            finger_names[finger_type].sort(key=get_hierarchy_depth)

    result['fingers'] = {k: v for k, v in finger_names.items() if v}

    return result


def raycast_center_of_mass(mesh_obj, surface_pos, direction):
    """
    Raycast from front and back to find center of mass inside mesh.

    Args:
        mesh_obj: The mesh object
        surface_pos: Position on mesh surface
        direction: Ray direction (usually +Y or -Y for front/back)

    Returns:
        Center position between front and back surfaces
    """
    import bpy
    from mathutils import Vector

    # Create a depsgraph for ray casting
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh_eval = mesh_obj.evaluated_get(depsgraph)

    # Cast ray from front
    front_hit, front_loc, front_normal, front_index = mesh_eval.ray_cast(surface_pos, direction, distance=10.0)

    # Cast ray from back (opposite direction)
    back_direction = -direction
    back_hit, back_loc, back_normal, back_index = mesh_eval.ray_cast(surface_pos, back_direction, distance=10.0)

    # Calculate center of mass between front and back
    if front_hit and back_hit:
        return (front_loc + back_loc) / 2.0
    elif front_hit:
        # Only front hit, offset inward slightly
        return front_loc - direction * 0.05
    elif back_hit:
        # Only back hit, offset inward slightly
        return back_loc + direction * 0.05
    else:
        # No hits, return original position
        return surface_pos


def detect_body_landmarks(mesh_obj):
    """
    Automatically detect body landmarks INSIDE mesh using center-of-mass calculation.
    Similar to Mixamo/AccuRig auto-detection.

    Returns dict with landmark positions:
    {
        'head': Vector,
        'neck': Vector,
        'chest': Vector,
        'hips': Vector,
        'left_shoulder': Vector,
        'right_shoulder': Vector,
        'left_hand': Vector,
        'right_hand': Vector,
        'left_foot': Vector,
        'right_foot': Vector
    }
    """
    if not mesh_obj or mesh_obj.type != 'MESH':
        return None

    import bmesh
    from mathutils import Vector

    # Get mesh data in world space
    mesh = mesh_obj.data
    matrix_world = mesh_obj.matrix_world

    # Create bmesh for vertex access
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    # Get all vertex positions in world space
    vertices = [matrix_world @ v.co for v in bm.verts]

    if not vertices:
        bm.free()
        return None

    # Calculate bounding box
    min_x = min(v.x for v in vertices)
    max_x = max(v.x for v in vertices)
    min_y = min(v.y for v in vertices)
    max_y = max(v.y for v in vertices)
    min_z = min(v.z for v in vertices)
    max_z = max(v.z for v in vertices)

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    width = max_x - min_x
    height = max_z - min_z
    depth = max_y - min_y

    # Ray direction for front/back casting (usually Y-axis in Blender)
    ray_direction = Vector((0, 1, 0))

    # Detect landmarks based on bounding box regions, then find center of mass
    landmarks = {}

    # HEAD: Top 10% of mesh, center X
    head_z = max_z - (height * 0.05)
    head_verts = [v for v in vertices if v.z > head_z and abs(v.x - center_x) < width * 0.15]
    if head_verts:
        surface_avg = sum(head_verts, Vector()) / len(head_verts)
        landmarks['head'] = raycast_center_of_mass(mesh_obj, surface_avg, ray_direction)

    # NECK: 80-85% height, center X
    neck_z = min_z + (height * 0.82)
    neck_verts = [v for v in vertices if abs(v.z - neck_z) < height * 0.05 and abs(v.x - center_x) < width * 0.12]
    if neck_verts:
        surface_avg = sum(neck_verts, Vector()) / len(neck_verts)
        landmarks['neck'] = raycast_center_of_mass(mesh_obj, surface_avg, ray_direction)

    # CHEST: 65-70% height, center X
    chest_z = min_z + (height * 0.67)
    chest_verts = [v for v in vertices if abs(v.z - chest_z) < height * 0.05 and abs(v.x - center_x) < width * 0.15]
    if chest_verts:
        surface_avg = sum(chest_verts, Vector()) / len(chest_verts)
        landmarks['chest'] = raycast_center_of_mass(mesh_obj, surface_avg, ray_direction)

    # HIPS: 45-50% height, center X
    hips_z = min_z + (height * 0.47)
    hips_verts = [v for v in vertices if abs(v.z - hips_z) < height * 0.05 and abs(v.x - center_x) < width * 0.2]
    if hips_verts:
        surface_avg = sum(hips_verts, Vector()) / len(hips_verts)
        landmarks['hips'] = raycast_center_of_mass(mesh_obj, surface_avg, ray_direction)

    # LEFT SHOULDER: 70-75% height, right side (positive X in Blender)
    shoulder_z = min_z + (height * 0.72)
    left_shoulder_verts = [v for v in vertices if abs(v.z - shoulder_z) < height * 0.05 and v.x > center_x + width * 0.15]
    if left_shoulder_verts:
        surface_avg = sum(left_shoulder_verts, Vector()) / len(left_shoulder_verts)
        landmarks['left_shoulder'] = raycast_center_of_mass(mesh_obj, surface_avg, ray_direction)

    # RIGHT SHOULDER: 70-75% height, left side (negative X)
    right_shoulder_verts = [v for v in vertices if abs(v.z - shoulder_z) < height * 0.05 and v.x < center_x - width * 0.15]
    if right_shoulder_verts:
        surface_avg = sum(right_shoulder_verts, Vector()) / len(right_shoulder_verts)
        landmarks['right_shoulder'] = raycast_center_of_mass(mesh_obj, surface_avg, ray_direction)

    # LEFT HAND: 40-50% height, extreme right X
    hand_z = min_z + (height * 0.45)
    left_hand_verts = [v for v in vertices if abs(v.z - hand_z) < height * 0.15 and v.x > max_x - width * 0.15]
    if left_hand_verts:
        surface_avg = sum(left_hand_verts, Vector()) / len(left_hand_verts)
        landmarks['left_hand'] = raycast_center_of_mass(mesh_obj, surface_avg, ray_direction)

    # RIGHT HAND: 40-50% height, extreme left X
    right_hand_verts = [v for v in vertices if abs(v.z - hand_z) < height * 0.15 and v.x < min_x + width * 0.15]
    if right_hand_verts:
        surface_avg = sum(right_hand_verts, Vector()) / len(right_hand_verts)
        landmarks['right_hand'] = raycast_center_of_mass(mesh_obj, surface_avg, ray_direction)

    # LEFT FOOT: Bottom 10%, right side
    foot_z = min_z + (height * 0.05)
    left_foot_verts = [v for v in vertices if v.z < foot_z and v.x > center_x + width * 0.05]
    if left_foot_verts:
        surface_avg = sum(left_foot_verts, Vector()) / len(left_foot_verts)
        landmarks['left_foot'] = raycast_center_of_mass(mesh_obj, surface_avg, ray_direction)

    # RIGHT FOOT: Bottom 10%, left side
    right_foot_verts = [v for v in vertices if v.z < foot_z and v.x < center_x - width * 0.05]
    if right_foot_verts:
        surface_avg = sum(right_foot_verts, Vector()) / len(right_foot_verts)
        landmarks['right_foot'] = raycast_center_of_mass(mesh_obj, surface_avg, ray_direction)

    bm.free()
    return landmarks


class CROSSRIG_OT_SmartMapArmatureToMesh(Operator):
    """Smart map entire armature to body mesh (Mixamo/AccuRig style)"""
    bl_idname = "crossrig.smart_map_armature_to_mesh"
    bl_label = "Smart Map Armature to Mesh"
    bl_description = "Automatically detect body landmarks and position all bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings
        armature_obj = settings.bone_reposition_armature
        mesh_obj = settings.bone_reposition_mesh

        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature object")
            return {'CANCELLED'}

        if not mesh_obj or mesh_obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Detect body landmarks
        self.report({'INFO'}, "Detecting body landmarks on mesh...")
        landmarks = detect_body_landmarks(mesh_obj)

        if not landmarks or len(landmarks) < 5:
            self.report({'ERROR'}, "Could not detect enough body landmarks on mesh")
            return {'CANCELLED'}

        self.report({'INFO'}, f"✓ Detected {len(landmarks)} body landmarks: {', '.join(landmarks.keys())}")

        # Here you would implement the actual bone positioning
        # For now, just report what was detected
        msg = f"✓ Auto-detected body landmarks:\n"
        for landmark, position in landmarks.items():
            msg += f"  • {landmark.replace('_', ' ').title()}: {position}\n"

        self.report({'INFO'}, msg)

        return {'FINISHED'}


class CROSSRIG_OT_SmartMapHandFingers(Operator):
    """Smart map hand with all finger bones (Mixamo/AccuRig style)"""
    bl_idname = "crossrig.smart_map_hand_fingers"
    bl_label = "Smart Map Hand & Fingers"
    bl_description = "Automatically detect and prepare hand-finger hierarchy for repositioning"
    bl_options = {'REGISTER', 'UNDO'}

    side: StringProperty(
        name="Side",
        description="Which hand to map",
        default="LEFT"
    )

    def execute(self, context):
        settings = context.scene.crossrig_settings
        armature_obj = settings.bone_reposition_armature

        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature object first")
            return {'CANCELLED'}

        # Detect hand-finger hierarchy
        hierarchy = detect_hand_finger_hierarchy(armature_obj, self.side)

        if not hierarchy or not hierarchy['hand']:
            self.report({'ERROR'}, f"Could not detect {self.side.lower()} hand bone")
            return {'CANCELLED'}

        # Count detected bones
        finger_count = sum(len(bones) for bones in hierarchy['fingers'].values())

        # Build report message
        fingers_found = list(hierarchy['fingers'].keys())
        msg = f"✓ Detected: {hierarchy['hand']} + {len(fingers_found)} fingers ({finger_count} bones)"

        self.report({'INFO'}, msg)

        return {'FINISHED'}


class CROSSRIG_OT_StartBoneRepositionMode(Operator):
    """Start bone repositioning mode"""
    bl_idname = "crossrig.start_bone_reposition_mode"
    bl_label = "Start Bone Reposition Mode"
    bl_description = "Enter bone repositioning mode to adjust bone positions by clicking mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings

        armature_obj = settings.bone_reposition_armature
        mesh_obj = settings.bone_reposition_mesh

        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature object")
            return {'CANCELLED'}

        if not mesh_obj or mesh_obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Enter bone repositioning mode
        settings.bone_reposition_active = True

        self.report({'INFO'}, f"Bone reposition mode active for: {armature_obj.name}")
        return {'FINISHED'}


class CROSSRIG_OT_RepositionBone(Operator):
    """Click on mesh to reposition this bone"""
    bl_idname = "crossrig.reposition_bone"
    bl_label = "Reposition Bone"
    bl_description = "Click on mesh surface to move this bone's head position"
    bl_options = {'REGISTER', 'UNDO'}

    bone_name: StringProperty()

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window.cursor_modal_restore()
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            settings = context.scene.crossrig_settings
            mesh_obj = settings.bone_reposition_mesh
            armature_obj = settings.bone_reposition_armature

            if not mesh_obj or not armature_obj:
                self.report({'ERROR'}, "Missing mesh or armature")
                context.window.cursor_modal_restore()
                return {'CANCELLED'}

            # Get mouse position
            region = context.region
            rv3d = context.region_data
            coord = event.mouse_region_x, event.mouse_region_y

            # Get ray origin and direction
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            ray_direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)

            # Perform raycast
            ray_target = ray_origin + ray_direction * 1000

            # Convert to object space
            matrix_inv = mesh_obj.matrix_world.inverted()
            ray_origin_obj = matrix_inv @ ray_origin
            ray_target_obj = matrix_inv @ ray_target
            ray_direction_obj = ray_target_obj - ray_origin_obj

            # Raycast on mesh
            result, location, normal, index = mesh_obj.ray_cast(ray_origin_obj, ray_direction_obj)

            if result:
                # Perform opposite raycast to find center of mass
                opposite_ray_origin = location + (ray_direction_obj * 10)
                opposite_ray_direction = -ray_direction_obj

                result_back, location_back, normal_back, index_back = mesh_obj.ray_cast(
                    opposite_ray_origin, opposite_ray_direction
                )

                if result_back:
                    # Calculate center point between front and back hit
                    center_pos = (location + location_back) / 2
                else:
                    # If back raycast fails, offset inward from surface using normal
                    center_pos = location - (normal * 0.05)

                # Convert back to world space
                world_pos = mesh_obj.matrix_world @ center_pos

                # Switch to edit mode and move the bone
                context.view_layer.objects.active = armature_obj
                armature_obj.select_set(True)
                mesh_obj.select_set(False)

                # Store current mode
                current_mode = context.mode

                # Enter edit mode
                bpy.ops.object.mode_set(mode='EDIT')

                # Get the bone in edit mode
                edit_bone = armature_obj.data.edit_bones.get(self.bone_name)

                if edit_bone:
                    # Convert world position to armature space
                    armature_space_pos = armature_obj.matrix_world.inverted() @ world_pos

                    # Store original bone information
                    old_head = edit_bone.head.copy()
                    old_tail = edit_bone.tail.copy()
                    bone_length = edit_bone.length
                    bone_direction = (edit_bone.tail - edit_bone.head).normalized()

                    # Move the bone head to new position
                    edit_bone.head = armature_space_pos
                    edit_bone.tail = edit_bone.head + (bone_direction * bone_length)

                    # Handle parent bone - only rotate/point tail toward clicked position
                    if edit_bone.parent:
                        parent = edit_bone.parent
                        # Keep parent head in place, only rotate tail to point to clicked position
                        parent.tail = armature_space_pos

                        # If connected, adjust selected bone to stay at parent's tail
                        if edit_bone.use_connect:
                            edit_bone.head = parent.tail
                            edit_bone.tail = edit_bone.head + (bone_direction * bone_length)

                    # Recalculate offset after parent adjustments
                    final_head = edit_bone.head.copy()
                    final_tail = edit_bone.tail.copy()
                    actual_offset = final_tail - old_tail

                    # Track moved bones for reporting
                    moved_bones = []

                    # Move all descendants by the same offset to maintain hierarchy
                    def move_entire_hierarchy(bone, offset):
                        """Move entire bone hierarchy by offset, maintaining all relationships."""
                        for child in bone.children:
                            moved_bones.append(child.name)

                            child_length = child.length
                            child_direction = (child.tail - child.head).normalized()

                            if child.use_connect:
                                # Connected: head must be at parent's tail
                                child.head = bone.tail
                                child.tail = child.head + (child_direction * child_length)
                                # For connected bones, calculate their actual movement
                                child_offset = child.tail - (child.tail - offset)
                            else:
                                # Not connected: move by offset
                                child.head += offset
                                child.tail += offset
                                child_offset = offset

                            # Recursively move this child's hierarchy
                            move_entire_hierarchy(child, child_offset)

                    # Move entire child hierarchy with calculated offset
                    move_entire_hierarchy(edit_bone, actual_offset)

                    # Track repositioned bones
                    history = settings.bone_reposition_history
                    repositioned = set(history.split(',')) if history else set()
                    repositioned.add(self.bone_name)
                    repositioned.update(moved_bones)

                    # Mirror mode - reposition opposite side bone with full chain
                    if settings.bone_reposition_mirror:
                        mirrored_name = get_mirrored_bone_name(self.bone_name)

                        if mirrored_name and mirrored_name in armature_obj.data.edit_bones:
                            mirror_bone = armature_obj.data.edit_bones[mirrored_name]

                            # Mirror position across X axis (Blender's default mirror axis)
                            mirrored_pos = armature_space_pos.copy()
                            mirrored_pos.x = -mirrored_pos.x

                            # Store mirror bone original positions
                            mirror_old_tail = mirror_bone.tail.copy()
                            mirror_length = mirror_bone.length
                            mirror_direction = (mirror_bone.tail - mirror_bone.head).normalized()

                            # Move mirror bone to mirrored position
                            mirror_bone.head = mirrored_pos
                            mirror_bone.tail = mirror_bone.head + (mirror_direction * mirror_length)

                            # Handle mirror bone's parent - only rotate/point tail
                            if mirror_bone.parent:
                                mirror_parent = mirror_bone.parent
                                mirror_parent.tail = mirrored_pos

                                if mirror_bone.use_connect:
                                    mirror_bone.head = mirror_parent.tail
                                    mirror_bone.tail = mirror_bone.head + (mirror_direction * mirror_length)

                            # Move mirror bone's children using same recursive approach
                            mirror_actual_offset = mirror_bone.tail - mirror_old_tail
                            move_entire_hierarchy(mirror_bone, mirror_actual_offset)

                            # Track mirrored bone
                            repositioned.add(mirrored_name)

                            # Report with moved bones info
                            bones_info = ", ".join(moved_bones) if len(moved_bones) <= 10 else f"{len(moved_bones)} bones"
                            self.report({'INFO'}, f"✓ Repositioned: {self.bone_name} + Mirrored: {mirrored_name} | Moved: {bones_info}")
                        else:
                            bones_info = ", ".join(moved_bones) if len(moved_bones) <= 10 else f"{len(moved_bones)} bones"
                            self.report({'INFO'}, f"✓ Repositioned: {self.bone_name} | Moved: {bones_info} [No mirror found]")
                    else:
                        bones_info = ", ".join(moved_bones) if len(moved_bones) <= 10 else f"{len(moved_bones)} bones"
                        self.report({'INFO'}, f"✓ Repositioned: {self.bone_name} | Moved: {bones_info}")

                    # Save repositioned bones history
                    settings.bone_reposition_history = ','.join(sorted(repositioned))
                else:
                    self.report({'ERROR'}, f"Bone '{self.bone_name}' not found")

                # Stay in EDIT mode so user can see bone structure for next repositioning
                # (Don't switch back to object mode)

                context.window.cursor_modal_restore()
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Click on the mesh surface")

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        settings = context.scene.crossrig_settings
        armature_obj = settings.bone_reposition_armature

        if not settings.bone_reposition_mesh or not armature_obj:
            self.report({'ERROR'}, "Missing mesh or armature")
            return {'CANCELLED'}

        # Make sure we're in object mode first
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Highlight the bone by selecting it
        context.view_layer.objects.active = armature_obj
        armature_obj.select_set(True)

        # Enter EDIT mode to show bone structure
        bpy.ops.object.mode_set(mode='EDIT')

        # Deselect all bones first
        bpy.ops.armature.select_all(action='DESELECT')

        # Select the specific bone in edit mode
        if self.bone_name in armature_obj.data.edit_bones:
            bone = armature_obj.data.edit_bones[self.bone_name]
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
            armature_obj.data.edit_bones.active = bone

        # Set cursor to crosshair
        context.window.cursor_modal_set('CROSSHAIR')
        context.window_manager.modal_handler_add(self)

        self.report({'INFO'}, f"Click on mesh to reposition: {self.bone_name}")

        return {'RUNNING_MODAL'}


class CROSSRIG_OT_AlignFingerToHand(Operator):
    """Align finger bone chain to hand with proper angle"""
    bl_idname = "crossrig.align_finger_to_hand"
    bl_label = "Align Finger to Hand"
    bl_description = "Select finger tip, align entire finger chain to hand bone with proper angle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings
        armature_obj = settings.bone_reposition_armature

        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature object")
            return {'CANCELLED'}

        # Get active bone in pose mode
        if context.mode != 'POSE':
            self.report({'ERROR'}, "Please enter Pose Mode and select a finger bone")
            return {'CANCELLED'}

        if not context.active_pose_bone:
            self.report({'ERROR'}, "Please select a finger bone")
            return {'CANCELLED'}

        finger_bone = context.active_pose_bone

        # Find hand bone (parent chain)
        hand_bone = None
        current = finger_bone.parent
        while current:
            bone_lower = current.name.lower()
            if 'hand' in bone_lower and not any(f in bone_lower for f in ['thumb', 'index', 'middle', 'ring', 'pinky']):
                hand_bone = current
                break
            current = current.parent

        if not hand_bone:
            self.report({'ERROR'}, "Could not find hand bone in parent chain")
            return {'CANCELLED'}

        # Switch to edit mode to reposition bones
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = armature_obj.data.edit_bones

        finger_edit = edit_bones.get(finger_bone.name)
        hand_edit = edit_bones.get(hand_bone.name)

        if not finger_edit or not hand_edit:
            bpy.ops.object.mode_set(mode='POSE')
            self.report({'ERROR'}, "Could not access edit bones")
            return {'CANCELLED'}

        # Build finger chain from selected bone back to hand
        finger_chain = []
        current_bone = finger_edit
        while current_bone and current_bone != hand_edit:
            finger_chain.insert(0, current_bone)  # Insert at start to reverse order
            if current_bone.parent:
                current_bone = current_bone.parent
            else:
                break

        if not finger_chain:
            bpy.ops.object.mode_set(mode='POSE')
            self.report({'ERROR'}, "Could not build finger chain")
            return {'CANCELLED'}

        # Calculate direction from hand to first finger bone
        hand_to_finger = (finger_chain[0].head - hand_edit.tail).normalized()

        # Align entire finger chain
        for i, bone in enumerate(finger_chain):
            bone_length = bone.length

            if i == 0:
                # First bone: connect to hand tail
                bone.head = hand_edit.tail
                bone.tail = bone.head + (hand_to_finger * bone_length)
            else:
                # Subsequent bones: connect to previous bone tail
                bone.head = finger_chain[i-1].tail
                bone.tail = bone.head + (hand_to_finger * bone_length)

        # Return to pose mode
        bpy.ops.object.mode_set(mode='POSE')

        self.report({'INFO'}, f"✓ Aligned {len(finger_chain)} finger bones to {hand_bone.name}")
        return {'FINISHED'}


class CROSSRIG_OT_AlignFingerByMeshClick(Operator):
    """Click on finger tip mesh to automatically align finger bones"""
    bl_idname = "crossrig.align_finger_by_mesh_click"
    bl_label = "Align Finger by Mesh Click"
    bl_description = "Click on finger tip mesh to automatically align finger bones to hand"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.report({'INFO'}, "Cancelled finger alignment")
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            settings = context.scene.crossrig_settings
            mesh_obj = settings.bone_reposition_mesh
            armature_obj = settings.bone_reposition_armature

            if not mesh_obj or not armature_obj:
                self.report({'ERROR'}, "Mesh and armature must be set")
                return {'CANCELLED'}

            # Get mouse position
            region = context.region
            rv3d = context.region_data
            coord = event.mouse_region_x, event.mouse_region_y

            # Raycast from mouse position
            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            ray_target = ray_origin + view_vector * 1000

            # Convert to object space
            matrix_inv = mesh_obj.matrix_world.inverted()
            ray_origin_obj = matrix_inv @ ray_origin
            ray_target_obj = matrix_inv @ ray_target
            ray_direction_obj = ray_target_obj - ray_origin_obj

            # Raycast on mesh
            result, location, normal, index = mesh_obj.ray_cast(ray_origin_obj, ray_direction_obj)

            if result:
                # Convert to world space
                world_pos = mesh_obj.matrix_world @ location

                # Detect which finger was clicked based on position
                clicked_finger = self.detect_finger_from_position(context, armature_obj, world_pos)

                if not clicked_finger:
                    self.report({'WARNING'}, "Could not detect finger from clicked position")
                    return {'RUNNING_MODAL'}

                # Get hand and finger bones
                hand_data = detect_hand_finger_hierarchy(armature_obj, clicked_finger['side'])

                if not hand_data['hand']:
                    self.report({'ERROR'}, f"No hand bone found for {clicked_finger['side']} side")
                    return {'CANCELLED'}

                finger_bones = hand_data['fingers'].get(clicked_finger['type'], [])
                if not finger_bones:
                    self.report({'ERROR'}, f"No {clicked_finger['type']} finger bones found")
                    return {'CANCELLED'}

                # Align the finger to hand
                self.align_finger_chain(context, armature_obj, hand_data['hand'], finger_bones)

                self.report({'INFO'}, f"✓ Aligned {clicked_finger['side']} {clicked_finger['type']} finger to hand")
                return {'FINISHED'}

            else:
                self.report({'WARNING'}, "No mesh surface hit - try clicking on the finger tip")
                return {'RUNNING_MODAL'}

        return {'RUNNING_MODAL'}

    def detect_finger_from_position(self, context, armature_obj, world_pos):
        """Detect which finger was clicked based on world position."""
        # Try to detect hand bones on both sides
        left_hand_data = detect_hand_finger_hierarchy(armature_obj, 'LEFT')
        right_hand_data = detect_hand_finger_hierarchy(armature_obj, 'RIGHT')

        candidates = []

        # Check left hand fingers
        if left_hand_data['hand']:
            for finger_type, finger_bones in left_hand_data['fingers'].items():
                if finger_bones:
                    # Get the tip bone (last in chain)
                    tip_bone_name = finger_bones[-1]
                    pose_bone = armature_obj.pose.bones.get(tip_bone_name)
                    if pose_bone:
                        # Calculate distance from clicked position to finger tip
                        tip_world_pos = armature_obj.matrix_world @ pose_bone.tail
                        distance = (world_pos - tip_world_pos).length
                        candidates.append({
                            'side': 'LEFT',
                            'type': finger_type,
                            'distance': distance
                        })

        # Check right hand fingers
        if right_hand_data['hand']:
            for finger_type, finger_bones in right_hand_data['fingers'].items():
                if finger_bones:
                    tip_bone_name = finger_bones[-1]
                    pose_bone = armature_obj.pose.bones.get(tip_bone_name)
                    if pose_bone:
                        tip_world_pos = armature_obj.matrix_world @ pose_bone.tail
                        distance = (world_pos - tip_world_pos).length
                        candidates.append({
                            'side': 'RIGHT',
                            'type': finger_type,
                            'distance': distance
                        })

        # Return the closest finger
        if candidates:
            closest = min(candidates, key=lambda x: x['distance'])
            # Only return if within reasonable distance (20cm)
            if closest['distance'] < 0.2:
                return closest

        return None

    def align_finger_chain(self, context, armature_obj, hand_bone_name, finger_bones):
        """Align finger bone chain to hand with proper angle."""
        # Enter edit mode
        context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')

        hand_edit = armature_obj.data.edit_bones.get(hand_bone_name)
        if not hand_edit:
            self.report({'ERROR'}, f"Hand bone '{hand_bone_name}' not found")
            bpy.ops.object.mode_set(mode='OBJECT')
            return

        # Build finger chain
        finger_chain = []
        for bone_name in finger_bones:
            bone = armature_obj.data.edit_bones.get(bone_name)
            if bone:
                finger_chain.append(bone)

        if not finger_chain:
            self.report({'ERROR'}, "No finger bones found in hierarchy")
            bpy.ops.object.mode_set(mode='OBJECT')
            return

        # Calculate direction from hand to first finger bone
        hand_to_finger = (finger_chain[0].head - hand_edit.tail).normalized()

        # Align entire finger chain
        for i, bone in enumerate(finger_chain):
            bone_length = bone.length

            if i == 0:
                # First bone: start at hand tail
                bone.head = hand_edit.tail
                bone.tail = bone.head + (hand_to_finger * bone_length)
            else:
                # Subsequent bones: continue in same direction
                parent_bone = finger_chain[i - 1]
                bone.head = parent_bone.tail
                bone.tail = bone.head + (hand_to_finger * bone_length)

        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

    def invoke(self, context, event):
        settings = context.scene.crossrig_settings

        if not settings.bone_reposition_armature or not settings.bone_reposition_mesh:
            self.report({'ERROR'}, "Please select both armature and mesh")
            return {'CANCELLED'}

        # Ensure we're in object mode
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        context.window_manager.modal_handler_add(self)
        self.report({'INFO'}, "Click on finger tip to align bones (Right-click or ESC to cancel)")
        return {'RUNNING_MODAL'}


class CROSSRIG_OT_SmartAlignFingerToMesh(Operator):
    """Smart align finger bones to mesh with proper angles"""
    bl_idname = "crossrig.smart_align_finger_to_mesh"
    bl_label = "Smart Align Finger to Mesh"
    bl_description = "Click on finger tip to align entire finger chain with smart angle calculation"
    bl_options = {'REGISTER', 'UNDO'}

    finger_type: StringProperty()  # thumb, index, middle, ring, pinky
    side: StringProperty()  # LEFT, RIGHT

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.report({'INFO'}, "Cancelled finger alignment")
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            settings = context.scene.crossrig_settings
            mesh_obj = settings.bone_reposition_mesh
            armature_obj = settings.bone_reposition_armature

            if not mesh_obj or not armature_obj:
                self.report({'ERROR'}, "Mesh and armature must be set")
                return {'CANCELLED'}

            # Get mouse position
            region = context.region
            rv3d = context.region_data
            coord = event.mouse_region_x, event.mouse_region_y

            # Raycast from mouse position
            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            ray_target = ray_origin + view_vector * 1000

            # Convert to object space
            matrix_inv = mesh_obj.matrix_world.inverted()
            ray_origin_obj = matrix_inv @ ray_origin
            ray_target_obj = matrix_inv @ ray_target
            ray_direction_obj = ray_target_obj - ray_origin_obj

            # Raycast on mesh
            result, location, normal, index = mesh_obj.ray_cast(ray_origin_obj, ray_direction_obj)

            if result:
                # Convert to world space
                world_pos = mesh_obj.matrix_world @ location

                # Get hand and finger bones
                hand_data = detect_hand_finger_hierarchy(armature_obj, self.side)

                if not hand_data['hand']:
                    self.report({'ERROR'}, f"No hand bone found for {self.side} side")
                    return {'CANCELLED'}

                finger_bones = hand_data['fingers'].get(self.finger_type, [])
                if not finger_bones:
                    self.report({'ERROR'}, f"No {self.finger_type} finger bones found")
                    return {'CANCELLED'}

                # Calculate smart alignment with proper angles
                self.smart_align_finger_chain(context, armature_obj, hand_data['hand'], finger_bones, world_pos, mesh_obj)

                self.report({'INFO'}, f"✓ Smart aligned {self.side} {self.finger_type} finger")
                return {'FINISHED'}

            else:
                self.report({'WARNING'}, "No mesh surface hit - try clicking on the finger tip")
                return {'RUNNING_MODAL'}

        return {'RUNNING_MODAL'}

    def smart_align_finger_chain(self, context, armature_obj, hand_bone_name, finger_bones, tip_world_pos, mesh_obj):
        """Align finger chain straight forward with proper rotation toward clicked tip."""
        # Enter edit mode
        context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')

        hand_edit = armature_obj.data.edit_bones.get(hand_bone_name)
        if not hand_edit:
            self.report({'ERROR'}, f"Hand bone '{hand_bone_name}' not found")
            bpy.ops.object.mode_set(mode='OBJECT')
            return

        # Get finger bones in edit mode
        finger_chain = []
        for bone_name in finger_bones:
            bone = armature_obj.data.edit_bones.get(bone_name)
            if bone:
                finger_chain.append(bone)

        if not finger_chain:
            self.report({'ERROR'}, "No finger bones found")
            bpy.ops.object.mode_set(mode='OBJECT')
            return

        # Convert positions to armature space
        armature_inv = armature_obj.matrix_world.inverted()
        tip_armature_pos = armature_inv @ tip_world_pos

        # Start from hand tail
        start_pos = hand_edit.tail.copy()

        # Calculate single direction from hand to clicked tip
        finger_direction = (tip_armature_pos - start_pos).normalized()

        # Align all bones in the same direction (straight forward)
        current_pos = start_pos.copy()

        for i, bone in enumerate(finger_chain):
            bone_length = bone.length

            # Set bone head at current position
            bone.head = current_pos.copy()

            # Set bone tail along the finger direction
            bone.tail = bone.head + (finger_direction * bone_length)

            # Move current position to bone tail for next bone
            current_pos = bone.tail.copy()

        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

    def invoke(self, context, event):
        settings = context.scene.crossrig_settings

        if not settings.bone_reposition_armature or not settings.bone_reposition_mesh:
            self.report({'ERROR'}, "Please select both armature and mesh")
            return {'CANCELLED'}

        if not self.finger_type or not self.side:
            self.report({'ERROR'}, "Finger type and side must be specified")
            return {'CANCELLED'}

        # Ensure we're in object mode
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        context.window_manager.modal_handler_add(self)
        self.report({'INFO'}, f"Click on {self.side} {self.finger_type} finger tip (Right-click/ESC to cancel)")
        return {'RUNNING_MODAL'}


class CROSSRIG_OT_ClearBoneRepositionHistory(Operator):
    """Clear repositioned bones history"""
    bl_idname = "crossrig.clear_bone_reposition_history"
    bl_label = "Clear Reposition History"
    bl_description = "Clear the history of repositioned bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings
        settings.bone_reposition_history = ""

        self.report({'INFO'}, "Cleared bone reposition history")
        return {'FINISHED'}


class CROSSRIG_OT_ExitBoneRepositionMode(Operator):
    """Exit bone repositioning mode"""
    bl_idname = "crossrig.exit_bone_reposition_mode"
    bl_label = "Exit Bone Reposition Mode"
    bl_description = "Exit bone repositioning mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings
        settings.bone_reposition_active = False

        self.report({'INFO'}, "Exited bone reposition mode")
        return {'FINISHED'}


# Registration
classes = (
    CROSSRIG_OT_SmartMapArmatureToMesh,
    CROSSRIG_OT_SmartMapHandFingers,
    CROSSRIG_OT_AlignFingerToHand,
    CROSSRIG_OT_AlignFingerByMeshClick,
    CROSSRIG_OT_SmartAlignFingerToMesh,
    CROSSRIG_OT_StartBoneRepositionMode,
    CROSSRIG_OT_RepositionBone,
    CROSSRIG_OT_ClearBoneRepositionHistory,
    CROSSRIG_OT_ExitBoneRepositionMode,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
