


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
        self.id_dict = {}
        self.name_dict = {}
        self.id_to_DM = {}

    def add(self, user_id, name, DM=None):
        """
        self.id_dict[user_id] = name
        self.name_dict[name] = user_id
        """
        if self.id_dict.get(user_id) and self.name_dict.get(name):
            # names aleady set
            return None
        else:
            self.id_dict[user_id] = name
            self.name_dict[name] = user_id

            if DM:
                # direct message channel
                self.id_to_DM[user_id] = DM

USER_MAP = UserMap()

def get_user_map(g):
    """
    Let's everyone get access to this delicious UserMap.

    Shouldn't let you have it (since it's probably not set)
    if game is INACTIVE.
    """
    if g['STATUS'] == 'INACTIVE':
        return None
    else:
        return USER_MAP

def set_user_map(g, user_id, name, DM=None):
    """
    Only way I'm letting you schmucks update user map.
    Gets USER_MAP.
    Adds new user.

    """
    u = get_user_map(g)
    u.add(user_id, name, DM)

def reset_user_map():
    """
    Only used for testing.
    """
    global USER_MAP
    USER_MAP = UserMap()

