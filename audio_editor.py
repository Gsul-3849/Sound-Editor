import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pydub import AudioSegment

from create_wave import draw_wave


def configure_ffmpeg_paths():
    ffmpeg_path = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    ffprobe_path = shutil.which("ffprobe") or shutil.which("ffprobe.exe")

    if ffmpeg_path is None or ffprobe_path is None:
        common_locations = [
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            r"C:\Program Files\FFmpeg\bin",
            r"C:\Program Files (x86)\ffmpeg\bin",
            r"C:\Program Files (x86)\FFmpeg\bin",
            os.path.join(os.environ.get("USERPROFILE", ""), "ffmpeg", "bin"),
            os.path.join(os.environ.get("USERPROFILE", ""), "FFmpeg", "bin"),
        ]

        for folder in common_locations:
            if not folder:
                continue

            candidate_ffmpeg = os.path.join(folder, "ffmpeg.exe")
            candidate_ffprobe = os.path.join(folder, "ffprobe.exe")

            if ffmpeg_path is None and os.path.exists(candidate_ffmpeg):
                ffmpeg_path = candidate_ffmpeg

            if ffprobe_path is None and os.path.exists(candidate_ffprobe):
                ffprobe_path = candidate_ffprobe

    if ffmpeg_path:
        AudioSegment.converter = ffmpeg_path
    if ffprobe_path:
        AudioSegment.ffprobe = ffprobe_path


#configure_ffmpeg_paths()

AudioSegment.converter = "C:\\Users\\danie\\AppData\\Local\\Python\\Python-3.12.13\\Lib\\ffmpeg"

class AudioEditor:

    def __init__(self, root):
        self.root = root
        self.audio_files = {}
        self.current_audio = None

        self.root.title("Audio Editor")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        self.create_menu()
        self.create_toolbar()
        self.create_main_area()
        self.create_bottom_panel()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Add Music", command=self.add_music)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        menu_bar.add_cascade(label="File", menu=file_menu)

    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill="x", padx=5, pady=5)

        ttk.Button(
            toolbar,
            text="▶ Play",
            command=self.play_audio
        ).pack(side="left", padx=2)

        ttk.Button(
            toolbar,
            text="⏸ Pause",
            command=self.pause_audio
        ).pack(side="left", padx=2)

        ttk.Button(
            toolbar,
            text="⏹ Stop",
            command=self.stop_audio
        ).pack(side="left", padx=2)

        ttk.Separator(
            toolbar,
            orient="vertical"
        ).pack(side="left", fill="y", padx=10)

        ttk.Button(
            toolbar,
            text="✂ Split",
            command=self.split_audio
        ).pack(side="left", padx=2)

        ttk.Button(
            toolbar,
            text="🔊 Volume",
            command=self.change_volume
        ).pack(side="left", padx=2)

    def create_main_area(self):

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)

        # Left side
        library = ttk.Frame(main, width=220)
        library.pack(side="left", fill="y", padx=5, pady=5)

        ttk.Label(
            library,
            text="Music Library",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        self.file_list = tk.Listbox(library)
        self.file_list.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        ttk.Button(
            library,
            text="+ Add Music",
            command=self.add_music
        ).pack(fill="x", padx=5, pady=5)

        # Right side
        editor = ttk.Frame(main)
        editor.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.wave = tk.Canvas(
            editor,
            background="white"
        )

        self.wave.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )
        self.wave.bind("<Configure>", self._on_wave_resize)

    def create_bottom_panel(self):

        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=5, pady=5)

        self.time_label = ttk.Label(
            bottom,
            text="00:00 / 00:00"
        )

        self.time_label.pack(side="left")

        ttk.Label(
            bottom,
            text="Start:"
        ).pack(side="left", padx=(30, 2))

        self.start_label = ttk.Label(
            bottom,
            text="00:00"
        )

        self.start_label.pack(side="left")

        ttk.Label(
            bottom,
            text="End:"
        ).pack(side="left", padx=(15, 2))

        self.end_label = ttk.Label(
            bottom,
            text="00:00"
        )

        self.end_label.pack(side="left")

    def _on_wave_resize(self, event=None):
        if self.current_audio is not None:
            draw_wave(self, self.current_audio)

    def add_music(self):
        file_paths = filedialog.askopenfilenames(
            title="Select audio files",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac")]
        )

        if not file_paths:
            return

        for file_path in file_paths:
            name = os.path.basename(file_path)
            if name in self.audio_files:
                continue

            try:
                audio = AudioSegment.from_file(file_path)
            except Exception as exc:
                messagebox.showerror(
                    "Import Failed",
                    f"Could not load '{name}'.\n\n"
                    f"This usually means FFmpeg/FFprobe is missing or not on PATH.\n"
                    f"Details: {exc}"
                )
                continue

            self.audio_files[name] = audio
            self.file_list.insert(tk.END, name)
            self.current_audio = audio

            self.root.update_idletasks()
            self._update_time_labels(audio.duration_seconds)
            draw_wave(self, audio)

    def play_audio(self):
        if self.file_list.size() == 0:
            return

        selected_index = self.file_list.curselection()
        if not selected_index:
            return

        selected_name = self.file_list.get(selected_index[0])
        self.time_label.config(text=f"Playing: {selected_name}")

    def pause_audio(self):
        self.time_label.config(text="Paused")

    def stop_audio(self):
        self.time_label.config(text="Stopped")

    def split_audio(self):
        self.time_label.config(text="Split tool placeholder")

    def change_volume(self):
        self.time_label.config(text="Volume tool placeholder")

    def _update_time_labels(self, total_seconds):
        total_minutes = int(total_seconds // 60)
        total_seconds_display = int(total_seconds % 60)

        self.time_label.config(
            text=f"{total_minutes:02d}:{total_seconds_display:02d} / {total_minutes:02d}:{total_seconds_display:02d}"
        )
        self.start_label.config(text="00:00")
        self.end_label.config(text=f"{total_minutes:02d}:{total_seconds_display:02d}")