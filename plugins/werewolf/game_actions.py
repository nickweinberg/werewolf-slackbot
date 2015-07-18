"""
All game actions.
"""
from change_state import update_game_state, get_game_state
from send_message import send_message
import random
import copy
from collections import Counter
import time

from user_map import UserMap, get_user_name
from validations import mod_valid_action, is_valid_action

from status import (
        players_in_game,
        player_in_game,
        is_player_alive,
        alive_for_village,
        alive_for_werewolf,
        for_werewolf,
        player_role,
        player_side,
        player_status,
        has_voted,
        did_everyone_vote,
        get_all_alive,
        get_all_votes,
        get_current_round,
)


u = UserMap()

###############
# UI Commands #
###############

def list_players(g, user_id, *args):
    """

    * args is args to command list
    g -> string to Slack of players
      -> "\n".join([list of players])

      "player_name"|"status"

    """
    u = UserMap()

    # gets all names.
    return '\n'.join([u.get(user_id=p_id) + ' | ' + player_status(g, p_id)
                    for p_id in players_in_game(g)]), None



def list_votes(g, *args):
    """
    Print a list of all the people alive.

    votes is a dictionary with-
    key: voter_id
    value: voted_on_id

    """
    votes = get_all_votes(g)
    out_list = []
    if votes:
        u = UserMap()
        # turn id's into names
        # voter ' voted ' votee
        for v_id in votes.keys():
            voter_name = u.get(user_id=v_id)
            votee_name = u.get(user_id=votes[v_id])
            if votee_name:
                tmp = voter_name + ' voted ' + votee_name
            else:
                tmp = voter_name + ' passed.'
            out_list.append(tmp)

        return '\n'.join(out_list), None

    return 'Cannot list votes now.', None

""" fn's to add to crontable """
def annoy():
    check_bool, msg = check()
    if not check_bool:
        # not time to start countdown
        return msg, None
    print('hi')

def start_countdown(g, user_id, *args):
    """
    If during day and waiting on one more player to vote.

    Messages that player.

    If they take too long, their vote becomes a pass.

    """
    import threading
    def check():
        # who hasn't voted.
        # if round is still day
        check_g = get_game_state() # make sure state hasn't changed.
        result, message = mod_valid_action(user_id, 'countdown', check_g)
        if not result:
            return False, message

        all_alive = get_all_alive(g)
        yet_to_vote_list = [
                p_id for p_id in all_alive
                if not has_voted(g, p_id)]

        if len(yet_to_vote_list) > 1:
            return False, 'Countdown cannot start now.'

        yet_to_vote = yet_to_vote_list[0]
        return True, yet_to_vote

    def callback_vote():
        check_bool, yet_to_vote = check()
        print('checking vote')
        print(check_bool, yet_to_vote)
        if check_bool:
            check_g = get_game_state()
            send_message(player_vote(check_g, yet_to_vote, ['vote', 'pass'])[0])

    check_bool, msg = check()
    if not check_bool:
        # not time to start countdown
        return msg, None

    print('sending message')
    message_str = 'Countdown started. *20 seconds* left.\n ' + u.get(user_id=msg) + ' please vote. Or your vote will be passed.'

    t = threading.Timer(5.0, callback_vote)
    t.start()

    return message_str, None


################
# Game Actions #
################

def create_game(g, user_id, *args):
    """
    Reset state.
    Let people join.
    annouce

    STATUS -> "WAITING_FOR_JOIN"

    """

    # testing if i can append to outputs here.

    # Can only create a game
    #   if g['STATUS'] == 'INACTIVE'
    result, message = mod_valid_action(user_id, 'create', g)
    if result:
        # allowed to create game
        if g['STATUS'] != 'INACTIVE':
            return 'Can not create new game.', None
        # reset game state.
        new_g = update_game_state(g, 'reset_game_state')
        # change game status to WAITING
        new_g = update_game_state(new_g, 'status', status='WAITING_FOR_JOIN')
        # send message to channel
        return '_Waiting for players..._ \n*Type !join to join.*', None
    else:
        return message, None # return error message, and basic channel.


def start_game(g, user_id, *args):
    """
    Check if enough players.
    (optional) Pick config setup that works w/ num of players.
    Outut to channel (@channel) game is starting.
    Assign Roles.
    Message Users their roles.

    STATUS -> "RUNNING"
    """
    # can only start a game
    #   if enough players
    #   if g['STATUS'] == 'WAITING_FOR_JOIN'

    result, message = mod_valid_action(user_id, 'start', g)
    if not result:
        # cant start
        print(result, message)
        return message, None

    # tell everyone the game is starting
    send_message("@channel: Game is starting...")
    """ message everyone details of game. """
    players = players_in_game(g)
    num_werewolves = 1 # only one for now.

    p1_str = "_There are *%d* players in the game._\n" % len(players)
    p2_str = "There are *%d* werewolves in the game._" % num_werewolves
    send_message(p1_str + p2_str)
    g = update_game_state(g, 'status', status='RUNNING')
    # Go through and assign everyone in the game roles.
    new_g = assign_roles(g) # updated state w/ roles
    message_everyone_roles(new_g)

    # go to night round.

    return start_day_round(new_g), None # idk when this will return.



