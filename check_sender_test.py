import time
import random
import os

from rando_battleship import make_replacements_dict

def inject_checks(starting_buffer=10,interval=10):

    if os.path.exists('checks.txt'):
        os.remove("checks.txt")

    time.sleep(starting_buffer)

    checks = [x[:-5] for x in os.listdir('img')] + ['PeteOC', 'ArmoredXemnas1', 'ArmoredXemnas2']

    while len(checks) != 0:

        check = random.choice(checks)

        with open("checks.txt", "a") as bosses:
            
            bosses.write(check + '\n')
            checks.remove(check)
            time.sleep(interval)

inject_checks(10, 0.5)
