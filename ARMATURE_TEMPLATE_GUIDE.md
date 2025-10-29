# Armature Template System - User Guide

## Overview

The **Armature Template System** allows you to **save entire armature bone structures** as templates and **recreate them from scratch** in any scene. This is different from animation presets - it saves the skeleton itself.

Perfect for:
- ✅ Creating character skeletons from saved templates
- ✅ Sharing armature rigs with team members
- ✅ Building armature libraries for different character types
- ✅ Quickly setting up new characters with consistent bone structures
- ✅ Parenting armatures to imported meshes

---

## What Gets Saved

When you save an armature template, it captures:

✅ **Bone Hierarchy**: Parent-child relationships
✅ **Bone Positions**: Head, tail, and roll (edit mode data)
✅ **Bone Properties**: Deform, inherit rotation, scale, local location
✅ **Bone Layers**: Which layers bones are visible on
✅ **Armature Display**: Display type, show names, axes, X-ray
✅ **Custom Properties**: Any custom bone properties

❌ **Does NOT save**: Animation data, mesh skinning, constraints, modifiers

---

## How to Use

### 1. Save Armature Structure as Template

**Workflow:**
```
1. Select an armature in your scene
2. Click "Save Armature Structure" button
3. Enter template name and description
4. Click OK
```

**Result:** Template saved to `~/.mixanimo_armature_templates/YourTemplate.json`

**Example:**
```
Armature: Mixamo Y-Bot skeleton
Template Name: "Humanoid_Mixamo_Rig"
Description: "Standard Mixamo humanoid rig with 65 bones"
```

---

### 2. Recreate Armature from Template

#### **Method A: Quick Load**
```
1. Click "Quick Load" button
2. Select template from dropdown
3. Click OK
```

**Result:** Armature created at 3D cursor location

#### **Method B: Browse Files**
```
1. Click "Browse" button
2. Navigate to template file
3. Select .json file
4. Click "Load Armature Template"
```

---

### 3. Load Armature and Parent to Mesh

**Use Case:** You have a mesh character without skeleton

**Workflow:**
```
1. Select your mesh object
2. Click "Load to Mesh" button
3. Select armature template
4. Click OK
```

**Result:**
- Armature created at mesh location
- Automatically parented to mesh with automatic weights
- Ready for animation!

**Example:**
```
Mesh: Character_Body.fbx (imported, no skeleton)
Template: "Humanoid_Mixamo_Rig"
→ Armature recreated and parented
→ Weights automatically calculated
→ Ready to animate!
```

---

### 4. Delete Template

```
1. Click "Delete" button (in Armature Templates section)
2. Select template to delete
3. Confirm deletion (WARNING: Cannot be undone!)
4. Click OK
```

---

### 5. Open Template Folder

Click **"Open Template Folder"** to:
- View all saved templates
- Manually organize template files
- Share templates (copy .json files)
- Backup templates

**Location**: `~/.mixanimo_armature_templates/`

---

## Template File Format

Templates are saved as human-readable JSON:

```json
{
  "name": "Humanoid_Mixamo_Rig",
  "description": "Standard Mixamo humanoid skeleton",
  "display_type": "OCTAHEDRAL",
  "show_names": false,
  "show_axes": false,
  "show_in_front": false,
  "bones": [
    {
      "name": "mixamorig:Hips",
      "parent_name": null,
      "head": [0.0, 0.0, 0.95],
      "tail": [0.0, 0.0, 1.05],
      "roll": 0.0,
      "use_connect": false,
      "use_inherit_rotation": true,
      "inherit_scale": "FULL",
      "use_deform": true,
      "layers": [true, false, false, ...],
      "custom_properties": {}
    },
    {
      "name": "mixamorig:Spine",
      "parent_name": "mixamorig:Hips",
      "head": [0.0, 0.0, 1.05],
      "tail": [0.0, 0.0, 1.15],
      ...
    }
  ],
  "version": "1.0"
}
```

---

## Real-World Use Cases

### Use Case 1: Character Library

**Scenario:** Build a library of standard character skeletons

```
Save Templates:
- "Humanoid_Male.json"      (65 bones, adult proportions)
- "Humanoid_Female.json"    (65 bones, female proportions)
- "Humanoid_Child.json"     (65 bones, child proportions)
- "Creature_Quadruped.json" (Custom 4-legged rig)

When Creating New Character:
1. Import mesh only (no skeleton)
2. Select mesh
3. Load appropriate template → "Load to Mesh"
4. Armature created and weighted
5. Ready for animation!
```

---

### Use Case 2: Team Collaboration

**Scenario:** Share consistent rigs across team

```
Rigger Creates Template:
1. Build perfect Mixamo-compatible rig
2. Save as "Studio_Standard_Rig.json"
3. Share file via cloud/Git

Animator Receives Template:
1. Place file in ~/.mixanimo_armature_templates/
2. Import character mesh
3. Load "Studio_Standard_Rig" → parent to mesh
4. Consistent rig across all characters!
```

---

### Use Case 3: Rapid Prototyping

**Scenario:** Quickly test different skeleton designs

```
Create Variations:
- "Rig_Option_A.json" (standard bone count)
- "Rig_Option_B.json" (extra spine bones)
- "Rig_Option_C.json" (simplified limbs)

Testing:
1. Load Option A → test animation
2. Load Option B → test animation
3. Load Option C → test animation
4. Choose best design
```

---

### Use Case 4: Mesh + Skeleton Workflow

