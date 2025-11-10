# Arm Bone Logging Guide

## Overview
Comprehensive logging has been added to capture shoulder-to-hand bone positions before and after T-pose application. This helps debug and correct bone positioning issues.

## How to Get the Logs

### Step 1: Enable Blender Console
1. Open Blender
2. Go to **Window → Toggle System Console** (Windows) or run Blender from terminal (Mac/Linux)
3. The console window will show all print output

### Step 2: Generate Armature with Logging
1. In CrossRig panel, set up your Smart Rig landmarks
2. **Enable or Disable** "Auto T-Pose After Generation" depending on your test case
3. Click **"Generate Armature"** button
4. Watch the console for log output

### Step 3: Copy the Logs
The logs will appear in this format:

```
================================================================================
LOGGING ARM BONE POSITIONS - BEFORE T-POSE
================================================================================

================================================================================
ARM BONE POSITIONS LOG - BEFORE T-POSE
Timestamp: 2025-01-05 14:30:45
Armature: Mixamo
Naming: mixamo
================================================================================

--- LEFT ARM ---

mixamorig:LeftShoulder:
  Head (local):  <Vector (0.1234, 0.5678, 1.4500)>
  Tail (local):  <Vector (0.2345, 0.5678, 1.4500)>
  Head (world):  <Vector (0.1234, 0.5678, 1.4500)>
  Tail (world):  <Vector (0.2345, 0.5678, 1.4500)>
  Length:        0.1111
  Direction:     <Vector (1.0000, 0.0000, 0.0000)>
  Roll (deg):    0.00

mixamorig:LeftArm:
  Head (local):  <Vector (0.2345, 0.5678, 1.4500)>
  Tail (local):  <Vector (0.4567, 0.5678, 1.2300)>
  ...

--- RIGHT ARM ---
...

================================================================================
LOGGING ARM BONE POSITIONS - AFTER T-POSE
================================================================================
...
```

## What Gets Logged

### For Each Bone (Shoulder → Upper Arm → Forearm → Hand):

1. **Head (local)**: Bone start position in armature space
2. **Tail (local)**: Bone end position in armature space
3. **Head (world)**: Bone start position in world space
4. **Tail (world)**: Bone end position in world space
5. **Length**: Total bone length
6. **Direction**: Normalized direction vector (head → tail)
7. **Roll (degrees)**: Bone rotation around its axis

### Both Sides Logged:
- **LEFT ARM**: shoulder.L → upper_arm.L → forearm.L → hand.L
- **RIGHT ARM**: shoulder.R → upper_arm.R → forearm.R → hand.R

## Naming Conventions

### Standard Mode:
- `shoulder.L` / `shoulder.R`
- `upper_arm.L` / `upper_arm.R`
- `forearm.L` / `forearm.R`
- `hand.L` / `hand.R`

### Mixamo Mode:
- `mixamorig:LeftShoulder` / `mixamorig:RightShoulder`
- `mixamorig:LeftArm` / `mixamorig:RightArm`
- `mixamorig:LeftForeArm` / `mixamorig:RightForeArm`
- `mixamorig:LeftHand` / `mixamorig:RightHand`

## Sharing Logs with Developer

### What to Include:
1. **Complete BEFORE T-POSE log section**
2. **Complete AFTER T-POSE log section** (if T-pose was applied)
3. **Describe the problem**: "Arm is pointing down instead of sideways", "Hand is rotated wrong", etc.
4. **Screenshot**: Show the generated armature in Blender viewport
5. **Settings used**: Which landmarks were picked, naming mode (standard/mixamo), auto T-pose enabled/disabled

### How to Copy from Console:
- **Windows**: Right-click in console → Select All → Copy
- **Mac/Linux**: Select text with mouse, Ctrl+C to copy
- Save to a `.txt` file or paste directly in issue/message

## Example Use Cases

### Case 1: Arms Pointing Down Instead of Sideways
```
Problem: After generation, arms point downward instead of horizontal
Action: Generate armature with "Auto T-Pose" DISABLED
Result: Share BEFORE T-POSE logs showing arm bone positions
```

### Case 2: T-Pose Makes Arms Too High
```
Problem: T-pose application raises arms too much
Action: Generate armature with "Auto T-Pose" ENABLED
Result: Share both BEFORE and AFTER T-POSE logs
```

### Case 3: Hand Rotation Issues
```
Problem: Hand bones are rotated incorrectly
Action: Generate armature and check hand bone "Roll" values
Result: Share logs highlighting the hand bone roll angles
```

## Understanding the Logs

### Direction Vector Examples:
- `(1.0, 0.0, 0.0)` → Pointing along +X axis (right)
- `(-1.0, 0.0, 0.0)` → Pointing along -X axis (left)
- `(0.0, 1.0, 0.0)` → Pointing along +Y axis (forward)
- `(0.0, 0.0, 1.0)` → Pointing along +Z axis (up)

### Expected T-Pose Arm Direction:
- **Left arm**: Should point roughly in +X direction (to the left)
- **Right arm**: Should point roughly in -X direction (to the right)
- **Both**: Should be roughly horizontal (Z component near 0)

## Troubleshooting

### No Logs Appear
- Make sure System Console is open (Window → Toggle System Console)
- Check that you clicked "Generate Armature" after setting up landmarks

### "NOT FOUND" Messages
- Some bones might not exist if landmarks weren't picked
- This is normal for optional bones

### Logs Too Long
- You can scroll up in the console to find the beginning
- Or redirect output: Run Blender from command line with `> output.log`

## Next Steps

After sharing the logs, the developer can:
1. Analyze bone positions and identify incorrect placements
2. Adjust bone generation algorithms
3. Correct T-pose application logic
4. Fix bone roll calculations
5. Provide corrected version or specific fixes
