import time
import random
import os

from rando_battleship import make_replacements_dict

def inject_checks(starting_buffer=10,interval=10):

    if os.path.exists('seenbosses.txt'):
        os.remove("seenbosses.txt")

    time.sleep(starting_buffer)

    checks = ['ShanYu', 'Roxas', 'Saix']

    while len(checks) != 0:

        check = random.choice(checks)

        with open("seenbosses.txt", "a") as bosses:
            
            bosses.write(check + '\n')
            checks.remove(check)
            time.sleep(interval)

inject_checks(10, 0.5)
