"""
Service layer for animation data file operations.

Handles saving, loading, listing, and deleting animation data files
with validation and error handling.
"""

from pathlib import Path
from typing import List, Tuple, Optional
import json
import re
import time

from ..domain.animation_data_entities import AnimationData

# Cache for animation list to avoid repeated file I/O
_animation_list_cache = None
_animation_list_cache_time = 0
_CACHE_DURATION = 2.0  # Cache duration in seconds


def get_animation_data_directory() -> Path:
    """
    Get the directory where animation data is stored.

    Returns:
        Path: Path to ~/.crossrig_animations/
    """
    anim_dir = Path.home() / ".crossrig_animations"
    anim_dir.mkdir(parents=True, exist_ok=True)
    return anim_dir


def sanitize_filename(name: str) -> str:
    """
    Sanitize animation name for use as filename.

    Args:
        name: Animation name to sanitize

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


def invalidate_animation_list_cache():
    """
    Invalidate the animation list cache.

    Call this when animations are added, deleted, or modified.
    """
    global _animation_list_cache, _animation_list_cache_time
    _animation_list_cache = None
    _animation_list_cache_time = 0


def save_animation_data_to_file(
    anim_data: AnimationData,
    filepath: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Save animation data to JSON file.

    Args:
        anim_data: AnimationData to save
        filepath: Optional custom filepath. If None, uses default directory

    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        if filepath is None:
            anim_dir = get_animation_data_directory()
            safe_name = sanitize_filename(anim_data.name)
            filepath = anim_dir / f"{safe_name}.json"
        else:
            filepath = Path(filepath)

        # Convert to JSON
        json_str = anim_data.to_json()

        # Write to file
        filepath.write_text(json_str, encoding='utf-8')

        # Invalidate cache so new animation appears immediately
        invalidate_animation_list_cache()

        return (True, f"Animation saved: {filepath.name}")

    except Exception as e:
        return (False, f"Failed to save animation: {str(e)}")


def load_animation_data_from_file(filepath: str) -> Tuple[bool, str, Optional[AnimationData]]:
    """
    Load animation data from JSON file.

    Args:
        filepath: Path to animation data file

    Returns:
        Tuple[bool, str, Optional[AnimationData]]: (success, message, animation_data)
    """
    try:
        filepath = Path(filepath)

        if not filepath.exists():
            return (False, f"Animation file not found: {filepath.name}", None)

        # Read JSON
        json_str = filepath.read_text(encoding='utf-8')

        # Deserialize
        anim_data = AnimationData.from_json(json_str)

        return (True, f"Animation loaded: {anim_data.name}", anim_data)

    except json.JSONDecodeError as e:
        return (False, f"Invalid JSON format: {str(e)}", None)
    except Exception as e:
        return (False, f"Failed to load animation: {str(e)}", None)


def list_available_animations(use_cache: bool = True) -> List[Tuple[str, str]]:
    """
    List all available saved animations with caching for performance.

    Args:
        use_cache: Whether to use cached results (default: True)

    Returns:
        List[Tuple[str, str]]: List of (animation_name, filepath) tuples
    """
    global _animation_list_cache, _animation_list_cache_time

    current_time = time.time()

    # Return cached result if valid
    if use_cache and _animation_list_cache is not None:
        cache_age = current_time - _animation_list_cache_time
        if cache_age < _CACHE_DURATION:
            return _animation_list_cache

    # Rebuild cache
    anim_dir = get_animation_data_directory()
    animations = []

    for filepath in anim_dir.glob("*.json"):
        try:
            # Try to read animation name from file
            json_str = filepath.read_text(encoding='utf-8')
            data = json.loads(json_str)
            anim_name = data.get('name', filepath.stem)
            animations.append((anim_name, str(filepath)))
        except Exception:
            # If file is invalid, use filename
            animations.append((filepath.stem, str(filepath)))

    animations = sorted(animations, key=lambda x: x[0])

    # Update cache
    _animation_list_cache = animations
    _animation_list_cache_time = current_time

    return animations


def delete_animation_data_file(filepath: str) -> Tuple[bool, str]:
    """
    Delete animation data file.

    Args:
        filepath: Path to animation data file

    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        filepath = Path(filepath)

        if not filepath.exists():
            return (False, f"Animation file not found: {filepath.name}")

        filepath.unlink()

        # Invalidate cache so deleted animation disappears immediately
        invalidate_animation_list_cache()

        return (True, f"Animation deleted: {filepath.name}")

    except Exception as e:
        return (False, f"Failed to delete animation: {str(e)}")


def validate_animation_data(anim_data: AnimationData) -> Tuple[bool, str]:
    """
    Validate animation data.

    Args:
        anim_data: AnimationData to validate

    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    # Check animation name
    if not anim_data.name or not anim_data.name.strip():
        return (False, "Animation name cannot be empty")

    # Check has bones
    if not anim_data.bones:
        return (False, "Animation must contain at least one animated bone")

    # Check frame range
    if anim_data.frame_end <= anim_data.frame_start:
        return (False, "Invalid frame range: end must be after start")

    # Check bones have fcurves
    bones_with_fcurves = sum(1 for bone in anim_data.bones if bone.fcurves)
    if bones_with_fcurves == 0:
        return (False, "No animation curves found")

    return (True, "Animation data is valid")
