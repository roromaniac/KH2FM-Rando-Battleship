# KH2FM-Rando-Battleship
Battleship Board Generator for KH2FM Rando

Welcome to KH2FM Rando Battleship! Here are the instructions to get started.
                        
# Blind Mode (Pick ships BEFORE seeing board.)
1. Put your board into place mode by going to "Board Mode" -> "Place Mode (Blind)".
2. Place your ships. Confirm with your opponent what the ship sizes will be (standard is 5,4,3,3,2). Placed ships will show up in blue.
3. Once you have placed your ships, go to "Actions" -> "Download Ship Layout". This will create a file called "ships.zip."
4. Send the ships.zip file to your partner. This is how your partner will know whether they hit or miss your ships mid-run.
5. Make any customizations you want to make in the bottom few options of the Actions menu.
6. If you are the card generator, go to "Actions" -> "Download Board Settings". Then, go to "Actions" -> "Upload Board Settings" do get your customized board.  Send the settings.txt file in your battleship_rando folder over to all other opponents.
   If you are the seed receiver, go to "Actions" -> "Upload Board Settings" and select the txt you received from your opponent.
7. To get your opponent's ship data tracked, go to "Actions" -> "Upload Ship Layout" and select the "ships.zip" file you just received.
8. If you want autotracking, go to "Actions" -> "Start Autotracking". Note that it is recommended you wait until the game is loaded in before doing this.
9. If you did all of the above steps successfully, your ships that were marked blue have disappeared and the board is all black. You're ready to play!
    The button will turn blue if the check is a miss and red if the check is a hit.

# Visible Mode (Pick ships AFTER seeing board.)
1. If you are the card generator, go to "Actions" -> "Download Board Settings". Then, go to "Actions" -> "Upload Board Settings" to get your customized board.  Send the settings.txt file in your battleship_rando folder over to all other opponents.
   If you are the seed receiver, go to "Actions" -> "Upload Board Settings" and select the txt you received from your opponent.
2. Put your board into place mode by going to the "Board Mode" -> "Place Mode (Visible)".
3. Place your ships. Confirm with your opponent what the ship sizes will be (standard is 5,4,3,3,2). Placed ships will show up in blue.
4. Once you have placed your ships, go to "Actions" -> "Download Ship Layout". This will create a file called "ships.zip."
5. Send the ships.zip file to your partner. This is how your partner will know whether they hit or miss your ships mid-run.
6. To get your opponent's ship data tracked, go to "Actions" -> "Upload Ship Layout" and select the "ships.zip" file you just received.
7. If you want autotracking, go to "Actions" -> "Start Autotracking". Note that it is recommended you wait until the game is loaded in before doing this.
8. If you did all of the above steps successfully, your ships that were marked blue have green borders and the board is all black. You're ready to play!
   The button will turn blue if the check is a miss and red if the check is a hit.

# Same Board Mode
1. (Card Generator Only) Generate a new card with all of the restrictions and modifications you like.
2. (Card Generator Only) Download the settings by going to "Actions" -> "Download Board Settings".
3. (Card Generator Only) Send the settings.txt file over to all opponents.
4. (Everyone) Go to "Actions" -> "Upload Board Settings" and select the settings.txt you saved or received. Note that card generator must also do this. 
5. (Everyone) Select "Board Mode" -> "Same Board Mode". Now all players have the same battleships hidden but loaded.
6. (Everyone) If you want autotracking, go to "Actions" -> "Start Autotracking". Note that it is recommended you wait until the game is loaded in before doing this.

# Features in Development (and their expected release dates).
1. <ins>Interact w/ File Client to Upload Seed AND CHECK THAT THERE ARE HITS</ins> :white_check_mark: Included in v0.9.1.
2. <ins>Sunk Logic</ins>: Logic that changes the color of ship buttons once the whole ship is sunk. :white_check_mark: Included in v1.0.0.
3. <ins>Clear Board</ins>: Clear the board during placement mode. :white_check_mark: Included in v1.0.0.
4. <ins>Shared Board Mode</ins>: Generate a card with pre-placed ships to send to your opponent. You and your opponent can compete to clear the same board. :white_check_mark: Included in v1.0.0.
5. <ins>Custom Board Dimension</ins>: Customize the size of the battleship grid. :white_check_mark: Included in v1.0.0.
6. <ins>Assign hotkeys to certain actions so you don't have to go through the menus.</ins> :white_check_mark: Included in v1.0.1.
7. <ins>Toggle Checks for Inclusion</ins>: Toggle checks to be allowed in the pool of checks for battleship. :white_check_mark: Included in v1.1.0.
8. <ins>Ship Validation</ins>: Validate that ships of the appropriate sizes were placed. :white_check_mark: Included in v1.1.0.
9. <ins>Restrictions</ins>: Validate restrictions on ships (such as number of allowable bosses, level 4 movements, etc.). :white_check_mark: Included in v1.1.0.
10. <ins>Load Settings Automatically</ins>: Allow for board with the same restrictions/toggles/randomization etc. to be immediately loaded (as opposed to each player recreating the same board). :white_check_mark: Included in v1.1.1.
11. <ins>Presets</ins>: :white_check_mark: Included in v1.1.2.
12. <ins>Image and Window Quality</ins>: Make errors popout windows and improve image/window size quality with changing grid size. ETA: 2-3 weeks (from 7/24/22). Partially included in v1.0.1.
13. <ins>Autotracking</ins>: The ability for the button to be pressed once the check is found in KH2. :white_check_mark: Included in v1.2.0.
14. <ins>Boss Enemy Autotracking</ins>: Track the new boss instead of the replaced one in boss enemy seeds. :white_check_mark: Included in v1.3.0.
14. <ins>Markdown Assistance</ins>: The ability to right click to help you mark what might be important (or not important). ETA: 1-2 months (from 7/15/22)
15. <ins>Include icons with Xs to indicate sunken checks.</ins> ETA: ? Whenever someone wants to develop those icons.

# Autotracking

All bosses and checks are autotracked. Only 1 exception exists.

1. Light and Darkness will NOT trigger final form on the board. This is intentional. If you want to play so that L&D counts as finding final, you can manually click final.

# Credits

### Battleship Format Creator
* Ryujin

### Icon Developer
* Televo

### Dev Consultants

* roromaniac
* TopazTK
* codename_geek
* DA/o0DemonBoy0o

### Play Testers

* iiSalad
* Metthaios
* Lagg018
* cdrom1019
* Glint
* WallpeSH
* CrazyComics
* Zeddikus