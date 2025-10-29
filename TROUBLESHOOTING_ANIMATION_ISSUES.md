# Troubleshooting: Animation Transfer Issues

## Problem: Animation looks wrong or unrealistic after transfer

### Common Symptoms
- ✗ Pose doesn't match original
- ✗ Character moves unrealistically
- ✗ Limbs twisted or broken
- ✗ Character sliding or floating
- ✗ Bones pointing wrong directions

---

## Root Causes & Solutions

### Issue 1: Unapplied Transforms ⚠️ **MOST COMMON**

**Problem**: Armature has scale, rotation, or location values that aren't applied.

**Symptoms**:
- Animation looks completely wrong
- Character is scaled incorrectly
- Bones pointing in weird directions
- Sliding on ground

**How to Check**:
```
1. Select target armature
2. Look at properties panel (N key)
3. Check Transform section:
   - Location: Should be (0, 0, 0) or known value
   - Rotation: Should be (0, 0, 0) or known value
   - Scale: Should be (1, 1, 1)
```

**Solution**: Apply all transforms BEFORE applying animation

#### Fix Steps:
1. **Select target armature** (empty armature without animation)
2. In **3D Viewport**: Object mode
3. Press **Ctrl + A** (Apply menu)
4. Select **"All Transforms"**
5. ✅ Location, Rotation, Scale all reset
6. **Now apply animation**

#### Alternative: Apply individually
```
Ctrl + A → Location
Ctrl + A → Rotation
Ctrl + A → Scale
```

**Prevention**: Always apply transforms before animation transfer!

---

### Issue 2: Different Rest Poses

**Problem**: Source and target armatures have different rest poses (T-pose vs A-pose, etc.)

**Symptoms**:
- Arms or legs at wrong angles
- Character looks stiff
- Animation doesn't look natural
- Rotations are off but structure is correct

**How to Check**:
```
1. Select source armature → TAB (Edit mode)
2. Note arm angle, leg spread, etc.
3. ESC (Object mode)
4. Select target armature → TAB (Edit mode)
5. Compare poses - are they identical?
```

**Solution**: Match rest poses before transfer

#### Fix Steps:
1. **Both armatures must have identical rest poses**
2. If different:
   - Option A: Use source armature's rest pose for target
   - Option B: Bake animation to new rest pose (advanced)
   - Option C: Use AccuRig with same settings for both

**For AccuRig Users**:
- Always use same AccuRig settings/version
- Export from AccuRig with consistent options
- Don't modify rest pose after rigging

---

### Issue 3: Bone Rotation Modes

**Problem**: Bones use different rotation modes (Quaternion vs Euler XYZ/XZY/etc.)

**Symptoms**:
- Some bones rotate correctly, others don't
- Gimbal lock issues
- Rotations flip unexpectedly
- Animation partially works

**How to Check**:
```
1. Select source armature → Pose mode
2. Select any bone
3. Look at properties (N key) → Transform
4. Note "Rotation Mode" (Quaternion, XYZ Euler, etc.)
5. Repeat for target armature
6. They should match!
```

**Solution**: Match rotation modes

#### Fix Steps:

**Method 1: Change Target to Match Source**
```
1. Select target armature → Pose mode
2. Select all bones (A key)
3. In properties (N key) → Transform
4. Change "Rotation Mode" to match source
   (Usually "Quaternion" for game rigs)
5. Apply animation
```

**Method 2: Set All Bones to Quaternion**
```
1. Target armature → Pose mode
2. Select all bones (A)
3. Rotation Mode → Quaternion (WXYZ)
4. Repeat for source if needed
```

---

### Issue 4: Scale Differences

**Problem**: Armatures are different sizes

**Symptoms**:
- Animation plays but character is wrong size
- Steps too big or too small
- Reaches don't match environment

**How to Check**:
```
1. Select both armatures
2. Compare physical size in viewport
3. Check object scale (N key → Transform)
```

**Solution**: Match scales

#### Fix Steps:
```
1. Select target armature
2. Press S (scale)
3. Type scale value (e.g., 0.5 for half, 2 for double)
4. Enter
5. Ctrl + A → Scale (apply scale)
6. Apply animation
```

