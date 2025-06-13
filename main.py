import sys
import os
import pygame
import time
import ctypes
import random
import pystray
from PIL import Image
from threading import Thread
from typing import List, Optional
import subprocess
import traceback

# Hide console window
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Get the directory where the executable or script is located
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Define the sounds folder path relative to the executable/script
sounds_folder = os.path.join(base_dir, "sounds")

# Ensure sounds folder exists (create if not)
os.makedirs(sounds_folder, exist_ok=True)

SUPPORTED_FORMATS = ('.mp3', '.wav', '.ogg', '.flac')
VOLUME_STEP = 0.1

class MusicPlayer:
    def __init__(self):
        self.music_files: List[str] = []
        self.current_track_index: int = 0
        self.is_playing: bool = True
        self.icon: Optional[pystray.Icon] = None
        self.repeat_mode: bool = False  # False = Random, True = Repeat Current
        self.volume: float = 0.5  # 50% default
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)
        self.load_music_files()
        self.start_playback()

    def load_music_files(self) -> None:
        """Load all supported files from the sounds folder."""
        try:
            self.music_files = [
                f for f in os.listdir(sounds_folder)
                if f.lower().endswith(SUPPORTED_FORMATS)
            ]
            self.music_files.sort()
            if not self.music_files:
                self.show_empty_folder_prompt()
        except Exception as e:
            self.show_error("Error", f"Failed to load music files: {str(e)}")
            sys.exit(1)

    def show_error(self, title: str, message: str) -> None:
        """Show error message using tkinter."""
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()

    def show_empty_folder_prompt(self) -> None:
        """Show custom prompt if folder is empty."""
        import tkinter as tk
        from tkinter import messagebox

        def open_folder():
            subprocess.Popen(f'explorer "{sounds_folder}"')

        root = tk.Tk()
        root.withdraw()
        result = messagebox.askquestion(
            "No Music",
            "Please add your music files to the sounds folder.\n\nDo you want to open the folder now?",
            icon='warning'
        )
        if result == 'yes':
            open_folder()
        sys.exit(0)

    def play_random(self) -> None:
        if len(self.music_files) == 1:
            self.current_track_index = 0
        else:
            idx = self.current_track_index
            while True:
                new_idx = random.randint(0, len(self.music_files) - 1)
                if new_idx != idx:
                    break
            self.current_track_index = new_idx
        self.play_current_track()

    def play_next(self) -> None:
        """Play the next track."""
        self.current_track_index = (self.current_track_index + 1) % len(self.music_files)
        self.play_current_track()

    def play_previous(self) -> None:
        """Play the previous track."""
        self.current_track_index = (self.current_track_index - 1) % len(self.music_files)
        self.play_current_track()

    def play_current_track(self) -> None:
        """Play the current track."""
        try:
            pygame.mixer.music.load(os.path.join(sounds_folder, self.music_files[self.current_track_index]))
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.update_menu()
            self.update_tooltip()
        except Exception as e:
            self.show_error("Playback Error", f"Failed to play track: {str(e)}")

    def toggle_play_pause(self) -> None:
        """Toggle between play and pause."""
        if self.is_playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.is_playing = not self.is_playing
        self.update_menu()

    def open_sounds_folder(self) -> None:
        """Open the sounds folder in Explorer."""
        subprocess.Popen(f'explorer "{sounds_folder}"')

    def get_current_track(self) -> str:
        """Get the name of the current track."""
        return self.music_files[self.current_track_index]

    def volume_up(self) -> None:
        self.volume = min(1.0, self.volume + VOLUME_STEP)
        pygame.mixer.music.set_volume(self.volume)
        self.update_menu()
        self.update_tooltip()

    def volume_down(self) -> None:
        self.volume = max(0.0, self.volume - VOLUME_STEP)
        pygame.mixer.music.set_volume(self.volume)
        self.update_menu()
        self.update_tooltip()

    def toggle_repeat_mode(self) -> None:
        self.repeat_mode = not self.repeat_mode
        self.update_menu()
        self.update_tooltip()

    def get_playtime(self) -> str:
        try:
            pos = pygame.mixer.music.get_pos() // 1000
            mins, secs = divmod(pos, 60)
            return f"{mins:02}:{secs:02}"
        except Exception:
            return "00:00"

    def create_menu(self) -> pystray.Menu:
        """Create the system tray menu."""
        repeat_label = "Repeat: ON" if self.repeat_mode else "Repeat: OFF (Random)"
        return pystray.Menu(
            pystray.MenuItem(f"Currently Playing: {self.get_current_track()}", None, enabled=False),
            pystray.MenuItem(f"Playtime: {self.get_playtime()}", None, enabled=False),
            pystray.MenuItem("Next", lambda: self.play_next()),
            pystray.MenuItem("Previous", lambda: self.play_previous()),
            pystray.MenuItem("Play/Pause", lambda: self.toggle_play_pause()),
            pystray.MenuItem("Volume Up", lambda: self.volume_up()),
            pystray.MenuItem("Volume Down", lambda: self.volume_down()),
            pystray.MenuItem(repeat_label, lambda: self.toggle_repeat_mode()),
            pystray.MenuItem("Add Music", lambda: self.open_sounds_folder()),
            pystray.MenuItem("Exit", lambda: self.icon.stop() if self.icon else None)
        )

    def update_menu(self) -> None:
        """Update the system tray menu."""
        if self.icon:
            self.icon.menu = self.create_menu()

    def update_tooltip(self) -> None:
        if self.icon:
            track = self.get_current_track()
            playtime = self.get_playtime()
            self.icon.title = f"Playing: {track} ({playtime})"

    def setup_tray(self) -> None:
        """Setup the system tray icon."""
        try:
            icon_path = os.path.join(base_dir, "icon.png")
            icon_image = Image.open(icon_path)
            self.icon = pystray.Icon(
                "Background Music Player",
                icon_image,
                "Background Music Player",
                self.create_menu()
            )
            self.update_tooltip()
            self.icon.run()
        except Exception as e:
            self.show_error("Tray Error", f"Failed to setup system tray: {str(e)}")
            sys.exit(1)

    def start_playback(self) -> None:
        """Start playing music and setup system tray."""
        try:
            self.play_current_track()

            tray_thread = Thread(target=self.setup_tray)
            tray_thread.daemon = True
            tray_thread.start()

            while True:
                if not pygame.mixer.music.get_busy() and self.is_playing:
                    if self.repeat_mode:
                        self.play_current_track()
                    else:
                        self.play_random()
                time.sleep(0.2)  # Lower CPU usage
        except Exception as e:
            # Silent crash recovery: auto-restart
            traceback.print_exc()
            time.sleep(1)
            os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    MusicPlayer()
