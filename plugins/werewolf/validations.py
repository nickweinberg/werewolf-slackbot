from status import (
        players_in_game,
        player_in_game,
        player_role,
        is_player_alive,
        get_current_round,
        has_voted,
)

from user_map import UserMap

###################
# GAME VALIDATION #
###################

def mod_valid_action(user_id, action, g, target_name=None):
    """
    For game logistic actions only.
    - create
    - start
    - join

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
        if len(players) < 1: # change to 3 later.
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
    - vote
    - eat(kill)
    - TODO: seer
    - TODO: bodyguard
    user_id, action, game state
    -> (True/False, message)
    """
    # DRY yo, cleaner response messages.
    MSG = {
        'u_not_in_game':'You are not in the game',
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
        if has_voted(g, user_id):
            return False, MSG['has_voted']

        # after each success vote maybe should list all votes.
        return True, user_name + ' voted for ' + target_name  # no message


    def kill():
        print(user_id, target_name)
        # 1) Make sure player who made the command
        # is in the game
        if not player_in_game(g,user_id):
            return False, 'Not allowed.'
        # 1a) is a werewolf
        # Only werewolf can use kill. (for now)
        if player_role(g, user_id) != 'w':
            return False, 'Not allowed.'
        # 1c) is alive
        if not is_player_alive(g, user_id):
            return False, 'Dead wolves can not kill.'
        # 2) Kill command only valid at night.
        if get_current_round(g) != 'night':
            return False, 'Not allowed.'
        # 3) Target must be in game.
        if not player_in_game(g, target_id):
            return False, 'Not allowed.'
        # 4) Target must be alive.
        if not is_player_alive(g, target_id):
            return False, 'Not allowed.'

        return True, '' # no message

    def seer():
        return False, None

    u = UserMap()

    if target_name==None:
        """
        No current role that
        has no target.
        """
        return False, 'need a target.'

    # turn target name into an id
    if u:
        # if we have access to user map
        target_id = u.get(name=target_name)
        user_name = u.get(user_id)
        if not target_id:
            return False, 'User not in the game.' # user not in usermap
    else:
        return False, 'user map not set up' # user map None

    if action == 'vote':
        return vote()
    elif action == 'kill':
        return kill()
    elif action == 'seer':
        # Not implemented yet.
        return seer()
    else:
        # Not valid
        return False, 'not a valid action'


