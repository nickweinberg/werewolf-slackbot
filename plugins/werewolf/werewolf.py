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
from collections import defaultdict

config = yaml.load(file("rtmbot.conf", "r"))
ROOM = config["CHANNEL"]

state = {
    "is_created": False,
    "is_finished": False,
    "players": [],
    "players_names": [],
    "werewolves":[],
    "is_night": True,
    "votes": {}
}

USER_DICT = {}
R_USER_DICT = {}

"""
Game state
{
    players: {
            uid: {
                "name": username,
                "DM": "dm channel",
                "role": "v",
                "side": "v"
                "id": uid,
                "status": "alive"|"dead"
            },
            uid: {
                "name": username,
                "DM": "dm channel",
                "role": "w",
                "side": "w",
                "id"  : uid,
                "status": "alive"|"dead"
            }
        },
    votes: {
        uid: target,
        uid: target,
        uid: target
    },
    STATUS: "INACTIVE"|"WAITING_FOR_JOIN"|"RUNNING"
}
"""

def get_players_length(game_state):
    pass


def id_to_name(user_id):
    """ user_id -> user_name """
    user_name = "<something>"
    return user_name

def name_to_id(user_name):
    user_id = "<something>"
    return user_id

def get_game_state():
    """
    We have the game state hidden away somewhere.

    Returns a copy of the game_state.

    """
    game_state = {}
    return None

def update_game_state(mutated_g):
    """
    Only place we are allowed to change game state.

    If we save an ordered list of all game states,
    we can undo them all. And do automated playbacks.

    ex. Game_ID: [G0, G1, G2, G3.. Gn]
    If we hold this in like Redis, can resume if server breaks/internet goes down at exact position.

    """
    print(mutated_g) # for debugging.

    return updated_game_state


def is_valid_action(user_id, action, g):
    """
    For game actions only.
    user_id, action, game_state
    -> True/False
    """
    def vote():
        pass
    def kill():
        pass

    if action == 'vote':
        vote()
    elif action == 'kill':
        kill()



def kill_player(user_id, game_state):
    """
    Input
        user_id: a player's id in the game.
        game_state: a dictionary of the game's entire state.

    Output
        A new game state.

    Sets user_id from game_state to dead.
    """
    pass


def eat_player(user_id, target_name):
    """
    user_id who made command.
    target_name is user_name who was targeted.
    """
    pass

def command_logic(command, user_id):
    """
    Router is a dictionary of functions.

    --- Game Logistics ---
    create(create_game)  - create a new game (starts moderator- alerts channel)
    join(player_join)    - player attempts to join a created game
    start(start_game)    - starts game, assigns roles, other setup.
    players(list_players)- list players in the game.

    --- Game Actions ---
    kill(eat_player)   - werewolf attempts to eat a player
    vote(player_vote)
    """
    router = {
        "create": create_game,
        'start': start_game,
        'players': list_players,
        "join": join,
        "kill": eat_player,
        "vote": player_vote
    }


    if command[0] == "create" and state["is_created"] == False: # dont start game in progress
        new_game()
    elif command[0] == "players":
        if len(state["players"]) > 0:
            players_list = [USER_DICT[p]["user_name"] for p in state["players"]]
            players_str = '\n'.join(players_list)
            outputs.append([ROOM, players_str])
        else:
            outputs.append([ROOM, "No one joined yet."])
    elif command[0] == "join":
        if user_id not in state['players']:
            if USER_DICT.get(user_id, False):
                user_name = USER_DICT[user_id]["user_name"]
            else:
                user_name = get_user_name(user_id)
            state["players"].append(user_id)
            outputs.append([ROOM, user_name + " joined"])
        else:
            try:
                u = USER_DICT[user_id]
            except Exception as e:
                print(e)
                u = "INVALID USER"

            outputs.append([ROOM, u["user_name"] + " is already in game"])

    elif command[0] == "start":
        if state["players"] > 0 and state["is_finished"] == True:
            state["is_finished"] = False
            # game actually starts
            print("starting game")
            # create r user dict

            # set up reverse user dict
            # {user_id: {user_name: hi, dm: dhdhadh}}
            for u in USER_DICT.keys():
                R_USER_DICT[USER_DICT[u]["user_name"]] = u

            print(USER_DICT)
            print(R_USER_DICT)

            outputs.append([ROOM, "Starting Game"])

            # should be decently fair
            fair_num = int(math.sqrt(len(state["players"])))
            # only have 1 for now make it simpler
            state["werewolves"].append(random.choice(state["players"]))

            p1_str = "There are " + str(len(state["players"])) + " players."
            p2_str = "There are " +  str(len(state["werewolves"])) + " werewolves."
            outputs.append([ROOM, p1_str])
            outputs.append([ROOM, p2_str])
            for wolf in state["werewolves"]:
                wolf_dm_channel = USER_DICT[wolf]["DM"]
                outputs.append([wolf_dm_channel, "You are a werewolf. Awwoooooo!!"])
            night_round()
        else:
            outputs.append([ROOM, "Need more than 1 player to start."])
    elif command[0] == "kill":
        # command[1] should be name of player to be killed.
        # make sure player is a werewolf and its night
        if user_id in state["werewolves"] and state["is_night"] == True:
            # we have the player name not the id
            # turn username into id
            to_kill_id = R_USER_DICT.get(command[1], False)
            print(R_USER_DICT)
            if to_kill_id in state["players"]:
                outputs.append([ROOM, command[1] + " was eaten. S/he was delicious."])
                kill_index = state["players"].index(to_kill_id)

                state["players"].pop(kill_index)

                resolve_round("day")
            else:
                outputs.append([ROOM, command[1] + " cannot be killed."])
        else:
            outputs.append([ROOM, "You do not have the capacity for violent murder... or it is not not night"])
    elif command[0] == "vote":
        # command[1] = command[1] # everything after @ sign.
        if state['is_night'] == False:
            voted_on_id = R_USER_DICT.get(command[1], False)
            if user_id in state["players"]: # only players alive can vote
                if voted_on_id in state["players"]: # only vote on people in game
                    if not state["votes"].get(user_id, False): # cant vote more than once
                        voted = command[1]
                        state["votes"][user_id] = voted
                        vote_msg = USER_DICT[user_id]["user_name"] + " voted for " + voted

                        if len(state["votes"].keys()) == len(state["players"]):
                            # everyone has voted
                            outputs.append([ROOM, "Everyone has voted."])
                            resolve_vote_round()
                    else:
                        outputs.append([ROOM, USER_DICT[user_id]["user_name"] + ", you cannot vote more than once."])
                else:
                    outputs.append([ROOM, str(command[1]) + "is not playing"])
            else:
                outputs.append([ROOM, USER_DICT[user_id]['user_name'] + " can not vote."])
        else:
            outputs.append([ROOM, "Cant vote at night."])
    elif command[0] == "v":
        if state["is_night"] == False:
            if len(state["votes"].keys() > 0):
                # show all the votes
                vote_msg = [item for item in state["votes"].items()]
                # state["votes"][user_id] = voted
                outputs.append([ROOM, "\n".join(vote_msg)])


    else:
        outputs.append([ROOM, "Not a valid command."])


