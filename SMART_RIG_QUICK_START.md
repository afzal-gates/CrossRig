# Smart Rig Quick Start Guide

## 🚀 30-Second Start

1. **Select your character mesh** → Open CrossRig panel (N key)
2. **Armature Manage** → **Smart Rig** → **Start Smart Rig Mode**
3. **Pick landmarks**: Tab (Edit Mode) → Select vertex → Tab (Object Mode) → Click landmark button
4. **Repeat** for each landmark (minimum 3)
5. **Generate Rig** → Done! ✨

---

## 📍 Essential Landmarks (Minimum Setup)

### Quick 5-Landmark Rig:
```
1. Hips (spine_bottom)    - Center of pelvis
2. Neck                    - Base of neck
3. L Shoulder             - Left shoulder joint
4. L Hip                  - Left hip joint
5. R Hip                  - Right hip joint (or use Auto-Mirror)
```

### Complete 15-Landmark Rig:
```
Head & Spine:
├─ Head Top
├─ Neck
├─ Spine Top
├─ Spine Mid
└─ Hips

Arms (both sides):
├─ Shoulder
├─ Elbow
├─ Wrist
└─ Hand

Legs (both sides):
├─ Hip
├─ Knee
├─ Ankle
└─ Foot
```

---

## 🎯 Pro Tips

### Landmark Placement:
✅ **DO:**
- Place at joint centers (not surface)
- Use orthographic views (Numpad 1/3/7)
- Work in wireframe mode (Z key)
- Start with spine, then limbs

❌ **DON'T:**
- Place on clothing/armor
- Rush through placement
- Mix left/right sides

### Workflow Efficiency:
1. **Mark one side completely** (left arm/leg)
2. **Click Auto-Mirror** → instant symmetry
3. **Check landmarks** → count should be even for bilateral
4. **Generate with Auto Skin ON** → saves time

---

## 🔧 Common Issues

### "Need at least 3 landmarks"
→ Add more landmarks before generating

### "No vertex selected"
→ Select vertex in Edit Mode, then return to Object Mode before clicking button

### Rig looks wrong
→ Check landmark placement in orthographic views
→ Ensure neck is above hips, shoulders are at shoulder height

### Auto-mirror doesn't work
→ Ensure mesh is centered (origin at X=0)
→ Check landmarks are marked as LEFT or RIGHT (not CENTER)

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Tab | Edit/Object mode toggle |
| N | Show/hide sidebar panel |
| Z | Shading mode menu |
| Numpad 1 | Front view |
| Numpad 3 | Side view |
| Numpad 7 | Top view |

---

## 🎨 Marker Colors

- 🔴 **Red** = Left side
- 🔵 **Blue** = Right side
- 🟢 **Green** = Center

---

## 📊 Landmark Order (Recommended)

1. **Spine first** (Hips → Spine Mid → Spine Top → Neck)
2. **Head** (Head Top)
3. **Left Arm** (Shoulder → Elbow → Wrist → Hand)
4. **Auto-Mirror** for right arm
5. **Left Leg** (Hip → Knee → Ankle → Foot)
6. **Auto-Mirror** for right leg
7. **Generate Rig**

---

## ✨ Feature Highlights

- ✅ Visual landmark picking
- ✅ Auto-mirror for symmetry
- ✅ Industry-standard bone names
- ✅ Automatic skinning
- ✅ Proper bone hierarchy
- ✅ Works with any humanoid mesh

---

## 📚 Need More Help?

See **SMART_RIG_GUIDE.md** for:
- Detailed step-by-step instructions
- Advanced techniques
- Troubleshooting guide
- Technical customization

---

**Happy Rigging! 🦴✨**

_CrossRig Smart Rig v1.1.0_
