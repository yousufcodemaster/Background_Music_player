@echo off
echo Building MSI Installer...

:: Check if WiX Toolset is installed
where wix candle.exe >nul 2>&1
if errorlevel 1 (
    echo WiX Toolset is not installed! Please install WiX Toolset first.
    echo Download from: https://wixtoolset.org/releases/
    pause
    exit /b 1
)

:: First build the application
call build.bat

:: Build the MSI
echo Building MSI package...
wix candle.exe product.wxs
wix light.exe -ext WixUIExtension product.wixobj

echo MSI build completed! Check for BackgroundMusicPlayer.msi
pause 