---

### Issue 5: Wrong Animation Data Applied

**Problem**: Animation saved from one armature type, applied to different type without mapping

**Symptoms**:
- No movement at all
- Only some bones animate
- Console shows "Bone not found" errors

**How to Check**:
```
Window → Toggle System Console
Look for warnings like:
  "Bone not found: mixamorig:Hips"
```

**Solution**: Use correct workflow

#### Fix Steps:

**If Same Rig Type (AccuRig → AccuRig)**:
```
1. Don't use bone mapping!
2. Animation Manage → Save Animation (from source)
3. Animation Manage → Apply Animation (to target)
4. NO bone mapping needed for identical rigs
```

**If Different Rig Types (Mixamo → AccuRig)**:
```
1. MUST use bone mapping
2. Follow bone mapping workflow
3. Create/load mapping preset
4. Apply animation WITH mapping
```

---

## Diagnostic Workflow

### Step 1: Verify Armature Compatibility

**Check both armatures**:
```
□ Same rig type? (both AccuRig, both Mixamo, etc.)
□ Same bone names?
□ Same bone count?
□ Same hierarchy?
```

**If YES to all**: No bone mapping needed
**If NO to any**: Must use bone mapping

---

### Step 2: Pre-Application Checklist

**Before applying animation, verify target armature**:

```
□ Object mode selected
□ Target armature selected (orange highlight)
□ Location: (0, 0, 0) or known value
□ Rotation: (0, 0, 0) or known value
□ Scale: (1, 1, 1)
□ No active constraints (that interfere)
□ Pose mode: All bones in rest pose
```

**Fix any issues before proceeding!**

---

### Step 3: Application Test

**Apply animation and check**:
```
1. Apply animation
2. Frame 1: Character in starting pose?
3. Play: Animation smooth?
4. Check: All body parts move?
5. Ground: Feet touch ground correctly?
```

**If NO to any**: See specific issues below

---

## Specific AccuRig → AccuRig Issues

### Problem: AccuRig animation looks wrong on another AccuRig

**This should work perfectly! They're the same rig type.**

**Most likely causes (in order)**:

#### 1. Transforms Not Applied ⭐ **CHECK THIS FIRST**
```
Target armature has scale/rotation not applied
→ Solution: Ctrl + A → All Transforms
```

#### 2. Using Bone Mapping (Don't!)
```
You used bone mapping for same rig type
→ Solution: Use Animation Manage → Apply Animation
→ NO bone mapping needed!
```

#### 3. Different AccuRig Versions
```
Source: AccuRig v1.0
Target: AccuRig v2.0 (different bone names)
→ Solution: Use same AccuRig version for both
```

#### 4. Modified Rest Pose
```
Someone changed bone positions in Edit mode
→ Solution: Use fresh AccuRig export
```

#### 5. Constraints or Drivers
```
Target has IK, constraints, or drivers
→ Solution: Disable/delete before applying animation
```

---

## Step-by-Step Fix for AccuRig → AccuRig

### Correct Workflow (No Bone Mapping Needed!)

**Step 1: Prepare Source**
```
1. Load source AccuRig character (with animation)
2. Select armature
3. Animation Manage → Save Animation
4. Name: "MyAnimation"
5. Click OK
✅ Animation saved
```

**Step 2: Prepare Target**
```
1. Load target AccuRig character (empty)
2. Select armature
3. Object mode
4. Ctrl + A → All Transforms
5. Verify transforms in N panel:
   Location: (0, 0, 0)
   Rotation: (0, 0, 0)
   Scale: (1, 1, 1)
✅ Target ready
```

**Step 3: Apply Animation (NO BONE MAPPING!)**
```
1. Target armature still selected
2. Animation Manage → Apply Animation
3. Select: MyAnimation
4. Click OK
✅ Animation applied
```

**Step 4: Verify**
```
1. Press Spacebar
2. Animation should play perfectly
3. Pose matches original
4. Movement realistic
```

---

## Advanced Fixes

### Fix 1: Reset Target Armature to Default

If target armature is corrupted:

```
1. Delete target armature
2. Re-export from AccuRig with default settings
3. Import into Blender
4. Apply all transforms immediately
5. Try animation transfer again
```

