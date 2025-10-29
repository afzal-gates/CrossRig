# Mixanimo Lite v1.1.0 - Animation Preset System

## 🎉 New Feature: Save & Load Animation Presets

You asked for the ability to **save animation sequences as presets** and **load them on new armatures**. This feature is now complete and ready to use!

---

## ✨ What You Can Do Now

### 1. Save Your Animation Sequences
- Set up your animation sequence (actions, repeat counts, angles, settings)
- Click **"Save Preset"** button
- Give it a name and description
- Reuse it later on any character!

### 2. Load Presets on New Armatures
- Import a new character with Mixamo animations
- Click **"Load"** to quickly select from your saved presets
- OR use **"Browse Presets"** to navigate files
- Preset is applied instantly!

### 3. Manage Your Preset Library
- **Delete** unwanted presets
- **Open Preset Folder** to organize files
- **Share** preset files with team members
- **Backup** your animation library

---

## 🎨 UI Overview

New **"Animation Presets"** section in your panel:

```
┌─────────────────────────────────────┐
│  Animation Presets        FILE      │
├─────────────────────────────────────┤
│  [Save Preset]  [Load]              │  ← Quick actions
│  [Browse Presets]  [Delete]         │  ← Advanced options
│  [Open Preset Folder]               │  ← File management
└─────────────────────────────────────┘
```

---

## 📋 Quick Start Guide

### Save a Preset

1. **Set up your animation**:
   ```
   - Load Actions
   - Reorder as needed
   - Set repeat counts (e.g., Punch: 2x, Kick: 1x)
   - Set angles (e.g., Walk: 0°, Turn: 90°)
   - Configure overlap frames and root bone
   ```

2. **Click "Save Preset"**

3. **Enter details**:
   ```
   Preset Name: "Combat Combo"
   Description: "3-hit combo sequence for melee"
   ```

4. **Done!** Preset saved to `~/.mixanimo_presets/`

---

### Load a Preset

**Method 1: Quick Load (Recommended)**
```
1. Click "Load" button
2. Select "Combat Combo" from dropdown
3. Click OK
4. Actions loaded instantly!
```

**Method 2: Browse Files**
```
1. Click "Browse Presets"
2. Navigate to preset file
3. Select .json file
4. Actions loaded!
```

---

### Apply to New Character

```
1. Import new character (with Mixamo FBX files)
2. Select armature
3. Click "Load" → Select preset
4. Click "Confirm Order"
5. Click "Send to Timeline"
```

**Result**: Animation sequence applied to new character! 🎉

---

## 💡 Real-World Examples

### Example 1: Character Animation Library
```
Save Presets:
- "Idle_Breathing_Loop.json"  (Idle x2, Looking Around x1)
- "Walk_Run_Sprint.json"      (Walk 0°, Run 45°, Sprint 90°)
- "Combat_3Hit.json"          (Punch Left, Punch Right, Kick)

Use Case:
- Import new character
- Load "Combat_3Hit" preset
- Ready for action in 3 clicks!
```

---

### Example 2: Team Collaboration
```
Animator A creates preset:
- "CutsceneIntro.json"
  (Camera pan, Character enters, Wave animation)

Shares file with Animator B:
- Copy .json file to shared drive
- Animator B places in their ~/.mixanimo_presets/
- Load preset, instant setup!
```

---

### Example 3: Animation Templates
```
Create templates for different scenarios:
- "Boss_Attack_Pattern_A.json"
- "Boss_Attack_Pattern_B.json"
- "Boss_Attack_Pattern_C.json"

Test different patterns:
- Load Pattern A → Preview → Too slow
- Load Pattern B → Preview → Perfect!
- Use Pattern B for boss fight
```

---

## 📁 Preset File Format

Presets are saved as human-readable JSON:

```json
{
  "name": "Combat Combo",
  "description": "3-hit melee combo",
  "root_bone": "mixamorig:Hips",
  "overlap_frames": 3,
  "forward_axis": "Y+",
  "actions": [
    {
      "action_name": "Punch_Left",
      "use_action": true,
      "repeat_count": 1,
      "angle": 0
    },
    {
      "action_name": "Punch_Right",
      "use_action": true,
      "repeat_count": 1,
      "angle": 0
    },
    {
      "action_name": "Kick",
      "use_action": true,
      "repeat_count": 1,
      "angle": 45
    }
  ],
  "version": "1.0"
}
```

**Benefits**:
- ✅ Human-readable (can edit in text editor)
- ✅ Portable (works on Windows/Mac/Linux)
- ✅ Shareable (email, version control, shared drives)
- ✅ Version-tracked (JSON in Git)

---

## 🏗️ Architecture (Clean Architecture)

Following the same Clean Architecture pattern as the rest of the addon:

### Domain Layer (Pure Business Logic)
```
core/domain/preset_entities.py
- AnimationPreset: Complete preset data
- PresetActionItem: Individual action settings
- JSON serialization/deserialization
```

### Services Layer (File Operations)
```
core/services/preset_service.py
- save_preset_to_file()
- load_preset_from_file()
- list_available_presets()
- delete_preset_file()
- validate_preset()
```

### Use Cases Layer (Business Rules)
```
core/use_cases/save_preset.py
- save_animation_preset()
  → Converts Blender data to preset
  → Validates
  → Saves to file

core/use_cases/load_preset.py
- load_animation_preset()
  → Loads from file
  → Validates actions exist
  → Populates action collection
- apply_preset_to_armature()
  → Applies preset to specific armature
```

### Adapters Layer (Blender Integration)
```
adapters/blender/preset_operators.py
- MIXAMO_OT_SavePreset (dialog)
- MIXAMO_OT_LoadPreset (file browser)
- MIXAMO_OT_LoadPresetMenu (dropdown)
- MIXAMO_OT_DeletePreset (confirmation)
- MIXAMO_OT_OpenPresetFolder (system)
```

