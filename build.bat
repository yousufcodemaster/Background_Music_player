@echo off
echo Building Background Music Player...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python first.
    pause
    exit /b 1
)

:: Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

:: Clean previous build
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Build the application
echo Building application...
pyinstaller --clean --onefile --windowed --icon=icon.png main.py

echo Build completed! Check the dist folder for the executable.
pause 