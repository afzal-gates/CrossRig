# Addon Packaging Guide

This directory contains scripts to package CrossRig into a Blender-installable zip file.

## Available Scripts

### Windows Batch File (Recommended for Windows)
**File**: `create_addon_zip.bat`

**Usage**:
1. Double-click `create_addon_zip.bat`
2. Wait for the packaging to complete
3. Find `CrossRig_v1.0.1.zip` in the `release` folder

### PowerShell Script (Alternative)
**File**: `create_addon_zip.ps1`

**Usage**:
1. Right-click `create_addon_zip.ps1`
2. Select "Run with PowerShell"
   - Or open PowerShell and run: `.\create_addon_zip.ps1`
3. Find `CrossRig_v1.0.1.zip` in the `release` folder

**Note**: If you get an execution policy error, run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## What Gets Packaged

The scripts will include the following files in the zip:
- ✅ `__init__.py` (required - main addon entry point)
- ✅ `config/` (addon configuration files)
- ✅ `core/` (core business logic and utilities)
- ✅ `adapters/` (Blender integration layer)
- ✅ `README.md` (documentation)
- ✅ `LICENSE` (license file)
- ✅ `logo_mixanimo.png` (addon logo)

Files **excluded** from packaging:
- ❌ `__pycache__/` (Python cache files)
- ❌ `*.pyc` (compiled Python files)
- ❌ Packaging scripts and documentation
- ❌ Git-related files
- ❌ Development documentation

## Output Structure

The generated zip file will have this structure:
```
release/
└── CrossRig_v1.0.1.zip
    └── CrossRig/
        ├── __init__.py
        ├── config/
        ├── core/
        ├── adapters/
        ├── README.md
        ├── LICENSE
        └── logo_mixanimo.png
```

This structure is compatible with Blender's addon installation system.

## Installing the Addon in Blender

1. Open Blender
2. Go to **Edit > Preferences**
3. Select **Add-ons** tab
4. Click **Install...** button
5. Navigate to `release/` folder and select `CrossRig_v1.0.1.zip`
6. Click **Install Add-on**
7. Search for "CrossRig" in the addon list
8. Enable the addon by checking the checkbox
9. The addon will appear in **3D Viewport > Sidebar (N) > CrossRig** tab

## Troubleshooting

### Script won't run
- **Windows**: Make sure you have execution permissions
- **PowerShell**: Check execution policy (see PowerShell Script section above)

### Zip file already exists error
- The script automatically removes existing zip files in the `release/` folder before creating new ones

### Missing files in zip
- Verify that `__init__.py` exists in the same directory
- Check that you're running the script from the correct directory

## Changing Version Number

To change the version number in the output filename, update both:

1. **Batch file** (`create_addon_zip.bat`):
   ```batch
   set VERSION=1.0.1  # Change this line
   ```

2. **PowerShell script** (`create_addon_zip.ps1`):
   ```powershell
   $Version = "1.0.1"  # Change this line
   ```

3. **Main addon file** (`__init__.py`):
   ```python
   bl_info = {
       "version": (1, 0, 0),  # Change this line
       ...
   }
   ```

Keep all three in sync for consistency.

## Manual Packaging (Without Scripts)

If you prefer to package manually:

1. Create a folder named `CrossRig`
2. Copy the following into it:
   - `__init__.py`
   - `config/` (entire directory)
   - `core/` (entire directory)
   - `adapters/` (entire directory)
   - `README.md`
   - `LICENSE`
   - `logo_mixanimo.png`
3. Zip the folder (right-click > Send to > Compressed folder)
4. Rename the zip to `CrossRig_v1.0.1.zip`
5. Move it to the `release/` folder

## Release Folder

The `release/` folder is automatically created by the packaging scripts and contains:
- ✅ Versioned addon zip files ready for distribution
- ✅ `.gitkeep` file to track the folder in Git
- ❌ Zip files are excluded from Git tracking (see `.gitignore`)

This keeps your releases organized and separate from development files.
