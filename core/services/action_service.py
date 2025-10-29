"""
Service layer for action manipulation.

These services contain business logic that interacts with Blender actions
but are separated from operators for better testability.
"""

from mathutils import Vector
from ..domain.math_utils import rotate_2d_point, is_rotation_needed
from ...config.constants import REPEAT_ACTION_SUFFIX


def get_local_location_at_frame(action, bone_name: str, frame: int) -> Vector:
    """
    Get bone's local location at specific frame from action fcurves.

    Args:
        action: Blender Action object
        bone_name: Name of the bone
        frame: Frame number to evaluate

    Returns:
        Vector containing the location at that frame
    """
    loc = [0.0, 0.0, 0.0]
    data_path = f'pose.bones["{bone_name}"].location'

    for fc in action.fcurves:
        if fc.data_path == data_path:
            idx = fc.array_index
            loc[idx] = fc.evaluate(frame)

    return Vector(loc)


def get_action_start_location_local(action, bone_name: str) -> Vector:
    """
    Get bone's location at action start frame.

    Args:
        action: Blender Action object
        bone_name: Name of the bone

    Returns:
        Vector of starting location
    """
    start_frame = int(action.frame_range[0])
    return get_local_location_at_frame(action, bone_name, start_frame)


def get_action_end_location_local(action, bone_name: str) -> Vector:
    """
    Get bone's location at action end frame.

    Args:
        action: Blender Action object
        bone_name: Name of the bone

    Returns:
        Vector of ending location
    """
    end_frame = int(action.frame_range[1])
    return get_local_location_at_frame(action, bone_name, end_frame)


def offset_action_root_local(action, bone_name: str, offset_vec: Vector):
    """
    Apply offset to all location keyframes of bone.

    Args:
        action: Blender Action object
        bone_name: Name of the root bone
        offset_vec: Vector to add to all keyframes
    """
    data_path = f'pose.bones["{bone_name}"].location'
    fcurves = [fc for fc in action.fcurves if fc.data_path == data_path]

    if fcurves:
        for i, fc in enumerate(fcurves):
            for kp in fc.keyframe_points:
                if i < len(offset_vec):
                    kp.co[1] += offset_vec[i]
            fc.update()


def create_action_copy(original_action, repeat_index: int = 1):
    """
    Create a copy of action with repeat suffix.

    Args:
        original_action: Blender Action to copy
        repeat_index: Index for naming (1, 2, 3...)

    Returns:
        New Blender Action object
    """
    new_action = original_action.copy()
    new_action.name = f"{original_action.name}{REPEAT_ACTION_SUFFIX}{repeat_index}"
    return new_action


def rotate_action_root_trajectory(action, bone_name: str, angle_deg: float, forward_axis: str = 'Y+'):
    """
    Rotate the root bone's location trajectory by specified angle.

    This applies a 2D rotation to the character's movement path,
    allowing animations to be directed in different directions.

    Args:
        action: Blender Action object containing animation data
        bone_name: Name of the root bone (e.g., "mixamorig:Hips")
        angle_deg: Rotation angle in degrees (positive = counter-clockwise)
        forward_axis: Character's forward direction ('Y+', 'X+', etc.)

    Note:
        - Rotation is applied in the XY plane (ground plane)
        - Z-axis (vertical) is preserved for jumps/crouches
        - All keyframes are processed to maintain trajectory shape
    """
    # Edge case: No rotation needed
    if not is_rotation_needed(angle_deg):
        return

    # Find location fcurves for root bone
    data_path = f'pose.bones["{bone_name}"].location'
    fcurves_dict = {}

    for fc in action.fcurves:
        if fc.data_path == data_path:
            fcurves_dict[fc.array_index] = fc

    # Need at least X and Y curves to rotate
    if 0 not in fcurves_dict or 1 not in fcurves_dict:
        return

    fc_x = fcurves_dict[0]
    fc_y = fcurves_dict[1]

    # Process all keyframes
    num_keyframes = min(len(fc_x.keyframe_points), len(fc_y.keyframe_points))

    for i in range(num_keyframes):
        kp_x = fc_x.keyframe_points[i]
        kp_y = fc_y.keyframe_points[i]

        # Extract original X, Y values
        x = kp_x.co[1]  # co[0] is frame, co[1] is value
        y = kp_y.co[1]

        # Apply 2D rotation
        x_new, y_new = rotate_2d_point(x, y, angle_deg)

        # Update keyframe values
        kp_x.co[1] = x_new
        kp_y.co[1] = y_new

    # Update fcurves to apply changes
    fc_x.update()
    fc_y.update()


def stabilize_root_bone_axes(action, bone_name: str, axes: list = [0, 1]) -> int:
    """
    Stabilize specified axes of root bone to origin (0, 0, 0).

    Args:
        action: Blender Action object
        bone_name: Name of the root bone
        axes: List of axis indices to stabilize (0=X, 1=Y, 2=Z)

    Returns:
        Number of keyframes stabilized
    """
    data_path = f'pose.bones["{bone_name}"].location'
    fcurves_dict = {}

    for fc in action.fcurves:
        if fc.data_path == data_path:
            fcurves_dict[fc.array_index] = fc

    if not fcurves_dict:
        return 0

    keyframe_count = 0

    for axis_index in axes:
        if axis_index in fcurves_dict:
            fc = fcurves_dict[axis_index]

            if fc.keyframe_points:
                # Set all keyframes to origin (0.0)
                fixed_value = 0.0

                for kp in fc.keyframe_points:
                    kp.co[1] = fixed_value
                    keyframe_count += 1

                fc.update()

    return keyframe_count
