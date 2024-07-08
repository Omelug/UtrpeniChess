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

class User:
    @staticmethod
    def init_users(game_code, colors, colors_view):
        game_path = os.path.join(f"./games/{game_code}", "users.json")
        with open(game_path, "w+") as f:
            print(set(colors))
            json.dump({"view": colors_view, "colors": list(colors), "players":{}}, f)

class Chat:
    @staticmethod
    def init_chat(game_code):
        game_path = os.path.join(f"./games/{game_code}", "chat.json")
        with open(game_path, "w+") as f:
            json.dump([{'Server':{"msg":"START"}}], f)


def get_name(game_code, player_uuid):
    with open(f"./games/{game_code}/users.json", 'r') as f:
        jso = json.load(f)
        for color in jso['players'].keys():
            if jso['players'][color]['uuid'] == player_uuid:
                return jso['players'][color]['name']
    return "Anon"


def send_message(game_code,name, msg):
    chat_file_path = f"./games/{game_code}/chat.json"
    with open(chat_file_path, 'r+') as chat_file:
        chat_data = json.load(chat_file)
        chat_data.append({name: {"msg": msg}})

        chat_file.seek(0)
        json.dump(chat_data, chat_file)
        chat_file.truncate()

def save(config_name , game_code, map_json):
    with open(f"./games/{game_code}/{config_name}.json", 'w') as f:
        json.dump(map_json, f)
def load(config_name,game_code):
    with open(f"./games/{game_code}/{config_name}.json", 'r') as f:
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

        players = load('map',self.code)['status']['players']
        colors_view = { key:players[key]['view'] for key in players.keys()}
        User.init_users(self.code, colors=players.keys(), colors_view=colors_view)


    def connect_player(self, player_uuid, color='white', name=None):
        jso = load('users',self.code)

        for col in jso['players'].keys():
            uuid = jso['players'][col]['uuid']
            if uuid == player_uuid:
                selected = jso['players'][col]
                break # player already have color
        else:
            if len(jso['colors']) == 0:
                print("Game is full")
                return False

            if color in jso['colors']:
                add_new_color = jso['colors'].remove(color) # give player new color
            else:
                add_new_color = jso['colors'].pop(0) # give player pref_color
            jso['players'][add_new_color] = {'uuid': player_uuid, 'name': "Anon"}
            selected = jso['players'][add_new_color]

        selected['uuid'] = player_uuid
        if name is not None and name != "":
            selected['name'] = name
        save('users', self.code, jso)
        return True
