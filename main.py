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

class MusicPlayer:
    def __init__(self):
        self.music_files: List[str] = []
        self.current_track_index: int = 0
        self.is_playing: bool = True
        self.icon: Optional[pystray.Icon] = None
        pygame.mixer.init()
        self.load_music_files()
        self.start_playback()

    def load_music_files(self) -> None:
        """Load all .mp3 files from the sounds folder."""
        try:
            self.music_files = [
                f for f in os.listdir(sounds_folder)
                if f.lower().endswith(".mp3")
            ]

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
        """Play a random track."""
        self.current_track_index = random.randint(0, len(self.music_files) - 1)
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
            pygame.mixer.music.play()
            self.update_menu()
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

    def create_menu(self) -> pystray.Menu:
        """Create the system tray menu."""
        return pystray.Menu(
            pystray.MenuItem(f"Currently Playing: {self.get_current_track()}", None, enabled=False),
            pystray.MenuItem("Next", lambda: self.play_next()),
            pystray.MenuItem("Previous", lambda: self.play_previous()),
            pystray.MenuItem("Play/Pause", lambda: self.toggle_play_pause()),
            pystray.MenuItem("Add Music", lambda: self.open_sounds_folder()),
            pystray.MenuItem("Exit", lambda: self.icon.stop() if self.icon else None)
        )

    def update_menu(self) -> None:
        """Update the system tray menu."""
        if self.icon:
            self.icon.menu = self.create_menu()

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
                    self.play_random()
                time.sleep(0.5)
        except Exception as e:
            self.show_error("Runtime Error", f"An error occurred: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    player = MusicPlayer()
