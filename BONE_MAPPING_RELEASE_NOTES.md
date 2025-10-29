# Mixanimo Lite v1.4.0 - Bone Mapping Release

## 🎉 New Feature: Bone Mapping & Animation Transfer

Transfer animations between different armature types with intelligent bone mapping!

### Release Information

- **Version**: 1.4.0
- **Release Date**: October 29, 2025
- **Installer**: `Mixanimo_Lite_v1.4.0_BoneMapping_20251029.zip`
- **Minimum Blender Version**: 3.5.0

---

## 📦 Installation

### Method 1: Install from Zip (Recommended)

1. Download `Mixanimo_Lite_v1.4.0_BoneMapping_20251029.zip`
2. **DO NOT UNZIP** the file
3. Open Blender
4. Go to **Edit → Preferences → Add-ons**
5. Click **Install...** button
6. Select the downloaded zip file
7. Enable the addon by checking the checkbox next to "Mixanimo Lite"
8. **Restart Blender** for full functionality

### Method 2: Manual Installation

1. Unzip `Mixanimo_Lite_v1.4.0_BoneMapping_20251029.zip`
2. Copy the `Mixanimo_Lite` folder to your Blender addons directory:
   - **Windows**: `C:\Users\[YourName]\AppData\Roaming\Blender Foundation\Blender\[Version]\scripts\addons\`
   - **macOS**: `/Users/[YourName]/Library/Application Support/Blender/[Version]/scripts/addons/`
   - **Linux**: `/home/[YourName]/.config/blender/[Version]/scripts/addons/`
3. Open Blender
4. Go to **Edit → Preferences → Add-ons**
5. Search for "Mixanimo Lite"
6. Enable the addon
7. **Restart Blender**

---

## 🆕 What's New in v1.4.0

### Bone Mapping System

**Transfer animations between different armature types!**

- ✅ Create mappings between source and target armatures
- ✅ Intelligent fuzzy bone name matching (auto-mapping)
- ✅ Interactive bone mapping editor with search
- ✅ Save and reuse mapping presets
- ✅ Visual confidence indicators
- ✅ Validation before applying animations
- ✅ Non-destructive workflow

### Key Features

#### 1. Auto-Mapping Algorithm
- **Exact Match**: 100% confidence
- **Case-Insensitive**: 95% confidence
- **Prefix Removal**: Handles "mixamorig:", "DEF-", etc. (90% confidence)
- **Similarity Score**: Levenshtein distance (60-85% confidence)
- **Side Detection**: Handles .L/.R, _L/_R, Left/Right patterns

#### 2. Interactive Mapping Editor
- Source bone list from first armature
- Target bone search dropdown for easy selection
- Color-coded confidence badges:
  - ✓ = Manual mapping (100%)
  - % = Auto-mapped with confidence score
  - ? = Unmapped bone
- Edit any mapping manually
- Real-time validation

#### 3. Preset Management
- Save mappings to reusable preset files
- Load previously created mappings
- Browse all available presets
- Delete outdated presets
- Stored in `~/.mixanimo_bone_mappings/`

#### 4. Animation Transfer
- Apply animations using bone mappings
- Automatic bone name remapping
- Handles missing bones gracefully
- Creates unique actions per armature
- Preserves original animation data

---

## 📖 Quick Start Guide

### Basic Workflow

#### Step 1: Select Armatures
1. Open the **Mixanimo Lite** panel (3D Viewport sidebar)
2. Expand **"Bone Mapping"** section
3. In **Setup** subsection:
   - Select **Source Armature** (with animation)
   - Select **Target Armature** (to receive animation)
   - Enter **Preset Name** (e.g., "Mixamo_to_AccuRig")

#### Step 2: Create Mapping
1. Click **"Create Bone Mapping"**
2. Source bones populate the list
3. Each shows as: `SourceBone → [empty]`

#### Step 3: Auto-Map
1. Adjust **Auto-Map Threshold** (0.6-1.0)
   - Higher = stricter matching
   - Lower = more permissive
2. Click **"Auto-Map Bones"**
3. Algorithm matches bones automatically
4. Review results in console

#### Step 4: Review & Edit
- Review **Bone Mappings** list
- Click any row to edit target bone
- Use search dropdown to find bones
- Manual edits set confidence to 100%

#### Step 5: Save Preset
1. Expand **"Mapping Presets"**
2. Click **"Save Mapping"**
3. Enter name and description
4. Preset saved for future use

#### Step 6: Apply Animation
1. Expand **"Apply Animation"**
2. (Optional) Click **"Validate Mapping"**
3. Click **"Apply Animation with Mapping"**
4. Select animation file
5. Animation transfers to target armature!

---

## 🎯 Use Cases

### Mixamo → AccuRig
Transfer Mixamo animations to AccuRig characters with different bone naming conventions.

### Mixamo → Rigify
Apply Mixamo animations to Rigify rigs.

### Custom → Custom
Map between any two armature types with different structures.

### Animation Library
Create reusable mappings for character pipelines.

---

## 📁 File Structure

### Preset Storage
Mapping presets are stored in:
- **Windows**: `C:\Users\[YourName]\.mixanimo_bone_mappings\`
- **macOS/Linux**: `~/.mixanimo_bone_mappings/`

### Preset Format (JSON)
```json
{
  "name": "Mixamo_to_AccuRig",
  "source_armature_name": "Mixamo_Rig",
  "target_armature_name": "AccuRig_Character",
  "mappings": [
    {
      "source_bone": "mixamorig:Hips",
      "target_bone": "Root",
      "confidence": 0.9
    }
  ],
  "metadata": {
    "created_date": "2025-10-29T...",
    "mapped_count": 52
  },
  "version": "1.0"
}
```

---

## 🔧 Technical Details

### Architecture
- **Clean Architecture**: Separation of concerns across layers
- **Domain Layer**: Pure Python data structures
- **Services Layer**: File I/O with caching
- **Use Cases Layer**: Business logic
- **Adapters Layer**: Blender UI integration

### Performance
- 2-second caching for preset lists
- Efficient Levenshtein distance algorithm
- Lazy loading of bone lists
- Optimized UI refresh

### Compatibility
- Works with all Blender armature types
- Compatible with existing Mixanimo features
- Non-destructive to original data
- Version-safe preset format

---

## 🐛 Troubleshooting

### Issue: Addon not showing up
**Solution**: Restart Blender after installation

### Issue: Auto-mapping finds no matches
**Solution**: Lower the auto-map threshold (try 0.5-0.6)

### Issue: Some bones not mapping
**Solution**: Manually edit mappings using the bone search

### Issue: Animation not applying
**Solution**:
1. Run **"Validate Mapping"** first
2. Check console for warnings
3. Ensure target armature is selected

### Issue: Preset not saving
**Solution**: Check file permissions for `~/.mixanimo_bone_mappings/`

---

## 📊 What's Included

### New Files (v1.4.0)
- `core/domain/bone_mapping_entities.py` - Data structures
- `core/services/bone_mapping_service.py` - File operations
- `core/use_cases/create_bone_mapping.py` - Mapping creation
- `core/use_cases/auto_map_bones.py` - Fuzzy matching
- `core/use_cases/apply_animation_with_mapping.py` - Animation transfer
- `adapters/blender/bone_mapping_operators.py` - UI operators

### Modified Files
- `adapters/blender/properties.py` - Added bone mapping properties
- `adapters/blender/panels.py` - Added Bone Mapping section
- `adapters/blender/__init__.py` - Registered new operators

### Total Package
- 51 Python files
- 148 KB compressed
- Clean Architecture compliant

---

## 🎓 Tips & Best Practices

### Auto-Mapping
1. Start with threshold at 0.7
2. Review matches before saving
3. Manually adjust low-confidence mappings
4. Higher threshold = fewer but more accurate matches

### Preset Organization
- Use descriptive names: `SourceType_to_TargetType`
- Add descriptions for complex mappings
- Keep presets for different character types
- Test presets before production use

### Workflow Efficiency
1. Create mapping once
2. Save as preset
3. Reuse for all characters with same rig types
4. Update preset if you find better mappings

### Quality Checks
- Always validate before applying to production
- Check unmapped bones in console
- Test with simple animation first
- Review animation on target armature

---

## 🔮 Future Enhancements

Potential features for future versions:
- Hierarchical bone matching
- Template mappings for common rig types
- Batch animation transfer
- Mapping visualization
- Constraint transfer
- Weight paint transfer

---

## 📝 Changelog

### v1.4.0 (2025-10-29)
**New Features:**
- ✅ Bone mapping system for animation transfer
- ✅ Intelligent auto-mapping with fuzzy matching
- ✅ Interactive bone mapping editor
- ✅ Mapping preset save/load system
- ✅ Animation application with bone remapping
- ✅ Validation and confidence scoring

**Architecture:**
- Clean separation across 4 layers
- JSON-based preset storage
- 2-second caching for performance
- Comprehensive error handling

**UI Enhancements:**
- New "Bone Mapping" section in main panel
- Custom UIList for bone mappings
- 12 new operators
- Collapsible subsections
- Visual confidence indicators

---

## 📞 Support

- **Issues**: Report bugs and request features
- **Documentation**: See included INSTALLATION.md and guides
- **Examples**: Check preset JSON examples
- **Community**: Share your mapping presets!

---

## ⚖️ License

Same license as Mixanimo Lite base package.

---

## 🙏 Credits

Developed as an enhancement to Mixanimo Lite's animation management system.

**Key Technologies:**
- Blender Python API
- Levenshtein Distance Algorithm
- JSON Serialization
- Clean Architecture Pattern

---

**Enjoy transferring animations between different armature types! 🎬✨**
