"""
Test sending data to process_message.
"""


import pytest
from plugins.werewolf import app
from plugins.werewolf.user_map import get_user_map, set_user_map, reset_user_map

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
    return {
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
        }


def setup_users(g):
    # for users in g
    # setup an appropriate user map.
    for player in g['players'].keys():
        set_user_map(g, player, g['players'][player]['name'])

def tear_down():
    reset_user_map()

def test_setup_users():
    night_g = get_fake_game_state()
    setup_users(night_g)
    test_user_map = get_user_map(night_g)

    players = night_g['players'].keys()

    p1_id = players[0]
    p2_id = players[1]
    assert test_user_map.id_dict[p1_id] == 'nick'
    assert test_user_map.id_dict[p2_id] == 'not_nick'

    assert test_user_map.name_dict['nick'] == p1_id
    assert test_user_map.name_dict['not_nick'] == p2_id

    tear_down()

def test_basic_input():
    fake_message = {'text': 'sup noob', 'user':'ab'}
    night_g = get_fake_game_state()
    result = app.process_message(fake_message, night_g)

    assert result == None

    tear_down()

def test_no_vote_target_input():
    fake_message = {'text': '!vote', 'user': 'ab'}
    night_g = get_fake_game_state()
    setup_users(night_g)
    result = app.process_message(fake_message, night_g)
    assert result == 'Not a valid command.'

    tear_down()

def test_vote_user_not_in_game_input():
    fake_message = {'text': '!vote cd', 'user': 'cat'}
    night_g = get_fake_game_state()
    setup_users(night_g)
    message = app.process_message(fake_message, night_g)
    assert message  == 'User not in the game.'

    tear_down()

def test_night_vote_input():
    fake_message = {'text': '!vote not_nick', 'user': 'ab'}
    night_g = get_fake_game_state()

    setup_users(night_g)
    message = app.process_message(fake_message, night_g)
    assert message == 'It is not day.'

    tear_down()


def test_day_voting_input():
    fake_message = {'text': '!vote not_nick', 'user': 'ab'}
    user_name = 'nick'
    target_name = 'not_nick'

    day_g = get_fake_game_state()
    day_g['ROUND'] = 'day'
    setup_users(day_g)

    assert day_g['votes'] == {}

    message = app.process_message(fake_message, day_g)

    assert message == user_name + ' voted for ' + target_name
    tear_down()
