from abc import ABC, abstractmethod

class Figure(ABC):
    def __init__(self, figure, map_jso):
        self.figure = figure
        self.map_jso = map_jso

    @abstractmethod
    def move(self, to_x, to_y):
        return True


def kill(map_jso, target, socketio=None):
    if target is None:
        return False
    figures = map_jso['status']['figures']
    map_jso['status']['figures'] = [figure for figure in figures if figure != target]
    return True  # succefull

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
        hungry = ((delta_x == 1) and kill(self.map_jso, target)),
        return ((delta_x == 0) and (
                (delta_y == 1) or
                (delta_y == 2 and self.figure['moved'] == False))
                ) or hungry


class Horse(Figure):
    def move(self, to_x, to_y):
        delta_x, delta_y = delta(to_x, to_y, self.map_jso, self.figure)
        return (abs(delta_x) == 1 and abs(delta_y) == 2) or (abs(delta_x) == 2 and abs(delta_y) == 1)


class Bishop(Figure):
    def move(self, to_x, to_y):
        delta_x, delta_y = delta(to_x, to_y, self.map_jso, self.figure)
        return abs(delta_x) == abs(delta_y)

class Tower(Figure):
    def move(self, to_x, to_y):
        view =self.map_jso['status']['players'][self.figure['color']]['view']
        delta_x, delta_y = mview(to_x - self.figure['x'],to_y - self.figure['y'], view)
        return (delta_x == 0) or (delta_y == 0)


class Queen(Figure):
    def move(self, to_x, to_y):
        view = self.map_jso['status']['players'][self.figure['color']]['view']
        delta_x, delta_y = mview(to_x - self.figure['x'],to_y - self.figure['y'], view)
        return (abs(delta_x) == abs(delta_y)) or (delta_x == 0) or (delta_y == 0)


class King(Figure):
    def move(self, to_x, to_y):
        view =self.map_jso['status']['players'][self.figure['color']]['view']
        delta_x, delta_y = mview(to_x - self.figure['x'],to_y - self.figure['y'], view)
        return (abs(delta_x) <= 1) and (abs(delta_y) <= 1)

FIGURE_CLASSES = {
    'pawn': Pawn,
    'king': King,
    'bishop': Bishop,
    'tower': Tower,
    'queen': Queen,
    'horse': Horse,
}