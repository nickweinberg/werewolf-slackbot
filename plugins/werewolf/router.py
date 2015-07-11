from game_actions import (
    create_game,
    start_game,
    list_players,
    join,
    eat_player,
    player_vote
)



def command_router(command, user_id):
    """
    command: list [command, args]
    user_id: user id

    Router is a dictionary of functions.

    --- Game Logistics ---
    create(create_game)  - create a new game (starts moderator- alerts channel)
    join(player_join)    - player attempts to join a created game
    start(start_game)    - starts game, assigns roles, other setup.
    players(list_players)- list players in the game.

    --- Game Actions ---
    kill(eat_player)   - werewolf attempts to eat a player
    vote(player_vote)
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
        command_fn = router[command[0]]
        command_fn(user_id, command[1:])



