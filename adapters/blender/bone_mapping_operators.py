"""
Blender operators for bone mapping system.

Provides UI operators for creating, editing, saving, and applying bone mappings.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty, FloatProperty
import os
import subprocess
import platform

from ...core.use_cases.create_bone_mapping import (
    create_bone_mapping_from_armatures,
    get_source_bones_for_mapping,
    get_target_bones_for_mapping
)
from ...core.use_cases.auto_map_bones import auto_map_bones
from ...core.use_cases.apply_animation_with_mapping import (
    apply_animation_with_bone_mapping,
    load_and_apply_animation_with_mapping,
    validate_bone_mapping_for_animation
)
from ...core.services.bone_mapping_service import (
    save_bone_mapping_to_file,
    load_bone_mapping_from_file,
    list_available_bone_mappings,
    delete_bone_mapping_file,
    get_bone_mapping_directory,
    validate_bone_mapping_preset
)
from ...core.services.animation_data_service import (
    list_available_animations,
    load_animation_data_from_file
)
from ...core.domain.bone_mapping_entities import BoneMappingPreset, BoneMapping


class CROSSRIG_OT_CreateBoneMapping(Operator):
    """Create bone mapping from source and target armatures"""
    bl_idname = "crossrig.create_bone_mapping"
    bl_label = "Create Bone Mapping"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings

        source_arm = settings.bone_mapping_source_armature
        target_arm = settings.bone_mapping_target_armature

        if not source_arm:
            self.report({'ERROR'}, "Please select source armature")
            return {'CANCELLED'}

        if not target_arm:
            self.report({'ERROR'}, "Please select target armature")
            return {'CANCELLED'}

        if source_arm == target_arm:
            self.report({'ERROR'}, "Source and target armatures must be different")
            return {'CANCELLED'}

        # Create bone mapping preset
        success, message, mapping_preset = create_bone_mapping_from_armatures(
            source_arm,
            target_arm,
            preset_name=settings.bone_mapping_preset_name,
            description=""
        )

        if not success:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

        # Populate UI collection with empty mappings
        settings.bone_mappings.clear()

        # Get source bones
        success, msg, source_bones = get_source_bones_for_mapping(source_arm)
        if not success:
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}

        # Add empty mappings for each source bone
        for bone_name in source_bones:
            item = settings.bone_mappings.add()
            item.source_bone = bone_name
            item.target_bone = ""  # Empty - to be filled by user or auto-mapping
            item.confidence = 0.0

        self.report({'INFO'}, f"Created bone mapping: {len(source_bones)} bones ready for mapping")
        return {'FINISHED'}


class CROSSRIG_OT_AutoMapBones(Operator):
    """Automatically map bones using fuzzy name matching"""
    bl_idname = "crossrig.auto_map_bones"
    bl_label = "Auto-Map Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings

        source_arm = settings.bone_mapping_source_armature
        target_arm = settings.bone_mapping_target_armature

        if not source_arm or not target_arm:
            self.report({'ERROR'}, "Please select both source and target armatures")
            return {'CANCELLED'}

        # Get bone lists
        success, msg, source_bones = get_source_bones_for_mapping(source_arm)
        if not success:
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}

        success, msg, target_bones = get_target_bones_for_mapping(target_arm)
        if not success:
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}

        # Create temporary preset from UI collection
        mapping_preset = BoneMappingPreset(
            name=settings.bone_mapping_preset_name or f"{source_arm.name}_to_{target_arm.name}",
            source_armature_name=source_arm.name,
            target_armature_name=target_arm.name,
            source_bone_count=len(source_bones),
            target_bone_count=len(target_bones)
        )

        # Preserve existing manual mappings
        for item in settings.bone_mappings:
            if item.target_bone and item.target_bone.strip():
                if item.confidence >= 1.0:  # Manual mapping
                    mapping_preset.add_mapping(item.source_bone, item.target_bone, item.confidence)

        # Auto-map
        success, message, updated_preset = auto_map_bones(
            mapping_preset,
            source_bones,
            target_bones,
            threshold=settings.auto_map_threshold,
            preserve_existing=True
        )

        if not success:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

        # Update UI collection with auto-mapped results
        for item in settings.bone_mappings:
            target_bone = updated_preset.find_target_bone(item.source_bone)
            if target_bone:
                item.target_bone = target_bone
                # Find confidence
                for mapping in updated_preset.mappings:
                    if mapping.source_bone == item.source_bone:
                        item.confidence = mapping.confidence
                        break

        self.report({'INFO'}, message)
        return {'FINISHED'}


class CROSSRIG_OT_SaveBoneMapping(Operator):
    """Save bone mapping preset to file"""
    bl_idname = "crossrig.save_bone_mapping"
    bl_label = "Save Bone Mapping"
    bl_options = {'REGISTER', 'UNDO'}

    preset_name: StringProperty(
        name="Preset Name",
        description="Name for the bone mapping preset",
        default=""
    )

    description: StringProperty(
        name="Description",
        description="Optional description",
        default=""
    )

    def invoke(self, context, event):
        settings = context.scene.crossrig_settings

        # Default name
        if settings.bone_mapping_preset_name:
            self.preset_name = settings.bone_mapping_preset_name
        elif settings.bone_mapping_source_armature and settings.bone_mapping_target_armature:
            self.preset_name = f"{settings.bone_mapping_source_armature.name}_to_{settings.bone_mapping_target_armature.name}"

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")
        layout.prop(self, "description")

    def execute(self, context):
        settings = context.scene.crossrig_settings

        if not self.preset_name or not self.preset_name.strip():
            self.report({'ERROR'}, "Please enter a preset name")
            return {'CANCELLED'}

        if not settings.bone_mapping_source_armature or not settings.bone_mapping_target_armature:
            self.report({'ERROR'}, "Please select both source and target armatures")
            return {'CANCELLED'}

        # Create preset from UI collection
        mapping_preset = BoneMappingPreset(
            name=self.preset_name,
            source_armature_name=settings.bone_mapping_source_armature.name,
            target_armature_name=settings.bone_mapping_target_armature.name,
            description=self.description
        )

        # Add mappings
        for item in settings.bone_mappings:
            if item.target_bone and item.target_bone.strip():
                mapping_preset.add_mapping(
                    item.source_bone,
                    item.target_bone,
                    item.confidence
                )

        # Validate
        is_valid, msg = validate_bone_mapping_preset(mapping_preset)
        if not is_valid:
            self.report({'ERROR'}, f"Validation failed: {msg}")
            return {'CANCELLED'}

        # Save
        success, message = save_bone_mapping_to_file(mapping_preset)

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_LoadBoneMapping(Operator):
    """Load bone mapping preset from file"""
    bl_idname = "crossrig.load_bone_mapping"
    bl_label = "Load Bone Mapping"
    bl_options = {'REGISTER', 'UNDO'}

    def get_mapping_items(self, context):
        """Get available bone mapping presets."""
        items = []
        mappings = list_available_bone_mappings()

        for name, filepath in mappings:
            items.append((filepath, name, f"Load mapping: {name}"))

        if not items:
            items.append(('NONE', 'No mappings found', ''))

        return items

    mapping_preset: EnumProperty(
        name="Bone Mapping Preset",
        description="Select bone mapping preset to load",
        items=get_mapping_items
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "mapping_preset")

    def execute(self, context):
        if self.mapping_preset == 'NONE':
            self.report({'ERROR'}, "No bone mapping preset selected")
            return {'CANCELLED'}

        # Load mapping preset
        success, message, mapping_preset = load_bone_mapping_from_file(self.mapping_preset)

        if not success:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

        settings = context.scene.crossrig_settings

        # Clear current mappings
        settings.bone_mappings.clear()

        # Populate UI collection
        for mapping in mapping_preset.mappings:
            item = settings.bone_mappings.add()
            item.source_bone = mapping.source_bone
            item.target_bone = mapping.target_bone
            item.confidence = mapping.confidence

        # Set preset name
        settings.bone_mapping_preset_name = mapping_preset.name

        self.report({'INFO'}, f"Loaded mapping: {mapping_preset.name} ({mapping_preset.mapped_count} mappings)")
        return {'FINISHED'}


class CROSSRIG_OT_LoadBoneMappingMenu(Operator):
    """Quick load bone mapping from menu"""
    bl_idname = "crossrig.load_bone_mapping_menu"
    bl_label = "Browse Bone Mappings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Just call the full load operator
        bpy.ops.mixamo.load_bone_mapping('INVOKE_DEFAULT')
        return {'FINISHED'}


class CROSSRIG_OT_DeleteBoneMapping(Operator):
    """Delete bone mapping preset file"""
    bl_idname = "crossrig.delete_bone_mapping"
    bl_label = "Delete Bone Mapping"
    bl_options = {'REGISTER', 'UNDO'}

    def get_mapping_items(self, context):
        """Get available bone mapping presets."""
        items = []
        mappings = list_available_bone_mappings()

        for name, filepath in mappings:
            items.append((filepath, name, f"Delete mapping: {name}"))

        if not items:
            items.append(('NONE', 'No mappings found', ''))

        return items

    mapping_preset: EnumProperty(
        name="Bone Mapping Preset",
        description="Select bone mapping preset to delete",
        items=get_mapping_items
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="⚠️ This action cannot be undone", icon='ERROR')
        layout.prop(self, "mapping_preset")

    def execute(self, context):
        if self.mapping_preset == 'NONE':
            self.report({'ERROR'}, "No bone mapping preset selected")
            return {'CANCELLED'}

        success, message = delete_bone_mapping_file(self.mapping_preset)

        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_ClearBoneMappings(Operator):
    """Clear all bone mappings from current list"""
    bl_idname = "crossrig.clear_bone_mappings"
    bl_label = "Clear Mappings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings
        settings.bone_mappings.clear()
        self.report({'INFO'}, "Bone mappings cleared")
        return {'FINISHED'}


class CROSSRIG_OT_AddBoneMapping(Operator):
    """Add individual bone mapping"""
    bl_idname = "crossrig.add_bone_mapping"
    bl_label = "Add Bone Mapping"
    bl_options = {'REGISTER', 'UNDO'}

    source_bone: StringProperty(
        name="Source Bone",
        description="Source bone name"
    )

    target_bone: StringProperty(
        name="Target Bone",
        description="Target bone name"
    )

    def execute(self, context):
        settings = context.scene.crossrig_settings

        if not self.source_bone or not self.target_bone:
            self.report({'ERROR'}, "Both source and target bones must be specified")
            return {'CANCELLED'}

        # Check if mapping already exists
        for item in settings.bone_mappings:
            if item.source_bone == self.source_bone:
                item.target_bone = self.target_bone
                item.confidence = 1.0  # Manual mapping
                self.report({'INFO'}, f"Updated mapping: {self.source_bone} → {self.target_bone}")
                return {'FINISHED'}

        # Add new mapping
        item = settings.bone_mappings.add()
        item.source_bone = self.source_bone
        item.target_bone = self.target_bone
        item.confidence = 1.0  # Manual mapping

        self.report({'INFO'}, f"Added mapping: {self.source_bone} → {self.target_bone}")
        return {'FINISHED'}


class CROSSRIG_OT_RemoveBoneMapping(Operator):
    """Remove bone mapping from list"""
    bl_idname = "crossrig.remove_bone_mapping"
    bl_label = "Remove Bone Mapping"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.crossrig_settings

        if settings.bone_mapping_index >= 0 and settings.bone_mapping_index < len(settings.bone_mappings):
            settings.bone_mappings.remove(settings.bone_mapping_index)
            settings.bone_mapping_index = max(0, settings.bone_mapping_index - 1)
            self.report({'INFO'}, "Removed bone mapping")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No bone mapping selected")
            return {'CANCELLED'}


class CROSSRIG_OT_ApplyAnimationWithMapping(Operator):
    """Apply animation to armature using bone mapping"""
    bl_idname = "crossrig.apply_animation_with_mapping"
    bl_label = "Apply Animation with Mapping"
    bl_options = {'REGISTER', 'UNDO'}

    def get_animation_items(self, context):
        """Get available saved animations."""
        items = []
        animations = list_available_animations()

        for name, filepath in animations:
            items.append((filepath, name, f"Apply animation: {name}"))

        if not items:
            items.append(('NONE', 'No animations found', ''))

        return items

    animation_file: EnumProperty(
        name="Animation",
        description="Select animation to apply",
        items=get_animation_items
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "animation_file")

    def execute(self, context):
        settings = context.scene.crossrig_settings

        if self.animation_file == 'NONE':
            self.report({'ERROR'}, "No animation selected")
            return {'CANCELLED'}

        target_arm = settings.bone_mapping_target_armature
        if not target_arm:
            self.report({'ERROR'}, "Please select target armature")
            return {'CANCELLED'}

        # Create mapping preset from UI collection
        if not settings.bone_mapping_source_armature:
            self.report({'ERROR'}, "Please select source armature")
            return {'CANCELLED'}

        mapping_preset = BoneMappingPreset(
            name=settings.bone_mapping_preset_name or "temp_mapping",
            source_armature_name=settings.bone_mapping_source_armature.name,
            target_armature_name=target_arm.name
        )

        # Add mappings
        for item in settings.bone_mappings:
            if item.target_bone and item.target_bone.strip():
                mapping_preset.add_mapping(
                    item.source_bone,
                    item.target_bone,
                    item.confidence
                )

        if not mapping_preset.mappings:
            self.report({'ERROR'}, "No bone mappings defined")
            return {'CANCELLED'}

        # Load animation
        success, msg, anim_data = load_animation_data_from_file(self.animation_file)
        if not success:
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}

        # Apply with mapping
        success, message, warnings = apply_animation_with_bone_mapping(
            target_arm,
            anim_data,
            mapping_preset
        )

        if success:
            self.report({'INFO'}, message)
            if warnings:
                print("\nWarnings:")
                for warning in warnings:
                    print(f"  - {warning}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}


class CROSSRIG_OT_ValidateBoneMapping(Operator):
    """Validate bone mapping against animation and target armature"""
    bl_idname = "crossrig.validate_bone_mapping"
    bl_label = "Validate Mapping"
    bl_options = {'REGISTER'}

    def get_animation_items(self, context):
        """Get available saved animations."""
        items = []
        animations = list_available_animations()

        for name, filepath in animations:
            items.append((filepath, name, f"Validate against: {name}"))

        if not items:
            items.append(('NONE', 'No animations found', ''))

        return items

    animation_file: EnumProperty(
        name="Animation",
        description="Select animation to validate against",
        items=get_animation_items
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "animation_file")

    def execute(self, context):
        settings = context.scene.crossrig_settings

        if self.animation_file == 'NONE':
            self.report({'ERROR'}, "No animation selected")
            return {'CANCELLED'}

        target_arm = settings.bone_mapping_target_armature
        if not target_arm:
            self.report({'ERROR'}, "Please select target armature")
            return {'CANCELLED'}

        # Create mapping preset
        if not settings.bone_mapping_source_armature:
            self.report({'ERROR'}, "Please select source armature")
            return {'CANCELLED'}

        mapping_preset = BoneMappingPreset(
            name=settings.bone_mapping_preset_name or "temp_mapping",
            source_armature_name=settings.bone_mapping_source_armature.name,
            target_armature_name=target_arm.name
        )

        for item in settings.bone_mappings:
            if item.target_bone and item.target_bone.strip():
                mapping_preset.add_mapping(
                    item.source_bone,
                    item.target_bone,
                    item.confidence
                )

        # Load animation
        success, msg, anim_data = load_animation_data_from_file(self.animation_file)
        if not success:
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}

        # Validate
        is_valid, message, validation = validate_bone_mapping_for_animation(
            anim_data,
            mapping_preset,
            target_arm
        )

        # Report results
        print("\n" + "="*50)
        print("BONE MAPPING VALIDATION")
        print("="*50)
        print(message)
        print(f"\nValid mappings: {len(validation['valid_mappings'])}")
        print(f"Unmapped bones: {len(validation['unmapped_bones'])}")
        print(f"Missing target bones: {len(validation['missing_target_bones'])}")

        if validation['unmapped_bones']:
            print("\nUnmapped bones:")
            for bone in validation['unmapped_bones']:
                print(f"  - {bone}")

        if validation['missing_target_bones']:
            print("\nMissing target bones:")
            for mapping in validation['missing_target_bones']:
                print(f"  - {mapping}")

        print("="*50 + "\n")

        if is_valid:
            self.report({'INFO'}, "✅ Validation passed: " + message)
        else:
            self.report({'WARNING'}, "⚠️ Validation issues found - check console for details")

        return {'FINISHED'}


class CROSSRIG_OT_OpenBoneMappingFolder(Operator):
    """Open bone mapping folder in file explorer"""
    bl_idname = "crossrig.open_bone_mapping_folder"
    bl_label = "Open Folder"
    bl_options = {'REGISTER'}

    def execute(self, context):
        mapping_dir = get_bone_mapping_directory()

        try:
            if platform.system() == "Windows":
                os.startfile(str(mapping_dir))
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", str(mapping_dir)])
            else:  # Linux
                subprocess.Popen(["xdg-open", str(mapping_dir)])

            self.report({'INFO'}, f"Opened folder: {mapping_dir}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to open folder: {str(e)}")
            return {'CANCELLED'}


# Classes to register
classes = (
    CROSSRIG_OT_CreateBoneMapping,
    CROSSRIG_OT_AutoMapBones,
    CROSSRIG_OT_SaveBoneMapping,
    CROSSRIG_OT_LoadBoneMapping,
    CROSSRIG_OT_LoadBoneMappingMenu,
    CROSSRIG_OT_DeleteBoneMapping,
    CROSSRIG_OT_ClearBoneMappings,
    CROSSRIG_OT_AddBoneMapping,
    CROSSRIG_OT_RemoveBoneMapping,
    CROSSRIG_OT_ApplyAnimationWithMapping,
    CROSSRIG_OT_ValidateBoneMapping,
    CROSSRIG_OT_OpenBoneMappingFolder,
)


def register():
    """Register operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister operator classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
