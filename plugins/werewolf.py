"""
July 9th, 2015
werewolf
"""
import time
import math
import yaml
import json
from slackclient import SlackClient
import random

config = yaml.load(file("rtmbot.conf", "r"))
ROOM = config["CHANNEL"]
crontable = []
outputs = []

state = {
    "is_finished": True,
    "players": [],
    "werewolves":[]
    "is_night": False
}

USER_DICT = {}

def command_logic(command, user_id):
    print(command)
    if command[0] == "create" and state["is_finished"] == True: # dont start game in progress
        new_game()
    elif command[0] == "join":
        if user_id not in state['players']:
            if USER_DICT.get(user_id, False):
                user_name = USER_DICT[user_id]["user_name"]
            else:
                user_name = get_user_name(user_id)
            state["players"].append(user_id)
            outputs.append([ROOM, user_name + " joined"])
        else:
            outputs.append(ROOM, USER_DICT[user_id], + " is already in game")
    elif command[0] == "start":
        # game actually starts
        print("starting game")
        outputs.append([ROOM, "Starting Game"])

        # should be decently fair
        fair_num = int(math.sqrt(len(state["players"])))
        # only have 1 for now make it simpler
        state["werewolves"].append(random.choice(state["players"]))

        outputs.append([ROOM, "There are " + str(len(state["players"])) + " players."])
        outputs.append([ROOM, "There are " +  str(len(state["werewolves"])), + " werewolves."])
        for wolf in state["werewolves"]:
            wolf_dm_channel = USER_DICT[wolf]["DM"]
            outputs.append([wolf_dm_channel, "You are a werewolf. Awwoooooo!!"])
        night_round()
    elif command[0] == "kill":
        # command[1] should be name of player to be killed.
        # make sure player is a werewolf and its night
        if user_id in state["werewolves"] and state["is_night"] == True:
            if command[1] in state["players"]:
                killed = USER_DICT[command[1]]["user_name"]
                outputs.append([ROOM, killed + " was eaten. S/he was delicious."])
                resolve_round()
            else:
                outputs.append([ROOM, command[1] + " cannot be killed."])
        else:
            outputs.append([ROOM, "You do not have the capacity for violent murder... or it is not not night"])


def night_round():
    """ night round happenings"""
    state["is_night"] = True
    outputs.append([ROOM, "It is now night time. DM me '!kill username' ya wanna eat?"])

def resolve_round():
    """ durrr """
    outputs.append([ROOM, "There are " +str(len(state["players"])) + " players left."])
    if len(state["players"]) <= len(state["werewolves"]):
        outputs.append([ROOM, "Werewolves win."])
    elif len(state["werewolves"]):
        outputs.append([ROOM, "Village wins."])
    else:
        day_round()

def new_game():
    # reset state
    state['is_finished'] =  False
    state['players'] = []
    state['werewolves'] = []
    state['is_night'] = False

    print("waiting for players...")
    outputs.append([ROOM, "waiting for players..."])

def process_message(data):
    print(data)
    message = data['text']
    if message.startswith('!'): # trigger is "!"
        command = message[1:] # everything after !
        command = message.split(" ")
        command_logic(command, data['user'])


# slack client api necessities
sc = SlackClient(config["SLACK_TOKEN"])
def get_user_name(user_id):
    user_obj = json.loads(sc.api_call("users.info", user=user_id))
    user_name = user_obj["user"]["name"]
    im = json.loads(sc.api_call("im.open", user=user_id))

    USER_DICT[user_id] = {'user_name':user_name, 'DM': im["channel"]["id"]}
    return user_name



