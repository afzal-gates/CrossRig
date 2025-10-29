"""
Use case for loading and recreating armature from template.

Creates a new armature object in Blender from template structure.
"""

from typing import Tuple, Optional
import bpy

from ..domain.armature_entities import ArmatureTemplate, BoneData
from ..services.armature_template_service import load_armature_template_from_file


def create_armature_from_template(
    template: ArmatureTemplate,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
) -> Tuple[bool, str, Optional[bpy.types.Object]]:
    """
    Create a new armature object from template.

    Args:
        template: ArmatureTemplate to recreate
        location: World location for the new armature
        rotation: Rotation in radians (X, Y, Z)
        scale: Scale factor (X, Y, Z)

    Returns:
        Tuple[bool, str, Optional[Object]]: (success, message, armature_object)
    """
    try:
        # Create armature data
        armature_data = bpy.data.armatures.new(name=template.name)

        # Create armature object
        armature_obj = bpy.data.objects.new(name=template.name, object_data=armature_data)

        # Link to scene collection
        bpy.context.collection.objects.link(armature_obj)

        # Set location, rotation, and scale
        armature_obj.location = location
        armature_obj.rotation_euler = rotation
        armature_obj.scale = scale

        # Apply armature display properties
        armature_data.display_type = template.display_type
        armature_data.show_names = template.show_names
        armature_data.show_axes = template.show_axes
        armature_obj.show_in_front = template.show_in_front

        # Set as active and enter EDIT mode to create bones
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')

        edit_bones = armature_data.edit_bones

        # Create all bones first (without parents)
        bone_map = {}
        for bone_data in template.bones:
            edit_bone = edit_bones.new(name=bone_data.name)
            bone_map[bone_data.name] = edit_bone

            # Set bone position and rotation
            edit_bone.head = bone_data.head
            edit_bone.tail = bone_data.tail
            edit_bone.roll = bone_data.roll

            # Set bone properties
            edit_bone.use_connect = False  # Set to False initially
            edit_bone.use_inherit_rotation = bone_data.use_inherit_rotation
            edit_bone.inherit_scale = bone_data.inherit_scale
            edit_bone.use_local_location = bone_data.use_local_location
            edit_bone.use_deform = bone_data.use_deform

            # Set layers (compatibility: Blender < 4.0 only)
            try:
                if hasattr(edit_bone, 'layers'):
                    edit_bone.layers = bone_data.layers
                # Blender 4.0+ uses collections instead, skip layers
            except AttributeError:
                pass  # Layers not supported in this Blender version

        # Now set up parent relationships
        for bone_data in template.bones:
            if bone_data.parent_name and bone_data.parent_name in bone_map:
                edit_bone = bone_map[bone_data.name]
                parent_bone = bone_map[bone_data.parent_name]
                edit_bone.parent = parent_bone
                edit_bone.use_connect = bone_data.use_connect

        # Return to OBJECT mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Apply custom properties to pose bones
        if armature_obj.pose:
            for bone_data in template.bones:
                if bone_data.custom_properties:
                    pose_bone = armature_obj.pose.bones.get(bone_data.name)
                    if pose_bone:
                        for key, value in bone_data.custom_properties.items():
                            try:
                                pose_bone[key] = value
                            except:
                                pass

        # Select the new armature
        bpy.ops.object.select_all(action='DESELECT')
        armature_obj.select_set(True)
        bpy.context.view_layer.objects.active = armature_obj

        bone_count = len(template.bones)
        message = f"Armature created: {template.name} ({bone_count} bones)"

        return (True, message, armature_obj)

    except Exception as e:
        return (False, f"Failed to create armature: {str(e)}", None)


def load_and_create_armature_template(
    filepath: str,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
) -> Tuple[bool, str, Optional[bpy.types.Object]]:
    """
    Load armature template from file and create armature in scene.

    Args:
        filepath: Path to template file
        location: World location for the new armature
        rotation: Rotation in radians (X, Y, Z)
        scale: Scale factor (X, Y, Z)

    Returns:
        Tuple[bool, str, Optional[Object]]: (success, message, armature_object)
    """
    # Load template from file
    success, message, template = load_armature_template_from_file(filepath)

    if not success or not template:
        return (False, message, None)

    # Create armature from template
    return create_armature_from_template(template, location, rotation, scale)


def load_armature_template_to_mesh(
    filepath: str,
    mesh_obj: bpy.types.Object
) -> Tuple[bool, str, Optional[bpy.types.Object]]:
    """
    Load armature template and parent it to a mesh object.

    Args:
        filepath: Path to template file
        mesh_obj: Mesh object to parent armature to

    Returns:
        Tuple[bool, str, Optional[Object]]: (success, message, armature_object)
    """
    # Validate mesh object
    if not mesh_obj or mesh_obj.type != 'MESH':
        return (False, "Target object is not a mesh", None)

    # Create armature at mesh location
    success, message, armature_obj = load_and_create_armature_template(
        filepath,
        location=mesh_obj.location
    )

    if not success or not armature_obj:
        return (False, message, None)

    try:
        # Parent mesh to armature with automatic weights
        bpy.context.view_layer.objects.active = armature_obj
        mesh_obj.select_set(True)
        armature_obj.select_set(True)

        # Set armature as parent with automatic weights
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        message += f"\nParented to mesh: {mesh_obj.name}"
        return (True, message, armature_obj)

    except Exception as e:
        return (False, f"Armature created but parenting failed: {str(e)}", armature_obj)
