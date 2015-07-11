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

#config = yaml.load(file("rtmbot.conf", "r"))

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
        self.id_to_DM = {}

    def add(self, user_id, name, DM=None):
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

            if DM:
                # direct message channel
                self.id_to_DM[user_id] = DM


class GameState:
    """
    Don't worry not actually using OO lol.
    A light wrapper. Only used by get_game_state set_state function.

    """
    def __init__(self):
        self.state = {}
        self.games = []

USER_MAP = UserMap()



GAME_STATE = GameState() # not set yet.

# main entry into the app.
def process_message(data):
    message = data.get('text', '')
    if message.startswith('!'): # trigger is "!"
        command = message[1:].split(" ") # everything after !

        # let the router deal with this nonsense
        command_router(command, data['user'])

def send_message(message, channel=room_from_config):
    """
    Abstract away dumb idea to send message by
    appending to list outputs.

    We just do it in here so no one has to know!
    """
    outputs.append([channel, message])
    return None

def get_user_map(g):
    """
    Let's everyone get access to this delicious UserMap.

    Shouldn't let you have it (since it's probably not set)
    if game is INACTIVE.
    """
    if g['STATUS'] == 'INACTIVE':
        return None
    else:
        return USER_MAP

def set_user_map(g, user_id, name, DM=None):
    """
    Only way I'm letting you schmucks update user map.
    Gets USER_MAP.
    Adds new user.

    """
    u = get_user_map(g)
    u.add(user_id, name, DM)


def reset_votes(g):
    """
    g - game state
    -> g

    returns state with votes removed.

    - then since we are not allowed to modify game state.
    - when it returns we have to call update_game_state(g)
    """
    game_state = g # copy, to not mutate original state.
    game_state['votes'] = {}
    return game_state

def reset_game_state():
    """
    Returns an empty game state object.
    """
    return {'players': {},
            'votes':{},
            'STATUS': 'INACTIVE',
            'ROUND': None}


def get_user_name(g, user_id):
    sc = SlackClient(config['SLACK_TOKEN'])
    def poll_slack_for_user():
        user_obj = json.loads(sc.api_call('users.info', user=user_id))
        user_name = user_obj['user']['name']
        im = json.loads(sc.api_call('im.open', user=user_id))
        return user_name, im

    try:
        user_name, im = poll_slack_for_user()
    except Exception as e:
        print(e)
        # try one more time.
        user_name, im = poll_slack_for_user()

    if user_name:
        set_user_map(g, user_id, user_name, DM=im)
        return user_name




