"""
July 10th, 2015
werewolf refactor
"""

import time
import math
import yaml
import json
from slackclient import SlackClient

import random
from collections import defaultdict

from router import command_router

config = yaml.load(file("rtmbot.conf", "r"))
room_from_config = config["CHANNEL"]

outputs = []

class UserMap:
    """
    So we don't have to keep track of two dictionaries.
    Easiest is just to keep one instance of this in the game state.

    We create this at the beginning of the game.

    So we can do -

    user_id -> name
    name -> user_id
    """
    def __init__(self):
        self.id_dict = {}
        self.name_dict = {}

    def add(self, user_id, name):
        """
        self.id_dict[user_id] = name
        self.name_dict[name] = user_id
        """
        if self.id_dict.get(user_id) and self.name_dict.get(name):
            # names aleady set
            return None
        else:
            self.id_dict[user_id] = name
            self.name_dict[name] = user_id


# main entry into the app.
def process_message(data):
    message = data.get('text', '')
    if message.startswith('!'): # trigger is "!"
        command = message[1:].split(" ") # everything after !

        # let the router deal with this nonsense
        command_router(command, data['user'])

def send_message(message, channel=room_from_config):
    """
    Abstract away dumb idea to send message by,
    appending to list outputs.

    We just do it in here so no one has to know!
    """
    outputs.append([channel, message])
    return None

