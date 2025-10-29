"""
Use case for saving armature structure as template.

Extracts bone structure from Blender armature and saves as template.
"""

from typing import Tuple, Optional
import bpy

from ..domain.armature_entities import ArmatureTemplate, BoneData
from ..services.armature_template_service import (
    save_armature_template_to_file,
    validate_armature_template
)


def extract_armature_structure(armature_obj: bpy.types.Object) -> ArmatureTemplate:
    """
    Extract armature bone structure from Blender armature object.

    Args:
        armature_obj: Blender armature object

    Returns:
        ArmatureTemplate: Extracted armature structure
    """
    armature_data = armature_obj.data
    bones_data = []

    # We need to be in EDIT mode to access bone positions
    # Save current mode
    original_mode = armature_obj.mode if armature_obj.mode else 'OBJECT'
    original_active = bpy.context.view_layer.objects.active

    try:
        # Set as active and enter EDIT mode
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')

        # Extract bone data
        edit_bones = armature_data.edit_bones

        for bone in edit_bones:
            # Get parent name
            parent_name = bone.parent.name if bone.parent else None

            # Get layers (compatibility: Blender < 4.0 uses layers, >= 4.0 uses collections)
            try:
                if hasattr(bone, 'layers'):
                    bone_layers = list(bone.layers)
                else:
                    # Blender 4.0+: No layers attribute, use default
                    bone_layers = [True] + [False] * 31
            except AttributeError:
                bone_layers = [True] + [False] * 31

            # Extract bone properties
            bone_data = BoneData(
                name=bone.name,
                parent_name=parent_name,
                head=tuple(bone.head),
                tail=tuple(bone.tail),
                roll=bone.roll,
                use_connect=bone.use_connect,
                use_inherit_rotation=bone.use_inherit_rotation,
                inherit_scale=bone.inherit_scale,
                use_local_location=bone.use_local_location,
                use_deform=bone.use_deform,
                layers=bone_layers
            )

            # Extract custom properties
            if hasattr(bone, 'keys'):
                for key in bone.keys():
                    if key not in ['_RNA_UI']:
                        try:
                            bone_data.custom_properties[key] = bone[key]
                        except:
                            pass

            bones_data.append(bone_data)

    finally:
        # Restore original mode and active object
        bpy.ops.object.mode_set(mode='OBJECT')
        if original_active:
            bpy.context.view_layer.objects.active = original_active
        if original_mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode=original_mode)
            except:
                pass

    # Create template
    template = ArmatureTemplate(
        name=armature_obj.name,
        bones=bones_data,
        display_type=armature_data.display_type,
        show_names=armature_data.show_names,
        show_axes=armature_data.show_axes,
        show_in_front=armature_obj.show_in_front
    )

    return template


def save_armature_template(
    armature_obj: bpy.types.Object,
    template_name: str,
    description: str = ""
) -> Tuple[bool, str, Optional[str]]:
    """
    Save armature structure as template.

    Args:
        armature_obj: Blender armature object
        template_name: Name for the template
        description: Optional description

    Returns:
        Tuple[bool, str, Optional[str]]: (success, message, filepath)
    """
    # Validate input
    if not armature_obj or armature_obj.type != 'ARMATURE':
        return (False, "Selected object is not an armature", None)

    if not template_name or not template_name.strip():
        return (False, "Template name cannot be empty", None)

    try:
        # Extract armature structure
        template = extract_armature_structure(armature_obj)

        # Override name and description
        template.name = template_name.strip()
        template.description = description.strip()

        # Validate template
        valid, validation_message = validate_armature_template(template)
        if not valid:
            return (False, f"Validation failed: {validation_message}", None)

        # Save to file
        success, message = save_armature_template_to_file(template)

        if success:
            from ..services.armature_template_service import get_armature_template_directory, sanitize_filename
            template_dir = get_armature_template_directory()
            safe_name = sanitize_filename(template.name)
            filepath = str(template_dir / f"{safe_name}.json")
            return (True, message, filepath)
        else:
            return (False, message, None)

    except Exception as e:
        return (False, f"Failed to save armature template: {str(e)}", None)
