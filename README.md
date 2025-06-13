# Background Music Player

A lightweight, background music player that runs in the system tray and plays music from a local folder.

## How to Use

1. **Setup:**
   - Ensure you have Python installed (3.6 or higher).
   - Install the required packages:
     ```
     pip install pygame pystray pillow
     ```
   - Place your music files in the `sounds` folder, named as `1.mp3`, `2.mp3`, ..., `29.mp3`.

2. **Running the App:**
   - Run the executable (`main.exe` or `BackgroundMusicPlayer.exe`).
   - The app will start in the background and appear in the system tray.
   - Right-click the tray icon to see the currently playing song and control options (Next, Previous, Play/Pause, Exit).

3. **Setting as Startup App:**
   - Copy the executable (`main.exe` or `BackgroundMusicPlayer.exe`) to your Windows startup folder.
   - **Important:** Also copy the `sounds` folder to the same location as the executable in the startup folder.
   - After copying, you can hide the `sounds` folder to keep your startup folder clean.

## Features

- Plays music in the background with no visible UI.
- Controlled via the system tray icon.
- Automatically plays a random song when the current song ends.
- Shows the currently playing song name in the tray menu.

## Troubleshooting

- If you see an error message saying "No music files found," ensure the `sounds` folder is in the same directory as the executable and contains files named `1.mp3`, `2.mp3`, etc.
- If the app doesn't start, check that the `sounds` folder is correctly placed and not hidden.

## License

This project is open-source and available under the MIT License. 