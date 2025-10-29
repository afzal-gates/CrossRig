# Bone Mapping Examples

This directory contains example bone mapping presets for common armature combinations.

## Included Presets

### Mixamo_to_AccuRig.json
**Use Case**: Transfer Mixamo animations to AccuRig humanoid rigs

**Coverage**: 65/65 bones (100%)

**How to Use**:
1. Copy this file to `~/.mixanimo_bone_mappings/`
2. Or load directly from Blender:
   - **Bone Mapping** → **Mapping Presets** → **Browse Mappings**
   - Navigate to `[addon_path]/examples/`
   - Select `Mixamo_to_AccuRig.json`
3. Click **Apply Animation with Mapping**

**When to Use**:
- Standard Mixamo characters from mixamo.com
- AccuRig humanoid rigs (standard template)
- Full body animations with fingers
- Any Mixamo animation → AccuRig workflow

**Expected Results**:
- ✅ 100% bone coverage
- ✅ No manual editing needed
- ✅ Perfect animation transfer
- ✅ All fingers, toes, and facial bones mapped

## Installing Presets

### Method 1: Automatic (Recommended)
Presets in the `examples/` folder are automatically available:
- **Bone Mapping** → **Mapping Presets** → **Browse Mappings**
- Look in the addon installation directory

### Method 2: Manual Copy
Copy preset files to your home directory:

**Windows**:
```
Copy to: C:\Users\[YourName]\.mixanimo_bone_mappings\
```

**macOS/Linux**:
```bash
cp Mixamo_to_AccuRig.json ~/.mixanimo_bone_mappings/
```

### Method 3: Load Directly
Use the **Browse Mappings** button to load from any location.

## Creating Your Own Presets

1. **Map Once**:
   - Create bone mapping in Blender
   - Use auto-mapping for initial setup
   - Manually adjust as needed

2. **Save Preset**:
   - Click **Save Mapping**
   - Give it a descriptive name
   - Add description of source/target rigs

3. **Reuse Forever**:
   - Load preset for similar rig pairs
   - Transfer entire animation libraries
   - Share with team members

## Preset File Format

All presets are JSON files with this structure:

```json
{
  "name": "Source_to_Target",
  "source_armature_name": "Source_Rig_Type",
  "target_armature_name": "Target_Rig_Type",
  "description": "What this preset is for",
  "mappings": [
    {
      "source_bone": "bone_name_1",
      "target_bone": "mapped_bone_1",
      "confidence": 1.0
    }
  ],
  "metadata": {
    "created_date": "2025-10-29T...",
    "mapped_count": 65
  },
  "version": "1.0"
}
```

## Common Rig Pairs

### Planned Examples
- `Mixamo_to_Rigify.json` - Mixamo to Blender Rigify
- `Mixamo_to_UE5_Manny.json` - Mixamo to Unreal Engine 5 Manny/Quinn
- `AccuRig_to_Rigify.json` - AccuRig to Rigify
- `UE4_to_UE5.json` - Unreal Engine 4 to 5

*Community contributions welcome!*

## Tips

### For Best Results
- Use standard rig templates when possible
- Avoid custom bone names before mapping
- Test with simple animation first
- Save presets for reuse

### Troubleshooting
- If preset doesn't work: Check bone names match exactly
- If some bones unmapped: Edit manually using search
- If wrong mappings: Adjust confidence in preset file

### Sharing Presets
- Share your presets with the community
- Include description of source/target rigs
- Note any special requirements or limitations
- Test with multiple animations before sharing

## Support

For more information:
- See `MIXAMO_ACCURIG_MAPPING_GUIDE.md` for detailed guide
- See `BONE_MAPPING_QUICKSTART.md` for quick start
- Check main documentation for troubleshooting

---

**Happy mapping! 🎬**
