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


