"""
July 10th, 2015
werewolf refactor
"""
import time
import math
import yaml
import json

import random
from collections import defaultdict

import change_state

from router import command_router

from send_message import send_message


# main entry into the app.
def process_message(data):
    message = data.get('text', '')
    if message.startswith('!'): # trigger is "!"
        g = change_state.get_game_state()
        command = message[1:].split(" ") # everything after !

        # let the router deal with this nonsense
        game_response, channel = command_router(g, command, data['user'])
        print(game_response, channel)

        if channel:
            send_message(game_response, channel)
        else:
            send_message(game_response)


