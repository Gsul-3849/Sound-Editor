import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pygame


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
            os.environ.get("LOCALAPPDATA", ""),
        ]

        for folder in common_locations:
            if not folder or not os.path.isdir(folder):
                continue

            for current, _, files in os.walk(folder):
                if ffmpeg_path is None and "ffmpeg.exe" in files:
                    ffmpeg_path = os.path.join(current, "ffmpeg.exe")

                if ffprobe_path is None and "ffprobe.exe" in files:
                    ffprobe_path = os.path.join(current, "ffprobe.exe")

                if ffmpeg_path and ffprobe_path:
                    break

            if ffmpeg_path and ffprobe_path:
                break

    path_entries = os.environ.get("PATH", "").split(os.pathsep)

    if ffmpeg_path:
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        if ffmpeg_dir and ffmpeg_dir not in path_entries:
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

    if ffprobe_path:
        ffprobe_dir = os.path.dirname(ffprobe_path)
        if ffprobe_dir and ffprobe_dir not in path_entries:
            os.environ["PATH"] = ffprobe_dir + os.pathsep + os.environ.get("PATH", "")

    return ffmpeg_path, ffprobe_path


ffmpeg_path, ffprobe_path = configure_ffmpeg_paths()

from pydub import AudioSegment

from create_wave import draw_wave


if ffmpeg_path:
    AudioSegment.converter = ffmpeg_path
if ffprobe_path:
    AudioSegment.ffprobe = ffprobe_path

