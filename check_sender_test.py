import time
import random
import os

from rando_battleship import make_replacements_dict

def inject_checks(starting_buffer=10,interval=10):

    if os.path.exists('seenbosses.txt'):
        os.remove("seenbosses.txt")
    if os.path.exists('checks.txt'):
        os.remove("checks.txt")

    time.sleep(starting_buffer)

    checks = ['Report1', 'Report2', 'Report12', 'Report13', 'Sark', 'Pete', 'Scar', 'Barbossa', 'Saix', 'Vexen']
    checks_found = ['Report1', 'Report2', 'Report12', 'Report13', 'Sark', 'Pete', 'Scar', 'Barbossa', 'Saix', 'Vexen']

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
