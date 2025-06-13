@echo off
echo Building MSI Installer...

:: Build the MSI
echo Building MSI package...
"C:\Program Files (x86)\WiX Toolset v3.11\bin\candle.exe" product.wxs
"C:\Program Files (x86)\WiX Toolset v3.11\bin\light.exe" -ext WixUIExtension product.wixobj

echo MSI build completed! Check for BackgroundMusicPlayer.msi
pause