### Fix 2: Bake Animation with Constraints

If target has IK or constraints:

```
1. Apply animation
2. Select target armature → Pose mode
3. Select all bones (A)
4. Animation menu → Bake Action
5. Settings:
   - Visual Keying: ON
   - Clear Constraints: ON
   - Bake Data: Pose
6. Click OK
```

### Fix 3: Match Exact Rest Pose

For perfect matching:

```
1. Source armature → Edit mode
2. Select all bones (A)
3. Copy (Ctrl + C)
4. Target armature → Edit mode
5. Select all bones (A)
6. Paste (Ctrl + V)
7. Object mode
8. Apply animation
```

---

## Prevention Checklist

**Before Starting Any Animation Transfer**:

### For Source Armature:
```
□ Animation plays correctly on source
□ All transforms applied (if moving to target)
□ No temporary constraints or drivers
□ Animation saved with descriptive name
```

### For Target Armature:
```
□ Fresh export from rig tool (AccuRig/Mixamo/etc)
□ Location: (0, 0, 0)
□ Rotation: (0, 0, 0)
□ Scale: (1, 1, 1)
□ Ctrl + A → All Transforms applied
□ No constraints (or disable them first)
□ Same rig version as source
```

### During Transfer:
```
□ Using correct workflow (mapping vs no mapping)
□ Target armature selected (highlighted)
□ Console open to see warnings
□ Test with simple animation first
```

### After Transfer:
```
□ Animation plays smoothly
□ Pose matches original at frame 1
□ All body parts move correctly
□ Feet touch ground properly
□ No console errors
```

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Sliding/floating | Apply location transform |
| Twisted bones | Apply rotation transform |
| Wrong size | Apply scale transform |
| Partial animation | Check bone names match |
| No animation | Target not selected |
| Broken animation | Reset rest pose |
| Gimbal lock | Change to Quaternion rotation |

---

## When to Use Bone Mapping

**Use Bone Mapping When**:
- ✅ Different rig types (Mixamo → AccuRig)
- ✅ Different bone names
- ✅ Different bone counts
- ✅ Custom rig → Standard rig

**Don't Use Bone Mapping When**:
- ❌ Same rig type (AccuRig → AccuRig)
- ❌ Same bone names
- ❌ Identical structure
- ❌ From same export source

---

## Console Error Messages

### "Bone not found in target: [BoneName]"
**Cause**: Animation has bones not in target
**Fix**: Use bone mapping OR ensure exact same rig type

### "No active action on armature"
**Cause**: Animation wasn't applied
**Fix**: Verify target armature selected, try again

### "RuntimeError: Error: name 'Dict' is not defined"
**Cause**: Old version of addon
**Fix**: Install latest FIXED or COMPLETE version

### "Animation data is empty"
**Cause**: Animation file corrupted or empty
**Fix**: Re-save animation from source

---

## Getting Help

### Information to Provide:

1. **Rig Types**:
   - Source: AccuRig v? / Mixamo / Other?
   - Target: AccuRig v? / Mixamo / Other?

2. **Workflow Used**:
   - Bone Mapping: Yes/No?
   - Steps followed?

3. **Transform Values** (N panel):
   - Location: ?
   - Rotation: ?
   - Scale: ?

4. **Console Output**:
   - Any error messages?
   - Any warnings?

5. **Symptoms**:
   - Describe exactly what looks wrong
   - Screenshot if possible

---

## Video Tutorial: Fixing Common Issues

**Scene 1: Unapplied Transforms** (30 sec)
```
- Show armature with scale 2.0
- Animation looks 2x too big
- Ctrl + A → All Transforms
- Animation now correct
```

**Scene 2: Wrong Workflow** (30 sec)
```
- AccuRig → AccuRig with bone mapping (wrong!)
- Show errors in console
- Redo without bone mapping
- Works perfectly
```

**Scene 3: Rest Pose Difference** (30 sec)
```
- Show arms at different angles
- Animation transfers but looks off
- Match rest poses
- Perfect transfer
```

---

**Key Takeaway**: For AccuRig → AccuRig, apply all transforms first and DON'T use bone mapping!
