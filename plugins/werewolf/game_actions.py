"""
All game actions.

"""
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
    player_ids = players_in_game(g)
    player_names




