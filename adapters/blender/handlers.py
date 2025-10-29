"""
Blender event handlers for Mixanimo Lite.
"""

import bpy
from bpy.app.handlers import persistent


@persistent
def sync_selection_from_armature(scene):
    """
    Sync action list selection when armature's action changes.

    This handler updates the UI to highlight the active action.
    """
    prefs = bpy.context.scene.crossrig_settings
    arm = bpy.context.view_layer.objects.active

    if not arm or arm.type != 'ARMATURE':
        return
    if not arm.animation_data or not arm.animation_data.action:
        return

    current_action = arm.animation_data.action
    for i, item in enumerate(prefs.action_collection):
        if item.action_name == current_action.name:
            if prefs.action_index != i:
                prefs.action_index = i
            break


def register():
    """Register event handlers."""
    if sync_selection_from_armature not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(sync_selection_from_armature)


def unregister():
    """Unregister event handlers."""
    if sync_selection_from_armature in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(sync_selection_from_armature)
