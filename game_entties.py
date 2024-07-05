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
        self.colors = ['red', 'blue']

    def get_color(self):
        rand_color = random.sample(self.colors, 1)[0]
        self.colors.remove(rand_color)
        return rand_color

    def add_player(self, player):
        self.players.add(player)
        player.color = self.get_color()