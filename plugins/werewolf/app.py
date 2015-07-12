"""
July 10th, 2015
werewolf refactor
"""
import time
import math
import yaml
import json
import copy

import random
from collections import defaultdict
import change_state

from router import command_router

from send_message import send_message


# main entry into the app.
def process_message(data, g=None): # g=None so we can tests.
    message = data.get('text', '')
    if message.startswith('!'): # trigger is "!"
        if not g: # if g is not set get game state.
            g_copy = copy.deepcopy(change_state.get_game_state())
        else:
            g_copy = copy.deepcopy(g)

        command = message[1:].split(" ") # everything after !

        # let the router deal with this nonsense
        game_response, channel = command_router(g_copy, command, data['user'])
        if channel:
            send_message(game_response, channel)
        else:
            send_message(game_response)
        return game_response
    return None


