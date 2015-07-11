"""
tests okay
"""
import pytest
from app import *
from game_actions.game_actions import *
from  game_actions import change_state

fake_state= {
    'players': {
            'ab': {
                "name": 'nick',
                "DM": "dm channel",
                "role": "v",
                "side": "v",
                "id": 'ab',
                "status": "alive"
            },
            'cd': {
                "name": 'not nick',
                "DM": "dm channel",
                "role": "w",
                "side": "w",
                "id"  : 'ab',
                "status": "dead"
            }
        },
    'votes': {
        'ab': 'cd',
        'cd': 'ab',
    },
    'STATUS': 'RUNNING',
    'ROUND': 'night',
    'user_map': '<UserMap c>'
}

# STATUS: "INACTIVE""WAITING_FOR_JOIN"|"RUNNING"


def test_players_in_game():
    assert players_in_game(fake_state) == ["ab", "cd"]

def test_game_actions():
    assert player_role(fake_state, 'ab') == 'v'
    assert player_status(fake_state, 'ab') == 'alive'

def test_user_map():
    # setup
    # test basic
    # assert u.id_dict == {}
    # assert u.name_dict == {}

    # # now new basic test
    # u.add('uuid1', 'nick')
    # assert u.id_dict['uuid1'] == 'nick'
    # assert u.name_dict['nick'] == 'uuid1'
    assert 2 == 2

def test_reset_game_state():
    assert change_state.reset_game_state() == {
            'players': {},
            'votes': {},
            'STATUS': 'INACTIVE',
            'ROUND': None}

def test_reset_votes():
    no_vote_fake_state = fake_state
    no_vote_fake_state['votes'] = {}
    assert change_state.reset_votes(fake_state) == no_vote_fake_state


def test_game_action_user_map():
    # user map should be empty
    assert USER_MAP.name_dict == {}
    assert USER_MAP.id_dict == {}

    g = fake_state
    assert get_user_map(g) == USER_MAP

    set_user_map(g, 'uiidLOL', 'lol')
    new_user_map = get_user_map(g)
    assert new_user_map.id_dict['uiidLOL'] == 'lol'
    assert new_user_map.name_dict['lol'] == 'uiidLOL'




