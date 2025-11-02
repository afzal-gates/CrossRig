@echo off
REM ================================================================
REM CrossRig - Addon Packaging Script
REM Creates a Blender-installable zip file
REM ================================================================

echo.
echo ========================================
echo  CrossRig - Addon Packager
echo ========================================
echo.

REM Set variables
set ADDON_NAME=CrossRig
set VERSION=1.2.0
set RELEASE_DIR=release
set TEMP_DIR=%ADDON_NAME%_temp

REM Generate timestamp using PowerShell (YYYYMMDD_HHMMSS format)
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"`) do set TIMESTAMP=%%i

REM Create output filename with version and timestamp
set OUTPUT_ZIP=%RELEASE_DIR%\%ADDON_NAME%_v%VERSION%_%TIMESTAMP%.zip

REM Create release directory if it doesn't exist
if not exist "%RELEASE_DIR%" (
    echo Creating release directory...
    mkdir "%RELEASE_DIR%"
)

REM Clean up previous builds
if exist "%OUTPUT_ZIP%" (
    echo Removing previous zip file...
    del "%OUTPUT_ZIP%"
)

if exist "%TEMP_DIR%" (
    echo Removing previous temp directory...
    rmdir /s /q "%TEMP_DIR%"
)

echo.
echo Creating temporary addon directory...
mkdir "%TEMP_DIR%"
mkdir "%TEMP_DIR%\%ADDON_NAME%"

echo.
echo Copying addon files...

REM Copy main entry point
copy "__init__.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy __init__.py
    goto :error
)
echo   [OK] __init__.py

REM Copy directory structure (config, core, adapters)
if exist "config" (
    xcopy /E /I /Q "config" "%TEMP_DIR%\%ADDON_NAME%\config\" >nul
    echo   [OK] config/
)

if exist "core" (
    xcopy /E /I /Q "core" "%TEMP_DIR%\%ADDON_NAME%\core\" >nul
    echo   [OK] core/
)

if exist "adapters" (
    xcopy /E /I /Q "adapters" "%TEMP_DIR%\%ADDON_NAME%\adapters\" >nul
    echo   [OK] adapters/
)

REM Copy optional documentation files
if exist "README.md" (
    copy "README.md" "%TEMP_DIR%\%ADDON_NAME%\" >nul
    echo   [OK] README.md
)

if exist "LICENSE" (
    copy "LICENSE" "%TEMP_DIR%\%ADDON_NAME%\" >nul
    echo   [OK] LICENSE
)

if exist "logo_mixanimo.png" (
    copy "logo_mixanimo.png" "%TEMP_DIR%\%ADDON_NAME%\" >nul
    echo   [OK] logo_mixanimo.png
)

echo.
echo Creating zip archive...

REM Use PowerShell to create zip (Windows 7+)
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { Compress-Archive -Path '%TEMP_DIR%\%ADDON_NAME%' -DestinationPath '%OUTPUT_ZIP%' -Force }"

if %errorlevel% neq 0 (
    echo ERROR: Failed to create zip file
    goto :error
)

echo.
echo Cleaning up temporary files...
rmdir /s /q "%TEMP_DIR%"

echo.
echo ========================================
echo  SUCCESS!
echo ========================================
echo.
echo Addon packaged successfully:
echo   File: %OUTPUT_ZIP%
echo   Location: %CD%\%RELEASE_DIR%
echo.
echo Installation Instructions:
echo   1. Open Blender
echo   2. Go to Edit ^> Preferences ^> Add-ons
echo   3. Click "Install..."
echo   4. Select %OUTPUT_ZIP%
echo   5. Enable "CrossRig"
echo.
echo ========================================
echo.

pause
exit /b 0

:error
echo.
echo ========================================
echo  PACKAGING FAILED
echo ========================================
echo.
if exist "%TEMP_DIR%" (
    rmdir /s /q "%TEMP_DIR%"
)
pause
exit /b 1
