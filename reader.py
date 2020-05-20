from tkinter import StringVar, Label, Tk, Button
from tkinter import filedialog
import os
import chardet
import math
import json


class App:
    def __init__(self):
        self.curr_speed = 60
        self.text = []
        self.curr_word = 0
        self.curr_file = None
        self.started = False
        self.offsets = {}
        self._get_offsets()
        self.tk = None
        self.info = None
        self.speed = None
        self.label_inf = None
        self.label_speed = None
        self.start_button = None
        self.quit_button = None

    def _build_window(self):
        """
        This method used to create and build tkinter window of application.
        """
        self.tk = Tk()
        self.tk.title("Читаем быстро")
        self.info = StringVar("")
        self.speed = StringVar("")
        self.speed.set(f"{self.curr_speed} wpm")
        # небольшой хак, чтобы основной текст был по середине окна
        lbl = Label(self.tk, textvariable="", font=("Courier", "28"))
        lbl.pack()
        self.label_inf = Label(self.tk, textvariable=self.info, font=("Courier", "28"))
        self.label_speed = Label(self.tk, textvariable=self.speed, font=("Courier", "16"))
        self.tk.geometry("500x200")
        self.label_inf.pack()
        self.start_button = Button(self.tk, text='Select file', command=self.select_book)
        self.start_button.pack(side="left")
        self.start_button = Button(self.tk, text='Start/Pause', command=self.change_state)
        self.start_button.pack(side="left")
        self.quit_button = Button(self.tk, text='Quit', command=self.quit)
        self.quit_button.pack(side="left")
        self.label_speed.pack(side="right")

        self.tk.bind("<space>", self.change_state)
        self.tk.bind("<Up>", self.speed_up)
        self.tk.bind("<Down>", self.speed_down)
        self.tk.bind("<Left>", self.prev)
        self.tk.bind("<Right>", self.next)
        self.tk.bind("<Escape>", self.quit)

    def run(self):
        """
        Calls method to build window and starts main loop of application.
        """
        self._build_window()
        self.tk.mainloop()

    def _get_offsets(self):
        """
        Gets offsets for used books from service file 'offsets'
        """
        if os.path.exists("offsets"):
            with open("offsets", "r") as read_file:
                self.offsets = json.load(read_file)

    def select_book(self):
        """
        Method to select book for reading or choose other book.
        """
        file_path = filedialog.askopenfilename()
        file_name = os.path.basename(file_path)
        if self.curr_file is not None:
            self.offsets[self.curr_file] = self.curr_word

        # определим кодировку файла, чтобы можно было без проблем открывать файлы в разной кодировке
        rawdata = open(file_path, "rb").read()
        result = chardet.detect(rawdata)
        charenc = result['encoding']

        with open(file_path, "r", encoding=charenc) as f:
            data = f.readlines()
            self.text = []
            for line in data:
                self.text.extend(line.split())
        self.curr_word = self.offsets[file_name] if file_name in self.offsets else 0
        self.curr_file = os.path.basename(file_path)

    def _update(self):
        """
        Method for setting next word of text in reading field.
        """
        self.info.set(self.text[self.curr_word])

    def quit(self, event=None):
        """
        Method for quit action from app. It's saves and dumps new version of offsets.
        """
        self.offsets[self.curr_file] = self.curr_word

        with open("offsets", "w") as f:
            json.dump(self.offsets, f)
        self.tk.destroy()

    def do_tick(self):
        """
        Automatically changes state of the reading field of app.
        """
        if not self.started:
            return
        self.info.set(self.text[self.curr_word])
        self.curr_word += 1
        n = math.log2(1 + len(self.text[self.curr_word]))
        self.label_inf.after(int(60_000 / self.curr_speed + 50 * n), self.do_tick)

    def speed_up(self, event=None):
        """
        Method for speed up bottom.
        """
        self.curr_speed += 10
        self.speed.set(f"{self.curr_speed} wpm")

    def speed_down(self, event=None):
        """
        Method for speed down bottom.
        """
        self.curr_speed -= 10
        self.speed.set(f"{self.curr_speed} wpm")

    def change_state(self, event=None):
        """
        Method for start/pause bottom.
        """
        if not self.started:
            self.started = True
            self.do_tick()
        else:
            self.started = False

    def next(self, event=None):
        """
        Method for next word bottom.
        """
        if self.curr_word < len(self.text) and not self.started:
            self.curr_word += 1
            self._update()

    def prev(self, event=None):
        """
        Method for prev word bottom.
        """
        if self.curr_word and not self.started:
            self.curr_word -= 1
            self._update()


if __name__ == "__main__":
    app = App()
    app.run()
