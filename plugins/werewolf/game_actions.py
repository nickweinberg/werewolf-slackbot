"""
All game actions.
"""

# user id stuff
# we'll move this into players.py probs.

# end user id stuff

def players_in_game(g):
    return g['players'].keys()

def player_role(g, user_id):
    return g['players'].get(user_id).get('role')

def player_status(g, user_id):
    return g['players'].get(user_id).get('status')

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

def is_valid_action(user_id, action, g, target=None):
    """
    For game actions only.
    user_id, action, game state
    -> (True/False, message)
    """
    def vote():
        pass
    def kill():
        # 1) Make sure player who made the command
        # is a werewolf
        # Only werewolf can use kill. (for now)
        if player_role(g, user_id) != 'w':
            return False, 'not a werewolf'
        # 2) Kill command only valid at night.
        if get_current_round(g) != 'night':
            return False, 'not at night'
        # 3) Target must be in game.

        # 4) Target must be alive.

        pass
    def seer():
        return False

    if target==None:
        """
        No current role that
        has no target.
        """
        return False

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

