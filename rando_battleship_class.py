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
import ast
import itertools as it

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

        self.generate_card(self.row_size, self.col_size)

        self.root.geometry("700x700")
        # Creating Menubar
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # board is initially visible so set blind to false
        self.blind = False

        # Board Mode Menu
        board_mode = Menu(menubar, tearoff = False)
        board_mode.add_command(label='Place Mode (Blind)', command=lambda: self.place_mode(self.row_size, self.col_size, blind=True))
        board_mode.add_command(label='Place Mode (Visible)', command=lambda : self.place_mode(self.row_size, self.col_size, blind=False))
        board_mode.add_command(label='Same Board Mode', command=lambda: self.generate_same_board(self.row_size, self.col_size))
        board_mode.add_command(label='Clear Placements', command=lambda blind=self.blind: self.place_mode(self.row_size, self.col_size, blind=blind))
        menubar.add_cascade(label ='Placement', menu=board_mode)

        # Action Mode Menu
        actions = Menu(menubar, tearoff = False)
        actions.add_command(label = 'Generate New Card', command=lambda: self.generate_card(self.row_size, self.col_size))
        actions.add_command(label = 'Load Card from Seed', command=self.change_seedname)
        actions.add_command(label = 'Resize Grid', command=self.resize_grid)
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
        self.row_size, self.col_size, self.seedname = ast.literal_eval(simpledialog.askstring(title="Seed", prompt="Seed Name: ", initialvalue=f"({self.row_size}, {self.col_size}, '{self.seedname}')"))
        self.generate_card(self.row_size, self.col_size, self.seedname)
        self.info.entryconfig(0, label=f'Seedname: {self.seedname}')


    def place_ship(self, x, y):
        self.place_grid[x,y] = 1 - self.place_grid[x,y]
        print(self.place_grid)
        return self.place_grid

    
    def generate_same_board(self, row_size, col_size):
        # keep track of possible ship placements
        placed_ships = np.zeros((row_size, col_size))
        possible_ship_heads = list(it.product(range(row_size), range(col_size)))
        # until you run out of ships to place...
        while len(self.ship_sizes) != 0:

            # pick a random ship
            current_random_ship = self.ship_sizes.pop(random.choice(range(len(self.ship_sizes))))

            valid_placement = False
            while not valid_placement:

                # pick a random but possible ship head placement
                current_ship_head = random.choice(list(set(possible_ship_heads) - set(list(it.product(range(row_size - current_random_ship, row_size), range(col_size - current_random_ship, col_size))))))

                # pick a random direction if 2 are possible.
                possible_directions = []
                if current_ship_head[0] + current_random_ship <= row_size and all(placed_ships[current_ship_head[0] + i, current_ship_head[1]] != 1 for i in range(current_random_ship)):
                    possible_directions.append("down")
                if current_ship_head[1] + current_random_ship <= col_size and all(placed_ships[current_ship_head[0], current_ship_head[1] + i] != 1 for i in range(current_random_ship)):
                    possible_directions.append("right")
                # place the ship and remove squares as possible placements going forward
                try: 
                    direction = random.choice(possible_directions)
                except IndexError:
                    continue
                x, y = current_ship_head
                if direction == "right":
                    # check that you can place the ship
                    for i in range(current_random_ship):
                        if (x, y + i) not in possible_ship_heads:
                            break
                    # place the ship if possible
                    else:
                        valid_placement = True
                        for i in range(current_random_ship):
                            placed_ships[x, y + i] = 1
                if direction == "down":
                    # check that you can place the ship
                    for i in range(current_random_ship):
                        if (x + i, y) not in possible_ship_heads:
                            break
                    else:
                        valid_placement = True
                        for i in range(current_random_ship):
                            placed_ships[x + i, y] = 1
            xs, ys = np.where(placed_ships == 1)
            unavailable_placements = [[xs[j], ys[j]] for j in range(len(xs))]
            # remove squares from available placements if the index is valid
            for square in unavailable_placements:
                # try left
                try:
                    possible_ship_heads.remove((square[0], square[1] - 1))
                except ValueError:
                    pass
                #try right
                try:
                    possible_ship_heads.remove((square[0], square[1] + 1))
                except ValueError:
                    pass
                #try up
                try:
                    possible_ship_heads.remove((square[0] - 1, square[1]))
                except ValueError:
                    pass
                #try down
                try:
                    possible_ship_heads.remove((square[0] + 1, square[1]))
                except ValueError:
                    pass   

        # apply hit and miss logic to start the game
        self.upload(placed_ships)


    def download(self):
        try:
            os.makedirs('ships')
        except FileExistsError:
            pass
        np.savetxt("ships/ships.txt", self.place_grid, fmt='%s')
        shutil.make_archive('ships/', 'zip', 'ships')


    def upload(self, same_board=None):

        # if you're uploading a manually placed board
        if same_board is None:

            # unpack zip file of opponent's ships
            filename = fd.askopenfilename()
            shutil.unpack_archive(filename, '.', 'zip')
        
            # load opponent ships
            opponent_ships = np.loadtxt('ships.txt')

            # load your ships
            your_ships = np.loadtxt('ships/ships.txt')

        # if you're using a prebuilt randomly generated board
        else:

            opponent_ships = same_board

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

        self.opponent_ships_with_ids = self.find_ships(opponent_ships)
        self.ships_left = list(range(1, int(np.max(self.opponent_ships_with_ids)) + 1))
        self.checks_found = np.zeros((self.row_size, self.col_size))

        for x in range(self.row_size):
            for y in range(self.col_size):
                hit_or_miss_color = "red" if opponent_ships[x,y] == 1 else "#0077be"
                if same_board is None:
                    border_color = "yellow" if your_ships[x][y] == 1 else "#333333"
                    border_width = 50 if your_ships[x][y] == 1 else 10
                else:
                    border_color = "#333333"
                    border_width = 10
                self.set_style(f"bloaded{x}{y}.TButton", background="black", bordercolor=border_color, highlightthickness=border_width, padding=0)
                self.button_dict[(x,y)].configure(style=f"bloaded{x}{y}.TButton", command = lambda row_index=x, col_index=y, hit_or_miss_color=hit_or_miss_color, current_border_color=border_color:
                                                                               self.change_button_color("black", hit_or_miss_color, row_index, col_index, current_border_color, False))


    def generate_card(self, row_size, col_size, seedname=None):
        Grid.rowconfigure(self.root, 0, weight=1)
        Grid.columnconfigure(self.root, 0, weight=1)

        # battleship settings (images and sizes)
        self.images = [ImageTk.PhotoImage(Image.open(f"img/{x}").resize((40,40))) for x in os.listdir("img")]
        if seedname is None:
            self.seedname = ''.join(random.choice(string.ascii_letters) for _ in range(26))
        random.Random(self.seedname).shuffle(self.images)
        self.place_grid = np.zeros((row_size, col_size))

        #Create & Configure frame 
        self.frame=Frame(self.root)
        self.frame.grid(row=0, column=0, sticky=N+S+E+W)

        self.button_dict = {}

        #Create a (rows x columns) grid of buttons inside the frame
        for row_index in range(row_size):
            Grid.rowconfigure(self.frame, row_index, weight=1)
            for col_index in range(col_size):
                Grid.columnconfigure(self.frame, col_index, weight=1)
                self.set_style(f"bnormal{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=10, padding=0)
                self.button_dict[(row_index, col_index)] = ttk.Button(self.frame, image = self.images[row_index*self.row_size + col_index], takefocus=False, style=f'bnormal{row_index}{col_index}.TButton')
                self.button_dict[(row_index, col_index)].grid(row=row_index, column=col_index, sticky="nsew")  


    def change_button_color(self, current_color, new_color, row_index, col_index, current_border_color, placing_ship=False):
        # place new ship if in place mode
        if placing_ship:
            self.place_ship(row_index, col_index)

        # change button color
        self.set_style(f"bclicked{row_index}{col_index}.TButton", background=new_color, bordercolor=current_border_color, highlightthickness=10, padding=0)
        self.button_dict[(row_index, col_index)].configure(style=f"bclicked{row_index}{col_index}.TButton", command = lambda row_index=row_index, col_index=col_index:
                                                                        self.change_button_color(new_color, current_color, row_index, col_index, current_border_color, placing_ship))

        # check if boat is sunk and change the button colors to reflect that
        if not placing_ship:
            self.checks_found[row_index, col_index] = 1
            for id in self.ships_left:
                xs, ys = np.where(self.opponent_ships_with_ids == id)
                if all([value == 1 for value in [ self.checks_found[xs[i], ys[i]] for i in range(len(xs))]]):
                    for index_x, index_y in [[xs[i], ys[i]] for i in range(len(xs))]:
                        self.set_style(f"bsunk{index_x}{index_y}.TButton", background="pink", bordercolor=current_border_color, highlightthickness=10, padding=0)
                        self.button_dict[(index_x, index_y)].configure(style=f"bsunk{row_index}{col_index}.TButton", command = lambda row_index=row_index, col_index=col_index:
                                                                            self.change_button_color("pink", "pink", row_index, col_index, current_border_color, placing_ship))
                    self.ships_left.remove(id)

    def copy_seed(self):
        subprocess.run("clip", universal_newlines=True, input=f"({self.row_size}, {self.col_size}, '{self.seedname}')")


    def open_help_window(self):
        webbrowser.open('https://github.com/roromaniac/KH2FM-Rando-Battleship')


    def find_ships(self, ship_layout):
        num_ships_detected = 0
        assert ship_layout.shape == (self.row_size, self.col_size), "The layout does not match the current grid shape."
        ship_layout_with_ids = np.zeros((self.row_size, self.col_size))
        id = 0
        for x in range(self.row_size):
            for y in range(self.col_size):
                if ship_layout[x, y] == 1 and ship_layout_with_ids[x, y] == 0:
                    id += 1
                    ship_layout_with_ids[x, y] = id
                    i = 1
                    try: 
                        while x + i < self.row_size:
                            if ship_layout[x + i, y] == 1:
                                ship_layout_with_ids[x + i, y] = id
                                i += 1
                            else:
                                break
                    except IndexError:
                        pass
                    i = 1
                    try: 
                        while y + i < self.col_size:
                            if ship_layout[x, y + i] == 1:
                                ship_layout_with_ids[x, y + i] = id
                                i += 1
                            else:
                                break
                    except IndexError:
                        pass
                    num_ships_detected += 1
        # run assertion that the appropriate number of ships were placed
        
        return ship_layout_with_ids

    
    def resize_grid(self):

        row_size = simpledialog.askstring(title="Row Dimension", prompt="Row Dimension: ", initialvalue=11)
        col_size = simpledialog.askstring(title="Column Dimension", prompt="Column Dimension: ", initialvalue=11)
        try:
            int(row_size)
            int(col_size)
        except TypeError:
            pass
            # create popup window that says sizes should be integers
        self.row_size, self.col_size = int(row_size), int(col_size)
        self.generate_card(self.row_size, self.col_size)
        
                            

    def place_mode(self, row_size, col_size, blind=True):
        # make the game blank so you can choose where to set ships
        self.blind = blind
        # entering place mode resets the grid
        self.place_grid = np.zeros((row_size, col_size))
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