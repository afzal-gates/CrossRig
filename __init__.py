"""
CrossRig - Clean Architecture Edition

A Blender addon for animation sequencing and cross-rig retargeting
with intelligent bone mapping, NLA timeline integration, and animation transfer.

Architecture:
- Domain Layer: Pure business logic and math utilities
- Services Layer: Action manipulation and bone mapping services
- Use Cases Layer: Application business rules
- Adapters Layer: Blender integration (Properties, Operators, Panels)

Author: Afzal Hossain
License: MIT
"""

bl_info = {
    "name": "CrossRig",
    "author": "Afzal Hossain",
    "version": (1, 0, 0),
    "blender": (3, 5, 0),
    "location": "View3D > Sidebar > CrossRig",
    "description": "Animation sequencing and cross-rig retargeting with intelligent bone mapping.",
    "category": "Animation"
}

# Import the Blender adapter layer
# This handles all Blender-specific registration
from . import adapters
blender = adapters.blender


def register():
    """
    Register the addon.

    This delegates to the adapter layer which handles all Blender
    class registration (Properties, Operators, Panels, Handlers).
    """
    blender.register()


def unregister():
    """
    Unregister the addon.

    This delegates to the adapter layer which handles all Blender
    class unregistration in the correct order.
    """
    blender.unregister()


# Allow running as standalone script for testing
if __name__ == "__main__":
    register()
