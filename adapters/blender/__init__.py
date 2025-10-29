"""
Blender adapters - UI integration layer.

This package contains all Blender-specific code (Properties, Operators, Panels).
"""

from . import properties
from . import operators
from . import preset_operators
from . import armature_template_operators
from . import animation_transfer_operators
from . import bone_mapping_operators
from . import panels
from . import handlers


def register():
    """Register all Blender adapter classes."""
    properties.register()
    operators.register()
    preset_operators.register()
    armature_template_operators.register()
    animation_transfer_operators.register()
    bone_mapping_operators.register()
    panels.register()
    handlers.register()


def unregister():
    """Unregister all Blender adapter classes."""
    handlers.unregister()
    panels.unregister()
    bone_mapping_operators.unregister()
    animation_transfer_operators.unregister()
    armature_template_operators.unregister()
    preset_operators.unregister()
    operators.unregister()
    properties.unregister()
