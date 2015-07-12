"""
All game actions.
"""
import yaml
import json
from change_state import update_game_state
from send_message import send_message

from slackclient import SlackClient


##############
# user stuff #
##############

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

USER_MAP = UserMap()

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

def get_user_name(g, user_id):
    config = yaml.load(file('rtmbot.conf', 'r'))
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



################
# GAME ACTIONS #
################

def players_in_game(g):
    return g['players'].keys()

def player_in_game(g, user_id):
    """
    game state, user_id
    -> True/False
    """
    return user_id in players_in_game(g)

def is_player_alive(g, user_id):
    """
    game state, user_id
    -> True/False
    """
    status = g['players'].get(user_id).get('status')
    if status == 'alive':
        return True
    elif status == 'dead':
        return False
    else:
        print('durr')

def player_role(g, user_id):
    return g['players'].get(user_id).get('role')

def player_status(g, user_id):
    return g['players'].get(user_id).get('status')

def has_voted(g, user_id):
    """
    g - game state
    user_id - user id
    -> True/False

    returns whether user has voted aka
    is user_id a key in votes.
    """
    return user_id in g['votes'].keys()

def list_players(g, user_id, *args):
    """
    * args is args to command list
    g -> string to Slack of players
      -> "\n".join([list of players])

      "player_name"|"status"
    """
    # player_ids = players_in_game(g)
    # player_names
    u = get_user_map(g)
    # for each player in players_in_game

    return "\n".join([u.id_dict[p_id]
                        for p_id in players_in_game(g)]), None

def get_current_round(g):
    """
    returns game state's current round:
        aka 'night' or 'day'
    """
    return g['ROUND']

################
# Game Actions #
################

def create_game(g, user_id, *args):
    """
    Reset state.
    Let people join.
    annouce

    STATUS -> "WAITING_FOR_JOIN"

    """

    # testing if i can append to outputs here.

    # Can only create a game
    #   if g['STATUS'] == 'INACTIVE'
    result, message = mod_valid_action(user_id, 'create', g)
    if result:
        # allowed to create game
        if g['STATUS'] != 'INACTIVE':
            return 'Can not create new game.', None
        # reset game state.
        new_g = update_game_state(g, 'reset_game_state')
        # change game status to WAITING
        new_g = update_game_state(new_g, 'status', status='WAITING_FOR_JOIN')
        # send message to channel
        return '_Waiting for players..._ \n*Type !join to join.*', None
    else:
        return message, None # return error message, and basic channel.


def start_game(g, user_id, *args):
    """
    Check if enough players.
    (optional) Pick config setup that works w/ num of players.
    Outut to channel (@channel) game is starting.
    Assign Roles.
    Message Users their roles.

    STATUS -> "RUNNING"
    """
    # can only start a game
    #   if enough players
    #   if g['STATUS'] == 'WAITING_FOR_JOIN'

    result, message = mod_valid_action(user_id, 'start', g)
    if not result:
        # cant start
        return "cannot start", None

    # tell everyone the game is starting
    send_message("@werewolf-test Game is starting...")
    """ message everyone details of game. """
    players = players_in_game(g)
    num_werewolves = 1 # only one for now.



    p1_str = "_There are *%d* players in the game._\n" % len(players)
    p2_str = "There are *%d* werewolves in the game._" % num_werewolves
    send_message(p1_str + p2_str)

    # Go through and assign everyone in the game roles.
    assign_roles(g)
    # go to night round.
    start_night_round(g)


    return '', None # idk when this will return.

def assign_roles(g):
    players = players_in_game(g)
    create_wolf = random.choice(players) # id of player
    new_g = g
    for player in players:
        if player == create_wolf:
            new_g = update_game_state(new_g, 'role', player=player, role='w')
        else:
            new_g = update_game_state(new_g, 'role', player=player, role='v')


def message_everyone_roles(g):
    """
    for every player in game.
    DM them their roles.

    """
    pass


def join(g, user_id, *args):
    """
    See if player is allowed to join.
    If so let add them to the game.

    """
    result, message = mod_valid_action(user_id, 'join', g)

    if not result:
        return message, None # could not join

    # if player successfully joins.
    u = get_user_map(g)
    user_name = u.id_dict.get(user_id)

    if not user_name:
        # user not in user_map yet
        # get_user_name polls slack and adds to user map
        user_name = get_user_name(g, user_id)

    # update state with new player
    mutated_g = update_game_state(g, 'join', player=user_id)

    # tell the channel the player joined.
    join_message = "%s joined the game." % user_name
    return join_message, None

def eat_player(g, user_id, *args):
    """
    args[0] is target player.

    user_name = u.id_dict.get(user_id)

    """
    if len(args) < 0: # no target no good
        return "Have to pick a target.", None
    else:
        u = get_user_map(g) # get usermap

        target_name = args[0]
        target_id =  u.name_dict.get(target_name) # turn name into id
        result, message = is_valid_action(user_id, 'kill', g, target=target_id)
        if not result:
            # was not a valid kill
            return message, None
        else:
            # player is eaten
            # update state
            # changes targeted player's status to dead
            new_g = update_game_state(g, 'player_status', player=target_id, status='dead')
            # tell the players.
            eaten_str = "%s was eaten." % (target)
            resolve_night_round(g)

            return eat_str, None

