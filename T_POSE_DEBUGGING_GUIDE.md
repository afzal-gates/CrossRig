# T-Pose Debugging Guide

## Overview

The addon now includes comprehensive logging to help analyze and perfect the T-pose. When you generate an armature, detailed bone information is printed to the **Blender Console**.

## How to Access the Logs

1. **Open Blender Console**:
   - Windows: `Window → Toggle System Console`
   - Mac/Linux: Launch Blender from terminal

2. **Generate Armature**:
   - Pick landmarks and click "Generate Armature"

3. **View Logs**:
   - Check the console for detailed bone information

## Log Structure

The logging outputs **3 sections**:

### 1. BEFORE T-POSE APPLICATION
Shows the initial bone state right after generation, before any T-pose rotations are applied.

**Key Information**:
- Initial bone positions (Head/Tail)
- Bone roll values
- Bone hierarchy (parent relationships)
- Original orientation

### 2. AFTER T-POSE ROTATION (BEFORE APPLY)
Shows bone state after T-pose rotations are set but BEFORE applying as rest pose.

**Key Information**:
- Rotation values in Euler angles (radians and degrees)
- Rotation quaternions
- World space bone direction vectors
- Local and world matrices

**Critical for Analysis**:
```
Rotation (Degrees): (X°, Y°, Z°)
Bone Direction (world): (x, y, z)
```

### 3. FINAL STATE AFTER APPLY AS REST POSE
Shows bone state after the pose is applied as the new rest pose.

**Key Information**:
- Updated Head/Tail positions
- New bone roll values
- Final bone orientation

### 4. T-POSE ANALYSIS SUMMARY
**Most Important Section** - Focuses on arm bones only.

**Displays**:
- World direction vectors for each arm bone
- Head and tail positions in world space
- Bone roll values
- Analysis: ✓ CORRECT or ✗ ISSUE

**Perfect T-Pose Indicators**:
```
mixamorig:LeftArm:
  World Direction: (-1.000, 0.000, 0.000)  ← Perfect horizontal left
  ✓ CORRECT: Arm is horizontal

mixamorig:RightArm:
  World Direction: (1.000, 0.000, 0.000)   ← Perfect horizontal right
  ✓ CORRECT: Arm is horizontal
```

## Understanding the Data

### Bone Direction Vectors

**Format**: `(x, y, z)` - normalized direction from head to tail

**T-Pose Target**:
- **Left Arm**: `(-1.0, 0.0, 0.0)` - pointing left (negative X)
- **Right Arm**: `(1.0, 0.0, 0.0)` - pointing right (positive X)
- **Left ForeArm**: `(-1.0, 0.0, 0.0)` - pointing left (straight continuation)
- **Right ForeArm**: `(1.0, 0.0, 0.0)` - pointing right (straight continuation)

**Tolerance**: `abs(x) > 0.9` indicates good horizontal alignment

### Rotation Euler Angles

**Format**: `(X, Y, Z)` in radians (also shown in degrees)

**Z-axis rotation** is key for T-pose:
- **Left Arm**: Should be around `+90°` (1.57 radians)
- **Right Arm**: Should be around `-90°` (-1.57 radians)

### Bone Roll

**Format**: Degrees

**Affects**: How the bone twists around its own axis

**For Arms**: Roll affects hand/finger orientation
- Mixamo standard: Usually `0°` after recalculation

## Troubleshooting T-Pose Issues

### Issue 1: Arms Not Horizontal

**Symptom**:
```
mixamorig:LeftArm:
  World Direction: (-0.707, -0.500, 0.500)  ← Not horizontal
  ✗ ISSUE: Arm not horizontal (X-direction: -0.707, should be close to ±1.0)
```

**Possible Causes**:
1. **Rotation axis wrong**: Using X or Y instead of Z
2. **Rotation angle wrong**: Not 90° exactly
3. **Parent bone affecting rotation**: Shoulder rotation interfering
4. **Bone roll issues**: Incorrect roll preventing proper rotation

**Solutions**:
- Adjust rotation angle in `set_t_pose()` function
- Try different rotation axes (X, Y, Z combinations)
- Adjust parent bone (shoulder) rotation
- Modify bone roll calculation

