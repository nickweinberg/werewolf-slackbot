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

from game_actions import change_state

from router import command_router

outputs = []


class Messager:
    """
    Abstract away dumb idea to send message by
    appending to list outputs.

    We just do it in here so no one has to know!
    """
    def __init__(self):
        config = yaml.load(file("rtmbot.conf", "r"))
        room_from_config = config["CHANNEL"]

        self.room_from_config = room_from_config

    def send_message(self, message, channel=None):
        print('sending message', message)
        if not channel:
            channel = self.room_from_config

        global outputs
        outputs.append([channel, message])

M = Messager()

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
            M.send_message(game_response, channel)
        else:
            M.send_message(game_response)


