# Interactive Finger Alignment Feature

## Overview

The Interactive Finger Alignment feature allows you to click on a finger tip mesh in Object Mode to automatically detect and align the entire finger bone chain to the hand bone with proper angle.

## Features

- **Interactive Mesh Clicking**: Click directly on finger tip mesh instead of selecting bones in Pose Mode
- **Automatic Finger Detection**: Detects which finger (thumb, index, middle, ring, pinky) and side (left/right) based on click position
- **Full Chain Alignment**: Aligns entire finger bone chain from hand to tip
- **Distance-Based Detection**: Uses 20cm threshold to match clicked position to closest finger tip

## How to Use

### Prerequisites
1. Have an armature with hand and finger bones
2. Have a mesh object representing the character
3. Both objects should be in the scene

### Steps

1. **Select Armature and Mesh**
   - In the CrossRig panel, go to "Armature Manage > Bone Repositioning"
   - Select your armature in "Armature" field
   - Select your mesh in "Target Mesh" field

2. **Start Interactive Alignment**
   - Ensure you're in Object Mode
   - Click the "Click Finger Tip to Align" button
   - You'll see a message: "Click on finger tip to align bones (Right-click or ESC to cancel)"

3. **Click on Finger Tip**
   - Click on any finger tip on the mesh
   - The system will automatically:
     - Detect which finger was clicked
     - Determine if it's left or right hand
     - Find all bones in that finger chain
     - Align the entire chain to the hand bone

4. **Cancel**
   - Right-click or press ESC to cancel the operation

## Technical Details

### Detection Algorithm

1. **Raycast**: Performs raycast from mouse position to mesh surface
2. **Finger Detection**: Checks all finger tip bone positions against clicked position
3. **Distance Threshold**: Only accepts matches within 20cm (0.2 Blender units)
4. **Closest Match**: Selects the closest finger tip to clicked position

### Alignment Process

1. **Hand Detection**: Uses `detect_hand_finger_hierarchy()` to find hand and finger bones
2. **Direction Calculation**: Calculates direction from hand tail to first finger bone head
3. **Chain Alignment**: Aligns entire finger chain in that direction:
   - First bone: Starts at hand tail
   - Subsequent bones: Continue in same direction from parent tail
   - All bones maintain their original length

### Supported Bone Naming Conventions

- **Mixamo**: `mixamorig:LeftHand`, `mixamorig:LeftHandThumb1`, etc.
- **Rigify**: `hand.L`, `thumb.01.L`, etc.
- **Standard**: `Hand.L`, `Thumb1.L`, etc.
- **UE4/MetaHuman**: `hand_l`, `thumb_01_l`, etc.

## Comparison with Pose Mode Alignment

### Interactive Mesh Click (NEW)
- **Mode**: Object Mode
- **Input**: Click on finger tip mesh
- **Detection**: Automatic finger detection
- **Use Case**: Quick alignment when working with mesh

### Pose Mode Selection (EXISTING)
- **Mode**: Pose Mode
- **Input**: Select finger tip bone
- **Detection**: Uses selected bone
- **Use Case**: Precise control over specific finger

## Implementation Details

### New Operator: `CROSSRIG_OT_AlignFingerByMeshClick`

**Location**: `adapters/blender/bone_reposition_operators.py:893-1076`

**Key Methods**:
- `modal()`: Handles mouse events and raycast
- `detect_finger_from_position()`: Identifies clicked finger
- `align_finger_chain()`: Aligns bones in edit mode
- `invoke()`: Sets up modal handler

### UI Integration

**Location**: `adapters/blender/panels.py:640-645`

Added button in Bone Repositioning section:
```python
row.operator("crossrig.align_finger_by_mesh_click",
             text="Click Finger Tip to Align",
             icon='HAND')
```

## Error Handling

- **No mesh hit**: "No mesh surface hit - try clicking on the finger tip"
- **No finger detected**: "Could not detect finger from clicked position"
- **No hand found**: "No hand bone found for [LEFT/RIGHT] side"
- **No finger bones**: "No [finger_type] finger bones found"

## Limitations

- **Distance Threshold**: Only detects clicks within 20cm of finger tip bone
- **Bone Naming**: Requires standard naming conventions for detection
- **Hand Detection**: Must have recognizable hand bone in hierarchy

## Future Enhancements

- Adjustable distance threshold
- Visual feedback showing detected finger before alignment
- Support for custom bone naming patterns
- Batch alignment of all fingers with single click on hand

## Related Features

- **Smart Hand Mapping**: Auto-detect hand and finger hierarchy
- **Bone Repositioning**: Interactive bone repositioning with mesh clicking
- **Finger Alignment (Pose Mode)**: Align selected finger bone to hand

## Version History

- **v1.2.0** (2025-11-03): Initial implementation of interactive finger alignment