def resolve_night_round(g):
    """
    Makes sure everyone has done all their roles.

    - if yes
        see if game is over.
        if yes
            set game to over.
            display results.
        if no
            change round to day.
    """
    # for each player in the game,
    # check if completed their action for the night.
    pass

def start_night_round(g):
    """
    set state to night round.
    print to screen


    """
    send_message("It is night time.")
    pass


def player_vote(g, user_id, *args):
    if len(args) < 0: # didn't vote on someone
        return "Have to vote FOR someone.", None
    else:
        u = get_user_map(g) # get usermap
        target_name = args[0]
        target_id =  u.name_dict.get(target_name) # turn name into id

        result, message = is_valid_action(user_id, 'vote', g, target=target_id)
    if not result:
        # was not a valid kill
        return message, None
    else:
        # player voted
        # update state
        # change votes to reflect their vote
        new_g = update_game_state(g, 'vote', voter=user_id, votee=target_id)


###################
# GAME VALIDATION #
###################

def mod_valid_action(user_id, action, g, target_name=None):
    """
    For game logistic actions only.
    user_id, action, game state
    -> (True/False, message)
    """
    MSG = {
        'already_join': 'You have already joined game.',
        'not_waiting': 'Game not waiting for players to join.',
        'num_players': 'Not enough players to start.',
    }

    def can_create():
        return True, None

    def can_start():
        """ some logic here """
        players = players_in_game(g)
        if len(players_in_game(g)) < 1: # change to 3 later.
            # not enough players to start
            return False, MSG['num_players']
        return True, None

    def can_join():#idk dont want to override join()
        # status is WAITING_FOR_JOIN
        if g.get('STATUS') != 'WAITING_FOR_JOIN':
            return False, MSG['not_waiting']
        # Not already in the game
        if player_in_game(g, user_id):
            return False, MSG['already_join']
        return True, None

    if action == 'create':
        return can_create()
    elif action == 'start':
        return can_start()
    elif action == 'join':
        return can_join()
    else:
        # Not valid
        return False, 'Not a valid command.'


def is_valid_action(user_id, action, g, target_name=None):
    """
    For game actions only.
    user_id, action, game state
    -> (True/False, message)
    """
    # DRY yo, cleaner response messages.
    MSG = {
        'u_not_in_game':'You are no in the game',
        'u_not_alive': 'You are not alive.',
        't_not_alive': 'Target is not alive.',
        't_not_in_game': 'Target is not in game.',
        'not_wolf': 'You are not a werewolf.',
        'not_night': 'It is not night.',
        'not_day': 'It is not day.',
        'has_voted': 'You have already voted.'
    }

    def vote():
        # 1) Make sure player who made the command
        # is in the game
        if not player_in_game(g, user_id):
            return False, MSG['u_not_in_game']
        # is alive
        if not is_player_alive(g, user_id):
            return False, MSG['u_not_alive']
        # target is in game
        if not player_in_game(g, target_id):
            return False, MSG['t_not_in_game']
        # target is alive
        if not is_player_alive(g, target_id):
            return False, MSG['t_not_alive']
        # only valid during day
        if get_current_round(g) != 'day':
            return False, MSG['not_day']
        # has not already voted
        if not has_voted(g, user_id):
            return False, MSG['has_voted']

        return True, None # no message


    def kill():
        # 1) Make sure player who made the command
        # is in the game
        if not player_in_game(g,user_id):
            return False, 'You are not in the game.'
        # 1a) is a werewolf
        # Only werewolf can use kill. (for now)
        if player_role(g, user_id) != 'w':
            return False, 'not a werewolf'
        # 1c) is alive
        if not is_player_alive(g, user_id):
            return False, 'Dead wolves can not kill.'
        # 2) Kill command only valid at night.
        if get_current_round(g) != 'night':
            return False, 'It is not night.'
        # 3) Target must be in game.
        if not player_in_game(g, target_id):
            return False, 'player not in game.'
        # 4) Target must be alive.
        if not is_player_alive(g, target_id):
            return False, 'Can not kill the dead.'

        return True, None # no message

    def seer():
        return False

    if target_name==None:
        """
        No current role that
        has no target.
        """
        return False

    # turn target name into an id
    u = get_user_map(g)
    if u:
        # if we have access to user map
        target_id = u.name_dict.get(target_name)
        if not target_id:
            return False # user not in usermap
    else:
        return False # user map None

    if action == 'vote':
        return vote()
    elif action == 'kill':
        return kill()
    elif action == 'seer':
        # Not implemented yet.
        return seer()
    else:
        # Not valid
        return False