def night_round():
    """ night round happenings"""
    state["is_night"] = True
    outputs.append([ROOM, "It is now night time. DM me '!kill username' ya wanna eat?"])

def day_round():
    """ night round. voting and stuff. """
    state["is_night"] = False
    outputs.append([ROOM, "It is now day time.\n  Type '!vote username'. When everyone has voted, user with most votes dies."])

def resolve_vote_round():
    """ count up votes """
    vote_count = defaultdict(int)
    for user in state["votes"]:
        vote_count[user] += 1

    killed_name = max(vote_count.iterkeys(), key=(lambda u: vote_count[u]))
    print(vote_count)
    print(killed_name)

    kill_output = [un + " got " + str(vote_count[un]) + " votes.\n"
                        for un in vote_count.keys()]
    outputs.append([ROOM, ''.join(kill_output)])

    outputs.append([ROOM, killed_name + " was killed."])

    try:
        killed_id = R_USER_DICT[killed_name]
        kill_index = state["players"].index(killed_id)
        state["players"].pop(kill_index)
    except Exception as e:
        print(e)


    state["votes"] = {}
    resolve_round("night")


def resolve_round(round_flag):
    """ durrr """
    # reset votes just in case

    outputs.append([ROOM, "There are " +str(len(state["players"])) + " players left."])
    if len(state["players"]) <= len(state["werewolves"]):
        outputs.append([ROOM, "Werewolves win."])
    elif len(state["werewolves"]) == 0:
        outputs.append([ROOM, "Village wins."])
    else:
        if round_flag == "day":
            day_round()
        elif round_flag == "night":
            night_round()


def new_game():
    # create a new game state
    state['is_finished'] = True
    state['is_created'] = True
    state['players'] = []
    state['werewolves'] = []
    state['is_night'] = False
    state['votes'] = {}

    print("waiting for players...")
    outputs.append([ROOM, "waiting for players..."])

def process_message(data):
    print(state)
    message = data.get('text', '')
    if message.startswith('!'): # trigger is "!"
        command = message[1:] # everything after !

        command = command.split(" ")
        command_logic(command, data['user'])


# slack client api necessities
sc = SlackClient(config["SLACK_TOKEN"])
def get_user_name(user_id):
    user_obj = json.loads(sc.api_call("users.info", user=user_id))
    user_name = user_obj["user"]["name"]
    im = json.loads(sc.api_call("im.open", user=user_id))

    USER_DICT[user_id] = {'user_name':user_name, 'DM': im["channel"]["id"]}
    return user_name



