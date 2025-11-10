"""
Smart Rig Generation Operators for CrossRig.

Provides Auto-Rig Pro-like functionality for automatic armature generation
from user-selected landmarks on a mesh.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bmesh


def cleanup_landmark_markers(force=False):
    """
    Safely clean up all landmark markers from the scene.

    Args:
        force: If True, removes all objects starting with 'Landmark_' regardless of settings

    This prevents crashes on undo/redo by ensuring orphaned markers are removed.
    """
    try:
        markers_removed = 0

        # Find all landmark marker objects
        markers_to_remove = []
        for obj in bpy.data.objects:
            if obj.name.startswith("Landmark_"):
                markers_to_remove.append(obj)

        # Remove them safely
        for marker in markers_to_remove:
            try:
                # Unlink from all collections first
                for collection in marker.users_collection:
                    collection.objects.unlink(marker)

                # Remove from bpy.data
                bpy.data.objects.remove(marker, do_unlink=True)
                markers_removed += 1
            except Exception as e:
                # If marker is already removed or invalid, skip
                print(f"Warning: Could not remove marker {marker.name}: {e}")
                pass

        return markers_removed

    except Exception as e:
        print(f"Warning: Error in cleanup_landmark_markers: {e}")
        return 0


def safe_mode_switch(target_mode='OBJECT'):
    """
    Safely switch to target mode, handling errors gracefully.

    Prevents crashes from invalid mode switches during undo/redo.
    """
    try:
        current_mode = bpy.context.mode

        # Already in target mode
        if current_mode.endswith(target_mode):
            return True

        # Try to switch mode
        bpy.ops.object.mode_set(mode=target_mode)
        return True

    except Exception as e:
        print(f"Warning: Could not switch to {target_mode} mode: {e}")
        # Try to at least get to object mode as fallback
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            return True
        except:
            return False


# Landmark definitions with bilateral support
LANDMARK_DEFINITIONS = [
    # Head/Neck
    ('head_top', 'Head Top', 'HEAD', False),
    ('head_center', 'Head Center', 'HEAD', False),
    ('neck', 'Neck', 'NECK', False),
    ('chin', 'Chin', 'CHIN', False),

    # Torso
    ('hips', 'Hips (Root/Pelvis)', 'SPINE', False),
    ('spine_bottom', 'Spine Bottom', 'SPINE', False),
    ('spine_mid', 'Spine Mid', 'SPINE', False),
    ('spine_top', 'Spine Top', 'SPINE', False),

    # Arms (Bilateral)
    ('shoulder', 'Shoulder', 'ARM', True),
    ('elbow', 'Elbow', 'ARM', True),
    ('wrist', 'Wrist', 'ARM', True),
    ('hand', 'Hand', 'ARM', True),

    # Fingers (Bilateral) - 3 bones per finger for detailed control
    # Thumb
    ('thumb_01', 'Thumb 01 (Base)', 'FINGER', True),
    ('thumb_02', 'Thumb 02 (Mid)', 'FINGER', True),
    ('thumb_03', 'Thumb 03 (Tip)', 'FINGER', True),
    # Index
    ('index_01', 'Index 01 (Base)', 'FINGER', True),
    ('index_02', 'Index 02 (Mid)', 'FINGER', True),
    ('index_03', 'Index 03 (Tip)', 'FINGER', True),
    # Middle
    ('middle_01', 'Middle 01 (Base)', 'FINGER', True),
    ('middle_02', 'Middle 02 (Mid)', 'FINGER', True),
    ('middle_03', 'Middle 03 (Tip)', 'FINGER', True),
    # Ring
    ('ring_01', 'Ring 01 (Base)', 'FINGER', True),
    ('ring_02', 'Ring 02 (Mid)', 'FINGER', True),
    ('ring_03', 'Ring 03 (Tip)', 'FINGER', True),
    # Pinky
    ('pinky_01', 'Pinky 01 (Base)', 'FINGER', True),
    ('pinky_02', 'Pinky 02 (Mid)', 'FINGER', True),
    ('pinky_03', 'Pinky 03 (Tip)', 'FINGER', True),

    # Legs (Bilateral)
    ('hip', 'Hip', 'LEG', True),
    ('knee', 'Knee', 'LEG', True),
    ('ankle', 'Ankle', 'LEG', True),
    ('foot', 'Foot', 'LEG', True),
    ('toe', 'Toe', 'LEG', True),
]

# Bone Set Presets (Auto-Rig Pro style)
BONE_SET_PRESETS = {
    'SMART': {
        'name': 'Smart (Auto-Rig Pro)',
        'description': 'Minimal landmarks with intelligent interpolation (6 picks)',
        'required': [
            ('neck', 'CENTER'),
            ('chin', 'CENTER'),
            ('hips', 'CENTER'),  # Hips/Root
            ('shoulder', 'LEFT'),
            ('wrist', 'LEFT'),
            ('ankle', 'LEFT'),
        ],
        'auto_mirror': True,
        'interpolate': True,
        'naming': 'standard',
    },
    'MIXAMO': {
        'name': 'Mixamo Standard',
        'description': 'Mixamo-compatible armature with mixamorig: prefix (6 picks)',
        'required': [
            ('neck', 'CENTER'),
            ('chin', 'CENTER'),
            ('hips', 'CENTER'),  # Hips/Root
            ('shoulder', 'LEFT'),
            ('wrist', 'LEFT'),
            ('ankle', 'LEFT'),
        ],
        'auto_mirror': True,
        'interpolate': True,
        'naming': 'mixamo',
    },
    'MINIMAL': {
        'name': 'Minimal',
        'description': 'Basic skeleton (8-10 landmarks)',
        'required': [
            ('neck', 'CENTER'),
            ('hips', 'CENTER'),
            ('shoulder', 'LEFT'),
            ('elbow', 'LEFT'),
            ('wrist', 'LEFT'),
            ('hip', 'LEFT'),
            ('knee', 'LEFT'),
            ('ankle', 'LEFT'),
        ],
        'auto_mirror': True,
        'interpolate': True,
        'naming': 'standard',
    },
    'STANDARD': {
        'name': 'Standard',
        'description': 'Complete humanoid rig (15-20 landmarks)',
        'required': [],
        'auto_mirror': False,
        'interpolate': False,
        'naming': 'standard',
    },
}


class CROSSRIG_OT_StartSmartRigMode(Operator):
    """Enter Smart Rig landmark selection mode"""
    bl_idname = "crossrig.start_smart_rig_mode"
    bl_label = "Start Smart Rig Mode"
    bl_description = "Enter landmark selection mode to generate armature from mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Safety: Clean up any leftover markers from previous sessions
        cleanup_landmark_markers(force=True)

        mesh_obj = context.active_object

        if not mesh_obj or mesh_obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Initialize smart rig settings
        settings = context.scene.crossrig_settings
        settings.smart_rig_active = True
        settings.smart_rig_target_mesh = mesh_obj

        # Clear previous landmarks
        settings.smart_rig_landmarks.clear()

        # Safely switch to object mode
        if not safe_mode_switch('OBJECT'):
            self.report({'WARNING'}, "Could not switch to object mode")

        self.report({'INFO'}, f"Smart Rig mode active for: {mesh_obj.name}")
        return {'FINISHED'}


class CROSSRIG_OT_PickLandmark(Operator):
    """Click on mesh surface to pick landmark (works in Object Mode)"""
    bl_idname = "crossrig.pick_landmark"
    bl_label = "Pick Landmark"
    bl_description = "Click anywhere on the mesh surface to set landmark"
    bl_options = {'REGISTER', 'UNDO'}

    landmark_id: StringProperty()
    landmark_side: EnumProperty(
        name="Side",
        items=[
            ('CENTER', 'Center', 'Center landmark'),
            ('LEFT', 'Left', 'Left side'),
            ('RIGHT', 'Right', 'Right side'),
        ],
        default='CENTER'
    )

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window.cursor_modal_restore()
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Perform raycast to get hit position on mesh
            mesh_obj = context.scene.crossrig_settings.smart_rig_target_mesh

            if not mesh_obj:
                self.report({'ERROR'}, "No target mesh")
                context.window.cursor_modal_restore()
                return {'CANCELLED'}

            # Get mouse position
            region = context.region
            rv3d = context.region_data
            coord = event.mouse_region_x, event.mouse_region_y

            # Raycast from view
            view_vector = bpy.context.space_data.region_3d.view_rotation @ Vector((0, 0, -1))
            ray_origin = bpy.context.space_data.region_3d.view_location

            # Use view3d_utils for accurate raycasting
            from bpy_extras import view3d_utils

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
                # Perform opposite raycast to find interior/center position
                # Cast ray from opposite direction to find the "depth"
                opposite_ray_origin = location + (ray_direction_obj * 10)  # Start beyond the mesh
                opposite_ray_direction = -ray_direction_obj

                result_back, location_back, normal_back, index_back = mesh_obj.ray_cast(
                    opposite_ray_origin, opposite_ray_direction
                )

                if result_back:
                    # Calculate center point between front and back hit
                    center_pos = (location + location_back) / 2
                else:
                    # If back raycast fails, offset inward from surface using normal
                    center_pos = location - (normal * 0.05)  # 5cm inward

                # Convert back to world space
                world_pos = mesh_obj.matrix_world @ center_pos

                # Store landmark
                settings = context.scene.crossrig_settings

                # Check if landmark already exists and update it
                existing = None
                for lm in settings.smart_rig_landmarks:
                    if lm.landmark_id == self.landmark_id and lm.landmark_side == self.landmark_side:
                        existing = lm
                        break

                if existing:
                    existing.position = world_pos
                else:
                    landmark = settings.smart_rig_landmarks.add()
                    landmark.landmark_id = self.landmark_id
                    landmark.landmark_side = self.landmark_side
                    landmark.position = world_pos

                # Create or update visual marker
                marker_name = f"Landmark_{self.landmark_id}_{self.landmark_side}"
                if marker_name in bpy.data.objects:
                    marker = bpy.data.objects[marker_name]
                    marker.location = world_pos
                else:
                    bpy.ops.object.empty_add(type='SPHERE', location=world_pos)
                    marker = context.active_object
                    marker.name = marker_name
                    marker.empty_display_size = 0.02  # Smaller size to prevent overlapping
                    marker.show_in_front = True

                    # Set color based on side
                    if self.landmark_side == 'LEFT':
                        marker.color = (1.0, 0.0, 0.0, 1.0)  # Red
                    elif self.landmark_side == 'RIGHT':
                        marker.color = (0.0, 0.0, 1.0, 1.0)  # Blue
                    else:
                        marker.color = (0.0, 1.0, 0.0, 1.0)  # Green

                # Restore mesh selection
                mesh_obj.select_set(True)
                context.view_layer.objects.active = mesh_obj

                landmark_name = f"{self.landmark_id} ({self.landmark_side})"
                self.report({'INFO'}, f"✓ {landmark_name}")

                context.window.cursor_modal_restore()
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Click on the mesh surface")

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        mesh_obj = context.scene.crossrig_settings.smart_rig_target_mesh

        if not mesh_obj:
            self.report({'ERROR'}, "No target mesh set")
            return {'CANCELLED'}

        # Make sure we're in object mode
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Set cursor to crosshair
        context.window.cursor_modal_set('CROSSHAIR')
        context.window_manager.modal_handler_add(self)

        landmark_name = f"{self.landmark_id} ({self.landmark_side})"
        self.report({'INFO'}, f"Click on mesh to place: {landmark_name}")

        return {'RUNNING_MODAL'}


class CROSSRIG_OT_ClearLandmark(Operator):
    """Clear a specific landmark"""
    bl_idname = "crossrig.clear_landmark"
    bl_label = "Clear Landmark"
    bl_description = "Remove this landmark"
    bl_options = {'REGISTER', 'UNDO'}

    index: StringProperty()

    def execute(self, context):
        settings = context.scene.crossrig_settings
        idx = int(self.index)

        if idx < len(settings.smart_rig_landmarks):
            landmark = settings.smart_rig_landmarks[idx]
            marker_name = f"Landmark_{landmark.landmark_id}_{landmark.landmark_side}"

            # Remove visual marker
            if marker_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[marker_name], do_unlink=True)

            settings.smart_rig_landmarks.remove(idx)
            self.report({'INFO'}, "Landmark cleared")

        return {'FINISHED'}


class CROSSRIG_OT_ClearAllLandmarks(Operator):
    """Clear all landmarks"""
    bl_idname = "crossrig.clear_all_landmarks"
    bl_label = "Clear All Landmarks"
    bl_description = "Remove all landmarks and visual markers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings

        # Use safe cleanup function
        markers_removed = cleanup_landmark_markers(force=True)

        settings.smart_rig_landmarks.clear()
        self.report({'INFO'}, f"All landmarks cleared ({markers_removed} markers removed)")

        return {'FINISHED'}


class CROSSRIG_OT_AutoDetectSymmetry(Operator):
    """Automatically detect and mirror landmarks for bilateral symmetry"""
    bl_idname = "crossrig.auto_detect_symmetry"
    bl_label = "Auto-Detect Symmetry"
    bl_description = "Automatically mirror landmarks from one side to the other"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Safety check: ensure we're in a valid state
        if not safe_mode_switch('OBJECT'):
            self.report({'ERROR'}, "Could not switch to object mode")
            return {'CANCELLED'}

        settings = context.scene.crossrig_settings
        mesh_obj = settings.smart_rig_target_mesh

        if not mesh_obj:
            self.report({'ERROR'}, "No target mesh set")
            return {'CANCELLED'}

        mirrored_count = 0

        # Collect all LEFT landmarks that need mirroring
        landmarks_to_mirror = []

        for landmark in settings.smart_rig_landmarks:
            if landmark.landmark_side != 'LEFT':
                continue

            # Check if this landmark has bilateral support
            landmark_def = next((ld for ld in LANDMARK_DEFINITIONS if ld[0] == landmark.landmark_id), None)

            # Special handling for finger segments (they have IDs like "thumb_01", "index_02", etc.)
            is_finger_segment = '_' in landmark.landmark_id and any(
                f in landmark.landmark_id for f in ['thumb', 'index', 'middle', 'ring', 'pinky']
            )

            # Check if bilateral (either in definitions or is a finger segment)
            if not landmark_def or not landmark_def[3]:
                if not is_finger_segment:
                    continue  # Not bilateral

            # Check if RIGHT side already exists
            opposite_side = 'RIGHT'
            exists = any(
                lm.landmark_id == landmark.landmark_id and lm.landmark_side == opposite_side
                for lm in settings.smart_rig_landmarks
            )

            if not exists:
                landmarks_to_mirror.append(landmark)

        # Mirror all collected landmarks
        for landmark in landmarks_to_mirror:
            opposite_side = 'RIGHT'

            # Mirror the position across X axis
            pos = landmark.position.copy()
            pos.x = -pos.x  # Mirror across X axis

            # Create new landmark
            new_landmark = settings.smart_rig_landmarks.add()
            new_landmark.landmark_id = landmark.landmark_id
            new_landmark.landmark_side = opposite_side
            new_landmark.position = pos

            # Create visual marker
            marker_name = f"Landmark_{landmark.landmark_id}_{opposite_side}"
            if marker_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[marker_name], do_unlink=True)

            bpy.ops.object.empty_add(type='SPHERE', location=pos, radius=0.02)
            marker = context.active_object
            marker.name = marker_name
            marker.show_in_front = True
            marker.empty_display_type = 'SPHERE'
            marker.empty_display_size = 0.02  # Smaller size to prevent overlapping
            marker.color = (0.0, 0.0, 1.0, 1.0)  # Blue for RIGHT

            mirrored_count += 1

        if mirrored_count > 0:
            self.report({'INFO'}, f"Mirrored {mirrored_count} landmark(s) to RIGHT side")
        else:
            self.report({'INFO'}, "No LEFT landmarks to mirror")

        return {'FINISHED'}


class CROSSRIG_OT_GenerateSmartRig(Operator):
    """Generate armature from selected landmarks"""
    bl_idname = "crossrig.generate_smart_rig"
    bl_label = "Generate Rig"
    bl_description = "Create armature from picked landmarks with automatic bone placement and naming"
    bl_options = {'REGISTER', 'UNDO'}

    auto_skin: BoolProperty(
        name="Auto Skin",
        description="Automatically parent mesh to armature with automatic weights",
        default=True
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        settings = context.scene.crossrig_settings

        landmark_count = len(settings.smart_rig_landmarks)
        bone_set = settings.smart_rig_bone_set

        layout.label(text=f"Landmarks Picked: {landmark_count}", icon='INFO')

        # Show what will be generated
        box = layout.box()
        box.label(text="Will Generate:", icon='ARMATURE_DATA')

        if bone_set == 'SMART' or bone_set == 'MIXAMO':
            base_bones = 25  # Hips + 3 Spine bones + Neck + Head + HeadTop_End + 8 Arms + 10 Legs
            finger_bones = 40 if settings.smart_rig_include_fingers else 0  # 4 bones per finger
            foot_bones = 0  # Will add later if foot details implemented
            total_bones = base_bones + finger_bones + foot_bones

            naming_type = "Mixamo" if bone_set == 'MIXAMO' else "Standard"
            box.label(text=f"• Complete body skeleton ({total_bones} bones)", icon='DOT')
            box.label(text=f"• Naming: {naming_type}", icon='DOT')
            box.label(text="• Hips + Spine chain (Spine, Spine1, Spine2)", icon='DOT')
            box.label(text="• Neck + Head + HeadTop_End", icon='DOT')
            box.label(text="• Arms (shoulder → elbow → wrist → hand) x2", icon='DOT')
            if settings.smart_rig_include_fingers:
                box.label(text="• Fingers (5 fingers × 4 bones × 2 hands = 40)", icon='DOT')
            box.label(text="• Legs (hip → knee → ankle → foot → toe) x2", icon='DOT')
            layout.separator()
            layout.label(text="All bones auto-calculated from your 6 picks!", icon='INFO')
        else:
            box.label(text=f"• Bones based on picked landmarks", icon='DOT')

        layout.separator()
        layout.prop(self, "auto_skin")

    def execute(self, context):
        # Safety: Ensure we're in object mode before starting
        if not safe_mode_switch('OBJECT'):
            self.report({'ERROR'}, "Could not switch to object mode")
            return {'CANCELLED'}

        settings = context.scene.crossrig_settings
        mesh_obj = settings.smart_rig_target_mesh
        bone_set = settings.smart_rig_bone_set

        if not mesh_obj:
            self.report({'ERROR'}, "No target mesh set")
            return {'CANCELLED'}

        # Validate mesh still exists
        if mesh_obj.name not in bpy.data.objects:
            self.report({'ERROR'}, "Target mesh no longer exists in scene")
            return {'CANCELLED'}

        # Different requirements for different modes
        landmark_count = len(settings.smart_rig_landmarks)
        if bone_set == 'SMART':
            # Smart mode can work with fewer landmarks due to interpolation
            if landmark_count < 1:
                self.report({'ERROR'}, "Smart mode: Pick at least 1 landmark")
                return {'CANCELLED'}
        else:
            # Other modes need at least 3 landmarks
            if landmark_count < 3:
                self.report({'ERROR'}, "Need at least 3 landmarks to generate rig")
                return {'CANCELLED'}

        # Call the rig generation service
        from ...core.services.smart_rig_service import generate_armature_from_landmarks

        # Determine naming convention from bone set
        naming = 'mixamo' if bone_set == 'MIXAMO' else 'standard'

        success, message, armature_obj = generate_armature_from_landmarks(
            landmarks=settings.smart_rig_landmarks,
            mesh_obj=mesh_obj,
            auto_skin=self.auto_skin,
            context=context,
            naming=naming,
            include_fingers=settings.smart_rig_include_fingers,
            include_foot_details=settings.smart_rig_include_foot_details
        )

        if success:
            # Clean up visual markers safely
            cleanup_landmark_markers(force=True)

            # Exit smart rig mode
            settings.smart_rig_active = False

            # Ensure we're back in object mode
            safe_mode_switch('OBJECT')

            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            # Try to recover to a safe state
            safe_mode_switch('OBJECT')
            return {'CANCELLED'}


class CROSSRIG_OT_ApplyBoneSetPreset(Operator):
    """Apply bone set preset - shows which landmarks to pick"""
    bl_idname = "crossrig.apply_bone_set_preset"
    bl_label = "Apply Bone Set"
    bl_description = "Apply selected bone set preset and show required landmarks"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings
        bone_set = settings.smart_rig_bone_set

        if bone_set not in BONE_SET_PRESETS:
            self.report({'ERROR'}, f"Unknown bone set: {bone_set}")
            return {'CANCELLED'}

        preset = BONE_SET_PRESETS[bone_set]

        # Clear existing landmarks
        settings.smart_rig_landmarks.clear()

        # Clean up visual markers
        for obj in bpy.data.objects:
            if obj.name.startswith("Landmark_"):
                bpy.data.objects.remove(obj, do_unlink=True)

        preset_name = preset['name']
        required_count = len(preset.get('required', []))

        if required_count > 0:
            self.report({'INFO'}, f"Applied '{preset_name}' - Pick {required_count} landmarks")
        else:
            self.report({'INFO'}, f"Applied '{preset_name}' - Pick any landmarks")

        return {'FINISHED'}


class CROSSRIG_OT_ExitSmartRigMode(Operator):
    """Exit Smart Rig mode without generating"""
    bl_idname = "crossrig.exit_smart_rig_mode"
    bl_label = "Exit Smart Rig Mode"
    bl_description = "Exit landmark selection mode without generating armature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings

        # Clean up visual markers safely
        cleanup_landmark_markers(force=True)

        settings.smart_rig_active = False
        settings.smart_rig_landmarks.clear()

        # Ensure we're back in a safe mode
        safe_mode_switch('OBJECT')

        self.report({'INFO'}, "Exited Smart Rig mode")
        return {'FINISHED'}


class CROSSRIG_OT_ApplyTPose(Operator):
    """Apply T-pose to selected armature and deform mesh"""
    bl_idname = "crossrig.apply_tpose"
    bl_label = "Apply T-Pose"
    bl_description = "Apply T-pose to the selected armature and move mesh with bones (automatically skins mesh if needed)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature_obj = context.active_object

        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature object")
            return {'CANCELLED'}

        # Find associated mesh object
        mesh_obj = None

        # Method 1: Check for parented mesh children
        for child in armature_obj.children:
            if child.type == 'MESH':
                mesh_obj = child
                break

        # Method 2: Check settings for target mesh (from smart rig or bone reposition)
        if not mesh_obj:
            settings = context.scene.crossrig_settings
            if settings.smart_rig_target_mesh:
                mesh_obj = settings.smart_rig_target_mesh
            elif settings.bone_reposition_mesh:
                mesh_obj = settings.bone_reposition_mesh

        # If mesh found, ensure it's skinned to armature
        if mesh_obj:
            # Check if mesh is already parented to armature
            is_parented = mesh_obj.parent == armature_obj
            has_armature_modifier = any(mod.type == 'ARMATURE' and mod.object == armature_obj
                                       for mod in mesh_obj.modifiers)

            if not is_parented or not has_armature_modifier:
                try:
                    # Skin mesh to armature with automatic weights
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.select_all(action='DESELECT')
                    mesh_obj.select_set(True)
                    armature_obj.select_set(True)
                    context.view_layer.objects.active = armature_obj

                    # Parent with automatic weights
                    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

                    self.report({'INFO'}, f"Skinned {mesh_obj.name} to {armature_obj.name}")

                except Exception as e:
                    self.report({'WARNING'}, f"Could not skin mesh automatically: {e}")

        # Detect naming convention
        is_mixamo = any('mixamorig:' in bone.name for bone in armature_obj.data.bones)
        naming = 'mixamo' if is_mixamo else 'standard'

        try:
            from ...core.services.smart_rig_service import set_t_pose

            # If mesh is found and skinned, we need to handle deformation properly
            if mesh_obj:
                # Store the armature modifier for later
                armature_mod = None
                for mod in mesh_obj.modifiers:
                    if mod.type == 'ARMATURE' and mod.object == armature_obj:
                        armature_mod = mod
                        break

                # Apply T-pose to armature (changes rest pose)
                set_t_pose(armature_obj, naming)

                # Now we need to apply the visual deformation to the mesh
                # The mesh is still in the old shape, so we apply the modifier to bake it
                if armature_mod:
                    try:
                        # Select mesh
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.select_all(action='DESELECT')
                        mesh_obj.select_set(True)
                        context.view_layer.objects.active = mesh_obj

                        # Apply the armature modifier to bake the deformation
                        bpy.ops.object.modifier_apply(modifier=armature_mod.name)

                        # Re-parent mesh to armature with automatic weights
                        # This creates a new armature modifier for the new rest pose
                        armature_obj.select_set(True)
                        context.view_layer.objects.active = armature_obj
                        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

                        self.report({'INFO'}, f"T-pose applied with mesh deformation - mesh baked to new rest pose")
                    except Exception as e:
                        self.report({'WARNING'}, f"Mesh deformation baking failed: {e}")

                else:
                    self.report({'INFO'}, f"T-pose applied to {armature_obj.name}")
            else:
                # No mesh found, just apply T-pose to armature
                set_t_pose(armature_obj, naming)
                self.report({'INFO'}, f"T-pose applied to {armature_obj.name} (no mesh found)")

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply T-pose: {str(e)}")
            return {'CANCELLED'}


class CROSSRIG_OT_GenerateControlRig(Operator):
    """Generate a full control rig for Mixamo armature with IK/FK controls"""
    bl_idname = "crossrig.generate_control_rig"
    bl_label = "Generate Control Rig"
    bl_description = "Generate IK/FK controls, pole targets, and animation controllers for Mixamo armature"
    bl_options = {'REGISTER', 'UNDO'}

    use_rigify: BoolProperty(
        name="Use Rigify",
        description="Use Rigify system (requires Rigify addon and proper rig types). Uncheck for custom Mixamo rig",
        default=False
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        armature_obj = context.active_object

        if armature_obj and armature_obj.type == 'ARMATURE':
            # Check if Mixamo armature
            is_mixamo = any('mixamorig:' in bone.name for bone in armature_obj.data.bones)

            if is_mixamo:
                layout.label(text="Mixamo Armature Detected!", icon='INFO')
                layout.separator()
                layout.label(text="Rig Type:")
                layout.prop(self, "use_rigify", text="Use Rigify System")
                layout.separator()

                if self.use_rigify:
                    box = layout.box()
                    box.label(text="Rigify Mode:", icon='MOD_ARMATURE')
                    box.label(text="• Requires Rigify addon enabled")
                    box.label(text="• Auto-assigns rig types")
                    box.label(text="• Full Rigify features")
                else:
                    box = layout.box()
                    box.label(text="Custom Mixamo Rig:", icon='ARMATURE_DATA')
                    box.label(text="• IK controls for hands & feet")
                    box.label(text="• Pole targets for elbows & knees")
                    box.label(text="• Root & COG controllers")
                    box.label(text="• Ready for animation")
            else:
                layout.label(text="Not a Mixamo armature", icon='ERROR')
                layout.label(text="Only Mixamo armatures supported", icon='INFO')

    def assign_rigify_types(self, armature_obj):
        """Assign Rigify rig types to bones based on their names."""
        # Bone name to Rigify type mapping
        rigify_type_map = {
            # Mixamo naming
            'mixamorig:Hips': 'spines.basic_spine',
            'mixamorig:Spine': None,  # Child of spine chain
            'mixamorig:Spine1': None,
            'mixamorig:Spine2': None,
            'mixamorig:Neck': None,
            'mixamorig:Head': None,

            # Arms
            'mixamorig:LeftShoulder': 'limbs.super_limb',
            'mixamorig:RightShoulder': 'limbs.super_limb',

            # Legs
            'mixamorig:LeftUpLeg': 'limbs.super_limb',
            'mixamorig:RightUpLeg': 'limbs.super_limb',

            # Fingers
            'mixamorig:LeftHandThumb1': 'limbs.super_finger',
            'mixamorig:LeftHandIndex1': 'limbs.super_finger',
            'mixamorig:LeftHandMiddle1': 'limbs.super_finger',
            'mixamorig:LeftHandRing1': 'limbs.super_finger',
            'mixamorig:LeftHandPinky1': 'limbs.super_finger',
            'mixamorig:RightHandThumb1': 'limbs.super_finger',
            'mixamorig:RightHandIndex1': 'limbs.super_finger',
            'mixamorig:RightHandMiddle1': 'limbs.super_finger',
            'mixamorig:RightHandRing1': 'limbs.super_finger',
            'mixamorig:RightHandPinky1': 'limbs.super_finger',

            # Standard naming
            'hips': 'spines.basic_spine',
            'shoulder.L': 'limbs.super_limb',
            'shoulder.R': 'limbs.super_limb',
            'thigh.L': 'limbs.super_limb',
            'thigh.R': 'limbs.super_limb',

            # Fingers (standard)
            'thumb_01.L': 'limbs.super_finger',
            'index_01.L': 'limbs.super_finger',
            'middle_01.L': 'limbs.super_finger',
            'ring_01.L': 'limbs.super_finger',
            'pinky_01.L': 'limbs.super_finger',
            'thumb_01.R': 'limbs.super_finger',
            'index_01.R': 'limbs.super_finger',
            'middle_01.R': 'limbs.super_finger',
            'ring_01.R': 'limbs.super_finger',
            'pinky_01.R': 'limbs.super_finger',
        }

        bpy.ops.object.mode_set(mode='EDIT')

        for bone in armature_obj.data.edit_bones:
            if bone.name in rigify_type_map:
                rig_type = rigify_type_map[bone.name]
                if rig_type:
                    bone['rigify_type'] = rig_type
                    self.report({'INFO'}, f"Assigned {rig_type} to {bone.name}")

        bpy.ops.object.mode_set(mode='OBJECT')

    def execute(self, context):
        armature_obj = context.active_object

        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature object")
            return {'CANCELLED'}

        # Check if Mixamo armature
        is_mixamo = any('mixamorig:' in bone.name for bone in armature_obj.data.bones)
        if not is_mixamo:
            self.report({'ERROR'}, "Not a Mixamo armature. Only Mixamo armatures are supported.")
            return {'CANCELLED'}

        # Store original armature name
        original_name = armature_obj.name

        # Choose rig generation method
        if self.use_rigify:
            # === RIGIFY METHOD ===
            # Check if Rigify is available
            if 'rigify' not in context.preferences.addons:
                self.report({'ERROR'}, "Rigify addon is not enabled. Please enable it in Preferences > Add-ons")
                return {'CANCELLED'}

            try:
                # Assign Rigify types to bones
                self.report({'INFO'}, f"Preparing Rigify metarig for: {original_name}")
                self.assign_rigify_types(armature_obj)

                # Generate the rig using Rigify
                self.report({'INFO'}, f"Generating Rigify control rig...")

                try:
                    # Ensure armature is selected and active
                    bpy.ops.object.select_all(action='DESELECT')
                    armature_obj.select_set(True)
                    context.view_layer.objects.active = armature_obj

                    # Enter POSE mode (required for Rigify generation)
                    bpy.ops.object.mode_set(mode='POSE')

                    # Try to generate using Rigify
                    bpy.ops.pose.rigify_generate()

                    self.report({'INFO'}, f"Successfully generated Rigify control rig from {original_name}")
                    return {'FINISHED'}

                except Exception as e:
                    self.report({'ERROR'}, f"Rigify generation failed: {str(e)}")
                    self.report({'WARNING'}, "The armature structure may not be compatible with Rigify")
                    self.report({'INFO'}, "Tip: Try custom Mixamo rig instead (uncheck 'Use Rigify')")
                    return {'CANCELLED'}

            except ImportError:
                self.report({'ERROR'}, "Could not import Rigify module. Please ensure Rigify is properly installed.")
                return {'CANCELLED'}

        else:
            # === CUSTOM MIXAMO RIG METHOD ===
            try:
                from ...core.services.mixamo_rig_service import generate_mixamo_control_rig

                self.report({'INFO'}, f"Generating custom Mixamo control rig for: {original_name}")

                success, message, rig_obj = generate_mixamo_control_rig(armature_obj, context)

                if success:
                    self.report({'INFO'}, message)
                    return {'FINISHED'}
                else:
                    self.report({'ERROR'}, message)
                    return {'CANCELLED'}

            except Exception as e:
                self.report({'ERROR'}, f"Custom rig generation failed: {str(e)}")
                return {'CANCELLED'}


# Registration
classes = (
    CROSSRIG_OT_StartSmartRigMode,
    CROSSRIG_OT_PickLandmark,
    CROSSRIG_OT_ClearLandmark,
    CROSSRIG_OT_ClearAllLandmarks,
    CROSSRIG_OT_AutoDetectSymmetry,
    CROSSRIG_OT_ApplyBoneSetPreset,
    CROSSRIG_OT_GenerateSmartRig,
    CROSSRIG_OT_ApplyTPose,
    CROSSRIG_OT_GenerateControlRig,
    CROSSRIG_OT_ExitSmartRigMode,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
