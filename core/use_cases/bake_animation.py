"""
Use case: Bake NLA animation into single action.
"""

import bpy


def bake_nla_to_action(armature, context) -> tuple:
    """
    Bake all NLA strips into a single action.

    Args:
        armature: Blender Armature object
        context: Blender context

    Returns:
        Tuple of (success: bool, message: str, action_name: str or None)
    """
    # Validate armature has NLA tracks
    if not armature.animation_data or not armature.animation_data.nla_tracks:
        return (False, "No NLA tracks found. Use 'Send to Timeline' first", None)

    # Find the overall frame range from all NLA strips
    min_frame = float('inf')
    max_frame = float('-inf')

    for track in armature.animation_data.nla_tracks:
        for strip in track.strips:
            min_frame = min(min_frame, strip.frame_start)
            max_frame = max(max_frame, strip.frame_end)

    if min_frame == float('inf') or max_frame == float('-inf'):
        return (False, "No NLA strips found", None)

    # Store original frame settings
    original_frame = context.scene.frame_current
    original_frame_start = context.scene.frame_start
    original_frame_end = context.scene.frame_end

    try:
        # Set scene frame range to match NLA range
        context.scene.frame_start = int(min_frame)
        context.scene.frame_end = int(max_frame)
        context.scene.frame_current = int(min_frame)

        # Create unique action name
        baked_action_name = "Baked_Animation"
        counter = 1
        while baked_action_name in bpy.data.actions:
            baked_action_name = f"Baked_Animation_{counter}"
            counter += 1

        # Store NLA state
        use_nla = armature.animation_data.use_nla
        use_tweak = armature.animation_data.use_tweak_mode

        # Enable NLA evaluation
        armature.animation_data.use_nla = True
        armature.animation_data.use_tweak_mode = False

        # Select all bones for baking
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')

        # Bake the animation
        bpy.ops.nla.bake(
            frame_start=int(min_frame),
            frame_end=int(max_frame),
            only_selected=False,
            visual_keying=True,
            clear_constraints=False,
            clear_parents=False,
            use_current_action=False,
            bake_types={'POSE'}
        )

        # Get the newly created action
        if armature.animation_data.action:
            armature.animation_data.action.name = baked_action_name
            baked_action = armature.animation_data.action
            message = f"Animation baked successfully: {baked_action_name} ({int(min_frame)}-{int(max_frame)} frames)"
            success = True
            result_action = baked_action_name
        else:
            message = "Baking completed but no action was created"
            success = False
            result_action = None

        # Restore NLA state
        armature.animation_data.use_nla = use_nla
        armature.animation_data.use_tweak_mode = use_tweak

    except Exception as e:
        message = f"Baking failed: {str(e)}"
        success = False
        result_action = None

    finally:
        # Restore original frame settings
        context.scene.frame_current = original_frame
        context.scene.frame_start = original_frame_start
        context.scene.frame_end = original_frame_end
        bpy.ops.object.mode_set(mode='OBJECT')

    return (success, message, result_action)
