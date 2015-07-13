"""
Test sending data to process_message.
"""


import pytest
from plugins.werewolf import app
from plugins.werewolf.user_map import get_user_map, set_user_map, reset_user_map
from plugins.werewolf.change_state import get_game_state, set_game_state
import copy

from test_fixtures import get_fake_game_state, get_empty_game_state, all_vote_but_one_state

def tear_down():
    reset_user_map()

def setup_users(g):
    # for users in g
    # setup an appropriate user map.
    for player in g['players'].keys():
        set_user_map(g, player, g['players'][player]['name'])

def test_setup_users():
    night_g = get_fake_game_state()
    setup_users(night_g)
    test_user_map = get_user_map(night_g)

    players = night_g['players'].keys()

    players.sort()
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
    result = app.process_message(fake_message, g=night_g)
    assert result == 'Not a valid command.'

    tear_down()

def test_vote_user_not_in_game_input():
    fake_message = {'text': '!vote cd', 'user': 'cat'}
    night_g = get_fake_game_state()
    setup_users(night_g)
    message = app.process_message(fake_message, g=night_g)
    assert message  == 'User not in the game.'

    tear_down()

def test_night_vote_input():
    fake_message = {'text': '!vote not_nick', 'user': 'ab'}
    night_g = get_fake_game_state()


    setup_users(night_g)
    message = app.process_message(fake_message, g=night_g)
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

    message = app.process_message(fake_message, g=day_g)
    assert day_g['votes'] == {} # shouldn't mutate day_g

    assert message == user_name + ' voted for ' + target_name
    new_day_g = get_game_state()
    assert new_day_g['votes'] == {'ab': 'cd'} # now it should be mutated

    # shouldn't be allowed to vote again.
    fake_message = {'text': '!vote not_nick', 'user': 'ab'}
    message = app.process_message(fake_message, g=new_day_g)
    assert message == 'You have already voted.'


    tear_down()

def test_kill_input():
    good_kill_msg = {'text': '!kill nick', 'user': 'cd'}
    no_target_msg = {'text': '!kill', 'user': 'cd'}
    too_many_targets_msg = {'text': '!kill you me and this', 'user': 'cd'}
    invalid_target_msg = {'text': '!kill yolo', 'user': 'cd'}
    not_wolf_msg = {'text': '!kill not_nick', 'user': 'ab'}

    night_g = get_fake_game_state()

    setup_users(night_g)
    message = app.process_message(too_many_targets_msg, g=night_g)
    assert message == 'Not a valid command.'

    message = app.process_message(no_target_msg, g=night_g)
    assert message == 'Not a valid command.'

    message = app.process_message(invalid_target_msg, g=night_g)
    assert message == 'User not in the game.'

    message = app.process_message(not_wolf_msg, g=night_g)
    assert message == 'Not allowed.'

    message_str = app.process_message(good_kill_msg, g=night_g)
    message_list = message_str.split('\n')
    assert message_list[0] == 'nick was eaten.'

    tear_down()


def test_reset_game():
    g = all_vote_but_one_state()
    setup_users(g)


    vote_lock_msg = {'text': '!vote nick', 'user': 'cd'}
    # g has all votes except for "cd" vote
    # "cd" is werewolf once he locks vote, game should be
    # over for the village.

    message_str = app.process_message(vote_lock_msg, g=g)
    message_list = message_str.split('\n')

    assert message_list[0] == 'not_nick was lynched.'

    new_g = get_game_state()
    print(new_g)
    assert new_g['STATUS'] == 'INACTIVE'
    assert new_g['votes'] == {}
    assert new_g['players'] == {}
    assert new_g['ROUND'] == None


    tear_down()
