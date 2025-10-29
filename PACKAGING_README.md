# Addon Packaging Guide

This directory contains scripts to package Mixanimo Lite into a Blender-installable zip file.

## Available Scripts

### Windows Batch File (Recommended for Windows)
**File**: `create_addon_zip.bat`

**Usage**:
1. Double-click `create_addon_zip.bat`
2. Wait for the packaging to complete
3. Find `Mixanimo_Lite_v1.0.0.zip` in the current directory

### PowerShell Script (Alternative)
**File**: `create_addon_zip.ps1`

**Usage**:
1. Right-click `create_addon_zip.ps1`
2. Select "Run with PowerShell"
   - Or open PowerShell and run: `.\create_addon_zip.ps1`
3. Find `Mixanimo_Lite_v1.0.0.zip` in the current directory

**Note**: If you get an execution policy error, run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## What Gets Packaged

The scripts will include the following files in the zip:
- ✅ `__init__.py` (required - main addon file)
- ✅ `README.md` (optional - documentation)
- ✅ `LICENSE` (optional - license file)
- ✅ `logo_mixanimo.png` (optional - addon logo)

Files **excluded** from packaging:
- ❌ `.DS_Store` (macOS metadata)
- ❌ `create_addon_zip.bat` (packaging script)
- ❌ `create_addon_zip.ps1` (packaging script)
- ❌ `PACKAGING_README.md` (this file)

## Output Structure

The generated zip file will have this structure:
```
Mixanimo_Lite_v1.0.0.zip
└── Mixanimo_Lite/
    ├── __init__.py
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
5. Navigate to and select `Mixanimo_Lite_v1.0.0.zip`
6. Click **Install Add-on**
7. Search for "Mixanimo Lite" in the addon list
8. Enable the addon by checking the checkbox
9. The addon will appear in **3D Viewport > Sidebar (N) > Mixanimo Lite** tab

## Troubleshooting

### Script won't run
- **Windows**: Make sure you have execution permissions
- **PowerShell**: Check execution policy (see PowerShell Script section above)

### Zip file already exists error
- Delete the existing `Mixanimo_Lite_v1.0.0.zip` file and run again
- Or the script will automatically remove it

### Missing files in zip
- Verify that `__init__.py` exists in the same directory
- Check that you're running the script from the correct directory

## Changing Version Number

To change the version number in the output filename:

**Batch file** (`create_addon_zip.bat`):
```batch
set VERSION=1.0.0  # Change this line
```

**PowerShell script** (`create_addon_zip.ps1`):
```powershell
$Version = "1.0.0"  # Change this line
```

## Manual Packaging (Without Scripts)

If you prefer to package manually:

1. Create a folder named `Mixanimo_Lite`
2. Copy `__init__.py`, `README.md`, `LICENSE`, and `logo_mixanimo.png` into it
3. Zip the folder (right-click > Send to > Compressed folder)
4. Rename the zip to `Mixanimo_Lite_v1.0.0.zip`

## Support

For issues with the addon itself, contact: mixanimoaddon@gmail.com
