import math
from abc import ABC, abstractmethod


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

class Pawn(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        first_step = (delta_y == 2 and self.figure['moved'] == False)
        hungry = ((abs(delta_x) == 1) and delta_y == 1 and kill(self.map_jso, target))
        print(delta_x, delta_y, first_step, hungry)

        result = ((delta_x == 0) and (delta_y == 1)) or first_step or hungry
        if result and not self.map_jso['status']['figures'][self.id]['moved']:
            self.map_jso['status']['figures'][self.id]['moved'] = True
        return result


class Horse(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        return (abs(delta_x) == 1 and abs(delta_y) == 2) or (abs(delta_x) == 2 and abs(delta_y) == 1)


class Bishop(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        valid_by_type = abs(delta_x) == abs(delta_y)
        free_path = self.free_gcd_path(to_x, to_y)
        return valid_by_type and free_path

class Tower(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        free_path = self.free_gcd_path(to_x, to_y)
        return (delta_x == 0) or (delta_y == 0) and free_path


class Queen(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        print(f"{delta_x=} {delta_y=}")
        free_path = self.free_gcd_path(to_x, to_y)
        return (abs(delta_x) == abs(delta_y)) or (delta_x == 0) or (delta_y == 0) and free_path


class King(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        return (abs(delta_x) <= 1) and (abs(delta_y) <= 1)

FIGURE_CLASSES = {
    'pawn': Pawn,
    'king': King,
    'bishop': Bishop,
    'tower': Tower,
    'queen': Queen,
    'horse': Horse,
}