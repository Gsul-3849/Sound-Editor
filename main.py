import pydub
from add_music import *
from audio_editor import AudioEditor
from tkinter import ttk
from tkinter import *

global file_paths
music_files = []
#---Collect Tracks---

#obtain file paths from user
def update_file_paths_list():
    paths_instance = add_music()
    new_files = paths_instance.fetch_music_files()
    music_files.extend(new_files)
   #print(file_paths)

root = Tk()
app = AudioEditor(root)
root.mainloop()