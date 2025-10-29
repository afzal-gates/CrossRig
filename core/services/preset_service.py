"""
Service layer for preset file operations.

Handles reading and writing preset files to disk.
"""

import os
import json
from pathlib import Path
from typing import List, Tuple, Optional
from ..domain.preset_entities import AnimationPreset


def get_preset_directory() -> Path:
    """
    Get the preset storage directory.

    Returns:
        Path to preset directory, creates it if doesn't exist
    """
    # Store presets in user's home directory under .crossrig_presets
    preset_dir = Path.home() / ".crossrig_presets"
    preset_dir.mkdir(parents=True, exist_ok=True)
    return preset_dir


def save_preset_to_file(preset: AnimationPreset, filepath: Optional[str] = None) -> Tuple[bool, str]:
    """
    Save preset to JSON file.

    Args:
        preset: AnimationPreset to save
        filepath: Optional custom filepath, otherwise uses preset name

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if filepath is None:
            preset_dir = get_preset_directory()
            # Sanitize preset name for filename
            safe_name = "".join(c for c in preset.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filepath = str(preset_dir / f"{safe_name}.json")

        # Convert to JSON and save
        json_data = preset.to_json()

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_data)

        return (True, f"Preset saved: {filepath}")

    except Exception as e:
        return (False, f"Failed to save preset: {str(e)}")


def load_preset_from_file(filepath: str) -> Tuple[bool, str, Optional[AnimationPreset]]:
    """
    Load preset from JSON file.

    Args:
        filepath: Path to preset file

    Returns:
        Tuple of (success: bool, message: str, preset: Optional[AnimationPreset])
    """
    try:
        if not os.path.exists(filepath):
            return (False, f"Preset file not found: {filepath}", None)

        with open(filepath, 'r', encoding='utf-8') as f:
            json_str = f.read()

        preset = AnimationPreset.from_json(json_str)
        return (True, f"Preset loaded: {preset.name}", preset)

    except json.JSONDecodeError as e:
        return (False, f"Invalid preset file format: {str(e)}", None)
    except Exception as e:
        return (False, f"Failed to load preset: {str(e)}", None)


def list_available_presets() -> List[Tuple[str, str]]:
    """
    List all available preset files.

    Returns:
        List of tuples (preset_name, filepath)
    """
    preset_dir = get_preset_directory()
    presets = []

    for filepath in preset_dir.glob("*.json"):
        try:
            # Quick load to get preset name
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                preset_name = data.get('name', filepath.stem)
                presets.append((preset_name, str(filepath)))
        except:
            # Skip invalid files
            continue

    return sorted(presets, key=lambda x: x[0])


def delete_preset_file(filepath: str) -> Tuple[bool, str]:
    """
    Delete a preset file.

    Args:
        filepath: Path to preset file to delete

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if not os.path.exists(filepath):
            return (False, f"Preset file not found: {filepath}")

        os.remove(filepath)
        return (True, f"Preset deleted: {filepath}")

    except Exception as e:
        return (False, f"Failed to delete preset: {str(e)}")


def validate_preset(preset: AnimationPreset) -> Tuple[bool, str]:
    """
    Validate preset data.

    Args:
        preset: AnimationPreset to validate

    Returns:
        Tuple of (valid: bool, message: str)
    """
    if not preset.name or not preset.name.strip():
        return (False, "Preset name cannot be empty")

    if not preset.actions:
        return (False, "Preset must contain at least one action")

    for action in preset.actions:
        if not action.action_name or not action.action_name.strip():
            return (False, "Action name cannot be empty")

        if action.repeat_count < 1 or action.repeat_count > 100:
            return (False, f"Invalid repeat count: {action.repeat_count} (must be 1-100)")

        if action.angle < -360 or action.angle > 360:
            return (False, f"Invalid angle: {action.angle} (must be -360 to 360)")

    if preset.overlap_frames < 0 or preset.overlap_frames > 100:
        return (False, f"Invalid overlap frames: {preset.overlap_frames} (must be 0-100)")

    return (True, "Preset is valid")
