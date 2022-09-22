import time
import random
import os

from rando_battleship import make_replacements_dict

def inject_checks(starting_buffer=10,interval=10):

    if os.path.exists('seenbosses.txt'):
        os.remove("seenbosses.txt")

    time.sleep(starting_buffer)

    checks = ['Xigbar', 'Sephiroth', 'Cerberus', 'Sark', 'Luxord', 'PrisonKeeper', 'GrimReaper1', 'GrimReaper2', 'Larxene', 'Pete', 'Axel1', 'Axel2', 'Scar', 'Thresholder', 'Hades', 'Barbossa', 'Beast', 'DarkThorn', 'Experiment', 'Lexaeus', 'OldPete', 'BlizzardLord', 'ArmoredXemnas', 'VolcanoLord', 'ShanYu', 'Demyx', 'Zexion', 'Marluxia', 'Vexen', 'TwilightThorn']
    checks_found = ['Sark', 'Xigbar', 'Luxord', 'Saix', 'Xaldin', 'PrisonKeeper', 'GrimReaper1', 'GrimReaper2', 'Larxene', 'Pete', 'Axel1', 'Axel2', 'Scar', 'Thresholder', 'Hades', 'HostileProgram', 'Roxas', 'DarkThorn', 'Experiment', 'Lexaeus', 'OldPete', 'BlizzardLord', 'ArmoredXemnas', 'VolcanoLord', 'ShanYu', 'Demyx', 'Zexion', 'Marluxia', 'Vexen', 'TwilightThorn']

    while len(checks) != 0:

        check = random.choice(checks)

        with open("seenbosses.txt", "a") as bosses:
            
            bosses.write(check + '\n')
            checks.remove(check)
            time.sleep(interval)

        check = random.choice(checks_found)    
        
        with open("checks.txt", "a") as mark:
            
            mark.write(check + '\n')
            checks_found.remove(check)
            time.sleep(interval)

inject_checks(10, 0.5)
