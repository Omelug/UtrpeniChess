import math
from abc import ABC, abstractmethod


def free_place(x, y, map_jso):
    return all(figure['x'] != x or figure['y'] != y for figure in map_jso['status']['figures'].values())


class Figure(ABC):
    def __init__(self, figure_id, figure, map_jso):
        self.id = figure_id
        self.figure = figure
        self.map_jso = map_jso

    @abstractmethod
    def move(self, to_x, to_y, target):
        return True

    def free_gcd_path(self, delta_x, delta_y):
        gcd = math.gcd(delta_x, delta_y)
        d_x = delta_x/gcd
        d_y = delta_y/gcd
        i = 1
        while True:
            p_x =  i*d_x
            p_y =  i*d_y
            if not free_place(self.figure['x'] + p_x, self.figure['y'] + p_y, self.map_jso):
                return False
            if p_x == delta_x and p_y == delta_y:
                return True
            i += 1

def kill(map_jso, target, socketio=None) -> bool: #killed?
    if target is None:
        return False
    figures = map_jso['status']['figures']
    map_jso['status']['figures'] = {key: value for key, value in figures.items() if key != target}
    return True

def mview(x, y ,view):
    if view == 3:
        return x, y
    if view == 4:
        return y, -x
    if view == 1:
        return -x, -y
    if view == 2:
        return -y, x

def delta(x, y, map_jso, figure):
    view = map_jso['status']['players'][figure['color']]['view']
    return  mview(x - figure['x'], y - figure['y'], view)

class Pawn(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = delta(to_x, to_y, self.map_jso, self.figure)
        first_step = (delta_y == 2 and self.figure['moved'] == False)
        if first_step:
            self.map_jso['status']['figures'][self.id]['moved'] = True
        print(first_step)
        hungry = ((abs(delta_x) == 1) and delta_y == 1 and kill(self.map_jso, target))
        print(hungry)
        return ((delta_x == 0) and (delta_y == 1)) or first_step or hungry


class Horse(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = delta(to_x, to_y, self.map_jso, self.figure)
        return (abs(delta_x) == 1 and abs(delta_y) == 2) or (abs(delta_x) == 2 and abs(delta_y) == 1)


class Bishop(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = delta(to_x, to_y, self.map_jso, self.figure)
        valid_by_type = abs(delta_x) == abs(delta_y)
        return valid_by_type and self.free_gcd_path(delta_x, delta_y)

class Tower(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = delta(to_x, to_y, self.map_jso, self.figure)
        return (delta_x == 0) or (delta_y == 0) and self.free_gcd_path(delta_x, delta_y)


class Queen(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = delta(to_x, to_y, self.map_jso, self.figure)
        return (abs(delta_x) == abs(delta_y)) or (delta_x == 0) or (delta_y == 0) and self.free_gcd_path(delta_x, delta_y)


class King(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = delta(to_x, to_y, self.map_jso, self.figure)
        return (abs(delta_x) <= 1) and (abs(delta_y) <= 1)

FIGURE_CLASSES = {
    'pawn': Pawn,
    'king': King,
    'bishop': Bishop,
    'tower': Tower,
    'queen': Queen,
    'horse': Horse,
}