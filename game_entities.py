import os
import shutil
import string
import uuid
import random

from flask import json


def get_uuid():
    return  uuid.uuid4().hex

games = set()

def new_game_code():
    global games
    while True:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
        if code not in games:
            games.add(code)
            return code.lower()

def remove_game(game_code):
    global games
    games.remove(game_code)

class Player:
    def __init__(self, starter=False, name=None):
        self.player_uuid = get_uuid()
        self.name = name

    def load_player(self):
        return {
            'name': self.name,
            'player_uuid': self.player_uuid
        }


class Map():
    def __init__(self):
        self.map_name = None
        self.players = None

    def create_map(self, map_name):
        self.map_name = map_name
        self.players = set()

    def get_color(self):
        rand_color = random.sample(self.colors, 1)[0]
        self.colors.remove(rand_color)
        return rand_color

    @staticmethod
    def init_map(code:str,map_name):
        source_path = f"./static/maps/{map_name}.json"
        destination_dir = f"./games/{code}"
        os.makedirs(destination_dir, exist_ok=True)

        game_map_path = os.path.join(destination_dir, "map.json")
        game_path = os.path.join(destination_dir, "game.json")

        shutil.copy2(source_path, game_map_path)
        with open(game_path, "w+") as f:
            json.dump({'map_name': map_name}, f)

    def load_map(self):
        players= {player.color: player.load_player() for player in self.players}
        return {self.map_name:{players}}



class Game():
    def __init__(self):
        self.code = None

    def create_new(self, data):
        if data is None:
            data = {}
        self.code = new_game_code()
        Map.init_map(self.code, data.get('map_name', 'chess_classic'))

    def add_player(self, player, color=None):
        self.players.add(player)
        player.color = self.get_color(color)

    @staticmethod #TODO znicit
    def get_chat():
        chat  = {'Chat': [
            {'black': "ahoj"},
            {'white': "no nazdar"}
        ]}
        return chat

    def get_json(self):
        return {
            'Map': self.load_map(),
            'Chat': self.get_chat()
        }

    def save_game(self):
        with open(f"/games/{self.code}/.json", 'w') as f:
            map_json = self.load_map()
            chat = self.chat.get_json()
            json.dump(self.get_json(), f)

    def load_game(self, game):
        with open(f"/games/{game.code}.json", 'w') as f:
            all = json.load(f)

