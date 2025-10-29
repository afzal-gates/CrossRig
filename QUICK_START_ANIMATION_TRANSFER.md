# 🚀 Quick Start: Transfer Animation in 60 Seconds

## The Fastest Way to Transfer Animation Between Armatures

---

## ⚡ Ultra-Quick Method (Mixamo → AccuRig)

### 1. Select Source Armature (5 sec)
```
Click on Mixamo character (with animation)
```

### 2. Save Animation (10 sec)
```
Mixanimo Panel → Animation Manage → Save Animation
- Name: "MyAnimation"
- Click OK
```

### 3. Load Preset (10 sec)
```
Bone Mapping → Mapping Presets → Browse Mappings
- Navigate to: [addon]/examples/
- Select: Mixamo_to_AccuRig.json
- Click OK
```

### 4. Select Target Armature (5 sec)
```
Click on AccuRig character (no animation)
Make sure it's highlighted (active)
```

### 5. Apply Animation (10 sec)
```
Bone Mapping → Apply Animation → Apply Animation with Mapping
- Select: MyAnimation
- Click OK
```

### 6. Play! (5 sec)
```
Press Spacebar to play
✅ Animation transferred!
```

**Total Time: ~45 seconds**

---

## 🎯 Standard Method (Any Rig → Any Rig)

### 1. Save Animation (10 sec)
```
Select source armature → Animation Manage → Save Animation
```

### 2. Setup Mapping (15 sec)
```
Bone Mapping → Setup
- Source Armature: [Pick source]
- Target Armature: [Pick target]
- Preset Name: Source_to_Target
- Click: Create Bone Mapping
```

### 3. Auto-Map (10 sec)
```
Still in Setup:
- Auto-Map Threshold: 0.7
- Click: Auto-Map Bones
(Check console for results)
```

### 4. Save Preset (10 sec)
```
Mapping Presets → Save Mapping
- Confirm name
- Click OK
```

### 5. Select Target (5 sec)
```
Click target armature in viewport
```

### 6. Apply (10 sec)
```
Apply Animation → Apply Animation with Mapping
- Select your animation
- Click OK
```

### 7. Verify (5 sec)
```
Press Spacebar
✅ Check animation plays correctly
```

**Total Time: ~65 seconds**

---

## 📋 Panel Location

```
3D Viewport (any)
├─ Press N (toggle sidebar)
├─ Click "Mixanimo Lite" tab
└─ Sections:
    ├─ Play Ground
    ├─ 🆕 Bone Mapping ← HERE!
    ├─ Armature Manage
    └─ Animation Manage
```

---

## 🎨 UI Layout Reference

```
╔══════════════════════════════════════╗
║  BONE MAPPING                   ▼    ║
╠══════════════════════════════════════╣
║  Setup                          ▼    ║
║  ├─ Source Armature: [Choose...]     ║
║  ├─ Target Armature: [Choose...]     ║
║  ├─ Preset Name: [Name]              ║
║  ├─ [Create Bone Mapping]            ║
║  └─ Auto-Map:                        ║
║      ├─ Threshold: ████▒▒▒ 0.70      ║
║      └─ [Auto-Map Bones]             ║
╠══════════════════════════════════════╣
║  Bone Mappings                  ▼    ║
║  ├─ Source → Target    Confidence    ║
║  ├─ Hips → Root            ✓         ║
║  ├─ Spine → Spine1         95%       ║
║  ├─ LeftArm → UpperArm.L   85%       ║
║  └─ ...                              ║
╠══════════════════════════════════════╣
║  Mapping Presets                ▼    ║
║  ├─ [Save Mapping] [Load]            ║
║  └─ [Browse Mappings] [Delete]       ║
╠══════════════════════════════════════╣
║  Apply Animation                ▼    ║
║  ├─ [Apply Animation with Mapping]   ║
║  └─ [Validate Mapping]               ║
╚══════════════════════════════════════╝
```

---

## ⚠️ Important Checks

### Before Applying
- [ ] Target armature is selected (highlighted)
- [ ] Bone mappings list is populated
- [ ] At least 90% of bones mapped

### After Applying
- [ ] Animation plays on target
- [ ] All body parts move
- [ ] No console errors

---

## 🔧 Troubleshooting Quick Fixes

### Animation doesn't apply?
```
✓ Check: Target armature selected?
✓ Check: Bone mappings list has entries?
✓ Try: Click target armature again
```

### Some parts don't animate?
```
✓ Check console for unmapped bones
✓ Lower threshold to 0.65
✓ Run: Validate Mapping
```

### Wrong bones moving?
```
✓ Review mappings with confidence < 80%
✓ Edit incorrect mappings manually
✓ Check left/right sides
```

---

## 💡 Pro Tips

### Tip 1: Save Preset First Time
After successful auto-map, always save preset!
Reuse = 80% time savings

### Tip 2: Start Simple
Test with walk/idle animation first
Complex animations after you verify mapping

### Tip 3: Check Console
Console shows detailed mapping results
Window → Toggle System Console

### Tip 4: Optimal Threshold
- Mixamo → AccuRig: 0.7
- Custom rigs: 0.65-0.75
- Very different rigs: 0.6

### Tip 5: Batch Transfer
Create mapping once
Transfer 100+ animations in minutes!

---

## 🎬 Expected Results

### Mixamo → AccuRig (Standard Rigs)
```
Auto-Map Coverage: 95-100%
Manual Edits: 0-3 bones
Time per animation: ~30 seconds
Confidence: High (0.85-1.0)
```

### Custom Rig → Custom Rig
```
Auto-Map Coverage: 70-90%
Manual Edits: 5-15 bones
Time per animation: ~60 seconds
Confidence: Medium (0.7-0.9)
```

### Very Different Rigs
```
Auto-Map Coverage: 50-70%
Manual Edits: 15-30 bones
Time per animation: ~2-5 minutes
Confidence: Low-Medium (0.6-0.8)
```

---

## 📞 Need Help?

### Check These Files
1. `APPLY_ANIMATION_WORKFLOW.md` - Detailed guide
2. `MIXAMO_ACCURIG_MAPPING_GUIDE.md` - Specific to Mixamo/AccuRig
3. `BONE_MAPPING_QUICKSTART.md` - Feature overview

### Common Issues Document
See troubleshooting section in workflow guide

### Console Output
Always check console for detailed information

---

## ✅ Success Checklist

Your animation transfer is successful if:

- [x] Target armature plays animation smoothly
- [x] All major body parts animate (arms, legs, spine, head)
- [x] No console errors about missing bones
- [x] Animation looks natural (not broken or glitchy)
- [x] Preset saved for future use
- [x] Process took < 2 minutes

---

## 🎯 Next Steps After First Success

1. **Batch Transfer**
   - Use saved preset
   - Transfer multiple animations
   - Build animation library

2. **Refine Mapping**
   - Review low confidence mappings
   - Edit for better results
   - Update saved preset

3. **Share Preset**
   - Export preset file
   - Share with team
   - Standardize workflow

4. **Export Animations**
   - Use Mixanimo's export features
   - Export as FBX
   - Use in game engine or other projects

---

**You're ready! Follow the steps above and transfer your first animation! 🚀**

---

## 📱 Print This Page

Keep this reference handy while working in Blender!