def assign_roles(g):
    players = players_in_game(g)
    create_wolf = random.choice(players) # id of player
    new_g = copy.deepcopy(g)

    for player in players:
        if player == create_wolf:
            new_g = update_game_state(new_g, 'role', player=player, role='w')
        else:
            new_g = update_game_state(new_g, 'role', player=player, role='v')
    return new_g


def message_everyone_roles(g):
    """
    for every player in game.
    DM them their roles.

    """
    u = UserMap()
    # player_role(g, player_id)

    all_alive = [(u.get(user_id=p_id, DM=True), player_role(g, p_id))
                for p_id in players_in_game(g)
                    if is_player_alive(g, p_id)]

    print(all_alive)

    for im, role in all_alive:
        if role=='v':
            nice=" Plain Villager"
        elif role=='w':
            nice=" Werewolf. *Awoooo!*"
        elif role=='s':
            nice=" Seer."
        elif role=='b':
            nice=" Bodyguard."
        send_message(nice, channel=im)

def join(g, user_id, *args):
    """
    See if player is allowed to join.
    If so let add them to the game.

    """
    result, message = mod_valid_action(user_id, 'join', g)

    if not result:
        return message, None # could not join

    # if player successfully joins.
    u = UserMap()

    user_name = u.get(user_id=user_id)

    if not user_name:
        # user not in user_map yet
        # get_user_name polls slack and adds to user map
        user_name = get_user_name(user_id)

    # update state with new player
    mutated_g = update_game_state(g, 'join', player=user_id)

    # tell the channel the player joined.
    join_message = "%s joined the game." % user_name
    return join_message, None

def eat_player(g, user_id, *args):
    """
    ex. *args = (['kill', 'maksym'], )
    arg_list =
    target_name = args[1]

    user_name = u.id_dict.get(user_id)

    """
    arg_list = args[0]

    if len(arg_list) < 1: # no target no good
        return "Have to pick a target.", None
    elif len(arg_list) > 2: # too many args
        return "Not a valid command.", None
    else:
        u = UserMap() # get usermap

        target_name = arg_list[1]
        target_id =  u.get(name=target_name) # turn name into id
        result, message = is_valid_action(user_id, 'kill', g, target_name=target_name)
        if not result:
            # was not a valid kill
            return message, None
        else:
            # player is eaten
            # update state
            # changes targeted player's status to dead
            new_g = update_game_state(g, 'player_status', player=target_id, status='dead')
            # tell the players.
            eaten_str = "%s was eaten." % (target_name)
            return resolve_night_round(new_g, alert=eaten_str), None

def seer_player(g, user_id, *args):
    """
    NOT IMPLEMENTED.
    Player attemps to investigate.

    If is seer & night. returns message, channel is Direct Message to seer.

    ex. *args = (['seer', 'maksym'], )
    arg_list = args[0]
    target_name = args[1]
    """
    arg_list = args[0]

    if len(arg_list) < 1: # no target no good
        return "Have to pick a target.", None
    elif len(arg_list) > 2: # too many args
        return "Not a valid command.", None
    else:
        target_name = arg_list[1]
        target_id = u.get(name=target_name)
        #result, message = is_valid_action(user_id, 'seer', g, target_name=target_name)
        return 'Not Implemented', None


def make_end_round_str(g, alert=None, game_over=None):
    """
    g - game state
    alert - string of any alerts
    game_over - string of role that won, if game is over.
    """
    round_end_str = ''

    if alert:
        round_end_str += alert

    if game_over:
        if game_over == 'w':
            # werewolves won
            round_end_str += "\n Game Over. Werewolves wins.\n"

        elif game_over == 'v':
            # village wins
            round_end_str += "\n Game Over. Village wins.\n"

        # Display list of players and their roles
        round_end_str += '\n'.join(
                [u.get(user_id=p_id) + "%s | *%s*." % (u.get(user_id=p_id), player_role(g, p_id))
                    for p_id in players_in_game(g)])

    return round_end_str


