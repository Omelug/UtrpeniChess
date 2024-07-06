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

        shutil.copy2(source_path, game_map_path)
        return map_name


def save_map(game_code, map_json):
    with open(f"./games/{game_code}/map.json", 'w') as f:
        json.dump(map_json, f)

def load_map(game_code):
    with open(f"./games/{game_code}/map.json", 'r') as f:
        return json.load(f)

class Chat:
    @staticmethod
    def init_chat(game_code):
        game_path = os.path.join(f"./games/{game_code}", "chat.json")
        with open(game_path, "w+") as f:
            json.dump([{'Server':{"msg":"START"}}], f)

def load_chat(self,):
    with open(f"./games/{self.code}/chat.json", 'r') as f:
        return json.load(f)

class Game:
    def __init__(self, code=None):
        self.code = code

    @staticmethod
    def init_game(game_code, map_name):
        game_path = os.path.join(f"./games/{game_code}", "game.json")
        with open(game_path, "w+") as f:
            json.dump({'map_name': map_name}, f)

    def create_new(self, data):
        if data is None:
            data = {}
        self.code = new_game_code()
        map_name=data.get('map_name', 'chess_classic')

        Map.init_map(self.code, map_name)
        Game.init_game(self.code, map_name=map_name)
        Chat.init_chat(self.code)

    @staticmethod #TODO znicit
    def get_chat():
        chat  = {'Chat': [
            {'black': "ahoj"},
            {'white': "no nazdar"}
        ]}
        return chat

    def save_game(self, json_object):
        with open(f"./games/{self.code}/game.json", 'w') as f:
           json.dump(json_object, f)

    def load_game(self):
        with open(f"./games/{self.code}/game.json", 'r') as f:
            return json.load(f)

    def connect_player(self, player_uuid, color='white', name=None):
        jso = load_map(self.code)

        colors = jso['status']['players'].keys()

        pref_color = False
        selected = None
        for col in colors:
            uuid = jso['status']['players'][col]['uuid']
            if uuid == player_uuid:
                selected = jso['status']['players'][col]
                break
            if uuid is None:
                if pref_color is False:
                    if col == color:
                        pref_color = True
                    selected = jso['status']['players'][col]

        if selected is not None:
            selected['uuid'] = player_uuid
            if name is not None:
                selected['name'] = name
            save_map(self.code, jso)
            return True

        print("Game is full")
        return False
