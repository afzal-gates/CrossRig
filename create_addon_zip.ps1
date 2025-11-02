# ================================================================
# CrossRig - Addon Packaging Script (PowerShell)
# Creates a Blender-installable zip file
# ================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CrossRig - Addon Packager" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set variables
$AddonName = "CrossRig"
$Version = "1.2.0"
$ReleaseDir = "release"
$TempDir = "${AddonName}_temp"

# Generate timestamp (YYYYMMDD_HHMMSS format)
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Create output filename with version and timestamp
$OutputZip = "${ReleaseDir}\${AddonName}_v${Version}_${Timestamp}.zip"

# Create release directory if it doesn't exist
if (-not (Test-Path $ReleaseDir)) {
    Write-Host "Creating release directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
}

# Clean up previous builds
if (Test-Path $OutputZip) {
    Write-Host "Removing previous zip file..." -ForegroundColor Yellow
    Remove-Item $OutputZip -Force
}

if (Test-Path $TempDir) {
    Write-Host "Removing previous temp directory..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $TempDir
}

Write-Host ""
Write-Host "Creating temporary addon directory..." -ForegroundColor Green
New-Item -ItemType Directory -Path "$TempDir\$AddonName" -Force | Out-Null

Write-Host ""
Write-Host "Copying addon files..." -ForegroundColor Green

# Copy essential addon files
try {
    Copy-Item "__init__.py" "$TempDir\$AddonName\" -ErrorAction Stop
    Write-Host "  [OK] __init__.py" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Failed to copy __init__.py" -ForegroundColor Red
    exit 1
}

# Copy directory structure (config, core, adapters)
if (Test-Path "config") {
    Copy-Item -Recurse "config" "$TempDir\$AddonName\"
    Write-Host "  [OK] config/" -ForegroundColor Green
}

if (Test-Path "core") {
    Copy-Item -Recurse "core" "$TempDir\$AddonName\"
    Write-Host "  [OK] core/" -ForegroundColor Green
}

if (Test-Path "adapters") {
    Copy-Item -Recurse "adapters" "$TempDir\$AddonName\"
    Write-Host "  [OK] adapters/" -ForegroundColor Green
}

# Copy optional documentation files
if (Test-Path "README.md") {
    Copy-Item "README.md" "$TempDir\$AddonName\"
    Write-Host "  [OK] README.md" -ForegroundColor Green
}

if (Test-Path "LICENSE") {
    Copy-Item "LICENSE" "$TempDir\$AddonName\"
    Write-Host "  [OK] LICENSE" -ForegroundColor Green
}

if (Test-Path "logo_mixanimo.png") {
    Copy-Item "logo_mixanimo.png" "$TempDir\$AddonName\"
    Write-Host "  [OK] logo_mixanimo.png" -ForegroundColor Green
}

Write-Host ""
Write-Host "Creating zip archive..." -ForegroundColor Green

try {
    Compress-Archive -Path "$TempDir\$AddonName" -DestinationPath $OutputZip -Force -ErrorAction Stop
} catch {
    Write-Host "ERROR: Failed to create zip file" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
    exit 1
}

Write-Host ""
Write-Host "Cleaning up temporary files..." -ForegroundColor Green
Remove-Item -Recurse -Force $TempDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " SUCCESS!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Addon packaged successfully:" -ForegroundColor White
Write-Host "  File: $OutputZip" -ForegroundColor Cyan
Write-Host "  Location: $PWD\$ReleaseDir" -ForegroundColor Cyan

# Get file info
$FileInfo = Get-Item $OutputZip
Write-Host "  Size: $([math]::Round($FileInfo.Length / 1KB, 2)) KB" -ForegroundColor Cyan
Write-Host "  Created: $($FileInfo.LastWriteTime)" -ForegroundColor Cyan

Write-Host ""
Write-Host "Installation Instructions:" -ForegroundColor Yellow
Write-Host "  1. Open Blender" -ForegroundColor White
Write-Host "  2. Go to Edit > Preferences > Add-ons" -ForegroundColor White
Write-Host "  3. Click 'Install...'" -ForegroundColor White
Write-Host "  4. Select $OutputZip" -ForegroundColor White
Write-Host "  5. Enable 'CrossRig'" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Pause equivalent
Read-Host "Press Enter to exit"
