from tkinter import Tk

from audio_editor import AudioEditor


if __name__ == "__main__":
    root = Tk()
    app = AudioEditor(root)
    root.mainloop()