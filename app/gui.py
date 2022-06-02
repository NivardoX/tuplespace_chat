import tkinter as tk
from tkinter import ttk, TOP, W, YES

import Pyro4

from app.client import Client
from settings import PYRO_URL


class Checkbar(tk.Frame):
    def __init__(self, parent=None, picks=[], side=TOP, anchor=W):
        tk.Frame.__init__(self, parent)

        self.vars = []
        for idx, pick in enumerate(picks):
            var = tk.IntVar()
            chk = tk.Checkbutton(self, text=pick, variable=var)
            chk.pack(side=side, anchor=anchor, expand=YES)
            self.vars.append((var, pick, chk))

    def state(self):
        return map((lambda var: var[0].get()), self.vars)

    @property
    def selected(self):
        for var in self.vars:
            if var[0].get():
                return var[1]
        return None

    def update(self):
        for var in self.vars:
            var[2].pack_forget()
        self.__init__()


class GUI:
    TEXT_WIDTH = 50

    def __init__(self, name):
        self.master = tk.Tk()

        self.client = Client(name=name)
        self.chatrooms = []

        self.input_value = (tk.StringVar(),)
        self.input_message = ("Escreva algo",)
        self.input_label = (None,)
        self.input_button = (None,)
        self.input_input = (None,)

        self.chat_value = tk.StringVar()
        self.chat_message = "Chat"
        self.chat_label = None
        self.chat_button = None
        self.chat_input = None

        self.select_room_value = tk.StringVar()
        self.select_room_message = "Selecione a sala"
        self.select_room_label = None
        self.select_room_button = None
        self.select_room_input = None

        self.participants_value = tk.StringVar()
        self.participants_message = "Participantes"
        self.participants_label = None
        self.participants_button = None
        self.participants_input = None

        self.create_room_value = tk.StringVar()
        self.create_room_message = "Criar Saça"
        self.create_room_label = None
        self.create_room_button = None
        self.create_room_input = None

        self.popup = None

    @property
    def target(self):
        if self.chkbar:
            return self.chkbar.selected
        return None

    def start(self):
        self.create_widgets()
        previous_rooms = self.client.rooms

        while True:
            self.update_all()
            if self.client.rooms != previous_rooms:
                self.update_chatrooms()
                previous_rooms = self.client.rooms

    def send_message(self):
        input_value = self.input_input.get()
        self.client.send_message(
            input_value, target=self.target, room=self.select_room_value.get()
        )

    def update_chat(self, value):
        self.chat_input.delete(1.0, "end")
        self.chat_input.insert("end", value)

    def create_input(self):
        # input
        self.input_input = tk.Entry(self.master, width=self.TEXT_WIDTH)
        self.input_input.grid(row=3, column=0, columnspan=3)
        # button
        self.input_button = tk.Button(
            self.master, text="Enviar", command=self.send_message, bd=3
        )
        self.input_button.grid(row=3, column=3, columnspan=1)

    def create_chat(self):
        # label
        self.chat_label = tk.Label(self.master, text=self.chat_message)
        self.chat_label.config(font=("helvetica", 10))
        self.chat_label.grid(row=0, column=0, columnspan=3)
        # chat
        self.chat_input = tk.Text(self.master, state="normal", width=self.TEXT_WIDTH)
        scrollbar = tk.Scrollbar(self.chat_input)
        scrollbar.place(relheight=1, relx=0.974)

        self.chat_input.grid(row=1, column=0, columnspan=3)

    def create_dropdown(self):
        # label
        self.select_room_label = tk.Label(self.master, text=self.select_room_message)
        self.select_room_label.config(font=("helvetica", 10))
        self.select_room_label.grid(row=6, column=0, columnspan=1)

        # select
        self.select_room_value.set("default")
        self.select_input = tk.OptionMenu(
            self.master, self.select_room_value, "default", *self.chatrooms
        )
        self.select_input.grid(row=6, column=1, columnspan=1)

        self.select_button = tk.Button(
            self.master, text="Criar Sala", command=self.create_room_popup, bd=3
        )
        self.select_button.grid(row=6, column=2, columnspan=1)

    def create_widgets(self):
        self.create_input()
        self.create_chat()
        self.create_participants()
        self.create_dropdown()

    def create_participants(self):
        self.participants = []
        self.chkbar = Checkbar(self.master, self.client.get_participants())

        self.chkbar.grid(row=1, column=3)

    def create_room_popup(self):
        def create_room(self):
            room = self.create_room_input.get()
            self.client.send_message("Criando nova sala", room)
            self.client.update()
            self.popup.destroy()
            self.popup = None

        if self.popup:
            return

        self.popup = tk.Toplevel()
        self.popup.wm_title("Window")

        self.create_room_label = tk.Label(self.popup, text=self.create_room_message)
        self.create_room_label.config(font=("helvetica", 10))
        self.create_room_label.grid(row=0, column=0, columnspan=2)

        self.create_room_input = tk.Entry(self.popup, width=self.TEXT_WIDTH)
        self.create_room_input.grid(row=1, column=0, columnspan=3)

        b = ttk.Button(self.popup, text="Okay", command=create_room)
        b.grid(row=2, column=0)

    def update_chatrooms(self):

        self.chatrooms = list(self.client.rooms)

        menu = self.select_input["menu"]
        variable = self.select_room_value
        menu.delete(0, "end")
        if self.select_room_value.get():
            variable.set(self.select_room_value.get())
        else:
            variable.set("default")

        def set_room(room):
            variable.set(room)
            if self.chkbar:
                self.chkbar.update()
            self.create_participants()

        for string in self.chatrooms:
            menu.add_command(label=string, command=lambda value=string: set_room(value))

    def update_all(self):
        self.master.update()
        self.client.room = self.select_room_value.get()

        self.client.update()

        self.update_chat("\n".join(self.client.messages))
