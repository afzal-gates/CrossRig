"""
Blender operators for animation transfer system.

Provides UI operators for saving and applying animation data.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
import os
import subprocess
import platform

from ...core.use_cases.save_animation_data import save_animation_data
from ...core.use_cases.apply_animation_data import load_and_apply_animation
from ...core.services.animation_data_service import (
    list_available_animations,
    delete_animation_data_file,
    get_animation_data_directory
)


class CROSSRIG_OT_SaveAnimationData(Operator):
    """Save animation from selected armature"""
    bl_idname = "crossrig.save_animation_data"
    bl_label = "Save Animation"
    bl_options = {'REGISTER', 'UNDO'}

    animation_name: StringProperty(
        name="Animation Name",
        description="Name for the saved animation",
        default="MyAnimation"
    )

    description: StringProperty(
        name="Description",
        description="Optional description for the animation",
        default=""
    )

    def get_action_items(self, context):
        """Get available actions for selected armature."""
        items = []

        armature = context.active_object
        if armature and armature.type == 'ARMATURE':
            # Get all actions
            for action in bpy.data.actions:
                items.append((action.name, action.name, f"Save action: {action.name}"))

        if not items:
            items.append(('NONE', 'No actions found', ''))

        return items

    action_to_save: EnumProperty(
        name="Action",
        description="Select action to save",
        items=get_action_items
    )

    def invoke(self, context, event):
        # Check if armature is selected
        if not context.active_object or context.active_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature object")
            return {'CANCELLED'}

        # Default name
        if context.active_object.animation_data and context.active_object.animation_data.action:
            self.action_to_save = context.active_object.animation_data.action.name
            self.animation_name = context.active_object.animation_data.action.name

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "action_to_save")
        layout.prop(self, "animation_name")
        layout.prop(self, "description")

    def execute(self, context):
        armature_obj = context.active_object

        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected")
            return {'CANCELLED'}

        if self.action_to_save == 'NONE':
            self.report({'ERROR'}, "No action selected")
            return {'CANCELLED'}

        # Save animation
        success, message, filepath = save_animation_data(
            armature_obj=armature_obj,
            action_name=self.action_to_save,
            save_name=self.animation_name,
            description=self.description
        )

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_ApplyAnimationData(Operator):
    """Apply saved animation to selected armature"""
    bl_idname = "crossrig.apply_animation_data"
    bl_label = "Apply Animation"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(
        name="File Path",
        description="Path to animation data file",
        subtype='FILE_PATH'
    )

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    def invoke(self, context, event):
        # Check if armature is selected
        if not context.active_object or context.active_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature object")
            return {'CANCELLED'}

        # Open file browser
        anim_dir = get_animation_data_directory()
        self.filepath = str(anim_dir)

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        armature_obj = context.active_object

        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected")
            return {'CANCELLED'}

        if not self.filepath:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}

        # Apply animation
        success, message, warnings = load_and_apply_animation(
            filepath=self.filepath,
            armature_obj=armature_obj
        )

        if success:
            self.report({'INFO'}, message)
            if warnings:
                for warning in warnings[:5]:  # Show first 5 warnings
                    self.report({'WARNING'}, warning)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_ApplyAnimationDataMenu(Operator):
    """Quick apply saved animation from menu"""
    bl_idname = "crossrig.apply_animation_data_menu"
    bl_label = "Quick Apply Animation"
    bl_options = {'REGISTER', 'UNDO'}

    def get_animation_items(self, context):
        """Generate enum items for available animations."""
        animations = list_available_animations()

        if not animations:
            return [('NONE', 'No animations found', 'Save an animation first')]

        items = []
        for name, filepath in animations:
            items.append((filepath, name, f"Apply animation: {name}"))

        return items

    animation: EnumProperty(
        name="Animation",
        description="Select animation to apply",
        items=get_animation_items
    )

    def invoke(self, context, event):
        # Check if armature is selected
        if not context.active_object or context.active_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature object")
            return {'CANCELLED'}

        animations = list_available_animations()
        if not animations:
            self.report({'WARNING'}, "No saved animations found")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Target: {context.active_object.name}")
        layout.prop(self, "animation", text="")

    def execute(self, context):
        armature_obj = context.active_object

        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected")
            return {'CANCELLED'}

        if self.animation == 'NONE':
            self.report({'WARNING'}, "No animation selected")
            return {'CANCELLED'}

        # Apply animation
        success, message, warnings = load_and_apply_animation(
            filepath=self.animation,
            armature_obj=armature_obj
        )

        if success:
            self.report({'INFO'}, message)
            if warnings:
                for warning in warnings[:5]:
                    self.report({'WARNING'}, warning)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_DeleteAnimationData(Operator):
    """Delete saved animation"""
    bl_idname = "crossrig.delete_animation_data"
    bl_label = "Delete Animation"
    bl_options = {'REGISTER', 'UNDO'}

    def get_animation_items(self, context):
        """Generate enum items for available animations."""
        animations = list_available_animations()

        if not animations:
            return [('NONE', 'No animations found', '')]

        items = []
        for name, filepath in animations:
            items.append((filepath, name, f"Delete: {name}"))

        return items

    animation: EnumProperty(
        name="Animation",
        description="Select animation to delete",
        items=get_animation_items
    )

    def invoke(self, context, event):
        animations = list_available_animations()
        if not animations:
            self.report({'WARNING'}, "No animations found")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text="WARNING: This cannot be undone!", icon='ERROR')
        layout.prop(self, "animation", text="")

    def execute(self, context):
        if self.animation == 'NONE':
            self.report({'WARNING'}, "No animation selected")
            return {'CANCELLED'}

        # Delete animation
        success, message = delete_animation_data_file(self.animation)

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_OpenAnimationDataFolder(Operator):
    """Open animation data folder in system file browser"""
    bl_idname = "crossrig.open_animation_data_folder"
    bl_label = "Open Animation Folder"

    def execute(self, context):
        anim_dir = get_animation_data_directory()

        try:
            system = platform.system()

            if system == "Windows":
                os.startfile(str(anim_dir))
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(anim_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(anim_dir)])

            self.report({'INFO'}, f"Opened: {anim_dir}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to open folder: {str(e)}")
            return {'CANCELLED'}


# Registration
classes = (
    MIXAMO_OT_SaveAnimationData,
    MIXAMO_OT_ApplyAnimationData,
    MIXAMO_OT_ApplyAnimationDataMenu,
    MIXAMO_OT_DeleteAnimationData,
    MIXAMO_OT_OpenAnimationDataFolder,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
