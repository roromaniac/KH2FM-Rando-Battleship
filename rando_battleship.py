import random
import os
import numpy as np
import string
import subprocess
import shutil
import webbrowser
import json
import itertools as it
import ast
import psutil
import base64

from tkinter import *
from tkinter import ttk
from tkinter.colorchooser import askcolor
from PIL import ImageTk, Image
from copy import deepcopy


from tkinter import filedialog as fd
from tkinter import simpledialog
from cryptography.fernet import Fernet

from PIL import Image, ImageOps

class BattleshipBoard():

    def __init__(self, row_size=11, col_size=11):

        # tracker settings
        self.scaling_factor = 1.37
        self.color_types = 6

        # battleship setting
        self.row_size, self.col_size = row_size, col_size
        self.ship_sizes = [5, 4, 3, 3, 2]

        # timing settings 
        self.latency = 1000
        self.auto_detect_counter = 0

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
                                'cups_fight',
                                'sc/om',  
                                'form',
                                'tornpage',
                                'summon', 
                                'proof',
                                'progression',
                                'promise',
                                'extra', 
                                'armored_xemnas', 
                                'final_xemnas',
                                'as',        
                                'sephiroth', 
                                'terra'
                            ]

        # reset your own ships
        reset_ships_array = np.zeros((self.row_size, self.col_size))
        if not os.path.isdir('ships'):
            os.mkdir('ships')
        np.savetxt("ships/ships.txt", reset_ships_array, fmt='%s')

        # set bingo to false by default to avoid errors
        self.bingo = False

        # set mystery to false by default
        self.mystery = False

        # set maze to false by default
        self.maze = False

        # Create & Configure root 
        self.root = Tk()
        self.root.title("Rando Battleship (v2.1.2)")

        # board is initially visible so set blind to false
        self.blind = False

        # Create Shortcuts
        self.root.bind_all("<Control-b>", lambda event: self.place_mode(self.row_size, self.col_size, blind=True))
        self.root.bind_all("<Control-v>", lambda event: self.place_mode(self.row_size, self.col_size, blind=False))
        self.root.bind_all("<Control-s>", lambda event: self.upload_ship_layout(True))
        self.root.bind_all("<Control-c>", lambda event: self.place_mode(self.row_size, self.col_size, blind=self.blind))
        self.root.bind_all("<Control-g>", lambda event: self.generate_card(self.row_size, self.col_size, mystery=self.mystery, maze=self.maze))
        self.root.bind_all("<Control-r>", self.resize_grid)
        self.root.bind_all("<Control-i>", self.copy_seed)
        self.root.bind_all("<Control-u>", lambda event: self.upload_ship_layout(False))
        self.root.bind_all("<Control-d>", self.download_ship_layout)
        self.root.bind_all("<Control-h>", self.open_help_window)

        # Load in Current Tracker Settings
        with open("tracker_settings.txt", "r") as settings_file:
            settings = settings_file.readlines()
            for line in settings:
                exec(line)

        # Load in Settings from Previously Loaded Settings
        if os.path.exists("previous_preset.txt"):
            with open("previous_preset.txt", "r") as previous_settings:
                previous = previous_settings.readlines()
                for line in previous:
                    exec(line)

        self.generate_card(self.row_size, self.col_size, maze=self.maze, mystery=self.mystery)

        # Creating Menubar
        self.menubar = Menu(self.root)

        # Geometry moved into generate_card to reflect grid size.
        # self.root.geometry(f"{64*self.row_size}x{64*self.col_size}")

        # Board Mode Menu
        board_mode = Menu(self.menubar, tearoff = False)
        board_mode.add_command(label='Place Mode (Blind)', underline=5, command=lambda: self.place_mode(self.row_size, self.col_size, blind=True), accelerator="Ctrl+B")
        board_mode.add_command(label='Place Mode (Visible)', command=lambda : self.place_mode(self.row_size, self.col_size, blind=False), accelerator="Ctrl+V")
        board_mode.add_command(label='Same Board Mode', command=lambda: self.upload_ship_layout(True), accelerator="Ctrl+S")
        board_mode.add_command(label='Clear Placements', command=lambda: self.place_mode(self.row_size, self.col_size, blind=self.blind), accelerator="Ctrl+Z")
        self.menubar.add_cascade(label ='Placement', menu=board_mode)


        # Action Mode Menu
        actions = Menu(self.menubar, tearoff = False)
        actions.add_command(label = 'Generate New Card', command=lambda: self.generate_card(self.row_size, self.col_size, mystery=self.mystery, maze=self.maze), accelerator="Ctrl+G")
        actions.add_command(label = 'Change Seedname', command=lambda: self.set_seedname(simpledialog.askstring(title="Set Seedname", prompt="Seedname: "), gen_card=True))   
        actions.add_command(label = 'Copy Seed Name', command=self.copy_seed, accelerator="Ctrl+I")
        actions.add_command(label = 'Load Ship Layout', command=self.upload_ship_layout, accelerator="Ctrl+U")
        actions.add_command(label = 'Save Ship Layout', command=self.download_ship_layout, accelerator="Ctrl+D")
        actions.add_command(label = 'Save Board Settings', command=self.save_settings)
        actions.add_command(label = 'Load Board Settings', command=self.load_settings)
        actions.add_command(label = 'Load Preset', command=lambda: self.load_settings(True))
        actions.add_command(label = 'Save Settings as New Preset', command=lambda: self.save_settings(True))
        actions.add_command(label = 'Start Autotracking', command=self.autotracking_timer)
        actions.add_command(label = 'Load Boss Enemy Seed', command=self.load_bunter_seed)
        self.menubar.add_cascade(label = 'Actions', menu=actions)


        # Customize Mode Menu
        customize = Menu(self.menubar, tearoff = False)
        customize.add_command(label = 'Set Latency Timer', command=self.set_latency)
        autodetect_checked = IntVar(value = self.autodetect)
        customize.add_checkbutton(label = 'Include Autodetect', command=self.set_autodetect, variable=autodetect_checked)
        customize.add_command(label = 'Resize Grid', command=self.resize_grid, accelerator="Ctrl+R")
        customize.add_command(label = 'Change Ship Sizes', command=self.ship_setter_window)
        customize.add_command(label = 'Toggle Checks', command=self.check_inclusion_window)
        customize.add_command(label = 'Set Ship Restrictions', command=self.check_restriction_window)
        bingo_check = IntVar(value = self.bingo)
        customize.add_checkbutton(label = 'Bingo Mode', onvalue=1, offvalue=0, command=self.set_bingo, variable=bingo_check)
        self.mystery_check = IntVar(value = self.mystery)
        customize.add_checkbutton(label = 'Mystery Mode', onvalue=1, offvalue=0, command=self.change_mystery_mode, variable=self.mystery_check)
        maze_check = IntVar(value = self.maze)
        customize.add_checkbutton(label = 'Maze Mode', onvalue=1, offvalue=0, command=self.generate_maze_card, variable=maze_check)
        customize.add_command(label = 'Spoil Card', command=self.reveal_card)
        self.menubar.add_cascade(label = 'Customize', menu=customize)


        # Validation Mode Menu
        validations = Menu(self.menubar, tearoff = False)
        validations.add_command(label = 'Validate Your Ships', command=self.validate_self_ships)
        validations.add_command(label = 'Validate Opponent/Shared Ships', command=self.validate_opponent_ships)
        self.menubar.add_cascade(label = "Validate", menu=validations)


        # Visuals Mode Menu
        visuals = Menu(self.menubar, tearoff = False)
        visuals.add_command(label = 'Change Marking Color', command= lambda color_list=[v for v in self.marking_colors.values()]: self.change_marking_colors(color_list))
        visuals.add_command(label = 'Change Icon Style', command=self.set_icon_style)
        fill_checked = IntVar(value = self.fill)
        visuals.add_checkbutton(label = 'Hint Box Filled', onvalue=1, offvalue=0, command=self.set_fill, variable=fill_checked)
        custom_checked = IntVar(value = self.custom_images)
        visuals.add_checkbutton(label = 'Use Custom Images', onvalue=1, offvalue=0, command=self.include_custom_images, variable=custom_checked) #, command=self.set_fill, variable=fill_checked)
        self.menubar.add_cascade(label = "Visuals", menu=visuals)


        # Information Menu
        info = Menu(self.menubar, tearoff=False)
        info.add_command(label = 'Help', command=self.open_help_window, accelerator="Ctrl+H")
        self.menubar.add_cascade(label = 'Info', menu=info)


        # Seedname Display
        self.menubar.add_cascade(label = f'Seedname: {self.seedname}', command=self.copy_seed)


        # Autotracking Display
        self.menubar.add_cascade(label = f"Not tracking.")

        # Autotracking Display
        self.menubar.add_cascade(label = f" ")
        
        self.root.config(menu=self.menubar)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.iconbitmap("img/static/battleships.ico")
        if self.autodetect:
            self.autotracking_timer()
        self.root.mainloop()


    def set_fill(self):
        self.fill = not self.fill
        self.update_tracker_settings(self.fill, value="fill")


    def set_autodetect(self):
        self.autodetect = not self.autodetect
        self.update_tracker_settings(self.autodetect, value="autodetect")
        if self.autodetect:
            self.autotracking_timer()
        else:
            self.kill_autotracking_process()


    def on_closing(self):
        self.x, self.y = self.root.winfo_x(), self.root.winfo_y()
        self.update_tracker_settings((self.x, self.y), value="pos")
        self.kill_autotracking_process()
        self.root.destroy()


    def set_bingo(self):
        self.bingo = not self.bingo
        self.generate_card(self.row_size, self.col_size, self.seedname)


    def set_icon_style(self):
        if self.icons == "televo":
            self.icons = "sonic"
        elif self.icons == "sonic":
            self.icons = "televo"
        self.update_tracker_settings(self.icons, value="icons")
        self.generate_card(self.row_size, self.col_size, self.seedname)


    def set_style(self, name, background, bordercolor, highlightthickness, padding):
        style = ttk.Style(self.frame)
        style.theme_use('alt')
        style.configure(name, background=background, bordercolor=bordercolor, highlightthickness=highlightthickness, padding=padding, relief=SOLID)


    def set_seedname(self, new_seedname, gen_card=False):
        self.seedname = new_seedname
        self.menubar.entryconfig(7, label = f'Seedname: {self.seedname}')
        if gen_card:
            self.generate_card(self.row_size, self.col_size, self.seedname)


    def include_custom_images(self):
        self.custom_images = not self.custom_images
        self.update_tracker_settings(self.custom_images, value="custom")

    
    def has_custom(self, image_name):
        if self.custom_images and image_name in os.listdir('img/custom'):
            return True
        return False


    def reveal_card(self):
        self.width, self.height = self.root.winfo_width(), self.root.winfo_height()
        current_width = int(self.width / (self.col_size*self.scaling_factor))
        current_height = int(self.height / (self.row_size*self.scaling_factor))
        for row_index in range(self.row_size):
            for col_index in range(self.col_size):
                self.image_dict[(row_index, col_index)] = ImageTk.PhotoImage(self.used_images[row_index*self.col_size + col_index].resize((current_width, current_height)))
                self.button_dict[(row_index, col_index)].configure(image = self.image_dict[(row_index, col_index)])
                self.button_dict[(row_index, col_index)].image = self.image_dict[(row_index, col_index)]


    def set_fog_of_war(self, entries, window):

        # user hit "Apply and Generate New Card" with mystery directions so we can check the option in the Customize menu
        self.mystery_check.set(1)
        directions = ["N", "E", "W", "S", "NE", "NW", "SW", "SE"]
        # directions and span
        self.mystery = [directions[i] for i in range(len(entries) - 1) if entries[i + 1].instate(["selected"])], entries[len(entries)].get()
        window.destroy()
        # alter the seed but keep it consistent
        seedname_list = list(self.seedname)
        for i in range(len(self.seedname)):
            seedname_list[len(self.check_names[i]) % len(self.seedname)] = str((len(self.check_names[i]) - len(self.check_names[i + 1])) % 7)
        self.set_seedname("".join(seedname_list))
        self.generate_card(self.row_size, self.col_size, self.seedname, mystery=self.mystery, maze=self.maze)


    def change_mystery_mode(self):

        # since we have a popup menu, don't check mystery mode since the user may X out of it and remain in non-mystery mode
        self.mystery_check.set(0)

        if self.mystery:
            self.mystery = False
            self.generate_card(self.row_size, self.col_size, mystery=self.mystery, maze=self.maze)
            return None

        window = Tk() 
        window.title("Mystery Mode Settings")

        window.geometry("300x220")

        directions = ["N", "E", "W", "S", "NE", "NW", "SW", "SE"]

        labels = {}
        entries = {}

        for i in range(1, 9):

            labels[i] = ttk.Label(window, text = f"{directions[i - 1]}")
            labels[i].grid(row = i, column = 0)
            entries[i] = ttk.Checkbutton(window, cursor=None)
            entries[i].state(["!alternate"])
            if hasattr(self, 'directions'):
                entries[i].state(["!selected"])
                if self.directions[i - 1]:
                  entries[i].state(["selected"])  
            else:
                entries[i].state(["selected"])
            entries[i].grid(row = i, column = 1)

        labels[i+1] = ttk.Label(window, text = "Span")
        labels[i+1].grid(row = i + 1, column = 0)
        entries[i+1] = ttk.Entry(window, width = 5)
        entries[i+1].insert(0, 1)
        entries[i+1].grid(row = i + 1, column = 1)

        btn1 = ttk.Button(window, text = "Apply and Generate New Card", command = lambda: self.set_fog_of_war(entries, window))
        btn1.grid(row = i+2, column = 1)


    def update_tracker_settings(self, new_data, value=None):
        with open("tracker_settings.txt", "w") as f:
            f.write(f"self.icons = '{new_data}'\n" if value == "icons" else f"self.icons = '{self.icons}'\n")
            f.write(f"self.marking_colors = '{new_data}'\n" if value == "colors" else f"self.marking_colors = {self.marking_colors}\n")
            f.write(f"self.width = '{new_data[0]}'\n" if value == "dim" else f"self.width = {self.width}\n")
            f.write(f"self.height = '{new_data[1]}'\n" if value == "dim" else f"self.height = {self.height}\n")
            f.write(f"self.x = '{new_data[0]}'\n" if value == "pos" else f"self.x = {self.x}\n")
            f.write(f"self.y = '{new_data[1]}'\n" if value == "pos" else f"self.y = {self.y}\n")
            f.write(f"self.fill = '{new_data}'\n" if value == "fill" else f"self.fill = {self.fill}\n")
            f.write(f"self.custom_images = '{new_data}'\n" if value == "custom" else f"self.custom_images = {self.custom_images}\n")
            f.write(f"self.autodetect = '{new_data}'\n" if value == "autodetect" else f"self.autodetect = {self.autodetect}\n")
            f.write(f"self.directions = '{new_data}'\n" if value == "directions" else f"self.directions = {self.directions}\n")
        if hasattr(self, "preset_name") and value == "dim":
            try:
                with open(f"presets/{self.preset_name}", "r") as p:
                    preset_content = p.readlines()
                preset_content[-2] = f"self.width = {new_data[0]}\n"
                preset_content[-1] = f"self.height = {new_data[1]}\n"
                with open(f"presets/{self.preset_name}", "w") as p:
                    p.writelines(preset_content)
            except FileNotFoundError:
                pass

    def change_marking_colors(self, color_list = ["white"]):

        if len(color_list) < self.color_types:
            color_list += ["white"] * (self.color_types-len(color_list))

        window = Tk() 
        window.title("Color Settings")
        window.geometry("250x210")

        window_x, window_y, window_width, window_height = self.root.winfo_rootx(), self.root.winfo_rooty(), self.root.winfo_width(), self.root.winfo_height()
        self.root.update_idletasks()
        popup_width, popup_height = window.winfo_width(), window.winfo_height()
        window.geometry(f"+{window_x + window_width//2 - 43 * popup_width//80}+{window_y + window_height//2 - popup_height//2 - 3 * popup_height//10}")

        TitleLabel = ttk.Label(window, text = "Mode")
        TitleLabel.grid(row = 0, column = 1)

        labels = {}
        entries = {}

        modes = ["Marking Color", "Annotating Color", "Battleship Miss", "Battleship Hit", "Battleship Sink", "Bingo (Bunter)"]

        def change_color(i, modes = modes, color_list=color_list):
            colors = askcolor(title="Tkinter Color Chooser", initialcolor=self.marking_colors[modes[i - 1]])
            # only change the color if the OK button is clicked
            if colors[1] is not None:
                color_list[i - 1] = colors[1]
                self.marking_colors[modes[i - 1]] = colors[1]
                self.update_tracker_settings(self.marking_colors, value="colors")
            # write the color dict to tracker settings line 2
            window.destroy()
            self.change_marking_colors(color_list)

        for i in range(1, len(modes) + 1):

            labels[i] = ttk.Label(window, text = modes[i - 1], anchor='w', takefocus=False)
            labels[i].grid(row = i, column = 0)

            # have the colors be the default from tracker settings
            new_style = ttk.Style(window)
            new_style.theme_use('alt')
            new_style.configure(f"settings{i}.TButton", background = color_list[i - 1])
            entries[i] = ttk.Button(window, style = f"settings{i}.TButton", cursor=None, command=lambda i=i: change_color(i))
            entries[i].configure(width=5) # can we change the height?
            entries[i].grid(row = i, column = 1)

        btn0 = ttk.Button(window, text = "Restore to Default Colors", command = lambda window=window: self.restore_default_colors(window))
        btn0.grid(row = i+1, column = 0) 

        btn1 = ttk.Button(window, text = "Submit Toggles", command = lambda window=window: self.set_marking_colors(window))
        btn1.grid(row = i+1, column = 1)

        # self.generate_card(self.row_size, self.col_size, self.seedname)

    def restore_default_colors(self, window):
        self.marking_colors = {"Marking Color": "green", 'Annotating Color': '#FFAC1C', "Battleship Miss": "#0077be", "Battleship Hit": "red", "Battleship Sink": "pink", "Bingo (Bunter)": "purple"}
        self.update_tracker_settings(self.marking_colors, value="colors")
        window.destroy()
        self.change_marking_colors([v for v in self.marking_colors.values()])


    def set_marking_colors(self, window):
        window.destroy()

    
    def set_latency(self):
        try:
            self.latency = 1000 * int(simpledialog.askstring(title="Latency Timer", prompt="Set Latency to: ", initialvalue=2))
        except TypeError or ValueError:
            window_x, window_y, window_width, window_height = self.root.winfo_rootx(), self.root.winfo_rooty(), self.root.winfo_width(), self.root.winfo_height()
            popup = Tk()
            popup.iconbitmap("img/static/warning.ico")
            popup.wm_title("ERROR!")
            popup.geometry("281x70")
            self.root.update_idletasks()
            popup_width, popup_height = popup.winfo_width(), popup.winfo_height()
            popup.geometry(f"+{window_x + window_width//2 - 43 * popup_width//80}+{window_y + window_height//2 - popup_height//2 - 7 * popup_height//10}")
            label = ttk.Label(popup, text='ERROR: Please set your latency to an integer value.')
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Okay", command = lambda: popup.destroy())
            B1.pack()


    def place_ship(self, x, y, event=None):
        self.place_grid[x,y] = 1 - self.place_grid[x,y]
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
                            if ((x * self.col_size + (y + i)) < len(self.labels)) and (self.labels[x * self.col_size + (y + i)] in self.restrictions.keys()):
                                if restrictions_tracker[self.labels[x * self.col_size + (y + i)]] + 1 > self.restrictions[self.labels[x * self.col_size + (y + i)]]:
                                    break
                    # place the ship if possible
                    else:
                        valid_placement = True
                        for i in range(current_random_ship):
                            placed_ships[x, y + i] = 1
                            if hasattr(self, 'restrictions') and (self.labels[x * self.col_size + (y + i)] in self.restrictions.keys()):
                                restrictions_tracker[self.labels[x * self.col_size + (y + i)]] += 1
                if direction == "down":
                    # check that you can place the ship
                    for i in range(current_random_ship):
                        if (x + i, y) not in possible_ship_heads:
                            break
                        if hasattr(self, 'restrictions'):
                            if (((x + i) * self.col_size + y) < len(self.labels)) and (self.labels[(x + i) * self.col_size + y] in self.restrictions.keys()):
                                if restrictions_tracker[self.labels[(x + i) * self.col_size + y]] + 1 > self.restrictions[self.labels[(x + i) * self.col_size + y]]:
                                    break
                    else:
                        valid_placement = True
                        for i in range(current_random_ship):
                            placed_ships[x + i, y] = 1
                            if hasattr(self, 'restrictions') and (self.labels[(x + i) * self.col_size + y] in self.restrictions.keys()):
                                restrictions_tracker[self.labels[(x + i) * self.col_size + y]] += 1

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


    def download_ship_layout(self, event=None, key = b'7RiMHser-GrCxgcWMJ0HoOxjF_Sww5_RORHnyH-Dp50='):
        try:
            os.makedirs('ships')
        except FileExistsError:
            pass
        fernet = Fernet(key)
        encrypted_ships = fernet.encrypt(str(self.place_grid.tolist()).encode())
        np.savetxt("ships/ships.txt", self.place_grid, fmt='%s')
        with open("ships/encrypted_ships.txt", "wb") as f:
            f.write(encrypted_ships)
        subprocess.Popen(r'explorer /open,"."')
        


    def upload_ship_layout(self, same_board=False, key = b'7RiMHser-GrCxgcWMJ0HoOxjF_Sww5_RORHnyH-Dp50=', event=None):

        # if you're uploading a manually placed board
        if not same_board:

            # get opponent's encrypted ships
            filename = fd.askopenfilename()
        
            # load opponent ships
            # CHANGE IT SO THAT YOU LOAD IN THE encrypted txt and not the zip!
            fernet = Fernet(key)
            with open(filename, "rb") as opponent_file:
                encrypted_opponent_ships = opponent_file.read()
            # decrypt opponent ships
            opponent_ships = np.array(ast.literal_eval(fernet.decrypt(encrypted_opponent_ships).decode()))

            # load your ships
            your_ships = np.loadtxt('ships/ships.txt')

        # if you're using a prebuilt randomly generated board
        else:

            opponent_ships = self.generate_same_board(self.row_size, self.col_size)

        # load new board if there are ships to be hit
        window_x, window_y, window_width, window_height = self.root.winfo_rootx(), self.root.winfo_rooty(), self.root.winfo_width(), self.root.winfo_height()
        popup = Tk()
        if np.sum(opponent_ships) == 0:
            popup.iconbitmap("img/static/warning.ico")
            popup.wm_title("WARNING!")
            popup.geometry("530x80")
            self.root.update_idletasks()
            popup_width, popup_height = popup.winfo_width(), popup.winfo_height()
            popup.geometry(f"+{window_x + window_width//2 - 43 * popup_width//80}+{window_y + window_height//2 - popup_height//2 - 7 * popup_height//10}")
            label = ttk.Label(popup, text='WARNING: The zip file of the ship layouts has only misses. \n                     Double check that you uploaded the right zip and that your opponent sent the right file.')
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Okay", command = lambda: popup.destroy())
            B1.pack()
        else:
            popup.iconbitmap("img/static/success.ico")
            popup.wm_title("Success!")
            popup.geometry("155x70")
            self.root.update_idletasks()
            popup_width, popup_height = popup.winfo_width(), popup.winfo_height()
            popup.geometry(f"+{window_x + window_width//2 - 43 * popup_width//80}+{window_y + window_height//2 - popup_height//2 - 7 * popup_height//10}")
            label = ttk.Label(popup, text='Ships successfully loaded! :-)')
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Okay", command = lambda: popup.destroy())
            B1.pack()

        
        # remove opponent ships file to avoid cheating
        if os.path.exists('ships.txt'):
            os.remove('ships.txt')

        self.opponent_ships_with_ids = self.find_ships(opponent_ships)
        self.ships_left = list(range(1, int(np.max(self.opponent_ships_with_ids)) + 1))

        for x in range(self.row_size):
            for y in range(self.col_size):
                hit_or_miss_color = self.marking_colors["Battleship Hit"] if opponent_ships[x,y] == 1 else self.marking_colors["Battleship Miss"]
                if not same_board:
                    # #099125
                    border_color = "#22bb41" if your_ships[x][y] == 1 else "#333333"
                    border_width = 20 if your_ships[x][y] == 1 else 10
                else:
                    border_color = "#333333"
                    border_width = 10
                self.set_style(f"bloaded{x}{y}.TButton", background="black", bordercolor=border_color, highlightthickness=border_width, padding=0)
                self.button_dict[(x,y)].configure(style=f"bloaded{x}{y}.TButton", command = lambda row_index=x, col_index=y, hit_or_miss_color=hit_or_miss_color, current_border_color=border_color:
                                                                               self.change_button_color("black", hit_or_miss_color, row_index, col_index, current_border_color, False))


    def autotracking(self):

        self.auto_detect_counter += 1
        
        if self.auto_detect_counter == 10:
            self.auto_detect_counter = 0
            if not self.detect_game():
                if self.autodetect:
                    self.autotracking_timer()
                return

        key_list = list(self.autotracking_labels.keys())
        val_list = list(self.autotracking_labels.values())

        # read txt
        if os.path.exists('checks.txt'):
            with open("checks.txt") as checks_from_DAs_tracker:
                important_checks_found = checks_from_DAs_tracker.read().splitlines()
            # check if any new checks were collected
            new_checks = list(set(important_checks_found) - set(self.important_checks_recorded))
            # invoke the appropriate button
            for new_check in new_checks:
                self.important_checks_recorded.append(new_check)
                # if boss enemy has been invoked...
                if hasattr(self, 'replacements'):

                    # in (original) boss enemy we don't want to track Future Pete
                    if new_check == "Pete" and self.preset_name == "boss_enemy_bingo.txt":
                        continue
                    # in (original) boss enemy we don't want to track Armored Xemnas 2
                    if new_check == "ArmoredXemnas2" and self.preset_name == "boss_enemy_bingo.txt":
                        new_check = "ArmoredXemnas1"
                    # reveal final fights if Xemnas is defeated
                    if new_check == "Xemnas":
                        for fight in ["ArmoredXemnas1", "ArmoredXemnas2", "FinalXemnas"]:
                            try:
                                fight_key = key_list[val_list.index(self.replacements[fight])]
                                self.set_style(f"bbossfound{fight_key[0]}{fight_key[1]}.TButton", background = ttk.Style().lookup(f"bnormal{fight_key[0]}{fight_key[1]}.TButton", 'background'), bordercolor='#FF69B4', highlightthickness=10, padding=0)
                                ff_image = ImageTk.PhotoImage(self.used_images[fight_key[0]*self.col_size + fight_key[1]])
                                self.button_dict[fight_key].configure(image = ff_image)
                                self.button_dict[fight_key].image = ff_image
                                self.button_dict[fight_key].configure(style=f"bbossfound{fight_key[0]}{fight_key[1]}.TButton")
                                current_width = int(self.width / (self.col_size*self.scaling_factor))
                                current_height = int(self.height / (self.row_size*self.scaling_factor))
                                main_boss_photo = Image.open(f'img/{"custom" if self.has_custom(self.replacements[fight] + ".webp") else self.icons}/{self.replacements[fight]}.webp').resize((current_width, current_height)).convert('RGBA')
                                background = Image.new('RGBA', main_boss_photo.size, (255, 0, 0, 0))
                                paste_x, paste_y = main_boss_photo.size[0]//3, main_boss_photo.size[1]//3
                                arena_boss_photo = Image.open(f'img/{"custom" if self.has_custom(fight + ".webp") else self.icons}/{fight}.webp').convert('RGBA')
                                arena_boss_photo = arena_boss_photo.resize((paste_x, paste_y))
                                if self.fill:
                                    arena_white_background = Image.new("RGBA", arena_boss_photo.size, "WHITE")
                                    arena_white_background.paste(arena_boss_photo, (0,0), arena_boss_photo)
                                    arena_boss_photo = arena_white_background
                                index_x, index_y = fight_key[0], fight_key[1]
                                hinted_border_color = "white"
                                border = (max(1, self.width//250), max(1, self.width//250), max(1, self.height//250), self.height//250)
                                background.paste(main_boss_photo, (0,0), mask = main_boss_photo)
                                arena_boss_photo = ImageOps.expand(arena_boss_photo, border=border, fill=hinted_border_color)
                                background.paste(arena_boss_photo, (paste_x * 19 // 10, 0), mask = arena_boss_photo)
                                self.used_images[index_x*self.col_size + index_y] = background.resize((current_width, current_height))
                                hinted_image = ImageTk.PhotoImage(self.used_images[index_x*self.col_size + index_y])
                                self.button_dict[(index_x, index_y)].configure(image = hinted_image)
                                self.button_dict[(index_x, index_y)].image = hinted_image
                            except ValueError:
                                pass
                    # if a report is found and is a hint for bunter, change the tracker
                    # try:
                    #     # this could be placed in its own function but it doesn't change functionality too much
                    #     if new_check in self.hints.keys():
                    #         if "unchanged" in self.hints[new_check]:
                    #             orig_boss = replacement_boss = self.hints[new_check].split("is")[0]
                    #         else:
                    #             orig_boss, replacement_boss = self.hints[new_check].split("became")
                    #         orig_boss = boss_str_reformat(orig_boss, 'original', images = True)
                    #         replacement_boss = boss_str_reformat(replacement_boss, 'replacement', images = True)
                    #         # the try block applies to this b/c we only want the hint to apply if the replacement boss is on the tracker
                    #         hint_button_key = key_list[val_list.index(replacement_boss)]
                    #         current_width = int(self.width / (self.col_size*self.scaling_factor))
                    #         current_height = int(self.height / (self.row_size*self.scaling_factor))
                    #         main_boss_photo = Image.open(f'img/{"custom" if self.has_custom(replacement_boss + ".webp") else self.icons}/{replacement_boss}.webp').resize((current_width, current_height)).convert('RGBA')
                    #         background = Image.new('RGBA', main_boss_photo.size, (255, 0, 0, 0))
                    #         paste_x, paste_y = main_boss_photo.size[0]//3, main_boss_photo.size[1]//3
                    #         arena_boss_photo = Image.open(f'img/{"custom" if self.has_custom(orig_boss + ".webp") else self.icons}/{orig_boss}.webp').convert('RGBA')
                    #         arena_boss_photo = arena_boss_photo.resize((paste_x, paste_y))
                    #         if self.fill:
                    #             arena_white_background = Image.new("RGBA", arena_boss_photo.size, "WHITE")
                    #             arena_white_background.paste(arena_boss_photo, (0,0), arena_boss_photo)
                    #             arena_boss_photo = arena_white_background
                    #         index_x, index_y = hint_button_key[0], hint_button_key[1]
                    #         hinted_border_color = "white"
                    #         border = (max(1, self.width//250), max(1, self.width//250), max(1, self.height//250), self.height//250)
                    #         background.paste(main_boss_photo, (0,0), mask = main_boss_photo)
                    #         arena_boss_photo = ImageOps.expand(arena_boss_photo, border=border, fill=hinted_border_color)
                    #         if replacement_boss == "ArmoredXemnas1":
                    #             if self.armored_xemnas_hinted:
                    #                 # DOES THE IMAGE REALLY NEED TO BE SAVED AND REOPENED?
                    #                 background.paste(arena_boss_photo, (0, 0), mask = arena_boss_photo)
                    #                 background.save('temp.png')
                    #                 old_arena_boss_photo = Image.open(f'img/{"custom" if self.has_custom(self.first_boss_hint + ".webp") else self.icons}/{self.first_boss_hint}.webp').convert('RGBA')
                    #                 old_arena_boss_photo = old_arena_boss_photo.resize((paste_x, paste_y))
                    #                 if self.fill:
                    #                     old_arena_white_background = Image.new("RGBA", old_arena_boss_photo.size, "WHITE")
                    #                     old_arena_white_background.paste(old_arena_boss_photo, (0,0), old_arena_boss_photo)
                    #                     old_arena_boss_photo = old_arena_white_background
                    #                 old_arena_boss_photo = ImageOps.expand(old_arena_boss_photo, border=border, fill=hinted_border_color)
                    #                 background = Image.open('temp.png')
                    #                 background.paste(old_arena_boss_photo, (paste_x * 19 // 10, 0), mask = old_arena_boss_photo)
                    #                 os.remove('temp.png')
                    #             else:
                    #                 self.armored_xemnas_hinted = True
                    #                 self.first_boss_hint = orig_boss
                    #                 background.paste(arena_boss_photo, (paste_x * 19 // 10, 0), mask = arena_boss_photo)
                    #         else:
                    #             background.paste(arena_boss_photo, (paste_x * 19 // 10, 0), mask = arena_boss_photo)
                    #         self.used_images[index_x*self.col_size + index_y] = background.resize((current_width, current_height))
                    #         hinted_image = ImageTk.PhotoImage(self.used_images[index_x*self.col_size + index_y])
                    #         self.button_dict[(index_x, index_y)].configure(image = hinted_image)
                    #         self.button_dict[(index_x, index_y)].image = hinted_image
                    # except:
                    #     pass
                    # try to get the randomized boss instead of the vanilla boss
                    new_check = self.replacements.get(new_check, new_check)
                # if boss enemy isn't invoked, PeteTR is the real Pete
                else:
                    if new_check == "PeteTR":
                        new_check = "Pete"
                # don't want to invoke armored xemnas twice to go back to unmarked
                if (new_check == "ArmoredXemnas1"):
                    if self.armored_xemnas_found:
                        continue
                    else:
                        self.armored_xemnas_found = True
                # invoke button if it's possible
                try:
                    button_key = key_list[val_list.index(new_check)]
                    self.button_dict[button_key].invoke()
                    if hasattr(self, "last_found_check") and len(new_checks) != 0:
                        if ttk.Style().lookup(f"bbingo{self.last_found_check[0]}{self.last_found_check[1]}.TButton", 'background') != self.marking_colors["Bingo (Bunter)"]:
                            self.set_style(f"bclicked{self.last_found_check[0]}{self.last_found_check[1]}.TButton", background = ttk.Style().lookup(f"bclicked{self.last_found_check[0]}{self.last_found_check[1]}.TButton", 'background'), bordercolor=ttk.Style().lookup(f"bclicked{self.last_found_check[0]}{self.last_found_check[1]}.TButton", 'bordercolor'), highlightthickness=10, padding=0)
                            self.button_dict[self.last_found_check].configure(style=f"bclicked{self.last_found_check[0]}{self.last_found_check[1]}.TButton")
                        else:
                            self.set_style(f"bbingo{self.last_found_check[0]}{self.last_found_check[1]}.TButton", background = ttk.Style().lookup(f"bbingo{self.last_found_check[0]}{self.last_found_check[1]}.TButton", 'background'), bordercolor=ttk.Style().lookup(f"bbingo{self.last_found_check[0]}{self.last_found_check[1]}.TButton", 'bordercolor'), highlightthickness=10, padding=0)
                            self.button_dict[self.last_found_check].configure(style=f"bbingo{self.last_found_check[0]}{self.last_found_check[1]}.TButton")                            
                except ValueError:
                    pass
            try:
                if ttk.Style().lookup(f"bbingo{button_key[0]}{button_key[1]}.TButton", 'background') != self.marking_colors["Bingo (Bunter)"]:
                    self.set_style(f"bmostrecentlyfound{button_key[0]}{button_key[1]}.TButton", background = ttk.Style().lookup(f"bclicked{button_key[0]}{button_key[1]}.TButton", 'background'), bordercolor="yellow", highlightthickness=50, padding=0)
                else:
                    self.set_style(f"bmostrecentlyfound{button_key[0]}{button_key[1]}.TButton", background = ttk.Style().lookup(f"bbingo{button_key[0]}{button_key[1]}.TButton", 'background'), bordercolor="yellow", highlightthickness=50, padding=0)
                self.button_dict[button_key].configure(style=f"bmostrecentlyfound{button_key[0]}{button_key[1]}.TButton")
                self.last_found_check = button_key

            except UnboundLocalError:
                pass

        # read found bosses
        # happens AFTER b/c we don't want to create the mostrecentlyfound check for a boss that hasn't been beaten yet
        if os.path.exists('seenbosses.txt') and not self.mystery:
            with open("seenbosses.txt") as seenbosses_from_DAs_tracker:
                seen_bosses = seenbosses_from_DAs_tracker.read().splitlines()
            # check if any new bosses were seen
            new_bosses = list(set(seen_bosses) - set(self.seen_bosses_recorded))
            for new_boss in new_bosses:
                if new_boss in self.important_checks_recorded:
                    continue
                self.seen_bosses_recorded.append(new_boss)

                # if boss enemy has been invoked...
                if hasattr(self, 'replacements'):

                    # in (original) boss enemy we don't want to track Future Pete
                    if new_boss == "Pete" and self.preset_name == "boss_enemy_bingo.txt":
                        continue
                    # in (original) boss enemy we don't want to track Armored Xemnas 2
                    if new_boss == "ArmoredXemnas2" and self.preset_name == "boss_enemy_bingo.txt":
                        new_boss = "ArmoredXemnas1"

                    # try to get the randomized boss instead of the vanilla boss
                    new_boss = self.replacements.get(new_boss, new_boss)

                # if boss enemy isn't invoked, PeteTR is the real Pete
                else:
                    if new_boss == "PeteTR":
                        new_boss = "Pete"

                # don't want to invoke armored xemnas twice to go back to unmarked
                if (new_boss == "ArmoredXemnas1"):
                    if self.armored_xemnas_found:
                        continue
                    if not self.armored_xemnas_seen:
                        self.armored_xemnas_seen = True
                # invoke button if it's possible
                try:
                    button_key = key_list[val_list.index(new_boss)]
                    self.set_style(f"bbossfound{button_key[0]}{button_key[1]}.TButton", background = ttk.Style().lookup(f"bnormal{button_key[0]}{button_key[1]}.TButton", 'background'), bordercolor='blue', highlightthickness=10, padding=0)
                    self.button_dict[button_key].configure(style=f"bbossfound{button_key[0]}{button_key[1]}.TButton", borderwidth=25)
                except ValueError:
                    pass
    
        self.root.after(self.latency, self.autotracking)
        

    
    def kill_autotracking_process(self):
        if hasattr(self, 'autotracking_process'):
            self.autotracking_process.kill()
            if os.path.exists('checks.txt'):
                os.remove('checks.txt')


    def detect_game(self):
        detection = False
        for process in psutil.process_iter():
            if process.name() in ["KINGDOM HEARTS II FINAL MIX.exe", "pcsx2.exe"]:
                detection = True
        return detection


    def autotracking_timer(self):

        self.kill_autotracking_process()
        if hasattr(self, 'preset_name') and self.preset_name == "hitlist.txt":
            # run hitlist autotracker instead of vanilla
            self.autotracking_process = subprocess.Popen(os.path.join('autotracker', 'HitlistAutotracker', 'HitlistTrackerLogic.exe'), creationflags = subprocess.CREATE_NO_WINDOW)
        else:
            # run normal autotracker
            self.autotracking_process = subprocess.Popen(os.path.join('autotracker', 'Autotracker', 'BattleshipTrackerLogic.exe'), creationflags = subprocess.CREATE_NO_WINDOW)

        detection = self.detect_game()

        if detection:
            self.menubar.entryconfig(8, label = f'Autotracking!')
            self.root.after(self.latency, self.autotracking)
        else:
            self.root.after(7500, self.autotracking_timer)
            self.menubar.entryconfig(8, label = f'Not tracking.')


    def resize_image(self, event):
        self.width, self.height = self.root.winfo_width(), self.root.winfo_height()
        new_width = int(self.width / (self.col_size*self.scaling_factor))
        new_height = int(self.height / (self.row_size*self.scaling_factor))
        self.update_tracker_settings((self.width, self.height), value="dim")
        self.x, self.y = self.root.winfo_x(), self.root.winfo_y()
        self.update_tracker_settings((self.x, self.y), value="pos")
        self.image_dict = {}
        for row_index in range(self.row_size):
            for col_index in range(self.col_size):
                self.image_dict[(row_index, col_index)] = ImageTk.PhotoImage(self.used_images[row_index*self.col_size + col_index].resize((new_width, new_height)))
                if not self.blind:
                    if (not self.mystery or self.checks_found[row_index, col_index] == 1 or self.checks_revealed[row_index, col_index] == 1):
                        self.button_dict[(row_index, col_index)].configure(image = self.image_dict[(row_index, col_index)])
                        self.button_dict[(row_index, col_index)].image = self.image_dict[(row_index, col_index)]
                    else:
                        black_background = ImageTk.PhotoImage(Image.open('img/static/black.png').resize((new_width, new_height)))
                        self.button_dict[(row_index, col_index)].configure(image = black_background)
                        self.button_dict[(row_index, col_index)].image = black_background
        with open("previous_preset.txt", "w") as preset_size_save:
            preset_size_save.write(f"self.valid_checks = {self.valid_checks}\n")
            preset_size_save.write(f"self.row_size, self.col_size = {self.row_size}, {self.col_size}\n")
            if self.bingo:
                preset_size_save.write(f"self.bingo = {self.bingo}\n")
            preset_size_save.write(f"self.width = {self.width}\n")
            preset_size_save.write(f"self.height = {self.height}\n")
            if hasattr(self, "preset_name") and self.preset_name in os.listdir("presets"):
                preset_size_save.write(f"self.preset_name = '{self.preset_name}'")


    def display_edges(self, row_index, col_index):
        # add padding to display edges on unrevealed cells
        if self.button_dict.get((row_index - 1, col_index)) is not None and ((row_index - 1, col_index), (row_index, col_index)) in self.edges:
            self.padding_dict[(row_index - 1, col_index)][3] = 3
            pady = (self.padding_dict[(row_index - 1, col_index)][0], self.padding_dict[(row_index - 1, col_index)][3])
            self.button_dict[(row_index - 1, col_index)].grid(row=row_index - 1, column=col_index, pady=pady, sticky="nwes")

        if self.button_dict.get((row_index + 1, col_index)) is not None and ((row_index, col_index), (row_index + 1, col_index)) in self.edges:
            self.padding_dict[(row_index + 1, col_index)][0] = 3
            pady = (self.padding_dict[(row_index + 1, col_index)][0], self.padding_dict[(row_index + 1, col_index)][3])
            self.button_dict.get((row_index + 1, col_index)).grid(row=row_index + 1, column=col_index, pady=pady, sticky="nwes")

        if self.button_dict.get((row_index, col_index - 1)) is not None and ((row_index, col_index - 1), (row_index, col_index)) in self.edges:
            self.padding_dict[(row_index, col_index - 1)][2] = 3
            padx = (self.padding_dict[(row_index, col_index - 1)][1], self.padding_dict[(row_index, col_index - 1)][2])
            self.button_dict[(row_index, col_index - 1)].grid(row=row_index, column=col_index - 1, padx=padx, sticky="nwes")
            
        if self.button_dict.get((row_index, col_index + 1)) is not None and ((row_index, col_index), (row_index, col_index + 1)) in self.edges:
            self.padding_dict[(row_index, col_index + 1)][1] = 3
            padx = (self.padding_dict[(row_index, col_index + 1)][1], self.padding_dict[(row_index, col_index + 1)][2])
            self.button_dict[(row_index, col_index + 1)].grid(row=row_index, column=col_index + 1, padx=padx, sticky="nwes")
        

    def display_maze(self, row_index, col_index, mystery=False):
        neighbors = self.neighbor_dict[(row_index, col_index)]
        edge_sides = ""
        # get neighboring edges
        possible_edges = [min([((row_index, col_index), x), (x, (row_index, col_index))], key = lambda k: (k[0], k[1])) for x in neighbors]
        # add exterior edges
        # print((row_index, col_index))
        for possible_edge in possible_edges:
            if possible_edge in self.edges:
                if possible_edge[0][0] < row_index or row_index == 0:
                    edge_sides += "n"
                if possible_edge[1][0] > row_index or row_index == self.row_size - 1:
                    edge_sides += "s"
                if possible_edge[0][1] < col_index or col_index == 0:
                    edge_sides += "w"
                if possible_edge[1][1] > col_index or col_index == self.col_size - 1:
                    edge_sides += "e"
        if mystery:
            self.display_edges(row_index, col_index)
            self.display_edges(row_index - 1, col_index)
            self.display_edges(row_index + 1, col_index)
            self.display_edges(row_index, col_index - 1)
            self.display_edges(row_index, col_index + 1)
        padx = (6 if col_index == 0 else 3 if "w" in edge_sides else 0, 6 if col_index == self.col_size - 1 else 3 if "e" in edge_sides else 0)
        pady = (6 if row_index == 0 else 3 if "n" in edge_sides else 0, 6 if row_index == self.row_size - 1 else 3 if "s" in edge_sides else 0)
        self.padding_dict[(row_index, col_index)] = [pady[0], padx[0], padx[1], pady[1]]
        self.button_dict[(row_index, col_index)].grid(row=row_index, column=col_index, padx=padx, pady=pady, sticky="nwes")



    def generate_card(self, row_size, col_size, seedname=None, mystery=False, maze=False, event=None):

        if not self.autodetect:
            self.kill_autotracking_process()

        # reset the autotracker
        if maze:
            self.edges = self.generate_maze()
        if mystery:
            self.checks_revealed = np.zeros((row_size, col_size))
        self.armored_xemnas_hinted = False
        self.armored_xemnas_found = False
        self.armored_xemnas_seen = False
        self.important_checks_recorded = []
        self.seen_bosses_recorded = []
        # remove previous recorded checks and seen bosses
        if os.path.exists('checks.txt'):
            os.remove('checks.txt')
        if os.path.exists('seenbosses.txt'):
            os.remove('seenbosses.txt')

        if hasattr(self, 'autotracking_process'):
            self.autotracking_process.kill()
            if os.path.exists('checks.txt'):
                os.remove('checks.txt')
        if hasattr(self, 'menubar'):
            if not self.autodetect:
                self.menubar.entryconfig(8, label = f'Not tracking.')
            else:
                self.autotracking_timer()
        self.checks_found = np.zeros((row_size, col_size))
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.geometry(f"+{self.x}+{self.y}")
        Grid.rowconfigure(self.root, 0, weight=1)
        Grid.columnconfigure(self.root, 0, weight=1)

        # get the appropraite checks
        if seedname is None:
            if hasattr(self, 'menubar'):
                self.set_seedname(''.join(random.choice(string.ascii_letters) for _ in range(6)))
            else:
                self.seedname = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        self.check_names = [x for x in os.listdir(f"img/{self.icons}")]
        if hasattr(self, 'valid_checks'):
            self.check_names = [x for (x, include) in zip(self.check_names, self.valid_checks) if include]

        # set the randomization based on seedname
        random.Random(self.seedname).shuffle(self.check_names)
        
        # setup images
        self.raw_images = [Image.open(f'img/{"custom" if self.has_custom(check) else self.icons}/{check}').resize((int(self.width / (self.col_size*self.scaling_factor)), int(self.height / (self.row_size*self.scaling_factor)))) for check in self.check_names]
        if hasattr(self, "preset_name"):
            if self.preset_name == "hitlist.txt" and "Axel2.webp" in self.check_names:
                self.raw_images[self.check_names.index("Axel2.webp")] = Image.open('img/static/Axel2.webp')
            if self.preset_name == "boss_enemy_bingo.txt" and "ArmoredXemnas1.webp" in self.check_names:
                self.raw_images[self.check_names.index("ArmoredXemnas1.webp")] = Image.open('img/static/ArmoredXemnas1.webp')
        self.used_images = deepcopy(self.raw_images)
        self.images = [ImageTk.PhotoImage(used_image) for used_image in self.used_images]
        with open("img.json", "r") as checktypes_json:
            checktypes_dict = json.load(checktypes_json)
            self.labels = [checktypes_dict[check] for check in self.check_names]
        self.place_grid = np.zeros((row_size, col_size))

        #Create & Configure frame 
        self.frame=Frame(self.root)
        self.frame.grid(row=0, column=0, sticky=N+W+E+S)

        self.button_dict = {}
        self.autotracking_labels = {}

        #Create a (rows x columns) grid of buttons inside the frame
        for row_index in range(row_size):
            Grid.rowconfigure(self.frame, row_index, weight=1)
            for col_index in range(col_size):
                Grid.columnconfigure(self.frame, col_index, weight=1)
                # reset all existing styles (important if player generates a new card in the same window session)
                self.set_style(f"bnormal{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=10, padding=0)
                self.set_style(f"bbossfound{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=10, padding=0)
                self.set_style(f"bloaded{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=10, padding=0)
                self.set_style(f"bnoted{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=10, padding=0)
                self.set_style(f"bbingo{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=10, padding=0)
                self.set_style(f"bsunk{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=10, padding=0)
                self.set_style(f"bclicked{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=10, padding=0)
                self.set_style(f"bmostrecentlyfound{row_index}{col_index}.TButton", background="black", bordercolor="#333333", highlightthickness=10, padding=0)
                if not mystery:
                    self.button_dict[(row_index, col_index)] = ttk.Button(self.frame, image = self.images[row_index*self.col_size + col_index], takefocus=False, style=f'bnormal{row_index}{col_index}.TButton')
                    if maze:
                        self.display_maze(row_index, col_index)
                else:
                    black_background = ImageTk.PhotoImage(Image.open('img/static/black.png').resize((int(self.width / (self.col_size*self.scaling_factor)), int(self.height / (self.row_size*self.scaling_factor)))))
                    self.button_dict[(row_index, col_index)] = ttk.Button(self.frame, image = black_background, takefocus=False, style=f'bnormal{row_index}{col_index}.TButton')
                    self.button_dict[(row_index, col_index)].image = black_background

                if maze:
                    if (row_index, col_index) == (0,0):
                        self.set_style(f"bnormal{row_index}{col_index}.TButton", background="black", bordercolor="red", highlightthickness=10, padding=0)
                    elif (row_index, col_index) == (self.row_size - 1, self.col_size - 1):
                        self.set_style(f"bnormal{row_index}{col_index}.TButton", background="black", bordercolor="#32CD32", highlightthickness=10, padding=0)
                    padx = self.padding_dict[(row_index, col_index)][1], self.padding_dict[(row_index, col_index)][2]
                    pady = self.padding_dict[(row_index, col_index)][0], self.padding_dict[(row_index, col_index)][3]
                    self.button_dict[(row_index, col_index)].grid(row=row_index, column=col_index, sticky="nwes", padx=padx, pady=pady)
                else:
                    self.button_dict[(row_index, col_index)].grid(row=row_index, column=col_index, sticky="nwes")
                self.button_dict[(row_index, col_index)].configure(command = lambda row_index=row_index, col_index=col_index:
                                                                        self.change_button_color("black", self.marking_colors["Marking Color"], row_index, col_index, "red" if maze and (row_index, col_index) == (0, 0) else "#32CD32" if maze and (row_index, col_index) == (self.row_size - 1, self.col_size - 1) else "#333333", False))
                self.button_dict[(row_index, col_index)].bind('<Button-3>', lambda event, row_index=row_index, col_index=col_index:
                                                                        self.change_button_color("black", self.marking_colors["Annotating Color"], row_index, col_index, "red" if maze and (row_index, col_index) == (0, 0) else "#32CD32" if maze and (row_index, col_index) == (self.row_size - 1, self.col_size - 1) else "#333333", False, right_clicked=True))
                self.autotracking_labels[(row_index, col_index)] = self.check_names[row_index*self.col_size + col_index][:-5]
        
        self.frame.bind("<Configure>", self.resize_image)
        self.root.bind("<FocusIn>", self.resize_image)
        self.root.bind("<FocusOut>", self.resize_image)

        # setup bingo logic if bingo and board is square
        if self.bingo:
            if (row_size != col_size):
                window_x, window_y, window_width, window_height = self.root.winfo_rootx(), self.root.winfo_rooty(), self.root.winfo_width(), self.root.winfo_height()
                popup = Tk()
                popup.iconbitmap("img/static/warning.ico")
                popup.wm_title("WARNING!")
                popup.geometry("347x70")
                self.root.update_idletasks()
                popup_width, popup_height = popup.winfo_width(), popup.winfo_height()
                popup.geometry(f"+{window_x + window_width//2 - 43 * popup_width//80}+{window_y + window_height//2 - popup_height//2 - 7 * popup_height//10}")
                label = ttk.Label(popup, text='Warning: Bingo board must be square. Bingo logic will not work.')
                label.pack(side="top", fill="x", pady=10)
                B1 = ttk.Button(popup, text="Okay", command = lambda: popup.destroy())
                B1.pack()
            else:
                self.possible_bingos = self.identify_bingos(row_size)

        # Made obsolete really... keeping in case it's needed.
        # checks not inlucded = checks too late in the list to be included in the grid + checks removed due to board size changes from restrictions (this is the union)
        # checks_not_included = set(x[:-5] for x in self.check_names[row_size * col_size:]).union(set(x[:-5] for x in os.listdir(f'img/{self.icons}')) - set(x[:-5] for x in self.check_names))
        # print("------------------------------------------------")
        # print("New Card Generation Detected: Checks Removed are")
        # print("------------------------------------------------")
        # [print(removed_check) for removed_check in list(checks_not_included)]
        self.frame.bind("<Configure>", self.resize_image)
        self.root.bind("<FocusIn>", self.resize_image)
        self.root.bind("<FocusOut>", self.resize_image)


    def identify_bingos(self, dimension):
        bingo_arrays = []
        left_diag = np.zeros((dimension, dimension))
        right_diag = np.zeros((dimension, dimension))
        rows = np.zeros((dimension, dimension))
        columns = np.zeros((dimension, dimension))
        for i in range(dimension):
            rows[i] = np.ones(dimension)
            columns[:, i] = np.ones(dimension)
            left_diag[i, i] = 1
            right_diag[i, dimension - i - 1] = 1
            bingo_arrays.append(rows)
            bingo_arrays.append(columns)
            rows = np.zeros((dimension, dimension))
            columns = np.zeros((dimension, dimension))
        bingo_arrays.append(left_diag)
        bingo_arrays.append(right_diag)
        return bingo_arrays


    def generate_all_edges(self, squares):
        # the padding dictionary is used for the combination of mystery mode and maze mode
        self.padding_dict = {}
        edges = set()
        for square in squares:
            horizontal_coords = []
            vertical_coords = []
            left_neighbor_coord = square[1] - 1
            right_neighbor_coord = square[1] + 1
            up_neighbor_coord = square[0] - 1
            down_neighbor_coord = square[0] + 1
            self.padding_dict[square] = [0, 0, 0, 0] #nwes format
            if square[0] == 0:
                self.padding_dict[square][0] = 6
            if square[0] == self.row_size - 1:
                self.padding_dict[square][3] = 6
            if square[1] == 0:
                self.padding_dict[square][1] = 6
            if square[1] == self.col_size - 1:
                self.padding_dict[square][2] = 6 
            if left_neighbor_coord >= 0:
                horizontal_coords.append((square[0], left_neighbor_coord))
            if right_neighbor_coord < self.col_size:
                horizontal_coords.append((square[0], right_neighbor_coord))
            if up_neighbor_coord >= 0 :
                vertical_coords.append((up_neighbor_coord, square[1]))
            if down_neighbor_coord < self.row_size:
                vertical_coords.append((down_neighbor_coord, square[1]))
            neighbors = horizontal_coords + vertical_coords
            edges = edges.union(set([min([(square, x), (x, square)], key = lambda k: (k[0], k[1])) for x in neighbors]))
            self.neighbor_dict[square] = neighbors
        return edges

    # https://stackoverflow.com/questions/48563302/borders-on-some-sides (for visuals)        

    def generate_maze(self):
        self.maze = True
        self.neighbor_dict = {}
        squares = list(it.product(list(range(self.row_size)), list(range(self.col_size))))
        edges = self.generate_all_edges(squares)
        current = (0,0)
        visited = set()
        squares.remove(current)
        while len(visited) != self.row_size * self.col_size:
            visited.add(current)
            new_neighbor = random.choice(self.neighbor_dict.get(current))
            if new_neighbor not in visited:
                edges.discard(min([(current, new_neighbor), (new_neighbor, current)], key = lambda k: (k[0], k[1])))
            current = new_neighbor
        return edges


    def generate_maze_card(self):
        if self.maze:
            self.maze = False
            self.generate_card(self.row_size, self.col_size, mystery=self.mystery, maze=self.maze)
            return None
        self.edges = self.generate_maze()
        self.generate_card(self.row_size, self.col_size, mystery=self.mystery, maze=True)



    def change_button_color(self, current_color, new_color, row_index, col_index, current_border_color, placing_ship=False, event=None, right_clicked=False):
        
        # by default, the new_color should be the marking color
        # change the new_color to be the updated marking color if new_color isn't in marking_colors
        current_colors = list(self.marking_colors.values()) + ["black"] # color settings plus starting color
        if current_color not in current_colors:
            current_color = self.marking_colors["Marking Color"]
        if new_color not in current_colors:
            new_color = self.marking_colors["Marking Color"]

        # don't change button functionality if we're just making notes
        if right_clicked:
            # change the style to annotated
            if hasattr(self, "last_found_check") and self.last_found_check == (row_index, col_index):
                current_border_color = "yellow"
            elif ttk.Style().lookup(f"bbossfound{row_index}{col_index}.TButton", "bordercolor") == "blue" and ttk.Style().lookup(f"bclicked{row_index}{col_index}.TButton", 'background') == "#d9d9d9":
                current_border_color = "blue"
            elif ttk.Style().lookup(f"bnormal{row_index}{col_index}.TButton", "bordercolor") == "red" or ttk.Style().lookup(f"bnormal{row_index}{col_index}.TButton", "bordercolor") == "#32CD32":
                current_border_color = ttk.Style().lookup(f"bnormal{row_index}{col_index}.TButton", "bordercolor")
            elif ttk.Style().lookup(f"bloaded{row_index}{col_index}.TButton", 'bordercolor') == "#22bb41":
                current_border_color = "#22bb41"
            self.set_style(f"bnoted{row_index}{col_index}.TButton", background=new_color, bordercolor=current_border_color, highlightthickness=10, padding=0)
            self.button_dict[(row_index, col_index)].configure(style=f"bnoted{row_index}{col_index}.TButton")
            # figure out what the previous background color was so if we uncheck it the right background shows
            if ttk.Style().lookup(f"bbingo{row_index}{col_index}.TButton", 'background') == self.marking_colors["Bingo (Bunter)"]:
                if new_color == self.marking_colors["Annotating Color"]:
                    current_color = self.marking_colors["Bingo (Bunter)"]
                else:
                    new_color = self.marking_colors["Bingo (Bunter)"]
                self.button_dict[(row_index, col_index)].bind('<Button-3>', lambda event, row_index=row_index, col_index=col_index:
                                                                            self.change_button_color(new_color, current_color, row_index, col_index, "#333333", False, right_clicked=True))
            elif ttk.Style().lookup(f"bsunk{row_index}{col_index}.TButton", 'background') == self.marking_colors["Battleship Sink"]:
                if new_color == self.marking_colors["Annotating Color"]:
                    current_color = self.marking_colors["Battleship Sink"]
                else:
                    new_color = self.marking_colors["Battleship Sink"]
                self.button_dict[(row_index, col_index)].bind('<Button-3>', lambda event, row_index=row_index, col_index=col_index:
                                                                            self.change_button_color(new_color, current_color, row_index, col_index, "#333333", False, right_clicked=True))
            elif ttk.Style().lookup(f"bclicked{row_index}{col_index}.TButton", 'background') == self.marking_colors["Marking Color"]:
                if new_color == self.marking_colors["Annotating Color"]:
                    current_color = self.marking_colors["Marking Color"]
                else:
                    new_color = self.marking_colors["Marking Color"]
                self.button_dict[(row_index, col_index)].bind('<Button-3>', lambda event, row_index=row_index, col_index=col_index:
                                                                            self.change_button_color(new_color, current_color, row_index, col_index, "#333333", False, right_clicked=True))
            elif ttk.Style().lookup(f"bclicked{row_index}{col_index}.TButton", 'background') == self.marking_colors["Battleship Hit"]:
                if new_color == self.marking_colors["Annotating Color"]:
                    current_color = self.marking_colors["Battleship Hit"]
                else:
                    new_color = self.marking_colors["Battleship Hit"]
                self.button_dict[(row_index, col_index)].bind('<Button-3>', lambda event, row_index=row_index, col_index=col_index:
                                                                            self.change_button_color(new_color, current_color, row_index, col_index, "#333333", False, right_clicked=True))
            elif ttk.Style().lookup(f"bclicked{row_index}{col_index}.TButton", 'background') == self.marking_colors["Battleship Miss"]:
                if new_color == self.marking_colors["Annotating Color"]:
                    current_color = self.marking_colors["Battleship Miss"]
                else:
                    new_color = self.marking_colors["Battleship Miss"]
                self.button_dict[(row_index, col_index)].bind('<Button-3>', lambda event, row_index=row_index, col_index=col_index:
                                                                            self.change_button_color(new_color, current_color, row_index, col_index, "#333333", False, right_clicked=True))
            else:
                self.button_dict[(row_index, col_index)].bind('<Button-3>', lambda event, row_index=row_index, col_index=col_index:
                                                                            self.change_button_color(new_color, current_color, row_index, col_index, "#333333", False, right_clicked=True))
        else:
            # place new ship if in place mode
            if placing_ship:
                self.place_ship(row_index, col_index)

            # change button color
            border_color = ttk.Style().lookup(f"bloaded{row_index}{col_index}.TButton", 'bordercolor')
            self.set_style(f"bclicked{row_index}{col_index}.TButton", background=new_color, bordercolor=border_color, highlightthickness=10, padding=0)
            self.button_dict[(row_index, col_index)].configure(style=f"bclicked{row_index}{col_index}.TButton", command = lambda row_index=row_index, col_index=col_index:
                                                                            self.change_button_color(new_color, current_color, row_index, col_index, border_color, placing_ship))

            # reset the annotation behavior
            self.button_dict[(row_index, col_index)].bind('<Button-3>', lambda event, row_index=row_index, col_index=col_index:
                                                                            self.change_button_color(new_color, self.marking_colors["Annotating Color"], row_index, col_index, "#333333", False, right_clicked=True))
            
            if not placing_ship:
                
                # mark as found if it was previously unfound
                if self.checks_found[row_index, col_index] == 0:

                    self.checks_found[row_index, col_index] = 1
                    if self.mystery:
                        self.checks_revealed[row_index, col_index] = 1
                        directions, span = self.mystery[0], int(self.mystery[1])
                        current_width = int(self.root.winfo_width() / (self.col_size*self.scaling_factor))
                        current_height = int(self.root.winfo_height() / (self.row_size*self.scaling_factor))
                        self.image_dict[(row_index, col_index)] = ImageTk.PhotoImage(self.used_images[row_index*self.col_size + col_index].resize((current_width, current_height)))
                        self.button_dict[(row_index, col_index)].configure(image = self.image_dict[(row_index, col_index)])
                        self.button_dict[(row_index, col_index)].image = self.image_dict[(row_index, col_index)]
                        if self.maze:
                            self.display_maze(row_index, col_index, mystery=True)
                        for neighbor in range(1, span + 1):
                            direction_dict = {"N": (-neighbor, 0), "E": (0, neighbor), "W": (0, -neighbor), "S": (neighbor, 0), "NE": (-neighbor, neighbor), "NW": (-neighbor, -neighbor), "SE": (neighbor, neighbor), "SW": (neighbor, -neighbor)}
                            for direction in directions:
                                vert_offset, hori_offset = direction_dict[direction]
                                if row_index + vert_offset in range(0, self.row_size) and col_index + hori_offset in range(0, self.col_size):
                                    neighbor_row_index = row_index + vert_offset
                                    neighbor_col_index = col_index + hori_offset
                                    self.checks_revealed[neighbor_row_index, neighbor_col_index] = 1
                                    self.image_dict[((neighbor_row_index, neighbor_col_index))] = ImageTk.PhotoImage(self.used_images[neighbor_row_index*self.col_size + neighbor_col_index].resize((current_width, current_height)))
                                    self.button_dict[(neighbor_row_index, neighbor_col_index)].configure(image = self.image_dict[((neighbor_row_index, neighbor_col_index))])
                                    self.button_dict[(neighbor_row_index, neighbor_col_index)].image = self.image_dict[((neighbor_row_index, neighbor_col_index))]
                                    if self.maze:
                                        self.display_maze(neighbor_row_index, neighbor_col_index)
                    # check if a bingo has been achieved
                    if self.bingo and self.row_size == self.col_size:
                        for possible_bingo in self.possible_bingos:
                            if np.sum(possible_bingo * self.checks_found) == self.row_size:
                                xs, ys = np.where(possible_bingo == 1)
                                for index_x, index_y in [[xs[i], ys[i]] for i in range(len(xs))]:
                                    self.set_style(f"bbingo{index_x}{index_y}.TButton", background=self.marking_colors["Bingo (Bunter)"], bordercolor=current_border_color, highlightthickness=10, padding=0)
                                    self.button_dict[(index_x, index_y)].configure(style=f"bbingo{index_x}{index_y}.TButton", command = lambda row_index=index_x, col_index=index_y:
                                                                                        self.change_button_color(self.marking_colors["Bingo (Bunter)"], "black", row_index, col_index, current_border_color, placing_ship))
                    
                    # check if boat is sunk and change the button colors to reflect that or if there even are boats to begin with
                    elif hasattr(self, 'ships_left'):
                        for id in self.ships_left:
                            xs, ys = np.where(self.opponent_ships_with_ids == id)
                            if all([value == 1 for value in [self.checks_found[xs[i], ys[i]] for i in range(len(xs))]]):
                                for index_x, index_y in [[xs[i], ys[i]] for i in range(len(xs))]:
                                    border_color = ttk.Style().lookup(f"bloaded{index_x}{index_y}.TButton", 'bordercolor')
                                    self.set_style(f"bsunk{index_x}{index_y}.TButton", background=self.marking_colors["Battleship Sink"], bordercolor=border_color, highlightthickness=10, padding=0)
                                    sunk_background = Image.open(f'img/{"custom" if self.has_custom(self.check_names[self.col_size * index_x + index_y] + ".webp") else self.icons}/{self.check_names[self.col_size * index_x + index_y]}')
                                    sunk_foreground = Image.open("img/static/recusant_sigil.png").resize(sunk_background.size)
                                    current_width = int(self.width / (self.col_size*self.scaling_factor))
                                    current_height = int(self.height / (self.row_size*self.scaling_factor))
                                    self.used_images[index_x*self.col_size + index_y] = Image.alpha_composite(sunk_background.convert('RGBA'), sunk_foreground.convert('RGBA')).resize((current_width, current_height))
                                    sunk_image = ImageTk.PhotoImage(self.used_images[index_x*self.col_size + index_y])
                                    self.button_dict[(index_x, index_y)].configure(image = sunk_image, style=f"bsunk{index_x}{index_y}.TButton", command = lambda row_index=index_x, col_index=index_y:
                                                                                        self.change_button_color(self.marking_colors["Battleship Sink"], "black", row_index, col_index, current_border_color, placing_ship))
                                    self.button_dict[(index_x, index_y)].image = sunk_image

                # undo any bingos or sunk battleships if need be
                else:
                    
                    # if the mode is bingo
                    if self.bingo and self.row_size == self.col_size:
                        # get number of bingos before
                        old_bingo_squares = []
                        for possible_bingo in self.possible_bingos:
                            if np.sum(possible_bingo * self.checks_found) == self.row_size:
                                xs, ys = np.where(possible_bingo == 1)
                                old_bingo_squares += [(xs[i], ys[i]) for i in range(len(xs))]    

                        self.checks_found[row_index, col_index] = 0

                        # get the number of bingos that remain
                        new_bingo_squares = []
                        for possible_bingo in self.possible_bingos:
                            if np.sum(possible_bingo * self.checks_found) == self.row_size:
                                xs, ys = np.where(possible_bingo == 1)
                                new_bingo_squares += [(xs[i], ys[i]) for i in range(len(xs))]     

                        bingo_squares_removed = set(old_bingo_squares) - set(new_bingo_squares)

                        # remove previous bingos and change their functionality
                        for (i, j) in bingo_squares_removed:
                            if (i,j) == (row_index, col_index):
                                self.set_style(f"bbingo{i}{j}.TButton", background="black", bordercolor=current_border_color, highlightthickness=10, padding=0)
                                self.set_style(f"bnormal{i}{j}.TButton", background="black", bordercolor=current_border_color, highlightthickness=10, padding=0)
                                self.button_dict[(i, j)].configure(style=f"bnormal{i}{j}.TButton", command = lambda row_index=i, col_index=j:
                                                                                    self.change_button_color("black", self.marking_colors["Marking Color"], row_index, col_index, current_border_color, placing_ship))
                            if (i,j) != (row_index, col_index) and (i,j) in bingo_squares_removed:
                                self.set_style(f"bbingo{i}{j}.TButton", background=self.marking_colors["Marking Color"], bordercolor=current_border_color, highlightthickness=10, padding=0)
                                self.set_style(f"bclicked{i}{j}.TButton", background=self.marking_colors["Marking Color"], bordercolor=current_border_color, highlightthickness=10, padding=0)
                                self.button_dict[(i, j)].configure(style=f"bclicked{i}{j}.TButton", command = lambda row_index=i, col_index=j:
                                                                                    self.change_button_color(self.marking_colors["Marking Color"], "black", row_index, col_index, current_border_color, placing_ship))

                    # if the mode is battleships
                    elif hasattr(self, 'ships_left'):
                        # get the ships that were previously sunk
                        old_sunk_squares = []
                        for id in self.ships_left:
                            xs, ys = np.where(self.opponent_ships_with_ids == id)
                            if all([value == 1 for value in [self.checks_found[xs[i], ys[i]] for i in range(len(xs))]]):
                                for index_x, index_y in [[xs[i], ys[i]] for i in range(len(xs))]:
                                    old_sunk_squares.append((index_x, index_y))

                        self.checks_found[row_index, col_index] = 0

                        # get the sunk ships that remain
                        new_sunk_squares = []
                        for id in self.ships_left:
                            xs, ys = np.where(self.opponent_ships_with_ids == id)
                            if all([value == 1 for value in [self.checks_found[xs[i], ys[i]] for i in range(len(xs))]]):
                                for index_x, index_y in [[xs[i], ys[i]] for i in range(len(xs))]:
                                    new_sunk_squares.append((index_x, index_y))
                        
                        sunk_squares_removed = set(old_sunk_squares) - set(new_sunk_squares)
                        # remove previous battleships and change their functionality
                        for (i,j) in sunk_squares_removed:
                            correct_revert_sunk_color = self.marking_colors["Battleship Miss"] if self.opponent_ships_with_ids[i][j] == 0 else self.marking_colors["Battleship Hit"]
                            current_width = int(self.width / (self.col_size*self.scaling_factor))
                            current_height = int(self.height / (self.row_size*self.scaling_factor))
                            self.used_images[i * self.col_size + j] = self.raw_images[i * self.col_size + j].resize((current_width, current_height))
                            old_reverted_image = ImageTk.PhotoImage(self.used_images[i * self.col_size + j])
                            border_color = ttk.Style().lookup(f"bloaded{i}{j}.TButton", 'bordercolor')
                            if (i,j) == (row_index, col_index):
                                self.set_style(f"bsunk{i}{j}.TButton", background="black", bordercolor=border_color, highlightthickness=10, padding=0)
                                self.set_style(f"bnormal{i}{j}.TButton", background="black", bordercolor=border_color, highlightthickness=10, padding=0)
                                self.button_dict[(i, j)].configure(image = old_reverted_image, style=f"bnormal{i}{j}.TButton", command = lambda row_index=i, col_index=j:
                                                                                    self.change_button_color("black", correct_revert_sunk_color, row_index, col_index, current_border_color, placing_ship))
                            if (i,j) != (row_index, col_index) and (i,j) in sunk_squares_removed:
                                self.set_style(f"bsunk{i}{j}.TButton", background=correct_revert_sunk_color, bordercolor=border_color, highlightthickness=10, padding=0)
                                self.set_style(f"bclicked{i}{j}.TButton", background=correct_revert_sunk_color, bordercolor=border_color, highlightthickness=10, padding=0)
                                self.button_dict[(i, j)].configure(image = old_reverted_image, style=f"bclicked{i}{j}.TButton", command = lambda row_index=i, col_index=j:
                                                                                    self.change_button_color(correct_revert_sunk_color, "black", row_index, col_index, current_border_color, placing_ship))
                            self.button_dict[(i, j)].image = old_reverted_image

    def copy_seed(self, event=None):
        subprocess.run("clip", universal_newlines=True, input=f"{self.seedname}")


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
        self.generate_card(self.row_size, self.col_size, mystery=self.mystery, maze=self.maze)
                            

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
                if self.blind:
                    self.button_dict[(row_index, col_index)] = ttk.Button(self.frame, style=f"bnormal{row_index}{col_index}.TButton", takefocus=False, command=lambda x=row_index, y=col_index: self.change_button_color("black", "blue", x, y, "#333333", True)) #create a button inside frame 
                else:
                    self.button_dict[(row_index, col_index)] = ttk.Button(self.frame, image = self.images[row_index*col_size + col_index], style=f"bnormal{row_index}{col_index}.TButton", takefocus=False, command=lambda x=row_index, y=col_index: self.change_button_color("black", "blue", x, y, "#333333", True)) #create a button inside frame 
                self.button_dict[(row_index, col_index)].grid(row=row_index, column=col_index, sticky=N+E+S+W)


    def set_ship_sizes(self, entries, window):
        self.ship_sizes = list(it.chain(*[[i] * int(entries[i].get()) if entries[i].get() != "" else [] for i in range(1, max(self.row_size, self.col_size) + 1)]))
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
            entries[i].insert(0, sum([ship == i for ship in self.ship_sizes]))

        btn = ttk.Button(window, text = "Submit Answers", command = lambda: self.set_ship_sizes(entries, window))
        btn.grid(row = i+1, column = 1)


    def set_checks(self, entries, window, gen_card=True):
        self.frame.bind("<Configure>", lambda event: None)
        self.root.bind("<FocusIn>", lambda event: None)
        self.root.bind("<FocusOut>", lambda event: None)
        self.check_names = [x for x in os.listdir(f"img/{self.icons}")]
        with open("img.json", "r") as checktypes_json:
            checktypes_dict = json.load(checktypes_json)
            self.labels = [checktypes_dict[check] for check in self.check_names]
        self.selected_checks = [entries[i + 1].instate(['selected']) for i in range(len(self.check_types))]
        self.valid_types = [self.check_types[i] for i in range(len(self.check_types)) if entries[i + 1].instate(['selected'])]
        self.valid_checks = [True if x in self.valid_types else False for x in self.labels]
        self.row_size, self.col_size = [int(np.floor(np.sqrt(sum(self.valid_checks))))] * 2
        if gen_card:
            self.generate_card(self.row_size, self.col_size, mystery=self.mystery, maze=self.maze)
        window.destroy()


    def check_inclusion_window(self):
        # code that will remove checks from the grid pool
        window = Tk() 
        window.title("Check Inclusion Toggles")

        TitleLabel = ttk.Label(window, text = "Include?")
        TitleLabel.grid(row = 0, column = 1)

        check_type_labels = ["Reports", "Lvl 1 Magic", "Lvl 2 Magic", "Lvl 3 Magic", 
                             "Lvl 1 Movement", "Lvl 2 Movement", "Lvl 3 Movement", "Lvl 4 Movement", "Story Bosses", 
                             "Cups Fights", "Second Chance/Once More", "Drive Forms", "Torn Pages", "Summons", "Proofs", 
                             "World Progression Icons", "Promise Charm", "Extra Checks", "Armored Xemnas", "Final Xemnas",
                             "Absent Silhouettes", "Sephiroth", "Lingering Will"
        ] 

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
            restriction_values = [13, 6, 6, 6, 5, 5, 5, 5, 41, 4, 2, 5, 5, 4, 3, 11, 5]
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
            'cups_fight',
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
                                          "Cups Fights",
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
            8: 40,
            9: 5,
            10: 2,
            11: 5,
            12: 5,
            13: 4,
            14: 3,
            15: 11,
            16: 5,
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
                if self.bingo:
                    settings_file.write(f"self.bingo = {self.bingo}\n")
                settings_file.write(f"self.maze = {self.maze}\n")
                settings_file.write(f"self.mystery = {self.mystery}")

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
                if self.bingo:
                    settings_file.write(f"self.bingo = {self.bingo}\n")
                settings_file.write(f"self.maze = {self.maze}\n")
                settings_file.write(f"self.mystery = {self.mystery}")
        
        subprocess.Popen(r'explorer /open,"."')
    

    def load_settings(self, preset=False):
        if preset:
            settings_filename = fd.askopenfilename(initialdir="presets")
            self.preset_name = settings_filename.split('/')[-1]
        else:
            settings_filename = fd.askopenfilename()
        with open("previous_preset.txt", "w") as last_settings:
            with open(settings_filename, "r") as settings_file:
                settings = settings_file.readlines()
                for line in settings:
                    exec(line)
                    last_settings.write(line)
            if hasattr(self, "preset_name") and self.preset_name in os.listdir("presets"):
                last_settings.write(f"self.preset_name = '{self.preset_name}'")
        self.set_seedname(self.seedname)
        self.generate_card(self.row_size, self.col_size, self.seedname, mystery=self.mystery, maze=self.maze)

    
    def load_bunter_seed(self):
        

        # remove enemyspoilers before next load AT ALL COSTS
        filename = fd.askopenfilename()
        if os.path.exists('enemyspoilers'):
            shutil.rmtree('enemyspoilers')
        os.mkdir('enemyspoilers')
        shutil.unpack_archive(filename, './enemyspoilers', 'zip')
        self.replacements = make_replacements_dict()
        shutil.rmtree('enemyspoilers')
        window_x, window_y, window_width, window_height = self.root.winfo_rootx(), self.root.winfo_rooty(), self.root.winfo_width(), self.root.winfo_height()
        popup = Tk()
        if type(self.replacements) == tuple:
            self.replacements = self.replacements[1]
            popup.iconbitmap("img/static/warning.ico")
            popup.wm_title("WARNING!")
            popup.geometry("380x80")
            self.root.update_idletasks()
            popup_width, popup_height = popup.winfo_width(), popup.winfo_height()
            popup.geometry(f"+{window_x + window_width//2 - 43 * popup_width//80}+{window_y + window_height//2 - popup_height//2 - 7 * popup_height//10}")
            label = ttk.Label(popup, text='WARNING: This seed has a replacement that will likely crash your game. \n                     We recommend re-rolling.')
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Okay", command = lambda: popup.destroy())
            B1.pack()
        else:
            popup.iconbitmap("img/static/success.ico")
            popup.wm_title("Success!")
            popup.geometry("217x70")
            self.root.update_idletasks()
            popup_width, popup_height = popup.winfo_width(), popup.winfo_height()
            popup.geometry(f"+{window_x + window_width//2 - 43 * popup_width//80}+{window_y + window_height//2 - popup_height//2 - 7 * popup_height//10}")
            label = ttk.Label(popup, text='Your boss enemy successfully loaded! :-)')
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Okay", command = lambda: popup.destroy())
            B1.pack()
        self.menubar.entryconfig(9, label="B/E is ON")


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
                current_label = self.labels[x * self.col_size + y]
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

def make_replacements_dict():
    with open('enemyspoilers/enemies.rando', 'rb') as enemiesrandofile:
        replacements = enemiesrandofile.read()
    replacements = ast.literal_eval(base64.b64decode(replacements).decode('ascii'))["BOSSES"]
    replacements_dict = {}
    for replacement in replacements:
        original_boss = boss_str_reformat(replacement['original'], 'original')
        new_boss = boss_str_reformat(replacement['new'], 'replacement')
        replacements_dict[original_boss] = new_boss

    blacklisted_pairs = [("Scar", "Beast"), ("GrimReaper2", "Hades"), ("GrimReaper2", "BlizzardLord"), ("GrimReaper2", "VolcanoLord"), ("GrimReaper2", "Beast"), ("GrimReaper1", "Axel2"), ("ArmoredXemnas1", "Demyx"), ("ArmoredXemnas2", "Demyx"), ("VolcanoLord", "TwilightThorn"), ("BlizzardLord", "TwilightThorn"), ("BlizzardLord", "Xigbar"), ("VolcanoLord", "Xigbar"), ("Beast", "Xigbar"), ("VolcanoLord", "Roxas"), ("BlizzardLord", "Roxas")]
    if {'original': 'Luxord', 'new': 'Luxord (Data)'} in replacements:
        return ("ERROR", replacements_dict)
    for replacement in blacklisted_pairs:
        k, v = replacement
        if replacements_dict.get(k) == v:
            return ("ERROR", replacements_dict)

    return replacements_dict

def boss_str_reformat(boss, boss_type, images=False):
    boss = boss.strip().replace(" (1)", "").replace(" (2)", "").replace(" (3)", "").replace("Terra", "LingeringWill").replace("Axel (Data)", "Axel2").replace("II", "2").replace("I", "1").replace(" ", "").replace("-", "").replace("OC2", "OC").replace("(Data)", "").replace("Hades2", "Hades").replace("Past", "Old").replace("The", "").replace("ArmorXemnas1", "ArmoredXemnas1").replace("ArmorXemnas2", "ArmoredXemnas2").replace("Escape", "").replace("(Cups)", "").replace("Hades1", "Hades")
    if images or boss_type != "original":
        return boss.replace("PeteOC", "Pete").replace("PeteTR", "Pete")
    return boss

if __name__ == '__main__':
    BattleshipBoard() 