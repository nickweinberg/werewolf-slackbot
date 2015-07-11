"""
" all game state change
" in here.
"""



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