**Scenario:** Import meshes from modeling software without rigs

```
Traditional Workflow:
1. Import mesh
2. Manually create armature
3. Position each bone by hand
4. Set up hierarchy
5. Parent and weight
→ 30-60 minutes per character

With Templates:
1. Import mesh
2. Select mesh → "Load to Mesh"
3. Select template
→ 10 seconds, perfect rig every time!
```

---

## Tips & Best Practices

### Naming Conventions

✅ **Good Names:**
- "Humanoid_Mixamo_65Bones"
- "Quadruped_Dog_Rig"
- "Spider_8Legs_Rig"

❌ **Avoid:**
- "test"
- "armature1"
- "rig"

### Add Descriptions

```
Good: "Standard Mixamo humanoid rig with 65 bones, compatible with all Mixamo animations"
Bad: ""  (empty)
```

### Organize Templates

Create folders inside `~/.mixanimo_armature_templates/`:

```
~/.mixanimo_armature_templates/
├── Humanoid/
│   ├── Standard_Male.json
│   ├── Standard_Female.json
│   └── Child.json
├── Creatures/
│   ├── Quadruped_Dog.json
│   ├── Quadruped_Cat.json
│   └── Spider.json
└── Custom/
    ├── Stylized_Character.json
    └── Cartoon_Character.json
```

### Version Control

Templates are perfect for Git:
```bash
git add armature_templates/*.json
git commit -m "Add standard character rigs"
git push
```

---

## Troubleshooting

### Armature Not Created

**Problem:** Template loads but no armature appears

**Solutions:**
1. Check 3D cursor location (armature created there)
2. Check if armature exists but is hidden
3. Verify template file is valid JSON

---

### Bones Look Wrong

**Problem:** Bones in incorrect positions

**Solution:** Template stores bone positions as they were in edit mode. Ensure original armature was positioned correctly before saving.

---

### Parent to Mesh Fails

**Problem:** "Load to Mesh" creates armature but parenting fails

**Solutions:**
1. Ensure selected object is actually a MESH type
2. Check mesh has geometry (not empty)
3. Verify mesh doesn't already have parent

---

### Template Won't Load

**Problem:** Error when loading template

**Check:**
1. File is valid JSON (open in text editor)
2. Bone hierarchy is valid (no circular references)
3. No duplicate bone names
4. Parent bones exist for all children

---

## Advanced: Manual Template Editing

You can manually edit template `.json` files:

### Example 1: Scale All Bone Positions

```python
# Python script to scale all bone positions by 2x
import json

with open('template.json', 'r') as f:
    data = json.load(f)

for bone in data['bones']:
    bone['head'] = [x * 2 for x in bone['head']]
    bone['tail'] = [x * 2 for x in bone['tail']]

with open('template_scaled.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### Example 2: Rename Bone Prefix

```json
// Before
"name": "mixamorig:Hips"

// After (search & replace)
"name": "custom:Hips"
```

---

## Storage Location

**Windows**: `C:\Users\YourName\.mixanimo_armature_templates\`
**Mac**: `/Users/YourName/.mixanimo_armature_templates/`
**Linux**: `/home/yourname/.mixanimo_armature_templates/`

---

## Comparison: Animation Presets vs Armature Templates

| Feature | Animation Presets | Armature Templates |
|---------|------------------|-------------------|
| **Saves** | Action sequence settings | Bone structure |
| **Purpose** | Reuse animation workflows | Recreate skeletons |
| **Requires Existing** | Armature + Actions | Nothing (creates from scratch) |
| **Use Case** | Apply animation sequence | Create character rig |
| **Output** | NLA timeline setup | New armature object |
| **Storage** | `~/.mixanimo_presets/` | `~/.mixanimo_armature_templates/` |

**Both systems work together!**
```
Workflow:
1. Load Armature Template → Create skeleton
2. Import Mixamo animations
3. Load Animation Preset → Apply sequence
4. Export FBX
```

---

## Version Compatibility

- **Template Version**: 1.0
- **Blender**: 3.5.0 or higher
- **Platform**: Windows, Mac, Linux
- **Forward Compatible**: Templates designed for future versions

---

## FAQ

**Q: Can I edit the template file manually?**
A: Yes! They're JSON text files. Use any text editor.

**Q: Do templates include animations?**
A: No, only bone structure. Use Animation Presets for animations.

**Q: Can I share templates with others?**
A: Yes! Just copy the `.json` file. Works across all platforms.

**Q: How many templates can I have?**
A: Unlimited! Only limited by disk space.

**Q: Can I use templates from older Blender versions?**
A: Yes, templates are Blender-version independent.

**Q: Will this work with custom rigs?**
A: Yes! Any armature can be saved as template.

**Q: Can I organize templates in folders?**
A: Yes! Create subfolders in `~/.mixanimo_armature_templates/`

---

## Technical Details

### File Format
- **Format**: JSON (JavaScript Object Notation)
- **Encoding**: UTF-8
- **Extension**: `.json`
- **Version**: 1.0 (forward compatible)

### Data Stored Per Bone
- Name (string)
- Parent name (string or null)
- Head position (x, y, z)
- Tail position (x, y, z)
- Roll (float, radians)
- Properties (booleans)
- Layers (32-element boolean array)
- Custom properties (dictionary)

---

**Need Help?** Email: afzal.gates@gmail.com

**Version**: 1.2.0
**Feature Added**: October 28, 2025
