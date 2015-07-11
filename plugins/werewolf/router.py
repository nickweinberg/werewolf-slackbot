from game_actions.game_actions import(
    create_game,
    start_game,
    list_players,
    join,
    eat_player,
    player_vote
)


def command_router(g, command, user_id):
    """
    command: list [command, args]
    user_id: user id
    g      : game state object.

    Router is a dictionary of functions.

    --- Game Logistics ---
    create(create_game)  - create a new game (starts moderator- alerts channel)
    join(player_join)    - player attempts to join a created game
    start(start_game)    - starts game, assigns roles, other setup.
    players(list_players)- list players in the game.

    --- Game Actions ---
    kill(eat_player)   - werewolf attempts to eat a player
    vote(player_vote)  - players attempts to vote.
    """
    router = {
        "create": create_game,
        'start': start_game,
        'players': list_players,
        "join": join,
        "kill": eat_player,
        "vote": player_vote
    }

    if router.get(command[0]):
        # command[0] is command (ie. 'kill' if user sent '!kill')
        command_fn = router[command[0]]
        # command[1] is args (ie. 'maksym' if user sent '!kill maksym')
        # passes it back to process_mesage.
        return command_fn(g, user_id, command[1:])
    else:
        return 'Not a valid command', None

