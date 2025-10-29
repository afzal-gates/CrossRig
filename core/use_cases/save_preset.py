"""
Use case: Save current animation sequence as preset.
"""

from ..domain.preset_entities import AnimationPreset, PresetActionItem
from ..services.preset_service import save_preset_to_file, validate_preset


def save_animation_preset(preset_name: str, description: str, action_items: list,
                          root_bone: str, overlap_frames: int, forward_axis: str) -> tuple:
    """
    Save current animation sequence as a preset.

    Args:
        preset_name: Name for the preset
        description: Optional description
        action_items: List of Blender action items (MixamoActionItem)
        root_bone: Root bone name
        overlap_frames: Overlap frames setting
        forward_axis: Forward axis setting

    Returns:
        Tuple of (success: bool, message: str, filepath: Optional[str])
    """
    # Convert Blender action items to preset action items
    preset_actions = []
    for item in action_items:
        if item.use_action:  # Only save enabled actions
            preset_action = PresetActionItem(
                action_name=item.action_name,
                use_action=item.use_action,
                repeat_count=item.repeat_count,
                angle=item.angle
            )
            preset_actions.append(preset_action)

    # Create preset entity
    preset = AnimationPreset(
        name=preset_name,
        description=description,
        root_bone=root_bone,
        overlap_frames=overlap_frames,
        forward_axis=forward_axis,
        actions=preset_actions
    )

    # Validate preset
    valid, validation_message = validate_preset(preset)
    if not valid:
        return (False, validation_message, None)

    # Save to file
    success, message = save_preset_to_file(preset)

    if success:
        # Extract filepath from message
        filepath = message.split(": ", 1)[1] if ": " in message else None
        return (True, f"Preset '{preset_name}' saved successfully", filepath)
    else:
        return (False, message, None)
