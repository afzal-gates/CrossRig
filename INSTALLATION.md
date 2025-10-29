# Mixanimo Lite - Installation Guide

## Quick Installation

### Step 1: Install the Addon
1. Open **Blender** (version 3.5 or higher)
2. Go to **Edit → Preferences**
3. Click on the **Add-ons** tab
4. Click **Install...** button at the top
5. Navigate to and select `Mixanimo_Lite_v1.0.0.zip`
6. Click **Install Add-on**

### Step 2: Enable the Addon
1. In the Add-ons list, search for "**Mixanimo Lite**"
2. Check the checkbox next to the addon name to enable it
3. The addon is now active!

### Step 3: Access the Addon
1. Open the **3D Viewport** in Blender
2. Press **N** to open the sidebar (if not already visible)
3. Click on the **Mixanimo Lite** tab
4. You'll see the addon panel with all features

---

## What's Included in the ZIP

The installation package contains the complete **Clean Architecture** implementation:

### File Structure in ZIP
```
Mixanimo_Lite_v1.0.0.zip (87 KB)
└── Mixanimo_Lite/
    ├── __init__.py                      # Main entry point
    ├── README.md                        # User documentation
    ├── LICENSE                          # MIT License
    ├── logo_mixanimo.png               # Addon logo
    ├── config/                          # Configuration
    │   ├── __init__.py
    │   └── constants.py                 # All settings & defaults
    ├── core/                            # Business logic
    │   ├── __init__.py
    │   ├── domain/                      # Pure Python layer
    │   │   ├── __init__.py
    │   │   ├── entities.py              # Data structures
    │   │   └── math_utils.py            # Math functions
    │   ├── services/                    # Action services
    │   │   ├── __init__.py
    │   │   └── action_service.py        # FCurve operations
    │   └── use_cases/                   # Feature logic
    │       ├── __init__.py
    │       ├── send_to_timeline.py      # NLA sequencing
    │       ├── bake_animation.py        # Animation baking
    │       ├── stabilize_root.py        # Root stabilization
    │       └── export_fbx.py            # FBX export
    └── adapters/                        # Blender integration
        ├── __init__.py
        ├── blender/
        │   ├── __init__.py
        │   ├── properties.py            # PropertyGroups
        │   ├── operators.py             # Operators (11 classes)
        │   ├── panels.py                # UI panels
        │   └── handlers.py              # Event handlers
        └── interfaces/
            └── __init__.py              # Interface definitions
```

**Total**: 21 Python modules + 3 documentation files

---

## Features Available After Installation

### 🎬 Load & Organize Animations
- **Load Actions**: Import all Mixamo animations from your scene
- **Reorder**: Use up/down arrows to change sequence order
- **Repeat Count**: Set how many times each animation repeats (1-100)
- **Angle Rotation**: Rotate character trajectory (-360° to 360°)
- **Enable/Disable**: Toggle which animations to include

### 🎭 Nonlinear Animation (NLA)
- **Send to Timeline**: Create NLA strips with automatic blending
- **Overlap Blending**: Smooth transitions between animations
- **Multi-track Support**: Each action gets its own track

### 🔧 Advanced Tools
- **Bake Action**: Merge all NLA strips into a single action
- **Stabilize Root**: Remove horizontal movement for in-place animations
- **Root Bone Configuration**: Customize root bone name (default: "mixamorig:Hips")

### 📤 Export Options
- **Full Export**: Export armature + mesh + animation as FBX (for Unity/Unreal)
- **Armature Only**: Export skeleton + animation without mesh (for retargeting)
- **Game-Ready Settings**: Automatic Unity/Unreal axis configuration

---

## System Requirements

### Blender Version
- **Minimum**: Blender 3.5.0
- **Recommended**: Blender 3.6 or higher

### Operating Systems
- ✅ Windows 7/8/10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+)

### Hardware
- Any system that runs Blender 3.5+

---

## Typical Workflow

