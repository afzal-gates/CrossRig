# Animation Preset System - User Guide

## Overview

The Animation Preset System allows you to **save** your current animation sequences and **load** them later on different armatures. This is perfect for:

- ✅ Reusing animation sequences across multiple characters
- ✅ Sharing animation setups with team members
- ✅ Creating animation libraries for projects
- ✅ Quick workflow setups for common animation patterns

---

## Features

### Save Presets
- Save complete animation sequences with all settings
- Includes: action order, repeat counts, angles, overlap frames, root bone
- Stored as human-readable JSON files
- Descriptive names and optional descriptions

### Load Presets
- Quick load from dropdown menu
- Browse presets in file browser
- Automatic validation and error handling
- Warns about missing actions

### Manage Presets
- Delete unwanted presets
- Open preset folder for manual management
- Presets stored in user's home directory

---

## How to Use

### 1. Save a Preset

#### Step-by-Step:
1. **Set up your animation sequence**:
   - Load actions
   - Reorder as needed
   - Set repeat counts
   - Set rotation angles
   - Configure overlap frames and root bone

2. **Click "Save Preset"** button

3. **Enter preset details**:
   - **Preset Name**: Descriptive name (e.g., "Combat Combo", "Idle Variations")
   - **Description**: Optional notes about the preset

4. **Click OK** to save

**Result**: Preset is saved to `~/.mixanimo_presets/` directory

---

### 2. Load a Preset

#### Method 1: Quick Load (Dropdown)
1. Click **"Load"** button (next to Save Preset)
2. Select preset from dropdown menu
3. Click OK

**Result**: Preset is applied to action collection immediately

#### Method 2: Browse Files
1. Click **"Browse Presets"** button
2. Navigate to preset file (`.json`)
3. Select file and click "Load Preset"

**Result**: Opens file browser starting at preset directory

---

### 3. Apply Preset to New Armature

#### Workflow:
1. **Import new character** with Mixamo animations
2. **Select the armature** you want to apply preset to
3. **Load the preset** using either method above
4. **Confirm Order** (as usual)
5. **Send to Timeline**

**Important**: The preset only loads actions that exist in your current scene. If actions are missing, you'll see warnings but the preset will still load available actions.

---

### 4. Delete a Preset

1. Click **"Delete"** button
2. Select preset from dropdown
3. **Confirm deletion** (cannot be undone!)
4. Click OK

**Warning**: This permanently deletes the preset file.

---

### 5. Open Preset Folder

Click **"Open Preset Folder"** to:
- View all your saved presets
- Manually organize preset files
- Share presets with others (copy `.json` files)
- Backup your presets

**Location**: `~/.mixanimo_presets/` in your home directory

---

## Preset File Format

Presets are saved as JSON files with this structure:

```json
{
  "name": "Combat Combo",
  "description": "Basic 3-hit combo sequence",
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

---

## Use Cases

### 1. Character Animation Library
**Scenario**: You have standard animation sequences for all your game characters.

**Workflow**:
1. Create preset for "Walk Cycle" (walk → turn → walk back)
2. Create preset for "Idle Variations" (idle → look around → idle)
3. Create preset for "Combat Moves" (attack combos)
4. Load presets on new characters as needed

---

### 2. Team Collaboration
**Scenario**: Share animation setups with team members.

**Workflow**:
1. Create preset with detailed description
2. Share `.json` file (email, version control, shared drive)
3. Team member places file in their `~/.mixanimo_presets/` folder
4. Load preset in their Blender project

---

### 3. Animation Templates
**Scenario**: You have common patterns for different character types.

**Workflow**:
1. Create preset "Humanoid Basic" (standard bipedal moves)
2. Create preset "Creature Quadruped" (four-legged movements)
3. Create preset "Flying Character" (aerial animations)
4. Load appropriate preset based on character type

---

### 4. Quick Prototyping
**Scenario**: Rapidly test different animation sequences.

**Workflow**:
1. Create multiple preset variations (Preset A, B, C)
2. Quickly switch between them using Load menu
3. Test in game/preview
4. Choose best sequence

---

## Tips & Best Practices

### Naming Conventions
✅ **Good names**:
- "Combat_3Hit_Combo"
- "Idle_Breathing_Loop"
- "Locomotion_Walk_Run_Sprint"

❌ **Avoid**:
- "test"
- "preset1"
- "asdf"

### Use Descriptions
Add helpful descriptions:
- "3-hit combo for melee combat, ends with kick"
- "Breathing idle loop, 2 repetitions for smooth blending"
- "Full locomotion set: walk 0°, run 45°, sprint 90°"

### Organize Presets
Create folders inside `~/.mixanimo_presets/`:
```
~/.mixanimo_presets/
├── Combat/
│   ├── Combo_3Hit.json
│   └── Combo_5Hit.json
├── Locomotion/
│   ├── Walk_Cycle.json
│   └── Run_Sprint.json
└── Idle/
    ├── Breathing.json
    └── Looking_Around.json
