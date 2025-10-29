"""
Blender Operators for Mixanimo Lite.

These operators provide the user-facing actions in the addon.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ...config.constants import REPEAT_ACTION_SUFFIX
from ...core.use_cases import (
    send_actions_to_timeline,
    bake_nla_to_action,
    stabilize_root_animation,
    export_armature_as_fbx
)


class CROSSRIG_OT_SelectArmatureFromList(Operator):
    """Select armature from action list."""
    bl_idname = "crossrig.select_armature_from_list"
    bl_label = "Select Armature"

    armature_name: StringProperty()

    def execute(self, context):
        armature = bpy.data.objects.get(self.armature_name)
        if armature and armature.type == "ARMATURE":
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            self.report({'INFO'}, f"{self.armature_name} selected.")
        else:
            self.report({'WARNING'}, f"Armature '{self.armature_name}' not found.")
        return {'FINISHED'}


class CROSSRIG_OT_GetActions(Operator):
    """Load actions from scene."""
    bl_idname = "crossrig.get_actions"
    bl_label = "Load Actions"
    bl_description = "List actions in the scene"

    def execute(self, context):
        prefs = context.scene.crossrig_settings
        prefs.action_collection.clear()

        for act in bpy.data.actions:
            if REPEAT_ACTION_SUFFIX not in act.name:
                for fc in act.fcurves:
                    if "pose.bones[" in fc.data_path:
                        item = prefs.action_collection.add()
                        item.action_name = act.name
                        # Try to guess armature
                        for obj in bpy.data.objects:
                            if obj.type == 'ARMATURE' and obj.animation_data:
                                if obj.animation_data.action == act:
                                    item.armature_name = obj.name
                                    break
                        break

        prefs.order_confirmed = False
        self.report({'INFO'}, "Actions loaded. (Armature references assigned if found.)")
        return {'FINISHED'}


class CROSSRIG_OT_MoveActionUp(Operator):
    """Move action up in list."""
    bl_idname = "crossrig.move_action_up"
    bl_label = "Move Action Up"

    def execute(self, context):
        prefs = context.scene.crossrig_settings
        idx = prefs.action_index
        if idx > 0:
            prefs.action_collection.move(idx, idx-1)
            prefs.action_index -= 1
            prefs.order_confirmed = False
        return {'FINISHED'}


class CROSSRIG_OT_MoveActionDown(Operator):
    """Move action down in list."""
    bl_idname = "crossrig.move_action_down"
    bl_label = "Move Action Down"

    def execute(self, context):
        prefs = context.scene.crossrig_settings
        idx = prefs.action_index
        if idx < len(prefs.action_collection) - 1:
            prefs.action_collection.move(idx, idx+1)
            prefs.action_index += 1
            prefs.order_confirmed = False
        return {'FINISHED'}


class CROSSRIG_OT_ConfirmOrder(Operator):
    """Confirm action order and select armature."""
    bl_idname = "crossrig.confirm_order"
    bl_label = "Confirm Order"
    bl_description = "Assign selected actions to active Armature in specified order."

    def execute(self, context):
        prefs = context.scene.crossrig_settings

        if len(prefs.action_collection) == 0:
            self.report({'WARNING'}, "No action found.")
            return {'CANCELLED'}

        first_item = prefs.action_collection[0]
        if first_item.armature_name and first_item.armature_name in bpy.data.objects:
            arm = bpy.data.objects[first_item.armature_name]
            context.view_layer.objects.active = arm
            arm.select_set(True)
        else:
            self.report({'WARNING'}, "No armature assigned to the first action")
            return {'CANCELLED'}

        prefs.order_confirmed = True
        return {'FINISHED'}


class CROSSRIG_OT_SendToTimeline(Operator):
    """Send actions to NLA timeline."""
    bl_idname = "crossrig.send_to_timeline"
    bl_label = "Send to Timeline"
    bl_description = "Add selected actions to NLA editor in overlapped sequence."

    def execute(self, context):
        prefs = context.scene.crossrig_settings

        if not prefs.order_confirmed:
            self.report({'WARNING'}, "Run 'Confirm Order' before proceeding")
            return {'CANCELLED'}

        arm = context.active_object
        if not arm or arm.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an armature")
            return {'CANCELLED'}

        # Collect actions to send
        actions_to_send = []
        for item in prefs.action_collection:
            if item.use_action:
                act = bpy.data.actions.get(item.action_name)
                if act:
                    actions_to_send.append((act, item.repeat_count, item.angle))

        if not actions_to_send:
            self.report({'WARNING'}, "No action selected (use_action=True). Operation cancelled")
            return {'CANCELLED'}

        # Call use case
        send_actions_to_timeline(
            arm,
            actions_to_send,
            root_bone=prefs.root_bone,
            overlap_frames=prefs.overlap_frames,
            forward_axis=prefs.forward_axis
        )

        self.report({'INFO'}, f"{len(actions_to_send)} action entry(ies) sent to timeline (multi-track).")
        return {'FINISHED'}


class CROSSRIG_OT_BakeAction(Operator):
    """Bake NLA animation into single action."""
    bl_idname = "crossrig.bake_action"
    bl_label = "Bake Action"
    bl_description = "Bake all NLA strips into a single action"

    def execute(self, context):
        arm = context.active_object

        if not arm or arm.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an armature")
            return {'CANCELLED'}

        # Call use case
        success, message, action_name = bake_nla_to_action(arm, context)

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_StabilizeRoot(Operator):
    """Stabilize root bone for in-place animation."""
    bl_idname = "crossrig.stabilize_root"
    bl_label = "Stabilize Root"
    bl_description = "Remove horizontal movement from root bone, keeping character in place"

    def execute(self, context):
        prefs = context.scene.crossrig_settings
        arm = context.active_object

        if not arm or arm.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an armature")
            return {'CANCELLED'}

        # Call use case
        success, message, keyframe_count = stabilize_root_animation(arm, prefs.root_bone)

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_ExportFBX(Operator):
    """Export armature with mesh as FBX."""
    bl_idname = "crossrig.export_fbx"
    bl_label = "Export as FBX (Game-Ready)"
    bl_description = "Export armature with baked animation as FBX file for game engines"

    filepath: StringProperty(
        name="File Path",
        description="Path to save FBX file",
        maxlen=1024,
        subtype='FILE_PATH'
    )

    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'}
    )

    def execute(self, context):
        arm = context.active_object

        if not arm or arm.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an armature")
            return {'CANCELLED'}

        if not self.filepath:
            self.report({'WARNING'}, "No file path specified")
            return {'CANCELLED'}

        # Call use case (with mesh)
        success, message, obj_count = export_armature_as_fbx(
            arm, self.filepath, include_mesh=True, context=context
        )

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

    def invoke(self, context, event):
        # Set default filename based on action name
        arm = context.active_object
        if arm and arm.animation_data and arm.animation_data.action:
            action_name = arm.animation_data.action.name
            self.filepath = action_name + ".fbx"
        else:
            self.filepath = "animation.fbx"

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class CROSSRIG_OT_ExportFBX_ArmatureOnly(Operator):
    """Export armature only as FBX."""
    bl_idname = "crossrig.export_fbx_armature_only"
    bl_label = "Export FBX (Armature Only)"
    bl_description = "Export only armature with animation (no mesh)"

    filepath: StringProperty(
        name="File Path",
        description="Path to save FBX file",
        maxlen=1024,
        subtype='FILE_PATH'
    )

    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'}
    )

    def execute(self, context):
        arm = context.active_object

        if not arm or arm.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an armature")
            return {'CANCELLED'}

        if not self.filepath:
            self.report({'WARNING'}, "No file path specified")
            return {'CANCELLED'}

        # Call use case (without mesh)
        success, message, obj_count = export_armature_as_fbx(
            arm, self.filepath, include_mesh=False, context=context
        )

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

    def invoke(self, context, event):
        # Set default filename based on action name
        arm = context.active_object
        if arm and arm.animation_data and arm.animation_data.action:
            action_name = arm.animation_data.action.name
            self.filepath = action_name + "_armature.fbx"
        else:
            self.filepath = "armature.fbx"

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class CROSSRIG_OT_DisabledFeature(Operator):
    """Placeholder for disabled features."""
    bl_idname = "crossrig.disabled_feature"
    bl_label = "Pro"
    bl_description = "This feature is available soon."

    def execute(self, context):
        self.report({'WARNING'}, "This feature is available soon.")
        return {'CANCELLED'}


# Classes to register
classes = (
    MIXAMO_OT_SelectArmatureFromList,
    MIXAMO_OT_GetActions,
    MIXAMO_OT_MoveActionUp,
    MIXAMO_OT_MoveActionDown,
    MIXAMO_OT_ConfirmOrder,
    MIXAMO_OT_SendToTimeline,
    MIXAMO_OT_BakeAction,
    MIXAMO_OT_StabilizeRoot,
    MIXAMO_OT_ExportFBX,
    MIXAMO_OT_ExportFBX_ArmatureOnly,
    MIXAMO_OT_DisabledFeature,
)


def register():
    """Register operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister operator classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
