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
    players = set()
    def __init__(self):
        self.code = new_game_code()
    def add_player(self,player):
        players.add(player)