# KH2FM-Rando-Battleship
Battleship Board Generator for KH2FM Rando

Welcome to KH2FM Rando Battleship! Here are the instructions to get started.
                        
# Blind Mode (Pick ships BEFORE seeing board.)
1. Put your board into place mode by going to "Board Mode" -> "Place Mode (Blind)".
2. Place your ships. Confirm with your opponent what the ship sizes will be (standard is 5,4,3,3,2). Placed ships will show up in blue.
3. Once you have placed your ships, go to "Actions" -> "Download Ship Layout". This will create a file called "ships.zip."
4. Send the ships.zip file to your partner. This is how your partner will know whether they hit or miss your ships mid-run.
5. When you receive the ships.zip file, move it into the same folder you have the rando_battleship.exe. This replaces your old
   ships.zip and this is expected.
6. If you are the card generator, go to "Actions" -> "Generate New Card".  
   If you are the seed receiver, go to "Actions" -> "Load Card from Seed" and paste the seed you received from your opponent.
7. If you generated the seed, send the seed string to your opponent by either clicking "Info" -> "Seed" or "Actions" -> "Copy Seed Name".
   Either will copy the name of the string to your clipboard and you can send it to your opponent via Discord.
8. If you received the seed name, go to "Actions" -> "Load Card from Seed" and paste the seed name into the window.
9. To get your opponent's ship data tracked, go to "Actions" -> "Upload Ship Layout" and select the "ships.zip" file you just received.
10. If you did all of the above steps successfully, your ships that were marked blue have disappeared and the board is all black. You're ready to play!
    The button will turn gray if the check is a miss and red if the check is a hit.

# Visible Mode (Pick ships AFTER seeing board.)
1. If you are the card generator, go to "Actions" -> "Generate New Card". 
   If you are the seed receiver, go to "Actions" -> "Load Card from Seed" and paste the seed you received from your opponent.
2. If you generated the seed, send the seed string to your opponent by either clicking "Info" -> "Seed" or "Actions" -> "Copy Seed Name".
   Either will copy the name of the string to your clipboard and you can send it to your opponent via Discord.
3. If you received the seed name, go to "Actions" -> "Load Card from Seed" and paste the seed name into the window.
4. Put your board into place mode by going to the "Board Mode" -> "Place Mode (Visible)".
5. Place your ships. Confirm with your opponent what the ship sizes will be (standard is 5,4,3,3,2). Placed ships will show up in blue.
6. Once you have placed your ships, go to "Actions" -> "Download Ship Layout". This will create a file called "ships.zip."
7. Send the ships.zip file to your partner. This is how your partner will know whether they hit or miss your ships mid-run.
8. When you receive the ships.zip file, move it into the same folder you have the rando_battleship.exe. This replaces your old
   ships.zip and this is expected.
9. To get your opponent's ship data tracked, go to "Actions" -> "Upload Ship Layout" and select the "ships.zip" file you just received.
10. If you did all of the above steps successfully, your ships that were marked blue have disappeared and the board is all black. You're ready to play!
   The button will turn gray if the check is a miss and red if the check is a hit.
   
# Single Board Mode
1. Have a mutual party generate a battleship board and send you the zip.
2. When you receive the ships.zip file, move it into the same folder you have the rando_battleship.exe.
3. To get the ship data tracked, go to "Actions" -> "Upload Ship Layout" and select the "ships.zip" file you just received.
4. If you did all of the above steps successfully, you're ready to play! The button will turn gray if the check is a miss and red if the check is a hit.

# Features in Development (and their expected release dates).
1. <ins>Interact w/ File Client to Upload Seed AND CHECK THAT THERE ARE HITS</ins> :white_check_mark: Included in v0.9.1.
2. <ins>Sunk Logic</ins>: Logic that changes the color of ship buttons once the whole ship is sunk. ETA: Very soon. Should be included in v0.9.2.
3. <ins>Clear Board</ins>: Clear the board during placement mode. ETA: Very soon. Should be included in v0.9.2.
4. <ins>Shared Board Mode</ins>: Generate a card with pre-placed ships to send to your opponent. You and your opponent can compete to clear the same board. ETA: 2 weeks (from 7/10/22)
5. <ins>Custom Board Dimension</ins>: Customize the size of the battleship grid. ETA: 2 weeks (from 7/10/22).
6. <ins>Assign hotkeys to certain actions so you don't have to go through the menus.</ins> ETA: 2 weeks (from 7/10/22).
7. <ins>Toggle Checks for Inclusiuon</ins>: Toggle checks to be allowed in the pool of checks for battleship. ETA: 1-2 months (from 7/10/22).
8. <ins>Ship Validation</ins>: Validate that ships of the appropriate sizes were placed. ETA: 1-2 months (from 7/10/22).
9. <ins>Restrictions</ins>: Validate restrictions on ships (such as number of allowable bosses, level 4 movements, etc.). ETA 1-2 months (from 7/10/22).
10. <ins>Border Logic</ins>: Toggle to restrict ships from bordering one another. ETA: 2-3 months if at all (from 7/10/22). Seems like placing neighboring ships isn't all that desirable anyways.
11. <ins>Autotracking</ins>: The ability for the button to be pressed once the check is found in KH2. ETA: 2-3 months (from 7/10/22).
12. <ins>Include icons with Xs to indicate sunken checks.</ins> ETA: ? Whenever someone wants to develop those icons.