```

### Backup Important Presets
- Copy preset files to cloud storage
- Include in version control (if text-based)
- Export with project files

---

## Troubleshooting

### "Action not found" Warning

**Problem**: Preset references actions that don't exist in current scene.

**Solution**:
1. Import missing Mixamo FBX files
2. Load actions first (`Load Actions` button)
3. Then load preset again

**Note**: Preset will load available actions and warn about missing ones.

---

### Preset Doesn't Load

**Problem**: Preset file appears corrupted or invalid.

**Solutions**:
1. **Check file format**: Open `.json` file in text editor, verify structure
2. **Re-save preset**: Create preset again from scratch
3. **Validate JSON**: Use online JSON validator

---

### Can't Find Preset Folder

**Problem**: Don't know where presets are stored.

**Solution**: Click **"Open Preset Folder"** button in addon panel.

**Manual paths**:
- **Windows**: `C:\Users\YourName\.mixanimo_presets\`
- **Mac**: `/Users/YourName/.mixanimo_presets/`
- **Linux**: `/home/yourname/.mixanimo_presets/`

---

### Preset Settings Not Applied

**Problem**: Loaded preset but settings didn't change.

**Check**:
- Root bone name matches your armature
- Forward axis is correct for your character
- Overlap frames value is appropriate

**Fix**: Manually adjust settings after loading preset.

---

## Advanced: Manual Preset Editing

You can manually edit preset `.json` files:

### Example: Change All Angles
```json
"actions": [
  {"action_name": "Walk", "angle": 0},    // Change to 90
  {"action_name": "Run", "angle": 0},     // Change to 90
]
```

### Example: Batch Update Repeat Counts
Use find/replace in text editor:
- Find: `"repeat_count": 1`
- Replace: `"repeat_count": 2`

### Example: Add Description
```json
{
  "name": "Combat Combo",
  "description": "Added description here",  // Add this line
  "root_bone": "mixamorig:Hips",
  ...
}
```

---

## Integration with Workflow

### Typical Animation Workflow with Presets:

1. **Setup**:
   - Import character with Mixamo animations
   - Load Actions

2. **Create Sequence**:
   - Reorder actions
   - Set repeat counts and angles
   - Configure settings

3. **Save Preset**:
   - Save as "CharacterName_Sequence"
   - Add description

4. **Use Preset**:
   - Import new character
   - Load preset
   - Confirm Order
   - Send to Timeline

5. **Export**:
   - Bake Action
   - Stabilize Root (if needed)
   - Export FBX

---

## Keyboard Shortcuts

Currently no default shortcuts, but you can add them:

1. Blender → Edit → Preferences → Keymap
2. Search for "Mixamo"
3. Add shortcuts to operators:
   - `mixamo.save_preset`
   - `mixamo.load_preset_menu`

---

## Technical Details

### File Format
- **Format**: JSON (JavaScript Object Notation)
- **Encoding**: UTF-8
- **Extension**: `.json`
- **Version**: 1.0 (forward compatible)

### Storage Location
- **Path**: User home directory `~/.mixanimo_presets/`
- **Platform Independent**: Works on Windows, Mac, Linux
- **Portable**: JSON files can be copied between systems

### Data Stored
- ✅ Action names and order
- ✅ Repeat counts (1-100)
- ✅ Rotation angles (-360° to 360°)
- ✅ Root bone name
- ✅ Overlap frames (0-100)
- ✅ Forward axis setting
- ❌ NOT stored: Actual animation data (only references)

---

## FAQ

**Q: Can I share presets with others?**
A: Yes! Just copy the `.json` file. Both users need the same animation actions in their scenes.

**Q: Do presets include the animation data?**
A: No, presets only store references to action names and settings. You must have the FBX files imported.

**Q: Can I edit presets manually?**
A: Yes, they're JSON text files. Use any text editor.

**Q: Are presets version-compatible?**
A: Yes, v1.0 format is designed for forward compatibility.

**Q: How many presets can I have?**
A: Unlimited! Storage is only limited by disk space.

**Q: Can I organize presets in folders?**
A: Yes, create subfolders inside `~/.mixanimo_presets/`. Use "Browse Presets" to navigate.

---

## Version History

### v1.1.0 - Preset System Added
- Initial preset save/load functionality
- JSON file format
- UI integration
- Validation and error handling

---

**Need Help?** Email: afzal.gates@gmail.com
