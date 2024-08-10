import math
from abc import ABC, abstractmethod
import importlib


def free_place(x, y, map_jso):
    return all(figure['x'] != x or figure['y'] != y for figure in map_jso['status']['figures'].values())

def abs_delta(x, y, figure):
    return  x - figure['x'], y - figure['y'],

class Figure(ABC):
    def __init__(self, figure_id, figure, map_jso):
        self.id = figure_id
        self.figure = figure
        self.map_jso = map_jso

    @abstractmethod
    def move(self, to_x, to_y, target):
        return True

    @abstractmethod
    def after_move(self):
        return None


    def free_gcd_path(self, to_x, to_y): #for all figures with symetric move
        delta_x, delta_y = abs_delta(to_x, to_y, self.figure)
        gcd = math.gcd(delta_x, delta_y)
        d_x = delta_x/gcd
        d_y = delta_y/gcd
        i = 1
        while True:
            p_x =  i*d_x
            p_y =  i*d_y
            print(p_x, p_y)
            print(self.figure['x'] + p_x, self.figure['y'] + p_y)
            if p_x == delta_x and p_y == delta_y:
                return True
            if not free_place(self.figure['x'] + p_x, self.figure['y'] + p_y, self.map_jso):
                print("cesta je blokovana")
                return False
            i += 1

def kill(map_jso, target_key, socketio=None) -> bool: #killed?
    if target_key is None:
        return False
    figures = (map_jso['status']['figures'])
    map_jso['status']['figures'] = {key:value for key, value in figures.items() if key != target_key}
    print(f"Killed {target_key}")
    return True

def mview(x, y ,view):
    if view == 0:
        return x, -y
    if view == 1:
        return y, x
    if view == 2:
        return -x, y
    if view == 3:
        return -y, -x

def rel_delta(x, y, map_jso, figure):
    view = map_jso['status']['players'][figure['color']]['view']
    return  mview(x - figure['x'], y - figure['y'], view)

def get_fig_class(fig_type: str):
    try:
        module = importlib.import_module(f'figure_types.{fig_type}')
        return getattr(module, fig_type.capitalize())
    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Unknown figure type: {fig_type} {e}") from e


def exists(x, y, map_jso):
    if map_jso['start']['load_type'] == 'chess_classic':
        if 0 <= x < map_jso['start']['size'] and 0 <= y < map_jso['start']['size']:
            return True
        return False
    else:
        raise NotImplementedError("Not implemented for this load type")