### Issue 2: Arms Pointing Wrong Direction

**Symptom**:
```
mixamorig:LeftArm:
  World Direction: (0.000, -1.000, 0.000)  ← Pointing forward/backward
```

**Solution**: Change rotation axis from Z to Y or X

### Issue 3: Arms Tilted Up/Down

**Symptom**:
```
mixamorig:LeftArm:
  World Direction: (-0.866, 0.000, 0.500)  ← Has Z component (tilted up)
```

**Solution**: Add X or Y rotation to counteract tilt

## How to Adjust T-Pose

Based on log analysis, edit `smart_rig_service.py` in the `set_t_pose()` function:

### Current Settings (Line ~395-436)

```python
# Left Arm
pose_bones[left_arm].rotation_mode = 'XYZ'
pose_bones[left_arm].rotation_euler = (0, 0, math.radians(90))

# Right Arm
pose_bones[right_arm].rotation_mode = 'XYZ'
pose_bones[right_arm].rotation_euler = (0, 0, math.radians(-90))
```

### Adjustment Examples

**If arms tilted up (+Z direction)**:
```python
# Add negative X rotation to tilt down
pose_bones[left_arm].rotation_euler = (math.radians(-10), 0, math.radians(90))
pose_bones[right_arm].rotation_euler = (math.radians(-10), 0, math.radians(-90))
```

**If arms pointing forward/backward**:
```python
# Try Y-axis rotation instead of Z
pose_bones[left_arm].rotation_euler = (0, math.radians(90), 0)
pose_bones[right_arm].rotation_euler = (0, math.radians(-90), 0)
```

**If arms need combined rotation**:
```python
# Combine multiple axes
pose_bones[left_arm].rotation_euler = (
    math.radians(-5),   # Slight tilt down
    math.radians(10),   # Slight forward
    math.radians(85)    # Main horizontal rotation
)
```

## Workflow for Perfect T-Pose

1. **Generate armature** → Check console logs
2. **Analyze "T-POSE ANALYSIS SUMMARY"** section
3. **Note the actual direction vectors** for Left/Right Arm
4. **Calculate needed adjustments**:
   - Compare actual direction to target `(±1, 0, 0)`
   - Determine which rotation axis needs adjustment
5. **Edit `set_t_pose()` function** with new rotation values
6. **Regenerate armature** → Verify improvement
7. **Iterate** until arms are horizontal

## Expected Perfect Log Output

```
================================================================================
T-POSE ANALYSIS SUMMARY - ARM BONES ONLY
================================================================================

Target: Arms should be HORIZONTAL (90° from body, perpendicular to torso)
Expected: Bone direction in world space should be close to (±1, 0, 0) for horizontal

mixamorig:LeftShoulder:
  World Direction: (-0.866, -0.500, 0.000)
  Bone Roll: 0.00°

mixamorig:LeftArm:
  World Direction: (-1.000, 0.000, 0.000)
  ✓ CORRECT: Arm is horizontal (X-direction: -1.000)

mixamorig:LeftForeArm:
  World Direction: (-1.000, 0.000, 0.000)
  ✓ CORRECT: Arm is horizontal (X-direction: -1.000)

mixamorig:RightShoulder:
  World Direction: (0.866, -0.500, 0.000)
  Bone Roll: 0.00°

mixamorig:RightArm:
  World Direction: (1.000, 0.000, 0.000)
  ✓ CORRECT: Arm is horizontal (X-direction: 1.000)

mixamorig:RightForeArm:
  World Direction: (1.000, 0.000, 0.000)
  ✓ CORRECT: Arm is horizontal (X-direction: 1.000)

================================================================================
```

## Additional Tips

1. **Compare with Mixamo**: Import a Mixamo T-pose FBX and compare bone directions
2. **Visual Check**: Use Blender's "Axes" display in Armature properties
3. **Reference Image**: Compare with your T-pose reference (D:\T-pose.JPG)
4. **Test Animations**: Apply Mixamo animation to verify compatibility

## Next Steps

After reviewing the logs:
1. Share the "T-POSE ANALYSIS SUMMARY" section
2. Share the "World Direction" values for arm bones
3. We can calculate exact rotation adjustments needed
4. Update `set_t_pose()` function with precise values
