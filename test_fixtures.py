import copy

def get_empty_game_state():
    # hi there
    # make mock game state.
    # we'll have several fixtures
    # and a basic one we can set up in each test.
    return {'players':{},
            'votes':{},
            'STATUS': 'INACTIVE',
            'ROUND': None
        }

def get_fake_game_state():
    return copy.deepcopy({
            'players': {
                'ab': {
                    'name': 'nick',
                    'DM': 'dm channel',
                    'role': 'v',
                    'side': 'v',
                    'status': 'alive'
                    },
                'cd': {
                    'name': 'not_nick',
                    'dm': 'dm channel',
                    'role': 'w',
                    'side': 'w',
                    'status': 'alive'
                 }
            },
            'votes': {},
            'STATUS': 'RUNNING',
            'ROUND': 'night'
        })



def tear_down():
    reset_user_map()


