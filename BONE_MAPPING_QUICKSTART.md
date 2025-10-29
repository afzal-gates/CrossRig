# Bone Mapping Quick Start Guide

## What is Bone Mapping?

Bone Mapping allows you to transfer animations between armatures with different bone names and structures (e.g., Mixamo → AccuRig).

---

## 5-Minute Quick Start

### 1️⃣ Setup (30 seconds)
1. Open **CrossRig** panel (3D Viewport → N panel)
2. Expand **"Bone Mapping"** section
3. Select **Source Armature** (has the animation)
4. Select **Target Armature** (will receive animation)
5. Enter **Preset Name** (e.g., "Mixamo_to_AccuRig")

### 2️⃣ Create Mapping (10 seconds)
1. Click **"Create Bone Mapping"** button
2. Source bones load into the list

### 3️⃣ Auto-Map (20 seconds)
1. Set **Auto-Map Threshold** to 0.7 (slider)
2. Click **"Auto-Map Bones"** button
3. Wait for algorithm to match bones
4. Check console for results

### 4️⃣ Review (1 minute)
1. Scroll through **Bone Mappings** list
2. Look for confidence badges:
   - ✓ = Good (manual or exact match)
   - 80-99% = Probably correct
   - 60-79% = Check this one
   - ? = Not mapped
3. Click any row to edit target bone
4. Use search dropdown to find correct bone

### 5️⃣ Save Preset (10 seconds)
1. Expand **"Mapping Presets"**
2. Click **"Save Mapping"**
3. Confirm name and description
4. Preset saved for future use!

### 6️⃣ Apply Animation (30 seconds)
1. Expand **"Apply Animation"**
2. Click **"Apply Animation with Mapping"**
3. Select saved animation file
4. Animation transfers to target armature!

---

## Tips

**Best Threshold Values:**
- 0.8-1.0 = Very strict (fewer matches, higher accuracy)
- 0.7 = Recommended starting point
- 0.6 = More matches (review carefully)
- <0.6 = Too permissive (lots of false matches)

**When to Edit Manually:**
- Confidence < 80%
- Critical bones (spine, hips, head)
- Side-specific bones (.L/.R)

**Preset Reuse:**
- Create mapping once per rig type pair
- Reuse for all characters with same rig structure
- Update preset if you find better mappings

---

## Common Patterns

### Mixamo → AccuRig
- Source: mixamorig:Hips → Target: Root
- Source: mixamorig:Spine → Target: Spine1
- Threshold: 0.7-0.8 works well

### Mixamo → Rigify
- Handles DEF- prefix automatically
- Use threshold 0.7
- Check spine chain carefully

---

## Troubleshooting

**No matches found?**
→ Lower threshold to 0.6

**Wrong bones matched?**
→ Edit manually using search dropdown

**Animation not applying?**
→ Run "Validate Mapping" first

**Preset not saving?**
→ Check `~/.crossrig_bone_mappings/` folder exists

---

## Validation Checklist

Before applying animation to production:
- [ ] Auto-map threshold ≥ 0.7
- [ ] All critical bones mapped
- [ ] No ? (unmapped) bones for animated parts
- [ ] Validated with "Validate Mapping" button
- [ ] Tested with simple animation first
- [ ] Preset saved for reuse

---

## File Locations

**Mapping Presets:**
- Windows: `C:\Users\[You]\.crossrig_bone_mappings\`
- macOS/Linux: `~/.crossrig_bone_mappings/`

**Saved Animations:**
- Windows: `C:\Users\[You]\.crossrig_animations\`
- macOS/Linux: `~/.crossrig_animations/`

---

**That's it! You're ready to transfer animations between different armature types! 🎬**
