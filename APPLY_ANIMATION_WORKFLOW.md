# Apply Animation from Source to Target Armature - Complete Workflow

## Overview

This guide shows you how to transfer animation from one armature type to another (e.g., Mixamo → AccuRig) using Mixanimo Lite's bone mapping feature.

---

## Prerequisites

✅ Mixanimo Lite v1.4.0+ installed and enabled
✅ Source armature with animation (e.g., Mixamo character)
✅ Target armature without animation (e.g., AccuRig character)
✅ Both armatures loaded in the same Blender scene

---

## Workflow Methods

### 🚀 Method 1: Quick Transfer (Use Pre-Built Preset)
**Time**: ~1 minute | **Best for**: Mixamo → AccuRig standard rigs

### 🎯 Method 2: Auto-Map Transfer (First Time Setup)
**Time**: ~2 minutes | **Best for**: Any rig pair, reusable

### ⚙️ Method 3: Manual Mapping Transfer (Custom Rigs)
**Time**: ~5-10 minutes | **Best for**: Non-standard rigs

---

## Method 1: Quick Transfer (Pre-Built Preset)

### Step 1: Save Animation from Source
1. Select **source armature** (Mixamo character with animation)
2. Open **Mixanimo Lite** panel (N panel → Mixanimo Lite tab)
3. Expand **"Animation Manage"** section
4. Click **"Save Animation"** button
5. In dialog:
   - **Action**: Select the action to save (e.g., "Walking")
   - **Animation Name**: Enter name (e.g., "Mixamo_Walk")
   - **Description**: Optional description
6. Click **OK**
7. ✅ Animation saved to `~/.mixanimo_animations/Mixamo_Walk.json`

### Step 2: Load Bone Mapping Preset
1. Expand **"Bone Mapping"** section
2. Expand **"Mapping Presets"** subsection
3. Click **"Browse Mappings"** button
4. Navigate to:
   - `[Blender Addons]/Mixanimo_Lite/examples/`
   - Or `~/.mixanimo_bone_mappings/`
5. Select **"Mixamo_to_AccuRig.json"**
6. Click **OK**
7. ✅ Mapping loaded (65 bones mapped)

### Step 3: Select Target Armature
1. In **3D Viewport**, select **target armature** (AccuRig character)
2. Make it the **active object** (last selected, highlighted)
3. ✅ Target armature selected and active

### Step 4: Apply Animation with Mapping
1. Still in **"Bone Mapping"** section
2. Expand **"Apply Animation"** subsection
3. Click **"Apply Animation with Mapping"** button
4. In dialog:
   - **Animation**: Select "Mixamo_Walk" (or your saved animation)
5. Click **OK**
6. ✅ Animation applied to target armature!

### Step 5: Verify and Play
1. Move timeline to frame 1
2. Press **Spacebar** to play animation
3. ✅ AccuRig character now has Mixamo animation!

**Result**: Animation transferred in ~60 seconds!

---

## Method 2: Auto-Map Transfer (First Time Setup)

Use this when you don't have a pre-built preset but want to create one.

### Step 1: Save Animation from Source
*(Same as Method 1, Step 1)*

### Step 2: Setup Bone Mapping
1. Expand **"Bone Mapping"** section
2. Expand **"Setup"** subsection
3. Select armatures:
   - **Source Armature**: Select Mixamo character
   - **Target Armature**: Select AccuRig character
4. **Preset Name**: Enter name (e.g., "My_Mixamo_to_AccuRig")
5. Click **"Create Bone Mapping"** button
6. ✅ Bone list populated (all source bones listed)

### Step 3: Auto-Map Bones
1. Still in **"Setup"** subsection
2. Set **Auto-Map Threshold**: 0.7 (recommended)
   - Use slider or type value
3. Click **"Auto-Map Bones"** button
4. Wait ~2 seconds for algorithm
5. Check **Console** (Window → Toggle System Console) for results:
   ```
   Auto-mapping complete:
   Mapped: 62 bones
   Skipped: 0 bones (already mapped)
   Unmapped: 3 bones
   Total mappings: 62
   ```
6. ✅ Bones auto-mapped!

### Step 4: Review Mappings (Optional)
1. Expand **"Bone Mappings"** subsection
2. Scroll through the list
3. Check confidence badges:
   - ✓ = Perfect (100%)
   - 90-99% = Very good
   - 80-89% = Good
   - 70-79% = Review this
   - ? = Not mapped
4. To edit a mapping:
   - Click on the row
   - Use search dropdown to select correct target bone
   - Confidence auto-updates to 100%
