# CrossRig

**by Afzal Hossain**

Animation sequencing and cross-rig retargeting for Blender. Transfer animations between different armature structures with intelligent bone mapping.

CrossRig is an independently developed Blender addon for animation workflows. Works with Mixamo, AccuRig, Rigify, and custom rigs.

---

## 📜 License

This addon is released under the MIT License.

---

## 🔧 Core Features

### Animation Sequencing
✅ Load, organize, and sequence multiple animations
✅ NLA timeline integration with blend overlaps
✅ Animation presets (save/load sequences)
✅ Multi-armature workflow support
✅ Baking and root bone stabilization

### Cross-Rig Retargeting
✅ **Intelligent bone mapping** with auto-match algorithm
✅ **Transfer animations** between different rig types
✅ **Mapping presets** - create once, reuse forever
✅ **Confidence scoring** - see mapping quality at a glance
✅ **Manual override** - fine-tune auto-mapped bones

### Armature & Animation Management
✅ Save/load armature templates
✅ Save/load animation data
✅ Clean, organized UI in 3D Viewport sidebar

---

## 📦 Installation

1. Download **CrossRig** addon file
2. In Blender: **Edit → Preferences → Add-ons**
3. Click **Install** and select the addon file
4. Enable **CrossRig**
5. Find the addon in **3D View > Sidebar > CrossRig** tab

**Minimum Blender Version:** 3.5+

---

## ▶️ Quick Start

### Animation Sequencing
1. Click **Load Actions** to list available animations
2. Reorder, repeat, or exclude actions as needed
3. Click **Confirm Order**
4. Set overlap frames for blending
5. Click **Send to NLA** to build timeline sequence

### Cross-Rig Retargeting
1. Open **Bone Mapping** section
2. Select **Source Armature** (has animation)
3. Select **Target Armature** (will receive animation)
4. Click **Create Bone Mapping**
5. Click **Auto-Map Bones** (adjust threshold as needed)
6. Review mappings and manually fix any low-confidence matches
7. Click **Apply Animation with Mapping**

📖 **See [BONE_MAPPING_QUICKSTART.md](BONE_MAPPING_QUICKSTART.md) for detailed guide**

---

## 💡 Use Cases

- **Mixamo → AccuRig**: Transfer Mixamo animations to AccuRig characters
- **Mixamo → Rigify**: Use Mixamo animations with Rigify rigs
- **Custom Rig Retargeting**: Map between any two armature structures
- **Animation Libraries**: Build reusable preset libraries for your workflows
- **Multi-Character Scenes**: Transfer one animation across multiple character types

---

## 🎯 What Makes This Different?

Most animation tools require identical bone names. **CrossRig's intelligent bone mapping** lets you transfer animations between completely different rig structures:

- **Smart Matching**: Auto-map bones with fuzzy name matching
- **Visual Confidence**: Color-coded confidence scores show mapping quality
- **Reusable Presets**: Map once, apply to all characters with same rig type
- **Manual Control**: Override any auto-mapping for perfect results

---

## 📁 File Locations

**Mapping Presets:** `~/.crossrig_bone_mappings/`
**Animation Presets:** `~/.crossrig_presets/`
**Saved Animations:** `~/.crossrig_animations/`
**Armature Templates:** `~/.crossrig_armature_templates/`

---## 📧 Support

**Developed by:** Afzal Hossain
**Questions?** Email: afzal.gates@gmail.com
**Website:** https://afzalgates.com/

---

**Enjoy seamless animation transfer across any rig! ✨**