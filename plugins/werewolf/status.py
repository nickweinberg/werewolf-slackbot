"""
Game status functions

"""

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

def alive_for_village(g):
    players = players_in_game(g)
    return [p_id for p_id in players
            if is_player_alive(g, p_id) and
            player_side(g, p_id)=='v']

def alive_for_werewolf(g):
    players = players_in_game(g)
    return [p_id for p_id in players
            if is_player_alive(g, p_id) and
            player_side(g, p_id)=='w']

def for_werewolf(g):
    players = players_in_game(g)
    return [p_id for p_id in players
            if player_side(g, p_id=='w')]

def player_role(g, user_id):
    return g['players'].get(user_id).get('role')

def player_side(g, user_id):
    return g['players'].get(user_id).get('side')

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


def did_everyone_vote(g):
    """
    g - game state
    -> True/False

    return whether everyone who can vote
    has voted.
    """

    # only alive players
    alive = get_all_alive(g)

    alive_and_voted = [p_id
                        for p_id in alive
                        if has_voted(g, p_id)]

    return len(alive_and_voted) == len(alive)

def get_all_alive(g):
    return [p_id
            for p_id in players_in_game(g)
            if is_player_alive(g, p_id)]

def does_have_night_action(g, user_id):
    """
    players with night actions (atm)

    w: werewolf (or just alpha wolf)
    s: seer
    b: bodyguard
    c: chupa

    """
    night_action_list = ['w', 's', 'b', 'c']
    return player_role(g, user_id) in night_action_list





def get_all_votes(g):
    """
    All the votes.
    """
    # shouldn't get called if it is not the day
    # or game is inactive. but here just in case.
    if get_current_round(g) != 'day':
        return None
    elif g['STATUS'] == 'INACTIVE':
        return None

    return g.get('votes')

def get_current_round(g):
    """
    returns game state's current round:
        aka 'night' or 'day'
    """
    return g['ROUND']
