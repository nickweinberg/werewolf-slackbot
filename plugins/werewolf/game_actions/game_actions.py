"""
All game actions.
"""
# from app import get_user_map, send_message, get_user_name, send_message


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
    return None

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

    STATUS -> "WAITING_FOR_JOIN"
    """
    # Can only create a game
    #   if g['STATUS'] == 'INACTIVE'
    pass

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
    pass

def join(g, user_id, *args):
    """
    Let player join game.

    """
    result, message = mod_valid_action(user_id, 'join', g)

    if not result:
        send_message(message)
        return None # could not join

    # if player successfully joins.
    u = get_user_map(g)
    user_name = u.id_dict.get(user_id)

    if not user_name:
        # user not in user_map yet
        # get_user_name polls slack and adds to user map
        user_name = get_user_name(g, user_id)

    # tell the channel the player joined.
    join_message = "%s joined the game." % user_name
    send_message(join_message)
    return None

def eat_player(g, user_id, *args):
    if len(args) < 0:
        send_message("no target")
    pass

def player_vote(g, user_id, *args):
    pass


####
# GAME VALIDATION
####

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
        return True

    def can_start():
        return True

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