### Basic Animation Sequencing
1. **Import Animations**: Import Mixamo FBX files into Blender
2. **Load Actions**: Click "Load Actions" in Mixanimo Lite panel
3. **Organize**: Reorder animations, set repeat counts, adjust angles
4. **Confirm Order**: Click "Confirm Order"
5. **Set Overlap**: Adjust "Overlap Frames" for blending (default: 3)
6. **Send to Timeline**: Click "Send" to create NLA strips
7. **Preview**: Play timeline to see blended sequence

### Export for Game Engines
1. **Bake Animation**: Click "Bake Action" to merge NLA strips
2. **Stabilize (Optional)**: Click "Stabilize Root" for in-place animations
3. **Export**:
   - Click "Full (Mesh + Armature)" for complete character export
   - OR "Armature Only" for retargeting to different characters
4. **Use in Engine**: Import FBX into Unity/Unreal Engine

---

## Troubleshooting

### Addon Not Showing in List
- **Solution**: Search for "Mixanimo" in the Add-ons search box
- **Check**: Make sure you installed the correct ZIP file

### Panel Not Visible
- **Solution**: Press **N** in 3D Viewport to show sidebar
- **Check**: Click on "Mixanimo Lite" tab in the sidebar

### "No Armature Found" Error
- **Solution**: Select an armature object in your scene
- **Check**: Make sure the armature has animations

### Bake Action Fails
- **Solution**: First use "Send to Timeline" to create NLA strips
- **Check**: Make sure NLA tracks exist before baking

### Stabilize Root Not Working
- **Solution**: First bake your NLA strips into a single action
- **Check**: Verify root bone name matches your armature (usually "mixamorig:Hips")

### Export FBX No Mesh
- **Solution**: Use "Full (Mesh + Armature)" button instead of "Armature Only"
- **Check**: Verify mesh object is parented to armature or has armature modifier

---

## Uninstalling

1. Open **Edit → Preferences → Add-ons**
2. Search for "**Mixanimo Lite**"
3. Click the **Remove** button
4. Restart Blender

---

## Architecture Notes

This addon follows **Clean Architecture** principles:

- **Domain Layer**: Pure business logic (no Blender dependencies)
- **Services Layer**: Action manipulation services
- **Use Cases Layer**: Application business rules
- **Adapters Layer**: Blender integration (UI, Operators, Properties)

**Benefits**:
- Testable components
- Maintainable code structure
- Easy to extend with new features
- Professional software engineering practices

For technical details, see `ARCHITECTURE.md` in the source repository.

---

## Support

### Documentation
- **README.md**: Basic usage guide
- **ARCHITECTURE.md**: Technical architecture (developers)
- **REFACTORING_SUMMARY.md**: Refactoring details (developers)

### Issues & Questions
- Email: **afzal.gates@gmail.com**
- Website: **https://afzalgates.com/**

### License
This addon is released under the **MIT License** - free to use, modify, and distribute.

---

## Version Information

**Current Version**: 1.0.0

**Release Date**: October 2025

**Compatibility**: Blender 3.5+

**Package Size**: 87 KB

**Modules**: 21 Python files

**Architecture**: Clean Architecture with SOLID principles

---

## What's New in Version 1.0.0

### Refactored Architecture
- ✅ Clean Architecture implementation
- ✅ SOLID principles throughout
- ✅ Modular structure (21 focused modules)
- ✅ Testable components
- ✅ Professional code organization

### Features
- ✅ NLA timeline sequencing with blending
- ✅ Animation baking (NLA to single action)
- ✅ Root bone stabilization (in-place animations)
- ✅ FBX export (full and armature-only modes)
- ✅ Angle rotation for character trajectories
- ✅ Repeat count for animations (1-100 times)
- ✅ Customizable overlap blending (0-100 frames)

### Quality
- ✅ Comprehensive documentation
- ✅ Clear error messages
- ✅ Validated user inputs
- ✅ Blender 3.5+ compatibility

---

**Thank you for using Mixanimo Lite!** 🎉
