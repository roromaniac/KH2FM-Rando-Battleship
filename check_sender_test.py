import time
import random
import os

def inject_checks(starting_buffer=10,interval=10):

    desktop = False
    folder = "../../../../Desktop/battleship_rando/" if desktop else ""

    if os.path.exists(folder + 'seenbosses.txt'):
        os.remove(folder + "seenbosses.txt")
    if os.path.exists(folder + 'checks.txt'):
        os.remove(folder + "checks.txt")

    time.sleep(starting_buffer)

    checks = ['Report1', 'Report2', 'Report12', 'Report13', 'Sark', 'Pete', 'Scar', 'Barbossa', 'Saix', 'Vexen', 'Xemnas', 'Experiment', 'Marluxia', 'Axel2', 'Cerberus', 'Demyx', 'Larxene', 'PrisonKeeper', 'Axel1', 'Roxas', 'Hades', 'Thresholder']
    checks_found = ['Report1', 'Report2', 'Report12', 'Report13', 'Sark', 'Pete', 'Scar', 'Barbossa', 'Saix', 'Vexen', 'Xemnas', 'Experiment', 'Marluxia', 'Axel2', 'Cerberus', 'Demyx', 'Larxene', 'PrisonKeeper', 'Axel1', 'Roxas', 'Hades', 'Thresholder']

    while len(checks) != 0:

        check = random.choice(checks)

        with open(folder + "seenbosses.txt", "a") as bosses:
            
            bosses.write(check + '\n')
            checks.remove(check)
            time.sleep(interval)

        check = random.choice(checks_found)    
        
        with open(folder + "checks.txt", "a") as mark:
            
            mark.write(check + '\n')
            checks_found.remove(check)
            time.sleep(interval)

inject_checks(10, 0.5)
