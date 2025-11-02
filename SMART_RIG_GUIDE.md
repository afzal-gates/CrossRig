# Smart Rig Feature Guide

## Overview

The **Smart Rig** feature in CrossRig provides Auto-Rig Pro-like functionality for automatic armature generation from user-selected landmarks on a full-body mesh. This powerful tool allows you to:

- Pick landmarks directly on your character mesh
- Automatically generate a complete skeleton with proper bone hierarchy
- Get automatic bone naming following industry standards
- Apply automatic skinning with weight painting
- Mirror landmarks for symmetric characters

## Features

### 🎯 Core Capabilities

1. **Visual Landmark Selection**
   - Click vertices directly on your mesh to set landmarks
   - Visual markers (colored spheres) show where landmarks are placed
   - Different colors for left (red), right (blue), and center (green) landmarks

2. **Automatic Bone Generation**
   - Creates complete skeleton from minimal landmark input
   - Intelligent bone hierarchy (parent-child relationships)
   - Proper bone orientation and alignment

3. **Smart Naming**
   - Industry-standard bone names (e.g., `upper_arm.L`, `thigh.R`)
   - Compatible with common rigging conventions
   - Follows Blender's left/right suffix standards

4. **Symmetry Support**
   - Auto-mirror function for bilateral landmarks
   - Intelligent detection of opposite side landmarks
   - One-click mirroring across X-axis

5. **Automatic Skinning**
   - Optional automatic parenting with weights
   - Uses Blender's automatic weight algorithm
   - Saves manual weight painting time

## Workflow

### Step-by-Step Guide

#### 1. Prepare Your Mesh
- Import or create your character mesh
- Ensure the mesh is in a T-pose or A-pose for best results
- Select the mesh object

#### 2. Start Smart Rig Mode
1. Open the **CrossRig** panel in the 3D Viewport sidebar (N key)
2. Expand **Armature Manage** section
3. Expand **Smart Rig (Auto-Generate)** subsection
4. Click **Start Smart Rig Mode**

#### 3. Pick Landmarks
The UI will show buttons for each landmark type. For each landmark:

1. Enter **Edit Mode** (Tab key)
2. Select a vertex at the desired location
3. Return to **Object Mode** (Tab key)
4. Click the corresponding landmark button in the UI

**Landmark Types:**

**Head/Neck:**
- Head Top
- Neck

**Spine (Center):**
- Spine Top (upper chest)
- Spine Mid (mid chest)
- Hips (pelvis)

**Arms (Left & Right):**
- Shoulder
- Elbow
- Wrist
- Hand

**Legs (Left & Right):**
- Hip
- Knee
- Ankle
- Foot
- Toe

#### 4. Use Symmetry (Optional)
If you've marked landmarks on one side:
- Click **Auto-Mirror Landmarks** to automatically create the opposite side
- The system mirrors across the X-axis (standard Blender convention)

#### 5. Generate the Rig
1. Click **Generate Rig**
2. In the dialog:
   - Review landmark count (minimum 3 required)
   - Enable/disable **Auto Skin** option
3. Click **OK**

The system will:
- Create the armature object
- Generate bones with proper hierarchy
- Apply automatic skinning (if enabled)
- Clean up visual markers

#### 6. Adjust if Needed
After generation, you can:
- Enter Edit Mode on the armature to adjust bone positions
- Modify weight painting in Weight Paint mode
- Add additional bones or constraints as needed

## Tips & Best Practices

### 🎯 Landmark Placement

**Essential Landmarks (Minimum):**
- At least 3 landmarks required for generation
- Recommended minimum: Hips, Neck, one arm or leg landmark

**For Best Results:**
- Place landmarks at joint centers (not surface vertices)
- Use anatomically correct positions
- Include symmetric landmarks for balanced rigs

### ⚡ Workflow Efficiency

1. **Work in Orthographic Views:**
   - Use Front (Numpad 1), Side (Numpad 3), Top (Numpad 7) views
   - Easier to select precise vertex positions

2. **Start with Spine:**
   - Mark central landmarks first (spine, neck, head)
   - Then add bilateral landmarks (arms, legs)

