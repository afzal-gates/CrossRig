"""
Configuration constants for Mixanimo Lite addon.
"""

# Default values
DEFAULT_ROOT_BONE = "mixamorig:Hips"
DEFAULT_OVERLAP_FRAMES = 3
DEFAULT_FORWARD_AXIS = 'Y+'
DEFAULT_REPEAT_COUNT = 1
DEFAULT_ANGLE = 0

# Limits
MIN_REPEAT_COUNT = 1
MAX_REPEAT_COUNT = 100
SOFT_MAX_REPEAT_COUNT = 10

MIN_ANGLE = -360
MAX_ANGLE = 360
SOFT_MIN_ANGLE = -180
SOFT_MAX_ANGLE = 180

MIN_OVERLAP_FRAMES = 0
MAX_OVERLAP_FRAMES = 100

# Axis options
FORWARD_AXIS_OPTIONS = [
    ('X+', "X+", ""),
    ('X-', "X-", ""),
    ('Y+', "Y+", ""),
    ('Y-', "Y-", ""),
    ('Z+', "Z+", ""),
    ('Z-', "Z-", ""),
]

# Naming conventions
REPEAT_ACTION_SUFFIX = "_REPEAT_"
BAKED_ACTION_PREFIX = "Baked_Animation"

# FBX Export settings
FBX_AXIS_FORWARD = '-Z'  # Unity/Unreal standard
FBX_AXIS_UP = 'Y'
FBX_GLOBAL_SCALE = 1.0
FBX_BAKE_ANIM_STEP = 1.0
FBX_PRIMARY_BONE_AXIS = 'Y'
FBX_SECONDARY_BONE_AXIS = 'X'