class AudioEditor:

    def __init__(self, root):
        self.root = root
        self.audio_files = {}
        self.file_paths = {}
        self.current_audio = None
        self.currently_playing = None
        self.is_paused = False
        self.audio_ready = False
        self.progress_cursor_id = None
        self.progress_job = None
        self.start_marker_id = None
        self.end_marker_id = None
        self.selection_start_ms = 0
        self.selection_end_ms = 0
        self.cursor_ms = 0
        self.drag_mode = None

        try:
            pygame.mixer.init()
            self.audio_ready = True
        except Exception as exc:
            messagebox.showerror(
                "Audio Error",
                f"Could not initialize audio playback.\n\n{exc}"
            )

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
        self.wave.bind("<ButtonPress-1>", self._on_wave_press)
        self.wave.bind("<B1-Motion>", self._on_wave_drag)
        self.wave.bind("<ButtonRelease-1>", self._on_wave_release)

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
            self._draw_selection_markers()
            self._draw_progress_cursor()

    def _ms_to_canvas_x(self, milliseconds):
        if self.current_audio is None:
            return 0

        duration_ms = max(1, len(self.current_audio))
        width = max(1, self.wave.winfo_width())
        return min(max(0, int((milliseconds / duration_ms) * width)), width - 1)

    def _canvas_x_to_ms(self, x):
        if self.current_audio is None:
            return 0

        duration_ms = max(1, len(self.current_audio))
        width = max(1, self.wave.winfo_width())
        ratio = min(max(0, x / width), 1)
        return int(ratio * duration_ms)

    def _format_time(self, milliseconds):
        total_seconds = max(0, int(milliseconds / 1000))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _draw_selection_markers(self):
        if self.current_audio is None or self.wave.winfo_width() <= 1:
            return

        self.wave.delete("selection_markers")

        start_x = self._ms_to_canvas_x(self.selection_start_ms)
        end_x = self._ms_to_canvas_x(self.selection_end_ms)

        self.start_marker_id = self.wave.create_line(
            start_x,
            0,
            start_x,
            self.wave.winfo_height(),
            fill="green",
            width=3,
            tags="selection_markers",
        )
        self.end_marker_id = self.wave.create_line(
            end_x,
            0,
            end_x,
            self.wave.winfo_height(),
            fill="orange",
            width=3,
            tags="selection_markers",
        )

        self.start_label.config(text=self._format_time(self.selection_start_ms))
        self.end_label.config(text=self._format_time(self.selection_end_ms))

    def _draw_progress_cursor(self, elapsed_ms=None):
        if self.current_audio is None or self.wave.winfo_width() <= 1:
            return

        if elapsed_ms is None:
            elapsed_ms = self.cursor_ms

        if self.currently_playing is not None and self.current_audio is not None:
            if pygame.mixer.get_busy() and not self.is_paused:
                elapsed_ms = pygame.mixer.music.get_pos()

        self.cursor_ms = min(max(0, elapsed_ms), len(self.current_audio))

        if self.progress_cursor_id is not None:
            self.wave.delete(self.progress_cursor_id)

        x = self._ms_to_canvas_x(self.cursor_ms)

        self.progress_cursor_id = self.wave.create_line(
            x,
            0,
            x,
            self.wave.winfo_height(),
            fill="red",
            width=2,
            tags="progress_cursor",
        )

    def _on_wave_press(self, event):
        if self.current_audio is None:
            return

        start_x = self._ms_to_canvas_x(self.selection_start_ms)
        end_x = self._ms_to_canvas_x(self.selection_end_ms)

        if abs(event.x - start_x) <= 6:
            self.drag_mode = "start"
            return

        if abs(event.x - end_x) <= 6:
            self.drag_mode = "end"
            return

        self.drag_mode = "cursor"
        self._set_cursor_from_event(event.x)

    def _on_wave_drag(self, event):
        if self.current_audio is None or self.drag_mode is None:
            return

        if self.drag_mode == "cursor":
            self._set_cursor_from_event(event.x)
            if pygame.mixer.get_busy() and not self.is_paused:
                pygame.mixer.music.set_pos(self.cursor_ms / 1000)
            return

        if self.drag_mode == "start":
            new_start = min(self._canvas_x_to_ms(event.x), self.selection_end_ms)
            self.selection_start_ms = max(0, new_start)
        elif self.drag_mode == "end":
            new_end = max(self._canvas_x_to_ms(event.x), self.selection_start_ms)
            self.selection_end_ms = min(new_end, len(self.current_audio))

        self._draw_selection_markers()

    def _on_wave_release(self, event):
        self.drag_mode = None

    def _set_cursor_from_event(self, x):
        if self.current_audio is None:
            return

        self.cursor_ms = self._canvas_x_to_ms(x)
        self._draw_progress_cursor(self.cursor_ms)

    def _set_selection_from_current_audio(self):
        if self.current_audio is None:
            self.selection_start_ms = 0
            self.selection_end_ms = 0
            self.cursor_ms = 0
            return

        duration_ms = len(self.current_audio)
        self.selection_start_ms = 0
        self.selection_end_ms = duration_ms
        self.cursor_ms = 0
        self._draw_selection_markers()
        self._draw_progress_cursor(0)

    def _update_progress_cursor(self):
        if self.currently_playing is None or self.is_paused:
            return

        if self.current_audio is None:
            self._stop_progress_updates()
            return

        elapsed_ms = pygame.mixer.music.get_pos()
        self._draw_progress_cursor(elapsed_ms)
        self.progress_job = self.root.after(50, self._update_progress_cursor)

    def _stop_progress_updates(self):
        if self.progress_job is not None:
            self.root.after_cancel(self.progress_job)
            self.progress_job = None

        if self.progress_cursor_id is not None:
            self.wave.delete(self.progress_cursor_id)
            self.progress_cursor_id = None

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
            self.file_paths[name] = file_path
            self.file_list.insert(tk.END, name)
            self.current_audio = audio
            self._set_selection_from_current_audio()

            self.root.update_idletasks()
            self._update_time_labels(audio.duration_seconds)
            draw_wave(self, audio)
            self._draw_selection_markers()
            self._draw_progress_cursor(0)

    def play_audio(self):
        if self.file_list.size() == 0 or not self.audio_ready:
            return

        selected_index = self.file_list.curselection()
        if not selected_index:
            return

        selected_name = self.file_list.get(selected_index[0])
        file_path = self.file_paths.get(selected_name)

        if not file_path:
            return

        self.current_audio = self.audio_files[selected_name]
        self._set_selection_from_current_audio()
        self.cursor_ms = max(self.selection_start_ms, self.cursor_ms)

        if self.is_paused and self.currently_playing == selected_name:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.time_label.config(text=f"Playing: {selected_name}")
            self._start_progress_updates()
            return

        pygame.mixer.music.stop()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(start=self.cursor_ms / 1000)
        self.currently_playing = selected_name
        self.current_audio = self.audio_files[selected_name]
        self.is_paused = False
        self.time_label.config(text=f"Playing: {selected_name}")
        self._draw_progress_cursor(self.cursor_ms)
        self._start_progress_updates()

    def pause_audio(self):
        if not self.audio_ready:
            return

        if self.currently_playing is None:
            return

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.time_label.config(text=f"Playing: {self.currently_playing}")
            self._start_progress_updates()
            return

        pygame.mixer.music.pause()
        self.is_paused = True
        self._stop_progress_updates()
        self.time_label.config(text=f"Paused: {self.currently_playing}")

    def stop_audio(self):
        if not self.audio_ready:
            return

        pygame.mixer.music.stop()
        self.currently_playing = None
        self.is_paused = False
        self._stop_progress_updates()
        self._draw_progress_cursor(0)
        self.time_label.config(text="Stopped")

    def split_audio(self):
        self.time_label.config(text="Split tool placeholder")

    def change_volume(self):
        self.time_label.config(text="Volume tool placeholder")

    def _start_progress_updates(self):
        self._stop_progress_updates()
        self.progress_job = self.root.after(50, self._update_progress_cursor)

    def _update_time_labels(self, total_seconds):
        total_minutes = int(total_seconds // 60)
        total_seconds_display = int(total_seconds % 60)

        self.time_label.config(
            text=f"{total_minutes:02d}:{total_seconds_display:02d} / {total_minutes:02d}:{total_seconds_display:02d}"
        )
        self.start_label.config(text=self._format_time(self.selection_start_ms))
        self.end_label.config(text=self._format_time(self.selection_end_ms))