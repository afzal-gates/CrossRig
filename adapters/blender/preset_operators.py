"""
Blender Operators for Animation Preset Management.

These operators provide save, load, and delete functionality for presets.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty
from ...core.use_cases import (
    save_animation_preset,
    load_animation_preset,
    apply_preset_to_armature
)
from ...core.services.preset_service import (
    list_available_presets,
    delete_preset_file
)


class CROSSRIG_OT_SavePreset(Operator):
    """Save current animation sequence as preset."""
    bl_idname = "crossrig.save_preset"
    bl_label = "Save Animation Preset"
    bl_description = "Save current animation sequence as a reusable preset"

    preset_name: StringProperty(
        name="Preset Name",
        description="Name for this preset",
        default="MyPreset"
    )

    description: StringProperty(
        name="Description",
        description="Optional description for this preset",
        default=""
    )

    def execute(self, context):
        prefs = context.scene.crossrig_settings

        # Validate preset name
        if not self.preset_name or not self.preset_name.strip():
            self.report({'WARNING'}, "Preset name cannot be empty")
            return {'CANCELLED'}

        # Check if there are actions to save
        if len(prefs.action_collection) == 0:
            self.report({'WARNING'}, "No actions to save. Load actions first")
            return {'CANCELLED'}

        # Save preset
        success, message, filepath = save_animation_preset(
            preset_name=self.preset_name,
            description=self.description,
            action_items=prefs.action_collection,
            root_bone=prefs.root_bone,
            overlap_frames=prefs.overlap_frames,
            forward_axis=prefs.forward_axis
        )

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")
        layout.prop(self, "description")


class CROSSRIG_OT_LoadPreset(Operator):
    """Load animation preset and apply to current armature."""
    bl_idname = "crossrig.load_preset"
    bl_label = "Load Animation Preset"
    bl_description = "Load a saved animation preset"

    filepath: StringProperty(
        name="File Path",
        description="Path to preset file",
        subtype='FILE_PATH'
    )

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    def execute(self, context):
        if not self.filepath:
            self.report({'WARNING'}, "No preset file selected")
            return {'CANCELLED'}

        prefs = context.scene.crossrig_settings

        # Load preset
        success, message, actions_loaded, warnings = load_animation_preset(
            self.filepath,
            prefs.action_collection,
            prefs
        )

        if success:
            self.report({'INFO'}, message)
            # Show warnings if any
            for warning in warnings:
                self.report({'WARNING'}, warning)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

    def invoke(self, context, event):
        # Open file browser starting at preset directory
        from ...core.services.preset_service import get_preset_directory
        preset_dir = get_preset_directory()
        self.filepath = str(preset_dir / "")

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class CROSSRIG_OT_LoadPresetMenu(Operator):
    """Quick load preset from dropdown menu."""
    bl_idname = "crossrig.load_preset_menu"
    bl_label = "Quick Load Preset"
    bl_description = "Quickly load a preset from the list"

    def get_preset_items(self, context):
        """Get list of available presets."""
        presets = list_available_presets()

        if not presets:
            return [('NONE', 'No presets found', 'Create a preset first')]

        items = []
        for name, filepath in presets:
            items.append((filepath, name, f"Load preset: {name}"))

        return items

    preset: EnumProperty(
        name="Preset",
        description="Select preset to load",
        items=get_preset_items
    )

    def execute(self, context):
        if self.preset == 'NONE':
            self.report({'WARNING'}, "No presets available")
            return {'CANCELLED'}

        prefs = context.scene.crossrig_settings

        # Load preset
        success, message, actions_loaded, warnings = load_animation_preset(
            self.preset,
            prefs.action_collection,
            prefs
        )

        if success:
            self.report({'INFO'}, message)
            for warning in warnings:
                self.report({'WARNING'}, warning)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset")


class CROSSRIG_OT_DeletePreset(Operator):
    """Delete a saved preset."""
    bl_idname = "crossrig.delete_preset"
    bl_label = "Delete Preset"
    bl_description = "Delete a saved animation preset"

    def get_preset_items(self, context):
        """Get list of available presets."""
        presets = list_available_presets()

        if not presets:
            return [('NONE', 'No presets found', '')]

        items = []
        for name, filepath in presets:
            items.append((filepath, name, f"Delete preset: {name}"))

        return items

    preset: EnumProperty(
        name="Preset to Delete",
        description="Select preset to delete",
        items=get_preset_items
    )

    def execute(self, context):
        if self.preset == 'NONE':
            self.report({'WARNING'}, "No presets available")
            return {'CANCELLED'}

        # Delete preset file
        success, message = delete_preset_file(self.preset)

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset")
        layout.label(text="This action cannot be undone!", icon='ERROR')


class CROSSRIG_OT_OpenPresetFolder(Operator):
    """Open preset storage folder in file browser."""
    bl_idname = "crossrig.open_preset_folder"
    bl_label = "Open Preset Folder"
    bl_description = "Open the folder where presets are stored"

    def execute(self, context):
        import os
        import subprocess
        from ...core.services.preset_service import get_preset_directory

        preset_dir = get_preset_directory()

        try:
            # Open folder in system file browser
            if os.name == 'nt':  # Windows
                os.startfile(str(preset_dir))
            elif os.name == 'posix':  # Linux/Mac
                subprocess.Popen(['xdg-open', str(preset_dir)])
            else:
                subprocess.Popen(['open', str(preset_dir)])

            self.report({'INFO'}, f"Opened: {preset_dir}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to open folder: {str(e)}")
            return {'CANCELLED'}


# Classes to register
classes = (
    CROSSRIG_OT_SavePreset,
    CROSSRIG_OT_LoadPreset,
    CROSSRIG_OT_LoadPresetMenu,
    CROSSRIG_OT_DeletePreset,
    CROSSRIG_OT_OpenPresetFolder,
)


def register():
    """Register preset operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister preset operator classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
