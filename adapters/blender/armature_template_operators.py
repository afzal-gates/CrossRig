"""
Blender operators for armature template system.

Provides UI operators for saving, loading, and managing armature templates.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, FloatProperty, BoolProperty, FloatVectorProperty
import os
import subprocess
import platform
import math

from ...core.use_cases.save_armature_template import save_armature_template
from ...core.use_cases.load_armature_template import (
    load_and_create_armature_template,
    load_armature_template_to_mesh
)
from ...core.services.armature_template_service import (
    list_available_armature_templates,
    delete_armature_template_file,
    get_armature_template_directory
)


class CROSSRIG_OT_SaveArmatureTemplate(Operator):
    """Save selected armature structure as template"""
    bl_idname = "crossrig.save_armature_template"
    bl_label = "Save Armature Template"
    bl_options = {'REGISTER', 'UNDO'}

    template_name: StringProperty(
        name="Template Name",
        description="Name for the armature template",
        default="MyArmature"
    )

    description: StringProperty(
        name="Description",
        description="Optional description for the template",
        default=""
    )

    def invoke(self, context, event):
        # Check if armature is selected
        if not context.active_object or context.active_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature object")
            return {'CANCELLED'}

        # Default name from armature
        self.template_name = context.active_object.name

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "template_name")
        layout.prop(self, "description")

    def execute(self, context):
        armature_obj = context.active_object

        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected")
            return {'CANCELLED'}

        # Save template
        success, message, filepath = save_armature_template(
            armature_obj=armature_obj,
            template_name=self.template_name,
            description=self.description
        )

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_LoadArmatureTemplate(Operator):
    """Load armature template from file"""
    bl_idname = "crossrig.load_armature_template"
    bl_label = "Load Armature Template"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(
        name="File Path",
        description="Path to armature template file",
        subtype='FILE_PATH'
    )

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    apply_mixamo_fix: BoolProperty(
        name="Apply Mixamo Fix",
        description="Apply rotation X=90° and scale 0.01 (for Mixamo FBX imports)",
        default=False
    )

    rotation_x: FloatProperty(
        name="Rotation X",
        description="Rotation around X axis in degrees",
        default=90.0,
        min=-360.0,
        max=360.0,
        subtype='ANGLE'
    )

    uniform_scale: FloatProperty(
        name="Scale",
        description="Uniform scale factor",
        default=0.01,
        min=0.0001,
        max=100.0
    )

    def invoke(self, context, event):
        # Open file browser
        template_dir = get_armature_template_directory()
        self.filepath = str(template_dir)

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "apply_mixamo_fix")

        if self.apply_mixamo_fix:
            box = layout.box()
            box.label(text="Mixamo Adjustments:")
            box.prop(self, "rotation_x")
            box.prop(self, "uniform_scale")

    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}

        # Get cursor location or use origin
        cursor_location = context.scene.cursor.location.copy()

        # Calculate rotation and scale
        if self.apply_mixamo_fix:
            rotation = (math.radians(self.rotation_x), 0.0, 0.0)
            scale = (self.uniform_scale, self.uniform_scale, self.uniform_scale)
        else:
            rotation = (0.0, 0.0, 0.0)
            scale = (1.0, 1.0, 1.0)

        # Load and create armature
        success, message, armature_obj = load_and_create_armature_template(
            filepath=self.filepath,
            location=tuple(cursor_location),
            rotation=rotation,
            scale=scale
        )

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_LoadArmatureTemplateMenu(Operator):
    """Quick load armature template from menu"""
    bl_idname = "crossrig.load_armature_template_menu"
    bl_label = "Quick Load Armature"
    bl_options = {'REGISTER', 'UNDO'}

    def get_template_items(self, context):
        """Generate enum items for available templates."""
        templates = list_available_armature_templates()

        if not templates:
            return [('NONE', 'No templates found', 'Create a template first')]

        items = []
        for name, filepath in templates:
            items.append((filepath, name, f"Load armature template: {name}"))

        return items

    template: EnumProperty(
        name="Template",
        description="Select armature template to load",
        items=get_template_items
    )

    apply_mixamo_fix: BoolProperty(
        name="Apply Mixamo Fix",
        description="Apply rotation X=90° and scale 0.01 (for Mixamo FBX imports)",
        default=False
    )

    rotation_x: FloatProperty(
        name="Rotation X",
        description="Rotation around X axis in degrees",
        default=90.0,
        min=-360.0,
        max=360.0
    )

    uniform_scale: FloatProperty(
        name="Scale",
        description="Uniform scale factor",
        default=0.01,
        min=0.0001,
        max=100.0
    )

    def invoke(self, context, event):
        templates = list_available_armature_templates()
        if not templates:
            self.report({'WARNING'}, "No armature templates found")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "template", text="")

        layout.separator()
        layout.prop(self, "apply_mixamo_fix")

        if self.apply_mixamo_fix:
            box = layout.box()
            box.label(text="Mixamo Adjustments:")
            box.prop(self, "rotation_x", text="Rotation X (degrees)")
            box.prop(self, "uniform_scale", text="Scale")

    def execute(self, context):
        if self.template == 'NONE':
            self.report({'WARNING'}, "No template selected")
            return {'CANCELLED'}

        # Get cursor location
        cursor_location = context.scene.cursor.location.copy()

        # Calculate rotation and scale
        if self.apply_mixamo_fix:
            rotation = (math.radians(self.rotation_x), 0.0, 0.0)
            scale = (self.uniform_scale, self.uniform_scale, self.uniform_scale)
        else:
            rotation = (0.0, 0.0, 0.0)
            scale = (1.0, 1.0, 1.0)

        # Load template
        success, message, armature_obj = load_and_create_armature_template(
            filepath=self.template,
            location=tuple(cursor_location),
            rotation=rotation,
            scale=scale
        )

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_LoadArmatureTemplateToMesh(Operator):
    """Load armature template and parent to selected mesh"""
    bl_idname = "crossrig.load_armature_template_to_mesh"
    bl_label = "Load Armature to Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def get_template_items(self, context):
        """Generate enum items for available templates."""
        templates = list_available_armature_templates()

        if not templates:
            return [('NONE', 'No templates found', 'Create a template first')]

        items = []
        for name, filepath in templates:
            items.append((filepath, name, f"Load and parent: {name}"))

        return items

    template: EnumProperty(
        name="Template",
        description="Select armature template",
        items=get_template_items
    )

    apply_mixamo_fix: BoolProperty(
        name="Apply Mixamo Fix",
        description="Apply rotation X=90° and scale 0.01 (for Mixamo FBX imports)",
        default=False
    )

    rotation_x: FloatProperty(
        name="Rotation X",
        description="Rotation around X axis in degrees",
        default=90.0,
        min=-360.0,
        max=360.0
    )

    uniform_scale: FloatProperty(
        name="Scale",
        description="Uniform scale factor",
        default=0.01,
        min=0.0001,
        max=100.0
    )

    def invoke(self, context, event):
        # Check if mesh is selected
        if not context.active_object or context.active_object.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        templates = list_available_armature_templates()
        if not templates:
            self.report({'WARNING'}, "No armature templates found")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Target mesh: {context.active_object.name}")
        layout.prop(self, "template", text="Template")

        layout.separator()
        layout.prop(self, "apply_mixamo_fix")

        if self.apply_mixamo_fix:
            box = layout.box()
            box.label(text="Mixamo Adjustments:")
            box.prop(self, "rotation_x", text="Rotation X (degrees)")
            box.prop(self, "uniform_scale", text="Scale")

    def execute(self, context):
        mesh_obj = context.active_object

        if not mesh_obj or mesh_obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        if self.template == 'NONE':
            self.report({'WARNING'}, "No template selected")
            return {'CANCELLED'}

        # Calculate rotation and scale
        if self.apply_mixamo_fix:
            rotation = (math.radians(self.rotation_x), 0.0, 0.0)
            scale = (self.uniform_scale, self.uniform_scale, self.uniform_scale)
        else:
            rotation = (0.0, 0.0, 0.0)
            scale = (1.0, 1.0, 1.0)

        # Create armature at mesh location with transforms
        success, message, armature_obj = load_and_create_armature_template(
            filepath=self.template,
            location=tuple(mesh_obj.location),
            rotation=rotation,
            scale=scale
        )

        if not success or not armature_obj:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

        try:
            # Parent mesh to armature with automatic weights
            bpy.context.view_layer.objects.active = armature_obj
            mesh_obj.select_set(True)
            armature_obj.select_set(True)

            # Set armature as parent with automatic weights
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')

            message += f"\nParented to mesh: {mesh_obj.name}"
            self.report({'INFO'}, message)
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Armature created but parenting failed: {str(e)}")
            return {'CANCELLED'}


class CROSSRIG_OT_DeleteArmatureTemplate(Operator):
    """Delete armature template"""
    bl_idname = "crossrig.delete_armature_template"
    bl_label = "Delete Armature Template"
    bl_options = {'REGISTER', 'UNDO'}

    def get_template_items(self, context):
        """Generate enum items for available templates."""
        templates = list_available_armature_templates()

        if not templates:
            return [('NONE', 'No templates found', '')]

        items = []
        for name, filepath in templates:
            items.append((filepath, name, f"Delete: {name}"))

        return items

    template: EnumProperty(
        name="Template",
        description="Select template to delete",
        items=get_template_items
    )

    def invoke(self, context, event):
        templates = list_available_armature_templates()
        if not templates:
            self.report({'WARNING'}, "No templates found")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text="WARNING: This cannot be undone!", icon='ERROR')
        layout.prop(self, "template", text="")

    def execute(self, context):
        if self.template == 'NONE':
            self.report({'WARNING'}, "No template selected")
            return {'CANCELLED'}

        # Delete template
        success, message = delete_armature_template_file(self.template)

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_OpenArmatureTemplateFolder(Operator):
    """Open armature template folder in system file browser"""
    bl_idname = "crossrig.open_armature_template_folder"
    bl_label = "Open Armature Template Folder"

    def execute(self, context):
        template_dir = get_armature_template_directory()

        try:
            system = platform.system()

            if system == "Windows":
                os.startfile(str(template_dir))
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(template_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(template_dir)])

            self.report({'INFO'}, f"Opened: {template_dir}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to open folder: {str(e)}")
            return {'CANCELLED'}


# Registration
classes = (
    MIXAMO_OT_SaveArmatureTemplate,
    MIXAMO_OT_LoadArmatureTemplate,
    MIXAMO_OT_LoadArmatureTemplateMenu,
    MIXAMO_OT_LoadArmatureTemplateToMesh,
    MIXAMO_OT_DeleteArmatureTemplate,
    MIXAMO_OT_OpenArmatureTemplateFolder,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
