"""
Service layer for bone mapping preset file operations.

Handles saving, loading, listing, and deleting bone mapping presets
with validation and error handling.
"""

from pathlib import Path
from typing import List, Tuple, Optional
import json
import re
import time

from ..domain.bone_mapping_entities import BoneMappingPreset

# Cache for mapping list to avoid repeated file I/O
_mapping_list_cache = None
_mapping_list_cache_time = 0
_CACHE_DURATION = 2.0  # Cache duration in seconds


def get_bone_mapping_directory() -> Path:
    """
    Get the directory where bone mapping presets are stored.

    Returns:
        Path: Path to ~/.crossrig_bone_mappings/
    """
    mapping_dir = Path.home() / ".crossrig_bone_mappings"
    mapping_dir.mkdir(parents=True, exist_ok=True)
    return mapping_dir


def sanitize_filename(name: str) -> str:
    """
    Sanitize mapping preset name for use as filename.

    Args:
        name: Preset name to sanitize

    Returns:
        str: Safe filename
    """
    # Remove or replace invalid filename characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip('. ')
    # Limit length
    safe_name = safe_name[:100]
    return safe_name


def invalidate_mapping_list_cache():
    """
    Invalidate the mapping list cache.

    Call this when mappings are added, deleted, or modified.
    """
    global _mapping_list_cache, _mapping_list_cache_time
    _mapping_list_cache = None
    _mapping_list_cache_time = 0


def save_bone_mapping_to_file(
    mapping_preset: BoneMappingPreset,
    filepath: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Save bone mapping preset to JSON file.

    Args:
        mapping_preset: BoneMappingPreset to save
        filepath: Optional custom filepath. If None, uses default directory

    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        # Update metadata before saving
        mapping_preset.update_metadata()

        if filepath is None:
            mapping_dir = get_bone_mapping_directory()
            safe_name = sanitize_filename(mapping_preset.name)
            filepath = mapping_dir / f"{safe_name}.json"
        else:
            filepath = Path(filepath)

        # Convert to JSON
        json_str = mapping_preset.to_json()

        # Write to file
        filepath.write_text(json_str, encoding='utf-8')

        # Invalidate cache so new mapping appears immediately
        invalidate_mapping_list_cache()

        return (True, f"Bone mapping saved: {filepath.name}")

    except Exception as e:
        return (False, f"Failed to save bone mapping: {str(e)}")


def load_bone_mapping_from_file(filepath: str) -> Tuple[bool, str, Optional[BoneMappingPreset]]:
    """
    Load bone mapping preset from JSON file.

    Args:
        filepath: Path to bone mapping preset file

    Returns:
        Tuple[bool, str, Optional[BoneMappingPreset]]: (success, message, mapping_preset)
    """
    try:
        filepath = Path(filepath)

        if not filepath.exists():
            return (False, f"Bone mapping file not found: {filepath.name}", None)

        # Read JSON
        json_str = filepath.read_text(encoding='utf-8')

        # Deserialize
        mapping_preset = BoneMappingPreset.from_json(json_str)

        return (True, f"Bone mapping loaded: {mapping_preset.name}", mapping_preset)

    except json.JSONDecodeError as e:
        return (False, f"Invalid JSON format: {str(e)}", None)
    except Exception as e:
        return (False, f"Failed to load bone mapping: {str(e)}", None)


def list_available_bone_mappings(use_cache: bool = True) -> List[Tuple[str, str]]:
    """
    List all available saved bone mapping presets with caching for performance.

    Args:
        use_cache: Whether to use cached results (default: True)

    Returns:
        List[Tuple[str, str]]: List of (preset_name, filepath) tuples
    """
    global _mapping_list_cache, _mapping_list_cache_time

    current_time = time.time()

    # Return cached result if valid
    if use_cache and _mapping_list_cache is not None:
        cache_age = current_time - _mapping_list_cache_time
        if cache_age < _CACHE_DURATION:
            return _mapping_list_cache

    # Rebuild cache
    mapping_dir = get_bone_mapping_directory()
    mappings = []

    for filepath in mapping_dir.glob("*.json"):
        try:
            # Try to read mapping name from file
            json_str = filepath.read_text(encoding='utf-8')
            data = json.loads(json_str)
            preset_name = data.get('name', filepath.stem)
            mappings.append((preset_name, str(filepath)))
        except Exception:
            # If file is invalid, use filename
            mappings.append((filepath.stem, str(filepath)))

    mappings = sorted(mappings, key=lambda x: x[0])

    # Update cache
    _mapping_list_cache = mappings
    _mapping_list_cache_time = current_time

    return mappings


def delete_bone_mapping_file(filepath: str) -> Tuple[bool, str]:
    """
    Delete bone mapping preset file.

    Args:
        filepath: Path to bone mapping preset file

    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        filepath = Path(filepath)

        if not filepath.exists():
            return (False, f"Bone mapping file not found: {filepath.name}")

        filepath.unlink()

        # Invalidate cache so deleted mapping disappears immediately
        invalidate_mapping_list_cache()

        return (True, f"Bone mapping deleted: {filepath.name}")

    except Exception as e:
        return (False, f"Failed to delete bone mapping: {str(e)}")


def validate_bone_mapping_preset(mapping_preset: BoneMappingPreset) -> Tuple[bool, str]:
    """
    Validate bone mapping preset.

    Args:
        mapping_preset: BoneMappingPreset to validate

    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    # Check preset name
    if not mapping_preset.name or not mapping_preset.name.strip():
        return (False, "Preset name cannot be empty")

    # Check source armature name
    if not mapping_preset.source_armature_name or not mapping_preset.source_armature_name.strip():
        return (False, "Source armature name cannot be empty")

    # Check target armature name
    if not mapping_preset.target_armature_name or not mapping_preset.target_armature_name.strip():
        return (False, "Target armature name cannot be empty")

    # Check has mappings
    if not mapping_preset.mappings:
        return (False, "Bone mapping must contain at least one bone mapping")

    # Check for duplicate source bones
    source_bones = [m.source_bone for m in mapping_preset.mappings]
    if len(source_bones) != len(set(source_bones)):
        return (False, "Duplicate source bone mappings found")

    # Check for empty bone names
    for mapping in mapping_preset.mappings:
        if not mapping.source_bone or not mapping.source_bone.strip():
            return (False, "Source bone name cannot be empty")
        if not mapping.target_bone or not mapping.target_bone.strip():
            return (False, "Target bone name cannot be empty")

    # Check confidence values
    for mapping in mapping_preset.mappings:
        if mapping.confidence < 0.0 or mapping.confidence > 1.0:
            return (False, f"Invalid confidence value for {mapping.source_bone}: {mapping.confidence}")

    return (True, "Bone mapping preset is valid")


def get_mapping_summary(mapping_preset: BoneMappingPreset) -> str:
    """
    Get a human-readable summary of a bone mapping preset.

    Args:
        mapping_preset: BoneMappingPreset to summarize

    Returns:
        str: Summary text
    """
    lines = [
        f"Mapping: {mapping_preset.name}",
        f"Source: {mapping_preset.source_armature_name}",
        f"Target: {mapping_preset.target_armature_name}",
        f"Mappings: {mapping_preset.mapped_count}",
    ]

    if mapping_preset.auto_mapped_count > 0:
        lines.append(f"Auto-mapped: {mapping_preset.auto_mapped_count}")

    if mapping_preset.description:
        lines.append(f"Description: {mapping_preset.description}")

    return "\n".join(lines)
