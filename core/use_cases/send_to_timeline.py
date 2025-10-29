"""
Use case: Send actions to NLA timeline with sequencing and blending.
"""

from mathutils import Vector
from ..services.action_service import (
    create_action_copy,
    rotate_action_root_trajectory,
    get_action_start_location_local,
    get_action_end_location_local,
    offset_action_root_local
)


def send_actions_to_timeline(armature, actions_with_params: list, root_bone: str,
                             overlap_frames: int, forward_axis: str = 'Y+'):
    """
    Send multiple actions to NLA timeline with overlap blending.

    This is the main use case for sequencing animations in the NLA editor.

    Args:
        armature: Blender Armature object
        actions_with_params: List of tuples (action, repeat_count, angle_deg)
        root_bone: Name of the root bone (e.g., "mixamorig:Hips")
        overlap_frames: Number of frames to blend between actions
        forward_axis: Character's forward direction

    Note:
        - Clears existing animation data on armature
        - Creates new NLA tracks for each action
        - Applies rotation and offset to maintain continuity
        - Handles repeat counts by creating action copies
    """
    # Clear existing animation data
    if armature.animation_data:
        armature.animation_data_clear()
    armature.animation_data_create()

    prev_end_loc = Vector((0, 0, 0))
    current_start = 1
    track_index = 1

    for idx, (act, repeats, angle_deg) in enumerate(actions_with_params):
        track = armature.animation_data.nla_tracks.new()
        track.name = f"Track_{track_index}_{act.name}"
        track_index += 1

        for r in range(repeats):
            new_act = create_action_copy(act, repeat_index=r+1)
            length = int(new_act.frame_range[1] - new_act.frame_range[0])

            # Apply angle rotation if specified
            if abs(angle_deg) > 0.001:
                rotate_action_root_trajectory(new_act, root_bone, angle_deg, forward_axis)

            # Calculate strip timing
            if idx == 0 and r == 0:
                strip_start = current_start
            elif r == 0:
                strip_start = current_start - overlap_frames
                if strip_start < 1:
                    strip_start = 1
            else:
                strip_start = current_start

            strip_end = strip_start + length
            strip_start_int = int(round(strip_start))
            strip_end_int = int(round(strip_end))

            # Create NLA strip
            strip = track.strips.new(new_act.name, strip_start_int, new_act)
            strip.frame_start = strip_start_int
            strip.frame_end = strip_end_int

            # Set blending for transitions
            if idx > 0 and r == 0:
                strip.blend_in = overlap_frames
                strip.blend_out = 0
                strip.blend_type = 'REPLACE'
            else:
                strip.blend_in = 0
                strip.blend_out = 0

            # Apply offset for continuity
            start_loc = get_action_start_location_local(new_act, root_bone)
            if idx > 0 or r > 0:
                offset = prev_end_loc - start_loc
                offset_action_root_local(new_act, root_bone, offset)
            else:
                offset = Vector((0, 0, 0))

            prev_end_loc = get_action_end_location_local(new_act, root_bone)
            current_start = strip_end_int
