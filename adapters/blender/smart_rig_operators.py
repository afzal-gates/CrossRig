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


# Landmark definitions with bilateral support
LANDMARK_DEFINITIONS = [
    # Head/Neck
    ('head_top', 'Head Top', 'HEAD', False),
    ('head_center', 'Head Center', 'HEAD', False),
    ('neck', 'Neck', 'NECK', False),
    ('chin', 'Chin', 'CHIN', False),

    # Torso
    ('spine_top', 'Spine Top', 'SPINE', False),
    ('spine_mid', 'Spine Mid', 'SPINE', False),
    ('spine_bottom', 'Spine Bottom (Hips)', 'SPINE', False),

    # Arms (Bilateral)
    ('shoulder', 'Shoulder', 'ARM', True),
    ('elbow', 'Elbow', 'ARM', True),
    ('wrist', 'Wrist', 'ARM', True),
    ('hand', 'Hand', 'ARM', True),

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
            ('spine_bottom', 'CENTER'),  # Hip
            ('shoulder', 'LEFT'),
            ('wrist', 'LEFT'),
            ('ankle', 'LEFT'),
        ],
        'auto_mirror': True,
        'interpolate': True,
    },
    'MINIMAL': {
        'name': 'Minimal',
        'description': 'Basic skeleton (8-10 landmarks)',
        'required': [
            ('neck', 'CENTER'),
            ('spine_bottom', 'CENTER'),
            ('shoulder', 'LEFT'),
            ('elbow', 'LEFT'),
            ('wrist', 'LEFT'),
            ('hip', 'LEFT'),
            ('knee', 'LEFT'),
            ('ankle', 'LEFT'),
        ],
        'auto_mirror': True,
        'interpolate': True,
    },
    'STANDARD': {
        'name': 'Standard',
        'description': 'Complete humanoid rig (15-20 landmarks)',
        'required': [],
        'auto_mirror': False,
        'interpolate': False,
    },
}


class CROSSRIG_OT_StartSmartRigMode(Operator):
    """Enter Smart Rig landmark selection mode"""
    bl_idname = "crossrig.start_smart_rig_mode"
    bl_label = "Start Smart Rig Mode"
    bl_description = "Enter landmark selection mode to generate armature from mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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

        # Set to edit mode for vertex selection
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

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
                # Convert back to world space
                world_pos = mesh_obj.matrix_world @ location

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
                    marker.empty_display_size = 0.05
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

        # Remove all visual markers
        for landmark in settings.smart_rig_landmarks:
            marker_name = f"Landmark_{landmark.landmark_id}_{landmark.landmark_side}"
            if marker_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[marker_name], do_unlink=True)

        settings.smart_rig_landmarks.clear()
        self.report({'INFO'}, "All landmarks cleared")

        return {'FINISHED'}


class CROSSRIG_OT_AutoDetectSymmetry(Operator):
    """Automatically detect and mirror landmarks for bilateral symmetry"""
    bl_idname = "crossrig.auto_detect_symmetry"
    bl_label = "Auto-Detect Symmetry"
    bl_description = "Automatically mirror landmarks from one side to the other"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings
        mesh_obj = settings.smart_rig_target_mesh

        if not mesh_obj:
            self.report({'ERROR'}, "No target mesh set")
            return {'CANCELLED'}

        mirrored_count = 0

        # Find landmarks that need mirroring
        for landmark in settings.smart_rig_landmarks:
            # Check if this landmark has bilateral support
            landmark_def = next((ld for ld in LANDMARK_DEFINITIONS if ld[0] == landmark.landmark_id), None)
            if not landmark_def or not landmark_def[3]:  # Not bilateral
                continue

            # Check if opposite side exists
            opposite_side = 'RIGHT' if landmark.landmark_side == 'LEFT' else 'LEFT'
            if landmark.landmark_side == 'CENTER':
                continue

            # Check if opposite already exists
            exists = any(
                lm.landmark_id == landmark.landmark_id and lm.landmark_side == opposite_side
                for lm in settings.smart_rig_landmarks
            )

            if not exists:
                # Mirror the position
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

                bpy.ops.object.empty_add(type='SPHERE', location=pos, radius=0.05)
                marker = context.active_object
                marker.name = marker_name
                marker.show_in_front = True
                marker.empty_display_type = 'SPHERE'
                marker.color = (0.0, 0.0, 1.0, 1.0) if opposite_side == 'RIGHT' else (1.0, 0.0, 0.0, 1.0)

                mirrored_count += 1

        if mirrored_count > 0:
            self.report({'INFO'}, f"Mirrored {mirrored_count} landmark(s)")
        else:
            self.report({'INFO'}, "No landmarks to mirror")

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

        if bone_set == 'SMART':
            box.label(text="• Complete body skeleton (23 bones)", icon='DOT')
            box.label(text="• Spine chain (root + 3 vertebrae)", icon='DOT')
            box.label(text="• Neck + Head", icon='DOT')
            box.label(text="• Arms (shoulder → elbow → wrist → hand) x2", icon='DOT')
            box.label(text="• Legs (hip → knee → ankle → foot → toe) x2", icon='DOT')
            layout.separator()
            layout.label(text="All bones auto-calculated from your 6 picks!", icon='INFO')
        else:
            box.label(text=f"• Bones based on picked landmarks", icon='DOT')

        layout.separator()
        layout.prop(self, "auto_skin")

    def execute(self, context):
        settings = context.scene.crossrig_settings
        mesh_obj = settings.smart_rig_target_mesh
        bone_set = settings.smart_rig_bone_set

        if not mesh_obj:
            self.report({'ERROR'}, "No target mesh set")
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

        success, message, armature_obj = generate_armature_from_landmarks(
            landmarks=settings.smart_rig_landmarks,
            mesh_obj=mesh_obj,
            auto_skin=self.auto_skin,
            context=context
        )

        if success:
            # Clean up visual markers
            for landmark in settings.smart_rig_landmarks:
                marker_name = f"Landmark_{landmark.landmark_id}_{landmark.landmark_side}"
                if marker_name in bpy.data.objects:
                    bpy.data.objects.remove(bpy.data.objects[marker_name], do_unlink=True)

            # Exit smart rig mode
            settings.smart_rig_active = False

            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
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

        # Clean up visual markers
        for landmark in settings.smart_rig_landmarks:
            marker_name = f"Landmark_{landmark.landmark_id}_{landmark.landmark_side}"
            if marker_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[marker_name], do_unlink=True)

        settings.smart_rig_active = False
        settings.smart_rig_landmarks.clear()

        self.report({'INFO'}, "Exited Smart Rig mode")
        return {'FINISHED'}


# Registration
classes = (
    CROSSRIG_OT_StartSmartRigMode,
    CROSSRIG_OT_PickLandmark,
    CROSSRIG_OT_ClearLandmark,
    CROSSRIG_OT_ClearAllLandmarks,
    CROSSRIG_OT_AutoDetectSymmetry,
    CROSSRIG_OT_ApplyBoneSetPreset,
    CROSSRIG_OT_GenerateSmartRig,
    CROSSRIG_OT_ExitSmartRigMode,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