3. **Use Mirror Function:**
   - Mark one side completely
   - Use Auto-Mirror for the other side
   - Saves time and ensures symmetry

4. **Check Landmark Count:**
   - UI shows current landmark count
   - Ensure minimum 3 before generating

### 🔧 Advanced Usage

**Custom Bone Names:**
- Edit `smart_rig_service.py` → `BONE_NAMING` dictionary
- Modify to match your studio's naming conventions

**Bone Roll Adjustment:**
- After generation, enter Edit Mode
- Select bones and press Ctrl+N → Recalculate Roll
- Or manually adjust individual bone rolls

**Weight Painting Refinement:**
- Auto-skinning provides base weights
- Refine in Weight Paint mode for better deformation
- Use weight painting tools for detailed adjustments

## Keyboard Shortcuts

- **Tab**: Toggle Edit/Object mode
- **N**: Toggle sidebar panel
- **Numpad 1/3/7**: Front/Side/Top orthographic views
- **Z**: Shading mode menu (Wireframe useful for landmark picking)

## Troubleshooting

### "Need at least 3 landmarks to generate rig"
- Add more landmarks before generating
- Check that landmarks were successfully picked (visible markers)

### "No vertex selected"
- Make sure you're in Edit Mode when selecting vertices
- Select only ONE vertex before clicking landmark button
- Return to Object Mode after selection

### Generated rig has incorrect bone positions
- Review landmark placement accuracy
- Use orthographic views for better precision
- Regenerate after adjusting landmark positions

### Auto-skinning doesn't work properly
- Ensure mesh is close to armature position
- Check that mesh has no modifiers interfering
- Try manual parenting: Select mesh → Shift+select armature → Ctrl+P → Automatic Weights

### Symmetry doesn't mirror correctly
- Ensure mesh is centered on origin (X=0)
- Check that landmarks are placed on correct sides
- Manually place opposite landmark if auto-mirror fails

## Technical Details

### Bone Hierarchy
```
root
├── spine_02
│   ├── spine_03
│   │   ├── neck
│   │   │   └── head
│   │   ├── shoulder.L
│   │   │   └── upper_arm.L
│   │   │       └── forearm.L
│   │   │           └── hand.L
│   │   └── shoulder.R
│   │       └── upper_arm.R
│   │           └── forearm.R
│   │               └── hand.R
├── thigh.L
│   └── shin.L
│       └── foot.L
│           └── toe.L
└── thigh.R
    └── shin.R
        └── foot.R
            └── toe.R
```

### File Locations
- **Operators**: `adapters/blender/smart_rig_operators.py`
- **Service Logic**: `core/services/smart_rig_service.py`
- **Properties**: `adapters/blender/properties.py` → `SmartRigLandmark`
- **UI Panel**: `adapters/blender/panels.py` → Smart Rig subsection

## Future Enhancements

Planned features for future versions:
- IK/FK bone generation
- Custom bone shapes
- Preset landmark templates (human, creature, quadruped)
- Landmark adjustment mode (edit before generation)
- Export/import landmark configurations
- Advanced roll calculation algorithms
- Finger bone generation from hand landmarks

## Comparison with Auto-Rig Pro

### Similar Features:
✅ Visual landmark selection on mesh
✅ Automatic bone generation from points
✅ Automatic bone naming
✅ Automatic skinning
✅ Symmetry support

### CrossRig Advantages:
✅ Open source and customizable
✅ Integrated with CrossRig animation workflow
✅ No additional purchase required

### Auto-Rig Pro Advantages:
- More advanced IK/FK systems
- Facial rigging support
- More preset templates
- Advanced control rig generation

## License & Credits

This feature is part of CrossRig and follows the same license.

**Inspired by:** Auto-Rig Pro's Smart function
**Developer:** CrossRig Team
**Version:** 1.0.0

## Support

For issues or questions:
- GitHub: [Your Repository]
- Documentation: [Your Docs]
- Community: [Your Forum/Discord]

---

**Happy Rigging! 🦴✨**
