import tkinter as tk
from tkinter import *
from tkinter import filedialog
import os
from pydub import AudioSegment

class add_music:
    def __init__(self):
        self.music_file_paths = []

        self.master = tk.Tk()
        self.master.title("Add Music Files")
        self.master.geometry("400x400")

        section_label = Label(self.master, text="Add Music to the system")
        add_button = Button(
            master = self.master,
            command = self.add_music_files,
            height = 2,
            width = 10,
            text = "Add Music"
        )
        continue_button = Button(self.master, command=self.exit_program, width=10, height=2, text="Continue")
        self.labels = {}
        self.buttons = {}
        self.names = []
        self.label_position_index = 100

        section_label.place(x=130,y=50)
        add_button.place(x=110, y=350)
        continue_button.place(x=220, y=350)
        self.master.mainloop()

    def exit_program(self):
        self.master.destroy()

    def fetch_music_files(self):
        music_files = {}
        for name in self.names:
            for element in self.music_file_paths:
                if os.path.basename(element) == name:
                    music_files[name] = AudioSegment.from_file(element)
        return music_files

    def get_file_path(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Select File to Open") #filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
        root.destroy()
        return file_path

    def removeButton(self,name):
        if name in self.labels:
            for element in self.music_file_paths:
                if os.path.basename(element) == name:
                    self.music_file_paths.remove(element)
                    break

            self.labels[name].destroy()
            self.buttons[name].destroy()

            del self.labels[name]
            del self.buttons[name]

            self.names.remove(name)

            self.update_gui()

            print("File Deleted: " + name)

    def update_gui(self):
        y_position = 100

        for name in self.names:
            self.labels[name].place(x=110, y=y_position)
            self.buttons[name].place(x=250, y=y_position)

            y_position += 40

        self.label_position_index = y_position

    def add_music_files(self):
        file_path = self.get_file_path()
        self.music_file_paths.append(file_path)
        name = os.path.basename(file_path)
        self.names.append(name)
        self.labels[name] = Label(self.master, text=name, width=20, height=2, bg="dark grey", border=0.2)
        self.labels[name].place(x=110, y=self.label_position_index)
        self.buttons[name] = Button(master= self.master,
                                    command=lambda: self.removeButton(name),
                                    height=2,
                                    width=2,
                                    border=0.2,
                                    text=X)
        self.buttons[name].place(x=250, y=self.label_position_index)
        self.label_position_index += 40

if __name__ == "__main__":
    newClass = add_music()
