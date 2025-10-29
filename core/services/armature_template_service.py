"""
Service layer for armature template file operations.

Handles saving, loading, listing, and deleting armature templates
with validation and error handling.
"""

from pathlib import Path
from typing import List, Tuple, Optional
import json
import re

from ..domain.armature_entities import ArmatureTemplate


def get_armature_template_directory() -> Path:
    """
    Get the directory where armature templates are stored.

    Returns:
        Path: Path to ~/.crossrig_armature_templates/
    """
    template_dir = Path.home() / ".crossrig_armature_templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    return template_dir


def sanitize_filename(name: str) -> str:
    """
    Sanitize template name for use as filename.

    Args:
        name: Template name to sanitize

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


def save_armature_template_to_file(
    template: ArmatureTemplate,
    filepath: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Save armature template to JSON file.

    Args:
        template: ArmatureTemplate to save
        filepath: Optional custom filepath. If None, uses default directory

    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        if filepath is None:
            template_dir = get_armature_template_directory()
            safe_name = sanitize_filename(template.name)
            filepath = template_dir / f"{safe_name}.json"
        else:
            filepath = Path(filepath)

        # Convert to JSON
        json_str = template.to_json()

        # Write to file
        filepath.write_text(json_str, encoding='utf-8')

        return (True, f"Armature template saved: {filepath.name}")

    except Exception as e:
        return (False, f"Failed to save template: {str(e)}")


def load_armature_template_from_file(filepath: str) -> Tuple[bool, str, Optional[ArmatureTemplate]]:
    """
    Load armature template from JSON file.

    Args:
        filepath: Path to template file

    Returns:
        Tuple[bool, str, Optional[ArmatureTemplate]]: (success, message, template)
    """
    try:
        filepath = Path(filepath)

        if not filepath.exists():
            return (False, f"Template file not found: {filepath.name}", None)

        # Read JSON
        json_str = filepath.read_text(encoding='utf-8')

        # Deserialize
        template = ArmatureTemplate.from_json(json_str)

        return (True, f"Template loaded: {template.name}", template)

    except json.JSONDecodeError as e:
        return (False, f"Invalid JSON format: {str(e)}", None)
    except Exception as e:
        return (False, f"Failed to load template: {str(e)}", None)


def list_available_armature_templates() -> List[Tuple[str, str]]:
    """
    List all available armature templates.

    Returns:
        List[Tuple[str, str]]: List of (template_name, filepath) tuples
    """
    template_dir = get_armature_template_directory()
    templates = []

    for filepath in template_dir.glob("*.json"):
        try:
            # Try to read template name from file
            json_str = filepath.read_text(encoding='utf-8')
            data = json.loads(json_str)
            template_name = data.get('name', filepath.stem)
            templates.append((template_name, str(filepath)))
        except Exception:
            # If file is invalid, use filename
            templates.append((filepath.stem, str(filepath)))

    return sorted(templates, key=lambda x: x[0])


def delete_armature_template_file(filepath: str) -> Tuple[bool, str]:
    """
    Delete armature template file.

    Args:
        filepath: Path to template file

    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        filepath = Path(filepath)

        if not filepath.exists():
            return (False, f"Template file not found: {filepath.name}")

        filepath.unlink()
        return (True, f"Template deleted: {filepath.name}")

    except Exception as e:
        return (False, f"Failed to delete template: {str(e)}")


def validate_armature_template(template: ArmatureTemplate) -> Tuple[bool, str]:
    """
    Validate armature template data.

    Args:
        template: ArmatureTemplate to validate

    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    # Check template name
    if not template.name or not template.name.strip():
        return (False, "Template name cannot be empty")

    # Check bones exist
    if not template.bones:
        return (False, "Template must contain at least one bone")

    # Check for duplicate bone names
    bone_names = [bone.name for bone in template.bones]
    if len(bone_names) != len(set(bone_names)):
        return (False, "Template contains duplicate bone names")

    # Validate bone hierarchy (parent references)
    bone_name_set = set(bone_names)
    for bone in template.bones:
        if bone.parent_name and bone.parent_name not in bone_name_set:
            return (False, f"Bone '{bone.name}' references non-existent parent '{bone.parent_name}'")

    # Check for circular dependencies (basic check)
    for bone in template.bones:
        if bone.parent_name == bone.name:
            return (False, f"Bone '{bone.name}' cannot be its own parent")

    return (True, "Template is valid")
