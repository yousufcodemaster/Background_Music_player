import sys
import os
import pygame
import time
import ctypes
import random
import pystray
from PIL import Image
from threading import Thread

# Hide console window
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Get the directory where the executable or script is located
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Define the sounds folder path relative to the executable/script
sounds_folder = os.path.join(base_dir, "sounds")

# Get all .mp3 files from the sounds folder and sort them
music_files = []
for i in range(1, 30):  # 29 songs max
    file_path = f"{i}.mp3"
    if os.path.exists(os.path.join(sounds_folder, file_path)):
        music_files.append(file_path)

if not music_files:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("No Music Files", f"No music files found in the sounds folder.\nChecked path: {sounds_folder}\nPlease add files named 1.mp3, 2.mp3, ...")
    sys.exit(1)

# Global variables
current_track_index = 0
is_playing = True
icon = None

pygame.mixer.init()

def play_random():
    global current_track_index
    current_track_index = random.randint(0, len(music_files) - 1)
    pygame.mixer.music.load(os.path.join(sounds_folder, music_files[current_track_index]))
    pygame.mixer.music.play()

def play_next():
    global current_track_index
    current_track_index = (current_track_index + 1) % len(music_files)
    pygame.mixer.music.load(os.path.join(sounds_folder, music_files[current_track_index]))
    pygame.mixer.music.play()

def play_previous():
    global current_track_index
    current_track_index = (current_track_index - 1) % len(music_files)
    pygame.mixer.music.load(os.path.join(sounds_folder, music_files[current_track_index]))
    pygame.mixer.music.play()

def toggle_play_pause():
    global is_playing
    if is_playing:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()
    is_playing = not is_playing

def get_current_track():
    return music_files[current_track_index]

def create_menu():
    return pystray.Menu(
        pystray.MenuItem("Currently Playing: " + get_current_track(), None, enabled=False),
        pystray.MenuItem("Next", lambda: play_next()),
        pystray.MenuItem("Previous", lambda: play_previous()),
        pystray.MenuItem("Play/Pause", lambda: toggle_play_pause()),
        pystray.MenuItem("Exit", lambda: icon.stop())
    )

def setup_tray():
    global icon
    icon_path = os.path.join(base_dir, "icon.png")
    icon_image = Image.open(icon_path)
    icon = pystray.Icon("Background Music Player", icon_image, "Background Music Player", create_menu())
    icon.run()

# Start playing the first track
pygame.mixer.music.load(os.path.join(sounds_folder, music_files[current_track_index]))
pygame.mixer.music.play()

# Start the tray icon in a separate thread
tray_thread = Thread(target=setup_tray)
tray_thread.daemon = True
tray_thread.start()

# Keep the main thread alive and check for song end
while True:
    if not pygame.mixer.music.get_busy() and is_playing:
        play_random()
    time.sleep(1)
