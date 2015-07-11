"""
tests okay

"""
import pytest
from plugins.werewolf.game_actions import *


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
    'STATUS': 'RUNNING'
}

# STATUS: "INACTIVE""WAITING_FOR_JOIN"|"RUNNING"


def test_players_in_game():
    assert players_in_game(fake_state) == ["ab", "cd"]

def test_game_actions():
    assert player_role(fake_state, 'ab') == 'v'
    assert player_status(fake_state, 'ab') == 'alive'

