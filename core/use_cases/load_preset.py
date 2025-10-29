"""
Use case: Load animation preset and apply to action collection.
"""

import bpy
from ..services.preset_service import load_preset_from_file


def find_action_by_name(action_name: str, available_actions: dict) -> str:
    """
    Find action in scene with smart matching for Mixamo naming patterns.

    Mixamo FBX imports create names like:
    - "Armature|mixamo.com|Layer0"
    - "Armature.001|mixamo.com|Layer0"
    - Or just plain action names

    This function tries multiple strategies:
    1. Exact match
    2. Match by animation name (part after "mixamo.com|")
    3. Match by partial name (contains animation name)
    4. Case-insensitive match

    Args:
        action_name: Action name to find
        available_actions: Dict of {action_name: action_object}

    Returns:
        str: Found action name, or None if not found
    """
    if not action_name or not available_actions:
        return None

    # Strategy 1: Exact match (fastest)
    if action_name in available_actions:
        return action_name

    # Extract animation name from Mixamo pattern
    def extract_animation_name(name: str) -> str:
        """Extract the animation name from Mixamo pattern."""
        if not name:
            return ""
        if "|mixamo.com|" in name:
            # Return the part after "mixamo.com|"
            return name.split("|mixamo.com|", 1)[-1]
        elif "|" in name:
            # Generic pattern: return part after last pipe
            return name.split("|")[-1]
        return name

    target_anim_name = extract_animation_name(action_name)

    # Strategy 2: Match by extracted animation name (exact)
    for available_name in available_actions.keys():
        available_anim_name = extract_animation_name(available_name)
        if target_anim_name and target_anim_name == available_anim_name:
            return available_name

    # Strategy 3: Partial match - target name contains available name or vice versa
    # This handles cases where one has prefix/suffix
    for available_name in available_actions.keys():
        available_anim_name = extract_animation_name(available_name)

        # Check if animation names match as substrings
        if target_anim_name and available_anim_name:
            if target_anim_name in available_anim_name or available_anim_name in target_anim_name:
                return available_name

    # Strategy 4: Case-insensitive match
    action_name_lower = action_name.lower()
    target_anim_name_lower = target_anim_name.lower()

    for available_name in available_actions.keys():
        if available_name.lower() == action_name_lower:
            return available_name

        available_anim_name = extract_animation_name(available_name)
        if available_anim_name.lower() == target_anim_name_lower:
            return available_name

    # Strategy 5: Fuzzy match - ignore armature prefix entirely
    # Match if the part after first "|" matches
    if "|" in action_name:
        target_suffix = action_name.split("|", 1)[-1]
        for available_name in available_actions.keys():
            if "|" in available_name:
                available_suffix = available_name.split("|", 1)[-1]
                if target_suffix == available_suffix:
                    return available_name

    # No match found
    return None


def load_animation_preset(filepath: str, action_collection, settings) -> tuple:
    """
    Load preset and apply to Blender action collection.

    Args:
        filepath: Path to preset file
        action_collection: Blender collection property to populate
        settings: MixamoUnifiedSettings object

    Returns:
        Tuple of (success: bool, message: str, actions_loaded: int, warnings: list)
    """
    # Load preset from file
    success, message, preset = load_preset_from_file(filepath)

    if not success:
        return (False, message, 0, [])

    # Build dictionary of available actions
    available_actions = {action.name: action for action in bpy.data.actions}
    warnings = []

    # Debug: Log available actions
    print(f"\n=== PRESET LOADING DEBUG ===")
    print(f"Preset: {preset.name}")
    print(f"Available actions in scene ({len(available_actions)}):")
    for action_name in sorted(available_actions.keys()):
        print(f"  - {action_name}")
    print(f"\nActions in preset ({len(preset.actions)}):")
    for preset_action in preset.actions:
        print(f"  - {preset_action.action_name}")
    print("=" * 40 + "\n")

    # Clear existing collection
    action_collection.clear()

    # Populate action collection from preset
    actions_loaded = 0
    missing_actions = []

    for preset_action in preset.actions:
        # Try to find action with smart matching
        found_action_name = find_action_by_name(preset_action.action_name, available_actions)

        if not found_action_name:
            missing_actions.append(preset_action.action_name)
            warnings.append(f"Action not found: {preset_action.action_name}")
            print(f"  ❌ Failed to find match for: {preset_action.action_name}")
            continue

        print(f"  ✅ Matched: '{preset_action.action_name}' → '{found_action_name}'")

        # Add to collection with the actual action name found in scene
        item = action_collection.add()
        item.action_name = found_action_name  # Use the found name, not preset name
        item.use_action = preset_action.use_action
        item.repeat_count = preset_action.repeat_count
        item.angle = preset_action.angle

        # Try to find armature for this action
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.animation_data:
                if obj.animation_data.action and obj.animation_data.action.name == found_action_name:
                    item.armature_name = obj.name
                    break

        actions_loaded += 1

    # Apply preset settings
    settings.root_bone = preset.root_bone
    settings.overlap_frames = preset.overlap_frames
    settings.forward_axis = preset.forward_axis
    settings.order_confirmed = False  # Reset confirmation

    # Build result message
    result_message = f"Preset '{preset.name}' loaded: {actions_loaded} actions"

    if missing_actions:
        result_message += f"\nWarning: {len(missing_actions)} actions not found in scene"

    if actions_loaded == 0:
        return (False, "No actions from preset found in scene", 0, warnings)

    return (True, result_message, actions_loaded, warnings)


def apply_preset_to_armature(armature, preset_filepath: str, context) -> tuple:
    """
    Load preset and apply it to a specific armature.

    Args:
        armature: Blender Armature object
        preset_filepath: Path to preset file
        context: Blender context

    Returns:
        Tuple of (success: bool, message: str)
    """
    if not armature or armature.type != 'ARMATURE':
        return (False, "Invalid armature object")

    # Set armature as active
    context.view_layer.objects.active = armature
    armature.select_set(True)

    # Get settings
    settings = context.scene.crossrig_settings

    # Load preset
    success, message, actions_loaded, warnings = load_animation_preset(
        preset_filepath,
        settings.action_collection,
        settings
    )

    return (success, message)
