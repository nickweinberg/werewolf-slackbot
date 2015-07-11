"""
tests okay

"""
import pytest
from plugins.werewolf.game_actions import *
from plugins.werewolf.main import (
        UserMap,
        reset_game_state
        )


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
    u = UserMap()
    # test basic
    assert u.id_dict == {}
    assert u.name_dict == {}

    # now new basic test
    u.add('uuid1', 'nick')
    assert u.id_dict['uuid1'] == 'nick'
    assert u.name_dict['nick'] == 'uuid1'

def test_reset_game_state():
    assert reset_game_state() == {
            'players': {},
            'votes': {},
            'STATUS': 'INACTIVE',
            'ROUND': None}

def test_reset_votes():
    no_vote_fake_state = fake_state
    no_vote_fake_state['votes'] = {}
    assert reset_votes(fake_state) == no_vote_fake_state