**Total**: 5 new operators, 5 new modules

---

## 📊 Technical Details

### What Changed
| Aspect | v1.0.1 | v1.1.0 | Change |
|--------|--------|--------|--------|
| **Python Modules** | 21 | 26 | +5 modules |
| **Package Size** | 92 KB | 109 KB | +17 KB |
| **Operators** | 11 | 16 | +5 operators |
| **Documentation** | 5 files | 6 files | +PRESET_GUIDE.md |

### File Structure
```
Mixanimo_Lite/
├── core/
│   ├── domain/
│   │   └── preset_entities.py      ← NEW
│   ├── services/
│   │   └── preset_service.py       ← NEW
│   └── use_cases/
│       ├── save_preset.py          ← NEW
│       └── load_preset.py          ← NEW
└── adapters/
    └── blender/
        └── preset_operators.py     ← NEW
```

### Storage Location
- **Windows**: `C:\Users\YourName\.mixanimo_presets\`
- **Mac**: `/Users/YourName/.mixanimo_presets/`
- **Linux**: `/home/yourname/.mixanimo_presets/`

---

## ✅ Compatibility

### Backward Compatible
- ✅ All existing features work unchanged
- ✅ Existing workflows not affected
- ✅ Preset system is completely optional
- ✅ No breaking changes

### Version Requirements
- **Blender**: 3.5.0 or higher (tested with 4.5)
- **Platform**: Windows, Mac, Linux
- **Python**: 3.10+ (included with Blender)

---

## 📚 Complete Documentation

### User Guides
1. **PRESET_GUIDE.md** (9.6 KB) - Complete preset system guide
   - How-to guides
   - Real-world examples
   - Troubleshooting
   - FAQ

2. **INSTALLATION.md** (8 KB) - Installation guide
3. **README.md** (1.7 KB) - Quick start

### Developer Docs
1. **ARCHITECTURE.md** (13 KB) - Clean Architecture explanation
2. **REFACTORING_SUMMARY.md** (9.5 KB) - Refactoring details
3. **CHANGELOG.md** (8.5 KB) - Version history

---

## 🎯 Use Cases Solved

### ✅ Your Request
> "I want to save animation as preset then load and assign those animation to new armature"

**Solution**:
- Save current animation sequence with all settings
- Load preset on any new armature with same animations
- Instant setup, no manual reconfiguration needed

### ✅ Common Workflows
1. **Reuse across characters**: Save once, use on all characters
2. **Team collaboration**: Share preset files via email/Git
3. **Animation library**: Build reusable animation templates
4. **Quick prototyping**: Test different sequences rapidly

---

## 🚀 Installation

### New Users
1. Download `Mixanimo_Lite_v1.1.0.zip` (109 KB)
2. Blender → Edit → Preferences → Add-ons → Install
3. Enable "Mixanimo Lite"
4. Access via 3D Viewport → N key → "Mixanimo Lite" tab

### Upgrading from v1.0.1
1. Uninstall v1.0.1 in Blender
2. Close Blender
3. Install `Mixanimo_Lite_v1.1.0.zip`
4. Enable addon
5. All your workflows preserved + new preset features!

---

## 🎓 Tips & Best Practices

### Naming Presets
✅ **Good**: "Combat_3Hit_Combo", "Locomotion_Walk_Run"
❌ **Avoid**: "test", "preset1", "asdf"

### Add Descriptions
```
Good: "3-hit combo for melee combat, ends with 45° kick"
Bad: ""  (empty)
```

### Organize Presets
Create folders:
```
~/.mixanimo_presets/
├── Combat/
│   ├── Combo_3Hit.json
│   └── Combo_5Hit.json
├── Locomotion/
│   ├── Walk.json
│   └── Run.json
└── Idle/
    └── Breathing.json
```

### Backup Important Presets
- Copy to cloud storage
- Add to version control
- Share with team

---

## 🔧 Troubleshooting

### "Action not found" Warning
**Problem**: Preset references actions not in scene

**Solution**: Import Mixamo FBX files first, then load preset

---

### Can't Find Preset
**Solution**: Click "Open Preset Folder" to see location

---

### Preset Won't Load
**Check**:
- File is valid JSON (open in text editor)
- Blender has the animation actions imported
- Action names match exactly

---

## 📈 Future Enhancements

Possible future additions:
- Import/export presets from ZIP
- Preset categories and tags
- Search/filter presets
- Preset preview/thumbnails
- Batch apply to multiple armatures

---

## 🎉 Summary

### What You Get
✅ **Save** animation sequences as presets
✅ **Load** presets on new armatures
✅ **Manage** preset library (delete, organize)
✅ **Share** presets with team members
✅ **Reuse** sequences across projects

### How to Use
1. Set up animation → Click "Save Preset"
2. Import new character → Click "Load" → Select preset
3. Done! Animation applied instantly

### Package Details
- **Version**: 1.1.0
- **File**: `Mixanimo_Lite_v1.1.0.zip` (109 KB)
- **Modules**: 26 Python files
- **Architecture**: Clean Architecture + SOLID
- **Platform**: Windows, Mac, Linux

---

## 📦 Package Location

```
E:\AddOns\Mixanimo_Lite\Mixanimo_Lite\Mixanimo_Lite_v1.1.0.zip
```

**Ready to install in Blender 3.5+!**

---

## 🙏 Thank You!

Your feature request has been implemented following Clean Architecture principles, maintaining the same high-quality code organization.

**Need help?** See `PRESET_GUIDE.md` for complete documentation.

**Questions?** Email: afzal.gates@gmail.com

---

**Enjoy your new Animation Preset System!** 🎬✨
