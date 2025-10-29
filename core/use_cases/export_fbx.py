"""
Use case: Export armature and animation as FBX file.
"""

import bpy
from ...config.constants import (
    FBX_AXIS_FORWARD,
    FBX_AXIS_UP,
    FBX_GLOBAL_SCALE,
    FBX_BAKE_ANIM_STEP,
    FBX_PRIMARY_BONE_AXIS,
    FBX_SECONDARY_BONE_AXIS
)


def export_armature_as_fbx(armature, filepath: str, include_mesh: bool, context) -> tuple:
    """
    Export armature with baked animation as FBX file.

    Args:
        armature: Blender Armature object
        filepath: Full path to save FBX file
        include_mesh: Whether to include mesh objects
        context: Blender context

    Returns:
        Tuple of (success: bool, message: str, object_count: int)
    """
    # Validate action exists
    if not armature.animation_data or not armature.animation_data.action:
        return (False, "No active action found. Bake the animation first", 0)

    # Ensure .fbx extension
    if not filepath.lower().endswith('.fbx'):
        filepath += '.fbx'

    action = armature.animation_data.action

    try:
        # Store current selection
        original_selection = context.selected_objects.copy()
        original_active = context.view_layer.objects.active

        # Select armature
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        context.view_layer.objects.active = armature

        objects_to_export = [armature]

        # Find and select mesh objects if requested
        if include_mesh:
            for obj in bpy.data.objects:
                # Check if object is a child of the armature
                if obj.parent == armature and obj.type == 'MESH':
                    obj.select_set(True)
                    objects_to_export.append(obj)
                # Check if object has armature modifier pointing to this armature
                elif obj.type == 'MESH':
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE' and modifier.object == armature:
                            obj.select_set(True)
                            objects_to_export.append(obj)
                            break

        # Determine object types to export
        object_types = {'ARMATURE', 'MESH'} if include_mesh else {'ARMATURE'}

        # Export FBX with game-ready settings
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=True,
            object_types=object_types,

            # Animation settings
            bake_anim=True,
            bake_anim_use_all_actions=False,
            bake_anim_use_nla_strips=False,
            bake_anim_step=FBX_BAKE_ANIM_STEP,
            bake_anim_simplify_factor=0.0,

            # Transform settings
            global_scale=FBX_GLOBAL_SCALE,
            apply_scale_options='FBX_SCALE_NONE',
            axis_forward=FBX_AXIS_FORWARD,
            axis_up=FBX_AXIS_UP,

            # Geometry settings
            use_mesh_modifiers=True,
            mesh_smooth_type='FACE',

            # Armature settings
            primary_bone_axis=FBX_PRIMARY_BONE_AXIS,
            secondary_bone_axis=FBX_SECONDARY_BONE_AXIS,
            armature_nodetype='NULL',
            bake_anim_use_all_bones=True,
            add_leaf_bones=False,

            # Other settings
            embed_textures=False,
            path_mode='AUTO',
            batch_mode='OFF'
        )

        # Restore selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in original_selection:
            obj.select_set(True)
        context.view_layer.objects.active = original_active

        # Build success message
        mesh_count = len([obj for obj in objects_to_export if obj.type == 'MESH'])
        if include_mesh and mesh_count > 0:
            message = f"Exported: {filepath} (Armature + {mesh_count} mesh(es), Action: {action.name})"
        else:
            message = f"Exported: {filepath} (Armature only, Action: {action.name})"

        return (True, message, len(objects_to_export))

    except Exception as e:
        return (False, f"Export failed: {str(e)}", 0)
