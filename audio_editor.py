import tkinter as tk
from tkinter import ttk


class AudioEditor:

    def __init__(self, root):
        self.root = root

        self.root.title("Audio Editor")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        self.create_menu()
        self.create_toolbar()
        self.create_main_area()
        self.create_bottom_panel()

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