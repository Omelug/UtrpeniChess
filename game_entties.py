import string
import uuid
import random

def get_uuid():
    return  uuid.uuid4().hex  #


def new_game_code():
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
    return code.lower()

class Player():
    def __init__(self, starter=False):
        self.player_uuid = get_uuid()
        self.starter = starter

class Game():
    def __init__(self):
        self.players = set()
        self.code = new_game_code()

    def get_color(self):

    def add_player(self, player):
        self.players.add(player)
        player.color = self.get_color()
        return random.choice(['red', 'blue'])