
import pytest
from plugins.werewolf import app

from plugins.werewolf.user_map import get_user_map, set_user_map,reset_user_map

from plugins.werewolf.change_state import get_game_state
import copy


def setup_users(g):
    # for users in g
    # setup an appropriate user map.
    for player in g['players'].keys():
        set_user_map(g, player, g['players'][player]['name'])

def tear_down():
    reset_user_map()



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


def test_update_player_stats():
    fake_g = get_fake_game_state()