5. ✅ Mappings reviewed and corrected if needed

### Step 5: Save Mapping Preset (Important!)
1. Expand **"Mapping Presets"** subsection
2. Click **"Save Mapping"** button
3. In dialog:
   - **Preset Name**: Confirm or edit name
   - **Description**: "Mixamo standard to AccuRig humanoid"
4. Click **OK**
5. ✅ Preset saved for future use!

### Step 6: Apply Animation
1. Select **target armature** in 3D Viewport
2. Expand **"Apply Animation"** subsection
3. Click **"Apply Animation with Mapping"** button
4. Select animation from saved animations
5. Click **OK**
6. ✅ Animation applied!

### Step 7: Verify
1. Play animation (Spacebar)
2. Check all body parts animate correctly
3. ✅ Transfer complete!

**Result**: First time ~2 minutes, subsequent uses ~30 seconds!

---

## Method 3: Manual Mapping Transfer

Use this for custom rigs or fine-tuned control.

### Step 1-2: Save Animation & Setup
*(Same as Method 2, Steps 1-2)*

### Step 3: Manual Bone Mapping
1. Expand **"Bone Mappings"** subsection
2. For each unmapped bone (? icon):
   - Click the row
   - Click on **target bone field** (→ arrow)
   - Use **search dropdown** to find correct bone
   - Or type bone name directly
3. Repeat for all critical bones
4. ✅ All important bones mapped

**Critical Bones Checklist**:
- [ ] Root/Hips
- [ ] Spine chain (3 bones)
- [ ] Neck
- [ ] Head
- [ ] Shoulders (2)
- [ ] Arms (4 per side)
- [ ] Hands (2)
- [ ] Legs (4 per side)
- [ ] Feet (2)

### Step 4-7: Save, Apply, Verify
*(Same as Method 2, Steps 5-7)*

---

## Validation Before Applying

### Option: Validate Mapping
1. Before applying animation, click **"Validate Mapping"** button
2. Select animation to validate against
3. Check **Console** for validation report:
   ```
   ✅ Bone mapping is valid
   Coverage: 95.4% (62/65 bones)

   Valid mappings: 62
   Unmapped bones: 3
   Missing target bones: 0
   ```
4. If issues found:
   - Review unmapped bones list
   - Edit mappings as needed
   - Validate again

---

## Troubleshooting

### Issue: Animation doesn't apply
**Causes**:
- Target armature not selected
- No bone mappings defined
- Animation file not found

**Solutions**:
1. Ensure target armature is **active object** (highlighted in orange)
2. Check **Bone Mappings** list has entries
3. Verify animation file exists in saved animations

### Issue: Some body parts don't animate
**Causes**:
- Bones not mapped
- Wrong bone mapping
- Missing bones in target

**Solutions**:
1. Run **"Validate Mapping"** to find issues
2. Check console for unmapped bones list
3. Manually map missing bones
4. Verify target armature has required bones

### Issue: Animation looks broken
**Causes**:
- Wrong bones mapped
- Low confidence mappings
- Incorrect side (left/right)

**Solutions**:
1. Review all mappings with confidence < 80%
2. Check left/right bones map correctly
3. Use bone search to find correct matches
4. Test with simple animation first

### Issue: Fingers don't animate
**Causes**:
- Finger bones not mapped
- Target rig has no fingers
- Different finger bone names

**Solutions**:
1. Check if target has finger bones
2. Lower auto-map threshold to 0.65
3. Manually map finger bones
4. Or skip fingers if not needed

---

## Advanced: Batch Animation Transfer

Transfer multiple animations efficiently:

### 1. Setup Once
1. Create bone mapping
2. Save preset
3. Test with one animation

### 2. Batch Transfer
For each animation:
1. Load preset (5 seconds)
2. Apply animation (10 seconds)
3. Verify (10 seconds)

**Time per animation**: ~25 seconds

**Example**: 100 animations = 42 minutes (vs 4+ hours manual!)

---

## Tips for Perfect Results

### ✅ Do's
- ✅ Save bone mapping preset after first successful transfer
- ✅ Start with simple animation to test mapping
- ✅ Use threshold 0.7 for Mixamo → AccuRig
- ✅ Validate before applying to important projects
- ✅ Review all mappings with confidence < 80%
- ✅ Name presets descriptively
- ✅ Test left and right sides separately

### ❌ Don'ts
- ❌ Skip validation on first transfer
- ❌ Use threshold below 0.6 (too permissive)
- ❌ Ignore console warnings
- ❌ Apply without testing on simple animation first
- ❌ Forget to save preset for reuse
- ❌ Mix up source and target armatures
- ❌ Apply to wrong armature

