# Mixamo Animation Retargeting Guide

## Common Issues and Solutions

### Issue 1: Animation Plays Too Fast

**Cause**: FPS mismatch between source and target scenes

**Solution**:
1. Check the FPS of your Blender scene: **Output Properties → Frame Rate**
2. Mixamo animations are typically 30 FPS
3. Set your scene to **30 FPS** to match Mixamo
4. If animation is already imported, use **NLA Editor → Scale** to adjust speed

### Issue 2: Character Moves Out of Scene

**Cause**: Armature scale mismatch or root motion not matching

**Solutions**:

**Option A: Scale the Armature**
1. Select the armature in Object Mode
2. Press `S` (Scale)
3. Scale uniformly until character is in frame
4. Apply scale: `Ctrl+A` → **Apply → Scale**

**Option B: Adjust Root Motion**
1. In the NLA Editor or Dope Sheet
2. Select the **Hips** bone keyframes
3. Scale the position keyframes: `S` then `Z` then `0` (zero out Z movement)
4. Or manually edit the location curves in Graph Editor

**Option C: Use Animation Offset**
1. Select armature
2. **Object Properties → Animation → Action**
3. Add **Action Offset** to reposition character
4. Adjust Z-offset to bring character to ground level

### Issue 3: Wrong Pose (Arms Up/Twisted)

**Cause**: Bone orientation/roll mismatch between source and generated armature

**Solutions**:

**Option A: Use Recalculate Roll (Done Automatically)**
- The addon now automatically recalculates bone rolls
- Z-axis alignment for body/legs
- X-axis alignment for arms

**Option B: Manual Fix in Edit Mode**
1. Select armature → Enter **Edit Mode**
2. Select all bones: `A`
3. **Armature → Calculate Roll → Global +Z Axis**
4. Select arm bones only
5. **Armature → Calculate Roll → Global +X Axis**

**Option C: Use Retargeting Addon**
- Install **Rokoko Studio** or **Auto-Rig Pro** addon
- Use their animation retargeting features
- Automatically maps between different rigs

### Issue 4: Hands/Feet Pointing Wrong Direction

**Cause**: Bone tail positions not matching Mixamo conventions

**Solution**:
1. In **Edit Mode**, select the misaligned bone
2. **Armature → Calculate Roll → Active Bone to View**
3. Or manually adjust roll in **Bone Properties → Transform → Roll**

## Best Practices for Animation Retargeting

### 1. Match Proportions
- Ensure generated armature matches the source character proportions
- Use same landmark positions as the animated character
- Check bone lengths match (especially spine, arms, legs)

### 2. T-Pose/A-Pose Alignment
- **Automatic T-Pose**: CrossRig automatically applies T-pose after generating armature
- Character mesh should match the armature pose for best skinning results
- T-pose ensures maximum compatibility with Mixamo animations

### 3. Use Correct FPS
| Animation Source | FPS Setting |
|------------------|-------------|
| Mixamo | 30 FPS |
| Motion Capture | 60 FPS or 120 FPS |
| Game Engine | 30 FPS or 60 FPS |
| Film | 24 FPS |

### 4. Scale Considerations
- Mixamo characters are typically 1.7-1.8m tall
- Generate armature at correct scale from the start
- Avoid scaling animated armatures (causes issues)

### 5. Root Motion Handling

**For In-Place Animation**:
1. Clear root bone location keyframes
2. Keep only rotation keyframes on Hips

**For Locomotion Animation** (walking, running):
1. Keep root motion intact
2. Adjust ground plane if needed
3. Use constraints to limit movement range

## Workflow for Perfect Animation Retargeting

### Step 1: Generate Armature at Correct Scale
```
1. Load character mesh (should be ~1.7-1.8m tall)
2. Enter Smart Rig mode
3. Pick landmarks carefully (accurate positions)
4. Generate Armature
5. ✓ Bone rolls automatically calculated
6. ✓ T-pose automatically applied (arms extended)
```

### Step 2: Test with Simple Animation
```
1. Import a simple Mixamo animation (idle or T-pose)
2. Apply to generated armature
3. Check:
   - Arms pointing correct direction? ✓
   - Legs aligned properly? ✓
   - Character at correct height? ✓
```

### Step 3: Fix Any Issues Before Complex Animations
```
1. Adjust bone rolls if needed (Edit Mode)
2. Scale armature if too big/small
3. Apply all transforms (Ctrl+A)
```

### Step 4: Apply Target Animation
```
1. Set scene FPS to match source (usually 30 FPS)
2. Import/link animation
3. Play and verify
4. Adjust timing in NLA Editor if needed
```

## Quick Fixes Checklist

- [ ] Scene FPS set to 30 FPS
- [ ] Armature scale applied (Ctrl+A → Scale)
- [ ] Bone rolls recalculated (automatic)
- [ ] Character at ground level (Z=0 for feet)
- [ ] Rest pose matches animation source
- [ ] Bone names match exactly (case-sensitive)
- [ ] Parent relationships intact
- [ ] No negative scale values

## Advanced: NLA Editor Timeline Adjustments

1. **Speed Up Animation**: Scale strips horizontally (S → X → 0.5)
2. **Slow Down Animation**: Scale strips horizontally (S → X → 2.0)
3. **Loop Animation**: Duplicate strips, adjust blending
4. **Blend Animations**: Use NLA track mixing with influence

## Troubleshooting Decision Tree

```
Animation Issue?
├─ Too Fast/Slow?
│  └─ Fix: Adjust scene FPS or scale strip in NLA Editor
│
├─ Character Flying/Underground?
│  ├─ Scale armature uniformly (S)
│  └─ Or adjust Hips bone Z location offset
│
├─ Arms/Legs Wrong Orientation?
│  ├─ Auto-fixed: Recalculate roll (done automatically)
│  └─ Manual: Edit Mode → Calculate Roll → Global Axis
│
└─ Animation Not Playing?
   ├─ Check action is assigned to armature
   └─ Verify bone names match exactly (case-sensitive!)
```

## Support

If issues persist:
1. Check bone names are **exactly** matching (case-sensitive)
2. Verify armature structure matches Mixamo standard
3. Try with a known-good Mixamo animation first
4. Check Blender console for error messages
