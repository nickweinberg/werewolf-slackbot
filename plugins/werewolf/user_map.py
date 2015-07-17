import redis
import yaml
import json
from slackclient import SlackClient

##############
# user stuff #
##############

class UserMap:
    """
    So we don't have to keep track of two dictionaries.
    Easiest is just to keep one instance of this in the game state.

    We create this at the beginning of the game.

    So we can do -

    user_id -> name
    name -> user_id
    """
    def __init__(self):
        self.r_server = redis.Redis('localhost')

    def add(self, user_id, name, DM):
        """
        adds
        user_id -> name
        name -> user_id
        DM:user_id -> Direct Message channel.
        """
        self.r_server.hmset('users:game', {user_id: name, name: user_id, 'DM:'+user_id: DM})

    def get(self, user_id=None, name=None, DM=None):
        if DM and user_id:
            return self.r_server.hmget('users:game', 'DM:'+user_id)
        elif user_id:
            return self.r_server.hmget('users:game', user_id)
        elif name:
            return self.r_server.hmget('users:game', name)


def get_user_name(user_id):
    config = yaml.load(file('rtmbot.conf', 'r'))
    sc = SlackClient(config['SLACK_TOKEN'])
    u = UserMap()

    def poll_slack_for_user():
        user_obj = json.loads(sc.api_call('users.info', user=user_id))
        user_name = user_obj['user']['name']
        im = json.loads(sc.api_call('im.open', user=user_id))
        return user_name, im['channel']['id']

    try:
        user_name, im = poll_slack_for_user()
    except Exception as e:
        print(e)
        # try one more time.
        user_name, im = poll_slack_for_user()

    if user_name:
        u.add(user_id, user_name, im)
        return user_name


