from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import random
import os
from click import command
import numpy as np
import string
import subprocess
import shutil
import webbrowser

from tkinter import filedialog as fd
from tkinter import simpledialog

class BattleshipBoard():

    def __init__(self, row_size=11, col_size=11):

        # attribute setting
        self.row_size, self.col_size = row_size, col_size
        self.ship_sizes = [5, 4, 3, 3, 2]

        # reset your own ships
        reset_ships_array = np.zeros((self.row_size, self.col_size))
        if not os.path.isdir('ships'):
            os.mkdir('ships')
        np.savetxt("ships/ships.txt", reset_ships_array, fmt='%s')

        #Create & Configure root 
        self.root = Tk()
        self.root.title("Rando Battleship")

        self.generate_card()

        self.root.geometry("700x700")
        # Creating Menubar
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # Board Mode Menu
        board_mode = Menu(menubar, tearoff = False)
        board_mode.add_command(label='Place Mode (Blind)', command=lambda row_size=row_size, col_size=col_size: self.place_mode(row_size, col_size, blind=True))
        board_mode.add_command(label='Place Mode (Visible)', command=lambda row_size=row_size, col_size=col_size: self.place_mode(row_size, col_size, blind=False))
        menubar.add_cascade(label ='Board Mode', menu=board_mode)

        # Action Mode Menu
        actions = Menu(menubar, tearoff = False)
        actions.add_command(label = 'Generate New Card', command=self.generate_card)
        actions.add_command(label = 'Load Card from Seed', command=self.change_seedname)
        actions.add_command(label = 'Copy Seed Name', command=self.copy_seed)
        actions.add_command(label = 'Upload Ship Layout', command=self.upload)
        actions.add_command(label = 'Download Ship Layout', command=self.download)
        menubar.add_cascade(label = 'Actions', menu=actions)

        self.info = Menu(menubar, tearoff=False)
        self.info.add_command(label = f"Seedname: {self.seedname}", command=self.copy_seed)
        self.info.add_command(label = 'Help', command=self.open_help_window)
        menubar.add_cascade(label = 'Info', menu=self.info)
        self.root.mainloop()


    def set_style(self, name, background, bordercolor, highlightthickness, padding):
        style = ttk.Style(self.frame)
        style.theme_use('alt')
        style.configure(name, background=background, bordercolor=bordercolor, highlightthickness=highlightthickness, padding=padding, relief=SOLID)


    def change_seedname(self):
        self.seedname = simpledialog.askstring(title="Seed", prompt="Seed Name: ", initialvalue=f'{self.seedname}')
        self.generate_card(self.seedname)
        self.info.entryconfig(0, label=f'Seedname: {self.seedname}')


    def place_ship(self, x, y):
        self.place_grid[x,y] = 1 - self.place_grid[x,y]
        print(self.place_grid)
        return self.place_grid


    def download(self):
        try:
            os.makedirs('ships')
        except FileExistsError:
            pass
        np.savetxt("ships/ships.txt", self.place_grid, fmt='%s')
        shutil.make_archive('ships/', 'zip', 'ships')


    def upload(self):

        # unpack zip file
        filename = fd.askopenfilename()
        shutil.unpack_archive(filename, '.', 'zip')
        
        # load opponent ships
        opponent_ships = np.loadtxt('ships.txt')

        # load your ships
        your_ships = np.loadtxt('ships/ships.txt')

        # load new board if there are ships to be hit
        if np.sum(opponent_ships) == 0:
            all_zeros_window = Toplevel(self.root)
            all_zeros_window.geometry("750x750")
            all_zeros_window.title("Child Window")
            Label(all_zeros_window, text= '''The zip file you received is all misses. 
                                             Ask your opponent to send you the correct zip 
                                             by placing the board in place mode and downloading 
                                             the ship layout.''',
                                             font=('Impact 9 bold')).place(anchor=CENTER, relx=0.5, rely=0.5)
        if os.path.exists('ships.txt'):
            os.remove('ships.txt')
        for x in range(self.row_size):
            for y in range(self.col_size):
                hit_or_miss_color = "red" if opponent_ships[x,y] == 1 else "#0077be"
                border_color = "yellow" if your_ships[x][y] == 1 else "#333333"
                border_width = 50 if your_ships[x][y] == 1 else 10
                self.set_style(f"bloaded{x}{y}.TButton", background="black", bordercolor=border_color, highlightthickness=border_width, padding=0)
                self.button_dict[(x,y)].configure(style=f"bloaded{x}{y}.TButton", command = lambda row_index=x, col_index=y, hit_or_miss_color=hit_or_miss_color, current_border_color=border_color:
                                                                               self.change_button_color("black", hit_or_miss_color, row_index, col_index, current_border_color, False))


    def generate_card(self, seedname=None):
        Grid.rowconfigure(self.root, 0, weight=1)
        Grid.columnconfigure(self.root, 0, weight=1)

        # battleship settings (images and sizes)
        self.images = [ImageTk.PhotoImage(Image.open(f"img/{x}").resize((40,40))) for x in os.listdir("img")]
        if seedname is None:
            self.seedname = ''.join(random.choice(string.ascii_letters) for _ in range(26))
        random.Random(self.seedname).shuffle(self.images)
        self.place_grid = np.zeros((self.row_size, self.col_size))

        #Create & Configure frame 
        self.frame=Frame(self.root)
        self.frame.grid(row=0, column=0, sticky=N+S+E+W)

        self.button_dict = {}

        #Create a (rows x columns) grid of buttons inside the frame
        for row_index in range(self.row_size):
            Grid.rowconfigure(self.frame, row_index, weight=1)
            for col_index in range(self.col_size):
                Grid.columnconfigure(self.frame, col_index, weight=1)
                self.set_style(f"bnormal{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=10, padding=0)
                self.button_dict[(row_index, col_index)] = ttk.Button(self.frame, image = self.images[row_index*self.row_size + col_index], takefocus=False, style=f'bnormal{row_index}{col_index}.TButton',
                                                                    command = lambda row_index=row_index, col_index=col_index: 
                                                                              self.change_button_color("black", "blue", row_index, col_index, "#333333"))
                self.button_dict[(row_index, col_index)].grid(row=row_index, column=col_index, sticky="nsew")  


    def change_button_color(self, current_color, new_color, row_index, col_index, current_border_color, placing_ship=False):
        if placing_ship:
            self.place_ship(row_index, col_index)
        self.set_style(f"bclicked{row_index}{col_index}.TButton", background=new_color, bordercolor=current_border_color, highlightthickness=10, padding=0)
        self.button_dict[(row_index, col_index)].configure(style=f"bclicked{row_index}{col_index}.TButton", command = lambda row_index=row_index, col_index=col_index:
                                                                        self.change_button_color(new_color, current_color, row_index, col_index, current_border_color, placing_ship))


    def copy_seed(self):
        subprocess.run("clip", universal_newlines=True, input=self.seedname)


    def open_help_window(self):
        webbrowser.open('https://github.com/roromaniac/KH2FM-Rando-Battleship')


    def place_mode(self, row_size, col_size, blind=True):
        # make the game blank so you can choose where to set ships
        for row_index in range(row_size):
            Grid.rowconfigure(self.frame, row_index, weight=1)
            for col_index in range(col_size):
                Grid.columnconfigure(self.frame, col_index, weight=1)
                self.set_style(f"bnormal{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=1, padding=0)
                if blind:
                    self.button_dict[(row_index, col_index)] = ttk.Button(self.frame, style=f"bnormal{row_index}{col_index}.TButton", takefocus=False, command=lambda x=row_index, y=col_index: self.change_button_color("black", "blue", x, y, "#333333", True)) #create a button inside frame 
                else:
                    self.button_dict[(row_index, col_index)] = ttk.Button(self.frame, image = self.images[row_index*row_size + col_index], style=f"bnormal{row_index}{col_index}.TButton", takefocus=False, command=lambda x=row_index, y=col_index: self.change_button_color("black", "blue", x, y, "#333333", True)) #create a button inside frame 
                self.button_dict[(row_index, col_index)].grid(row=row_index, column=col_index, sticky=N+S+E+W)

BattleshipBoard()