"""
Blender Property Groups for CrossRig.

These define the data structures stored in Blender scenes.
"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    CollectionProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    PointerProperty
)
from ...config.constants import (
    DEFAULT_ROOT_BONE,
    DEFAULT_OVERLAP_FRAMES,
    DEFAULT_FORWARD_AXIS,
    DEFAULT_REPEAT_COUNT,
    DEFAULT_ANGLE,
    MIN_REPEAT_COUNT,
    MAX_REPEAT_COUNT,
    SOFT_MAX_REPEAT_COUNT,
    MIN_ANGLE,
    MAX_ANGLE,
    SOFT_MIN_ANGLE,
    SOFT_MAX_ANGLE,
    MIN_OVERLAP_FRAMES,
    MAX_OVERLAP_FRAMES,
    FORWARD_AXIS_OPTIONS
)


def action_index_update(self, context):
    """Update callback when action index changes."""
    if self.action_index < 0 or self.action_index >= len(self.action_collection):
        return

    item = self.action_collection[self.action_index]
    arm_name = item.armature_name

    if arm_name and arm_name in bpy.data.objects:
        arm_obj = bpy.data.objects[arm_name]
        bpy.ops.object.select_all(action='DESELECT')
        arm_obj.select_set(True)
        context.view_layer.objects.active = arm_obj


class CrossRigActionItem(PropertyGroup):
    """Property group for individual action items in the list."""

    action_name: StringProperty()
    armature_name: StringProperty(default="")
    use_action: BoolProperty(name="", description="Enable Action", default=True)

    repeat_count: IntProperty(
        name="Repeat",
        description="Number of times to repeat this animation",
        default=DEFAULT_REPEAT_COUNT,
        min=MIN_REPEAT_COUNT,
        max=MAX_REPEAT_COUNT,
        soft_max=SOFT_MAX_REPEAT_COUNT
    )

    angle: IntProperty(
        name="Angle",
        description="Rotation angle in degrees for character trajectory",
        default=DEFAULT_ANGLE,
        min=MIN_ANGLE,
        max=MAX_ANGLE,
        soft_min=SOFT_MIN_ANGLE,
        soft_max=SOFT_MAX_ANGLE
    )


class BoneMappingItem(PropertyGroup):
    """Property group for individual bone mapping items."""

    source_bone: StringProperty(
        name="Source Bone",
        description="Bone name in source armature"
    )

    target_bone: StringProperty(
        name="Target Bone",
        description="Bone name in target armature"
    )

    confidence: FloatProperty(
        name="Confidence",
        description="Mapping confidence score (0.0-1.0). 1.0 = manual/exact, <1.0 = auto-mapped",
        default=1.0,
        min=0.0,
        max=1.0
    )


class CrossRigSettings(PropertyGroup):
    """Main settings property group for the addon."""

    root_bone: StringProperty(
        name="Root Bone",
        description="Name of the root bone (e.g., 'mixamorig:Hips' for Mixamo rigs)",
        default=DEFAULT_ROOT_BONE
    )

    overlap_frames: IntProperty(
        name="Overlap Frames",
        description="Number of frames used for blending between strips",
        default=DEFAULT_OVERLAP_FRAMES,
        min=MIN_OVERLAP_FRAMES,
        max=MAX_OVERLAP_FRAMES
    )

    action_collection: CollectionProperty(type=CrossRigActionItem)
    action_index: IntProperty(default=0, update=action_index_update)
    order_confirmed: BoolProperty(default=False)

    forward_axis: EnumProperty(
        name="Character Forward Axis (Beta)",
        description="The direction the character is facing in the scene (Forward)",
        items=FORWARD_AXIS_OPTIONS,
        default=DEFAULT_FORWARD_AXIS
    )

    # UI expand/collapse toggles - Main Sections
    show_playground: BoolProperty(
        name="Play Ground",
        description="Show/Hide Play Ground section",
        default=True
    )

    show_armature_manage: BoolProperty(
        name="Armature Manage",
        description="Show/Hide Armature Manage section",
        default=False
    )

    show_animation_manage: BoolProperty(
        name="Animation Manage",
        description="Show/Hide Animation Manage section",
        default=False
    )

    # UI expand/collapse toggles - Play Ground Subsections
    show_load_organize: BoolProperty(
        name="Load & Organize Animations",
        description="Show/Hide Load & Organize subsection",
        default=True
    )

    show_nla: BoolProperty(
        name="Nonlinear Animation",
        description="Show/Hide NLA subsection",
        default=True
    )

    show_export: BoolProperty(
        name="Export",
        description="Show/Hide Export subsection",
        default=True
    )

    show_presets: BoolProperty(
        name="Animation Presets",
        description="Show/Hide Animation Presets subsection",
        default=True
    )

    # Bone Mapping Section
    show_bone_mapping: BoolProperty(
        name="Bone Mapping",
        description="Show/Hide Bone Mapping section",
        default=False
    )

    # Bone Mapping Properties
    bone_mapping_source_armature: PointerProperty(
        name="Source Armature",
        description="Source armature (with animation)",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )

    bone_mapping_target_armature: PointerProperty(
        name="Target Armature",
        description="Target armature (to receive animation)",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )

    bone_mapping_preset_name: StringProperty(
        name="Preset Name",
        description="Name for the bone mapping preset",
        default=""
    )

    bone_mappings: CollectionProperty(
        type=BoneMappingItem,
        name="Bone Mappings"
    )

    bone_mapping_index: IntProperty(
        name="Bone Mapping Index",
        description="Active bone mapping index",
        default=0
    )

    auto_map_threshold: FloatProperty(
        name="Auto-Map Threshold",
        description="Minimum confidence threshold for auto-mapping (0.0-1.0)",
        default=0.6,
        min=0.0,
        max=1.0,
        precision=2
    )

    # UI expand/collapse toggles - Bone Mapping Subsections
    show_bone_mapping_setup: BoolProperty(
        name="Setup",
        description="Show/Hide Setup subsection",
        default=True
    )

    show_bone_mapping_list: BoolProperty(
        name="Mapping List",
        description="Show/Hide Mapping List subsection",
        default=True
    )

    show_bone_mapping_presets: BoolProperty(
        name="Mapping Presets",
        description="Show/Hide Mapping Presets subsection",
        default=True
    )

    show_bone_mapping_apply: BoolProperty(
        name="Apply Animation",
        description="Show/Hide Apply Animation subsection",
        default=True
    )


# Classes to register
classes = (
    CrossRigActionItem,
    BoneMappingItem,
    CrossRigSettings,
)


def register():
    """Register property classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.crossrig_settings = bpy.props.PointerProperty(type=CrossRigSettings)


def unregister():
    """Unregister property classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.crossrig_settings