---

## Common Workflows

### Workflow A: Mixamo Library → AccuRig Character
**Goal**: Transfer 50 Mixamo animations to one AccuRig character

**Steps**:
1. Load Mixamo character + AccuRig character
2. Create/load Mixamo_to_AccuRig preset (once)
3. For each Mixamo animation:
   - Load animation on Mixamo character
   - Save animation
   - Apply to AccuRig with preset
   - Export or use in project

**Time**: ~2 min setup + 50 × 30 sec = ~27 minutes total

### Workflow B: One Animation → Multiple Characters
**Goal**: Apply one animation to 10 different AccuRig characters

**Steps**:
1. Save animation once
2. Load preset once
3. For each character:
   - Load character
   - Apply animation with preset
   - Export character with animation

**Time**: 10 × 30 sec = ~5 minutes total

### Workflow C: Custom Rigs
**Goal**: Transfer between non-standard rigs

**Steps**:
1. Create mapping with auto-map (threshold 0.65)
2. Manually review and edit all mappings
3. Test with simple animation
4. Adjust mappings if needed
5. Save preset
6. Batch transfer remaining animations

**Time**: ~10 min setup + testing, then 30 sec per animation

---

## File Locations

### Saved Animations
- **Windows**: `C:\Users\[You]\.mixanimo_animations\`
- **macOS/Linux**: `~/.mixanimo_animations/`

### Bone Mapping Presets
- **Windows**: `C:\Users\[You]\.mixanimo_bone_mappings\`
- **macOS/Linux**: `~/.mixanimo_bone_mappings/`

### Example Presets
- **Addon folder**: `[Blender]/addons/Mixanimo_Lite/examples/`

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  MIXANIMO BONE MAPPING WORKFLOW                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. SAVE ANIMATION                              │
│     Animation Manage → Save Animation           │
│                                                 │
│  2. SETUP MAPPING                               │
│     Bone Mapping → Setup                        │
│     - Select source armature                    │
│     - Select target armature                    │
│     - Create Bone Mapping                       │
│                                                 │
│  3. AUTO-MAP (Optional)                         │
│     Setup → Auto-Map Bones (threshold 0.7)      │
│                                                 │
│  4. REVIEW MAPPINGS                             │
│     Bone Mappings → Check confidence            │
│     - Edit low confidence mappings              │
│                                                 │
│  5. SAVE PRESET                                 │
│     Mapping Presets → Save Mapping              │
│                                                 │
│  6. APPLY ANIMATION                             │
│     Apply Animation → Apply with Mapping        │
│     - Select target armature first!             │
│                                                 │
│  7. VERIFY                                      │
│     - Play animation (Spacebar)                 │
│     - Check all body parts                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Video Tutorial Script (If Recording)

### Scene 1: Setup (30 seconds)
1. Show Mixamo character with walk animation
2. Show AccuRig character without animation
3. Open Mixanimo Lite panel
4. Highlight Bone Mapping section

### Scene 2: Save Animation (15 seconds)
1. Select Mixamo character
2. Animation Manage → Save Animation
3. Name: "Mixamo_Walk"
4. Confirm saved

### Scene 3: Create Mapping (30 seconds)
1. Bone Mapping → Setup
2. Select source (Mixamo)
3. Select target (AccuRig)
4. Create Bone Mapping
5. Auto-Map Bones (threshold 0.7)
6. Show mapped bones in list

### Scene 4: Apply (20 seconds)
1. Select AccuRig character
2. Apply Animation → Apply with Mapping
3. Select "Mixamo_Walk"
4. Confirm

### Scene 5: Result (15 seconds)
1. Play animation
2. Show AccuRig walking with Mixamo animation
3. Zoom in on hands, feet
4. Success!

**Total**: ~2 minutes

---

## Success Criteria

After following this workflow, you should have:

✅ Animation saved from source armature
✅ Bone mapping created and saved as preset
✅ Animation applied to target armature
✅ Target armature animates correctly
✅ All major body parts move properly
✅ Preset available for future transfers
✅ Process takes < 2 minutes

---

## Next Steps

After successful transfer:

1. **Export**: Use Mixanimo's export features
2. **Batch Process**: Transfer more animations
3. **Share Preset**: Share with team members
4. **Refine Mapping**: Adjust for better results
5. **Create Variants**: Different presets for different scenarios

---

**You're now ready to transfer animations between any armature types! 🎬✨**
