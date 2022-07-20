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
import json
import itertools as it

from tkinter import filedialog as fd
from tkinter import simpledialog

class BattleshipBoard():

    def __init__(self, row_size=11, col_size=11):

        # attribute setting
        self.row_size, self.col_size = row_size, col_size
        self.ship_sizes = [5, 4, 3, 3, 2]

        # checks allowed on grid
        self.check_types = [ 
                                'report', 
                                'magic1',
                                'magic2',
                                'magic3', 
                                'movement1', 
                                'movement2',
                                'movement3', 
                                'movement4', 
                                'story_boss', 
                                'sc/om',  
                                'form',
                                'tornpage',
                                'summon', 
                                'proof',
                                'progression',
                                'promise',
                                'extra', 
                                'armored_xemnas', 
                                'as',        
                                'sephiroth', 
                                'terra'
                            ]
        # reset your own ships
        reset_ships_array = np.zeros((self.row_size, self.col_size))
        if not os.path.isdir('ships'):
            os.mkdir('ships')
        np.savetxt("ships/ships.txt", reset_ships_array, fmt='%s')

        # Create & Configure root 
        self.root = Tk()
        self.root.title("Rando Battleship (v1.1.2)")

        # board is initially visible so set blind to false
        self.blind = False

        # Create Shortcuts
        self.root.bind_all("<Control-b>", lambda event: self.place_mode(self.row_size, self.col_size, blind=True))
        self.root.bind_all("<Control-v>", lambda event: self.place_mode(self.row_size, self.col_size, blind=False))
        self.root.bind_all("<Control-s>", lambda event: self.upload(True))
        self.root.bind_all("<Control-c>", lambda event: self.place_mode(self.row_size, self.col_size, blind=self.blind))
        self.root.bind_all("<Control-g>", lambda event: self.generate_card(self.row_size, self.col_size))
        self.root.bind_all("<Control-r>", self.resize_grid)
        self.root.bind_all("<Control-i>", self.copy_seed)
        self.root.bind_all("<Control-u>", lambda event: self.upload(False))
        self.root.bind_all("<Control-d>", self.download)
        self.root.bind_all("<Control-h>", self.open_help_window)


        self.generate_card(self.row_size, self.col_size)

        # Geometry moved into generate_card to reflect grid size.
        # self.root.geometry(f"{64*self.row_size}x{64*self.col_size}")

        # Creating Menubar
        menubar = Menu(self.root)

        # Board Mode Menu
        board_mode = Menu(menubar, tearoff = False)
        board_mode.add_command(label='Place Mode (Blind)', underline=5, command=lambda: self.place_mode(self.row_size, self.col_size, blind=True), accelerator="Ctrl+B")
        board_mode.add_command(label='Place Mode (Visible)', command=lambda : self.place_mode(self.row_size, self.col_size, blind=False), accelerator="Ctrl+V")
        board_mode.add_command(label='Same Board Mode', command=lambda: self.upload(True), accelerator="Ctrl+S")
        board_mode.add_command(label='Clear Placements', command=lambda: self.place_mode(self.row_size, self.col_size, blind=self.blind), accelerator="Ctrl+C")
        menubar.add_cascade(label ='Placement', menu=board_mode)

        # Action Mode Menu
        actions = Menu(menubar, tearoff = False)
        actions.add_command(label = 'Generate New Card', command=lambda: self.generate_card(self.row_size, self.col_size), accelerator="Ctrl+G")
        actions.add_command(label = 'Change Seedname', command=lambda: self.set_seedname(simpledialog.askstring(title="Set Seedname", prompt="Seedname: ")))
        actions.add_command(label = 'Resize Grid', command=self.resize_grid, accelerator="Ctrl+R")
        actions.add_command(label = 'Copy Seed Name', command=self.copy_seed, accelerator="Ctrl+I")
        actions.add_command(label = 'Upload Ship Layout', command=self.upload, accelerator="Ctrl+U")
        actions.add_command(label = 'Download Ship Layout', command=self.download, accelerator="Ctrl+D")
        actions.add_command(label = 'Download Board Settings', command=self.save_settings)
        actions.add_command(label = 'Upload Board Settings', command=self.load_settings)
        actions.add_command(label = 'Save Settings as New Preset', command=lambda: self.save_settings(True))
        menubar.add_cascade(label = 'Actions', menu=actions)

        # Customize Mode Menu
        customize = Menu(menubar, tearoff = False)
        customize.add_command(label = 'Change Ship Sizes', command=self.ship_setter_window)
        customize.add_command(label = 'Toggle Checks', command=self.check_inclusion_window)
        customize.add_command(label = 'Set Ship Restrictions', command=self.check_restriction_window)
        menubar.add_cascade(label = 'Customize', menu=customize)


        # Validation Mode Menu
        validations = Menu(menubar, tearoff = False)
        validations.add_command(label = 'Validate Your Ships', command=self.validate_self_ships)
        validations.add_command(label = 'Validate Opponent/Shared Ships', command=self.validate_opponent_ships)
        menubar.add_cascade(label = "Validate", menu=validations)

        # Information Menu
        self.info = Menu(menubar, tearoff=False)
        self.info.add_command(label = 'Help', command=self.open_help_window, accelerator="Ctrl+H")
        menubar.add_cascade(label = 'Info', menu=self.info)

        self.root.config(menu=menubar)
        self.root.mainloop()


    def set_style(self, name, background, bordercolor, highlightthickness, padding):
        style = ttk.Style(self.frame)
        style.theme_use('alt')
        style.configure(name, background=background, bordercolor=bordercolor, highlightthickness=highlightthickness, padding=padding, relief=SOLID)


    def set_seedname(self, new_seedname):
        self.seedname = new_seedname


    def place_ship(self, x, y, event=None):
        self.place_grid[x,y] = 1 - self.place_grid[x,y]
        print(self.place_grid)
        return self.place_grid

    
    def generate_same_board(self, row_size, col_size, event=None):
        random.seed(self.seedname)
        # keep track of possible ship placements
        placed_ships = np.zeros((row_size, col_size))
        possible_ship_heads = list(it.product(range(row_size), range(col_size)))
        ship_data = [x for x in self.ship_sizes]
        if hasattr(self, 'restrictions'):
            restrictions_tracker = {}
            for check_type in self.restrictions.keys():
                restrictions_tracker[check_type] = 0

        # until you run out of ships to place...
        while len(self.ship_sizes) != 0:

            # pick a random ship
            current_random_ship = self.ship_sizes.pop(random.choice(range(len(self.ship_sizes))))

            valid_placement = False
            while not valid_placement:

                # pick a random but possible ship head placement
                current_ship_head = random.choice(list(set(possible_ship_heads) - set(list(it.product(range(row_size - current_random_ship + 1, row_size), range(col_size - current_random_ship + 1, col_size))))))

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
                        if hasattr(self, 'restrictions'):
                            if ((x * self.row_size + (y + i)) < len(self.labels)) and (self.labels[x * self.row_size + (y + i)] in self.restrictions.keys()):
                                if restrictions_tracker[self.labels[x * self.row_size + (y + i)]] + 1 > self.restrictions[self.labels[x * self.row_size + (y + i)]]:
                                    break
                    # place the ship if possible
                    else:
                        valid_placement = True
                        for i in range(current_random_ship):
                            placed_ships[x, y + i] = 1
                            if hasattr(self, 'restrictions') and (self.labels[x * self.row_size + (y + i)] in self.restrictions.keys()):
                                restrictions_tracker[self.labels[x * self.row_size + (y + i)]] += 1
                if direction == "down":
                    # check that you can place the ship
                    for i in range(current_random_ship):
                        if (x + i, y) not in possible_ship_heads:
                            break
                        if hasattr(self, 'restrictions'):
                            if (((x + i) * self.row_size + y) < len(self.labels)) and (self.labels[(x + i) * self.row_size + y] in self.restrictions.keys()):
                                if restrictions_tracker[self.labels[(x + i) * self.row_size + y]] + 1 > self.restrictions[self.labels[(x + i) * self.row_size + y]]:
                                    break
                    else:
                        valid_placement = True
                        for i in range(current_random_ship):
                            placed_ships[x + i, y] = 1
                            if hasattr(self, 'restrictions') and (self.labels[(x + i) * self.row_size + y] in self.restrictions.keys()):
                                restrictions_tracker[self.labels[(x + i) * self.row_size + y]] += 1
                # print(restrictions_tracker)
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
        self.ship_sizes = ship_data
        return placed_ships


    def download(self, event=None):
        try:
            os.makedirs('ships')
        except FileExistsError:
            pass
        np.savetxt("ships/ships.txt", self.place_grid, fmt='%s')
        shutil.make_archive('ships/', 'zip', 'ships')


    def upload(self, same_board=False, event=None):

        # if you're uploading a manually placed board
        if not same_board:

            # unpack zip file of opponent's ships
            filename = fd.askopenfilename()
            shutil.unpack_archive(filename, '.', 'zip')
        
            # load opponent ships
            opponent_ships = np.loadtxt('ships.txt')

            # load your ships
            your_ships = np.loadtxt('ships/ships.txt')

        # if you're using a prebuilt randomly generated board
        else:

            opponent_ships = self.generate_same_board(self.row_size, self.col_size)

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
        
        # remove opponent ships file to avoid cheating
        if os.path.exists('ships.txt'):
            os.remove('ships.txt')

        self.opponent_ships_with_ids = self.find_ships(opponent_ships)
        self.ships_left = list(range(1, int(np.max(self.opponent_ships_with_ids)) + 1))
        self.checks_found = np.zeros((self.row_size, self.col_size))

        for x in range(self.row_size):
            for y in range(self.col_size):
                hit_or_miss_color = "red" if opponent_ships[x,y] == 1 else "#0077be"
                if not same_board:
                    border_color = "yellow" if your_ships[x][y] == 1 else "#333333"
                    border_width = 50 if your_ships[x][y] == 1 else 10
                else:
                    border_color = "#333333"
                    border_width = 10
                self.set_style(f"bloaded{x}{y}.TButton", background="black", bordercolor=border_color, highlightthickness=border_width, padding=0)
                self.button_dict[(x,y)].configure(style=f"bloaded{x}{y}.TButton", command = lambda row_index=x, col_index=y, hit_or_miss_color=hit_or_miss_color, current_border_color=border_color:
                                                                               self.change_button_color("black", hit_or_miss_color, row_index, col_index, current_border_color, False))


    def generate_card(self, row_size, col_size, seedname=None, event=None):
        self.root.geometry(f"{64*row_size}x{64*col_size}")
        Grid.rowconfigure(self.root, 0, weight=1)
        Grid.columnconfigure(self.root, 0, weight=1)

        # battleship settings (images and sizes) and randomization
        if seedname is None:
            self.seedname = ''.join(random.choice(string.ascii_letters) for _ in range(26))
        self.check_names = [x for x in os.listdir("img")]
        if hasattr(self, 'valid_checks'):
            self.check_names = [x for (x, include) in zip(self.check_names, self.valid_checks) if include]
        random.Random(self.seedname).shuffle(self.check_names)
        self.images = [ImageTk.PhotoImage(Image.open(f"img/{check}").resize((40,40))) for check in self.check_names]
        with open("img.json", "r") as checktypes_json:
            checktypes_dict = json.load(checktypes_json)
            self.labels = [checktypes_dict[check] for check in self.check_names]
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

        # checks not inlucded = checks too late in the list to be included in the grid + checks removed due to board size changes from restrictions (this is the union)
        checks_not_included = set(x[:-5] for x in self.check_names[row_size * col_size:]).union(set(x[:-5] for x in os.listdir('img')) - set(x[:-5] for x in self.check_names))
        print("------------------------------------------------")
        print("New Card Generation Detected: Checks Removed are")
        print("------------------------------------------------")
        [print(removed_check) for removed_check in list(checks_not_included)]


    def change_button_color(self, current_color, new_color, row_index, col_index, current_border_color, placing_ship=False, event=None):
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


    def copy_seed(self, event=None):
        subprocess.run("clip", universal_newlines=True, input=f"({self.row_size}, {self.col_size}, '{self.seedname}')")


    def open_help_window(self, event=None):
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

    
    def resize_grid(self, event=None):

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
                            

    def place_mode(self, row_size, col_size, blind=True, event=None):
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


    def set_ship_sizes(self, entries, window):
        self.ship_sizes = list(it.chain(*[[i] * int(entries[i].get()) if entries[i].get() != "" else [] for i in range(1, max(self.row_size, self.col_size) + 1)]))
        print(self.ship_sizes)
        window.destroy()


    def ship_setter_window(self):
        window = Tk() 
        window.title("Ship Size Setting")

        TitleLabel = ttk.Label(window, text = "Quantity")
        TitleLabel.grid(row = 0, column = 1)

        labels = {}
        entries = {}

        max_dim = max(self.row_size, self.col_size) + 1

        for i in range(1, max_dim):

            labels[i] = ttk.Label(window, text = f"# of {i} ships")
            labels[i].grid(row = i, column = 0)

            entries[i] = ttk.Entry(window, width = 5)
            entries[i].grid(row = i, column = 1)

        btn = ttk.Button(window, text = "Submit Answers", command = lambda: self.set_ship_sizes(entries, window))
        btn.grid(row = i+1, column = 1)


    def set_checks(self, entries, window, gen_card=True):
        self.check_names = [x for x in os.listdir("img")]
        with open("img.json", "r") as checktypes_json:
            checktypes_dict = json.load(checktypes_json)
            self.labels = [checktypes_dict[check] for check in self.check_names]
        self.selected_checks = [entries[i + 1].instate(['selected']) for i in range(len(self.check_types))]
        self.valid_types = [self.check_types[i] for i in range(len(self.check_types)) if entries[i + 1].instate(['selected'])]
        self.valid_checks = [True if x in self.valid_types else False for x in self.labels]
        self.row_size, self.col_size = [int(np.floor(np.sqrt(sum(self.valid_checks))))] * 2
        if gen_card:
            self.generate_card(self.row_size, self.col_size)
        window.destroy()


    def check_inclusion_window(self):
        # code that will remove checks from the grid pool
        window = Tk() 
        window.title("Check Inclusion Toggles")

        TitleLabel = ttk.Label(window, text = "Include?")
        TitleLabel.grid(row = 0, column = 1)

        check_type_labels = ["Reports", 
                             "Lvl 1 Magic", 
                             "Lvl 2 Magic", 
                             "Lvl 3 Magic", 
                             "Lvl 1 Movement", 
                             "Lvl 2 Movement", 
                             "Lvl 3 Movement", 
                             "Lvl 4 Movement", 
                             "Story Bosses", 
                             "Second Chance/Once More", 
                             "Drive Forms", 
                             "Torn Pages", 
                             "Summons", 
                             "Proofs", 
                             "World Progression Icons",
                             "Promise Charm",
                             "Extra Checks",
                             "Armored Xemnas",
                             "Absent Silhouettes",
                             "Sephiroth",
                             "Lingering Will"] 

        labels = {}
        entries = {}

        num_rows = len(check_type_labels) + 1

        for i in range(1, num_rows):

            labels[i] = ttk.Label(window, text = check_type_labels[i - 1], anchor='w', takefocus=False)
            labels[i].grid(row = i, column = 0)

            # have toggle checked by default
            entries[i] = ttk.Checkbutton(window, cursor=None)
            entries[i].state(["!alternate"])
            if hasattr(self, 'selected_checks'):
                entries[i].state(["!selected"])
                if self.selected_checks[i - 1]:
                  entries[i].state(["selected"])  
            else:
                entries[i].state(["selected"])
            entries[i].grid(row = i, column = 1)

        btn1 = ttk.Button(window, text = "Submit Toggles", command = lambda: self.set_checks(entries, window, gen_card=False))
        btn1.grid(row = i+1, column = 1)


    def set_restrictions(self, entries, window, reset=False):
        if reset:
            restriction_values = [13, 6, 6, 6, 5, 5, 5, 5, 31, 2, 5, 5, 4, 3, 11, 5]
        else:
            restriction_values = [int(entries[i].get()) for i in range(1, len(entries.keys()) + 1)]
        quantitative_check_labels = [
            'report', 
            'magic1',
            'magic2',
            'magic3', 
            'movement1', 
            'movement2',
            'movement3', 
            'movement4', 
            'story_boss', 
            'sc/om',  
            'form',
            'tornpage',
            'summon', 
            'proof',
            'progression',
            'as',        
        ]
        self.restrictions = {}
        for i in range(len(restriction_values)):
            self.restrictions[quantitative_check_labels[i]] = restriction_values[i]
        window.destroy()


    def check_restriction_window(self):
        window = Tk() 
        window.title("Ship Placement Restrictions")

        TitleLabel = ttk.Label(window, text = "Quantity")
        TitleLabel.grid(row = 0, column = 1)

        labels = {}
        entries = {}
        maxes = {}

        quantitative_check_type_labels = ["Reports", 
                                          "Lvl 1 Magic", 
                                          "Lvl 2 Magic", 
                                          "Lvl 3 Magic", 
                                          "Lvl 1 Movement", 
                                          "Lvl 2 Movement", 
                                          "Lvl 3 Movement", 
                                          "Lvl 4 Movement", 
                                          "Story Bosses", 
                                          "Second Chance/Once More", 
                                          "Drive Forms", 
                                          "Torn Pages", 
                                          "Summons", 
                                          "Proofs", 
                                          "World Progression Icons",
                                          "Absent Silhouettes",
                                        ]

        checktype_index_to_quantity_dict = {
            0: 13,
            1: 6,
            2: 6, 
            3: 6,
            4: 5,
            5: 5,
            6: 5,
            7: 5,
            8: 31,
            9: 2,
            10: 5,
            11: 5,
            12: 4,
            13: 3,
            14: 11,
            15: 5,
        }

        for i in range(1, len(quantitative_check_type_labels) + 1):

            labels[i] = ttk.Label(window, text = f"{quantitative_check_type_labels[i - 1]}")
            labels[i].grid(row = i, column = 0)

            entries[i] = ttk.Entry(window, width = 5)
            if hasattr(self, 'restrictions'):
                entries[i].insert(0, list(self.restrictions.values())[i - 1])
            else:
                entries[i].insert(0, checktype_index_to_quantity_dict[i - 1])
            entries[i].grid(row = i, column = 1)

            maxes[i] = ttk.Label(window, text=f"(max {checktype_index_to_quantity_dict[i - 1]})")
            maxes[i].grid(row = i, column = 2)

        btn0 = ttk.Button(window, text = "Reset Restrictions", command = lambda: self.set_restrictions(entries, window, reset=True))
        btn0.grid(row = i+1, column = 0)

        btn1 = ttk.Button(window, text = "Submit Answers", command = lambda: self.set_restrictions(entries, window))
        btn1.grid(row = i+1, column = 1)


    def save_settings(self, preset=False):
        if preset:
            preset_name = fd.asksaveasfilename(initialdir="/presets", defaultextension='.txt', filetypes=[("Text File", ".txt")])
            with open(preset_name, "w") as settings_file:
                if hasattr(self, 'selected_checks'):
                    settings_file.write(f"self.selected_checks = {self.selected_checks}\n")
                if hasattr(self, 'valid_checks'):
                    settings_file.write(f"self.valid_checks = {self.valid_checks}\n")
                if hasattr(self, 'restrictions'):
                    settings_file.write(f"self.restrictions = {self.restrictions}\n")
                settings_file.write(f"self.row_size, self.col_size = {self.row_size}, {self.col_size}\n")
                settings_file.write(f"self.ship_sizes = {self.ship_sizes}\n")
        else:
            with open("settings.txt", "w") as settings_file:
                if hasattr(self, 'selected_checks'):
                    settings_file.write(f"self.selected_checks = {self.selected_checks}\n")
                if hasattr(self, 'valid_checks'):
                    settings_file.write(f"self.valid_checks = {self.valid_checks}\n")
                if hasattr(self, 'restrictions'):
                    settings_file.write(f"self.restrictions = {self.restrictions}\n")
                settings_file.write(f"self.row_size, self.col_size = {self.row_size}, {self.col_size}\n")
                settings_file.write(f"self.seedname = '{self.seedname}'\n")
                settings_file.write(f"self.ship_sizes = {self.ship_sizes}\n")
    

    def load_settings(self):
        settings_filename = fd.askopenfilename()
        with open(settings_filename, "r") as settings_file:
            settings = settings_file.readlines()
            for line in settings:
                exec(line)
        self.set_seedname(self.seedname)
        self.generate_card(self.row_size, self.col_size, self.seedname)


    def validate_self_ships(self):
        ship_layout = np.loadtxt('ships/ships.txt')
        ship_layout_with_ids = self.find_ships(ship_layout)
        self.validate_ships(ship_layout_with_ids)


    def validate_opponent_ships(self):
        if not hasattr(self, 'opponent_ships_with_ids'):
            raise AttributeError("You probably did not load your opponent's ships or put the board in single board mode.")
        self.validate_ships(self.opponent_ships_with_ids)
    

    def validate_ships(self, ship_layout_with_ids):
        ships_found = []
        for ship_id in range(1, int(np.max(ship_layout_with_ids)) + 1):
            ships_found.append(np.sum(ship_layout_with_ids == ship_id))
        print_success = True
        if not sorted(ships_found) == sorted(self.ship_sizes):
            print(f"The ships you placed are {sorted(ships_found)} but they need to be {sorted(self.ship_sizes)}")
            print_success = False

        # add feature for checking for neighbors
        print(ship_layout_with_ids)
        for ship_id in range(1, int(np.max(ship_layout_with_ids)) + 1):
            xs, ys = np.where(ship_layout_with_ids == ship_id)
            current_ship_id_locations = [[xs[j], ys[j]] for j in range(len(xs))]
            for square in current_ship_id_locations:
                # try left
                try:
                    if ship_layout_with_ids[square[0], max(square[1] - 1, 0)] > ship_id:
                        print("You have neighboring ships.")
                        print_success = False
                        break
                except IndexError:
                    pass
                #try right
                try:
                    if ship_layout_with_ids[square[0], square[1] + 1] > ship_id:
                        print("You have neighboring ships.")
                        print_success = False
                        break
                except IndexError:
                    pass
                #try up
                try:
                    if ship_layout_with_ids[max(square[0] - 1, 0), square[1]] > ship_id:
                        print("You have neighboring ships.")
                        print_success = False
                        break
                except IndexError:
                    pass
                #try down
                try:
                    if ship_layout_with_ids[square[0] + 1, square[1]] > ship_id:
                        print(ship_id, (square[0] + 1, square[1]))
                        print_success = False
                        break
                except IndexError:
                    pass
   
        # add feature for validating types
        if hasattr(self, 'restrictions'):
            xs, ys = np.where(ship_layout_with_ids >= 1)
            ship_locations = [[xs[j], ys[j]] for j in range(len(xs))]
            check_types_on_ships = {}
            for x, y in ship_locations:
                current_label = self.labels[x * self.row_size + y]
                if current_label not in check_types_on_ships.keys():
                    check_types_on_ships[current_label] = 1
                else:
                    check_types_on_ships[current_label] += 1

            for check_type in check_types_on_ships.keys():
                if (check_type in self.restrictions.keys()) and (check_types_on_ships[check_type] > self.restrictions[check_type]):
                    print(f"You have too many checks of type {check_type} across your ships. Please remove some and try again.")
                    print_success = False  
                    break

        # if no errors detected, print ships look good
        if print_success:
            print(f"Ships look good!")


BattleshipBoard() 