def resolve_night_round(g, alert=None):
    """
    Makes sure everyone has done all their roles.

    - if yes
        see if game is over.
        if yes
            set game to over.
            display results.
        if no
            change round to day.
    """
    # TODO:  for each player in the game,
    # check if completed their action for the night.

    alive_v = alive_for_village(g)
    alive_w = alive_for_werewolf(g)

    if len(alive_w) >= len(alive_v):
        new_g = update_game_state(g, 'status', status='INACTIVE')
        # reset game state.
        new_g = update_game_state(new_g, 'reset_game_state')

        return  make_end_round_str(new_g, alert, 'w') # returns and sends message
    elif len(alive_w) == 0:
        new_g = update_game_state(g, 'status', status='INACTIVE')
        # reset game state.
        new_g = update_game_state(new_g, 'reset_game_state')

        return make_end_round_str(new_g, alert, 'v') # returns and sends message
    else:
        # turn it into morning and start day round.

        # idea:
        # game state has 'GAME_MESSAGES' : {'channel': <channel_id>, 'message': thing to say}
        # every night action adds game_message.
        # If all night actions have finished. Go through and send all those messages.
        # reset GAME_MESSAGES.

        round_end_str = make_end_round_str(g) + start_day_round(g)

        return round_end_str



def start_night_round(g):
    """
    set state to night round.
    print to screen

    """
    update_game_state(g, 'round', round='night')
    return "It is night time. \n Werewolf type_'/dm moderator !kill {who you want to eat}_ \n\n *Talking is NOT Allowed.*"

def start_day_round(g):
    update_game_state(g, 'round', round='day')
    return "It is now day time. \n type _!vote {username}_. If user has more than half the votes. They die."


def player_vote(g, user_id, *args):
    """
    ex. *args = (['vote', 'maksym'], )
    arg_list = args[0]
    target_name = arg_list[1]


    user_name = u.id_dict.get(user_id)

    """
    arg_list = args[0]

    if len(arg_list) < 1: # didn't vote
        return "Have to vote FOR someone.", None
    elif len(arg_list) > 2: # too many args
        return "Not a valid command.", None
    else:
        target_name = arg_list[1]
        target_id =  u.get(name=target_name) # turn name into id

        result, message = is_valid_action(user_id, 'vote', g, target_name=target_name)
        if not result:
            # was not a valid kill
            return message, None
        else:
            # player voted
            # update state
            # change votes to reflect their vote
            new_g = update_game_state(g, 'vote', voter=user_id, votee=target_id)

            # after each vote need to check if total
            # everyone has voted.
            if did_everyone_vote(new_g):
                # resolve vote round
                result_id = resolve_votes(new_g)
                if result_id:
                    # result is id of player
                    # set player status to dead.
                    result_name = u.get(user_id=result_id)

                    new_g_2 = update_game_state(new_g, 'player_status', player=result_id, status='dead')
                    # have to reset all the votes
                    new_g_3 = update_game_state(new_g_2, 'reset_votes')

                    # tell the players.
                    lynch_str = "%s was lynched." % (result_name)
                    # pass in game state before votes reset.
                    return resolve_day_round(new_g_2, alert=lynch_str), None

                else:
                    # list votes returns a tuple ('str', None)
                    return resolve_day_round(new_g, alert='*No one dies.*'), None
            else:
                # valid vote, but not everyone voted yet.
                # suggestion to list vote summary every vote.
                return list_votes(new_g)[0] + '\n\n' + message
            return message, None

def resolve_votes(g):
    """
    Everyone has voted.

    If anyone has more than half the votes.
    They die.

    If more than half the people passed then no one dies.

    votes is a dictionary
    key   - voter_id
    value - voted_on_id
    """
    votes = get_all_votes(g)
    # count up all the votes
    if votes:
        c = Counter(votes.values())
        # c.most_common()
        # [('b',2), ('a',1), ('c',1)]
        most_votes_id = c.most_common()[0][0]
        most_votes_count = c[most_votes_id]
        total_votes = len(votes.keys())
        if most_votes_count > total_votes // 2:
            # more than half the votes
            # they die.
            if most_votes_id == 'pass':
                return False # no one dies
            else:
                return most_votes_id

        else:
            return False

    return False # votes was none for some reason.



def resolve_day_round(g, alert=None):
    """
    Like resolve_night_round, but for the day!

    """
    alive_v = alive_for_village(g)
    alive_w = alive_for_werewolf(g)

    # we want to show vote results.
    vote_list_str = list_votes(g)[0] + '\n'

    if len(alive_w) >= len(alive_v):
        new_g = update_game_state(g, 'status', status='INACTIVE')
        new_g = update_game_state(new_g, 'reset_game_state')

        return  vote_list_str + make_end_round_str(new_g, alert, 'w') # returns and sends message

    elif len(alive_w) == 0:
        new_g = update_game_state(g, 'status', status='INACTIVE')
        new_g = update_game_state(new_g, 'reset_game_state')

        return  vote_list_str + make_end_round_str(new_g, alert, 'v') # returns and sends message
    else:
        # turn it into night and start night round

        round_end_str = vote_list_str + make_end_round_str(g) + start_night_round(g)
        return round_end_str


