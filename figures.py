import math
from abc import ABC, abstractmethod
import importlib
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def free_place(x, y, map_jso):
    """
    :param x:
    :param y:
    :param map_jso:
    :return: free?
    """
    return all(figure['x'] != x or figure['y'] != y for figure in map_jso['status']['figures'].values())

def get_figure_o(active_fig, figure, map_jso):
    return get_fig_class(figure['fig_type'])(active_fig, figure, map_jso)

#def checked(x, y, map_jso, color_exclude=None):
#    return any((figure['color'] != color_exclude and color_exclude, get_figure_o(fig_id, figure, map_jso).move(to_x=x,to_y=y,realize=False)) for fig_id, figure in map_jso['status']['figures'].items())

def checked(x, y, map_jso, color_exclude=None):
    for fig_id, figure \
        in ((fig_id, figure)\
        for fig_id, figure in map_jso['status']['figures'].items()\
        if figure['color'] != color_exclude):

        #print(f"Figure ID: {x},{y}")
        #print(figure['color'] ,"   ", color_exclude)
        result = get_figure_o(fig_id, figure, map_jso).move(to_x=int(x), to_y=int(y), realize=False)
        if result:
            #print(f"Figure ID: {fig_id}, Figure: {figure}, Move Result: {result}")
            return True
    return False

def get_fig_at(x, y, map_jso):
    for fig_id, figure in map_jso['status']['figures'].items():
        if figure['x'] == x and figure['y'] == y:
            return fig_id, figure
    return None, None

def abs_delta(x, y, figure):
    return  x - figure['x'], y - figure['y'],

class Figure(ABC):
    def __init__(self, figure_id, figure, map_jso):
        self.id = figure_id
        self.figure = figure
        self.map_jso = map_jso

    @abstractmethod
    def move(self, to_x:int, to_y:int, realize=True, **kwargs) -> bool:
        """
        :param to_x:
        :param to_y:
        :param kwargs: target, socketio
        :param realize: save changes for figures changes
        :return: if move is valid
        """
        raise NotImplementedError

    @abstractmethod # after move action, return what should be done after valid move
    def after_move(self, **kargs) -> dict|None:
        return None

    def checked(self, color_exclude=None):
        return checked(self.figure['x'], self.figure['y'], self.map_jso, color_exclude=color_exclude)



    #def attacking() -> {[int, int]}:
    #    #TODO get all attacking places
    #    return None

    def free_gcd_path(self, to_x=None, to_y=None, to=None, not_checked=False, check_exlude=None) -> bool | int:
        """
        For all figures with symetric move, check if path is free
        Option 1:
        :param to_x:
        :param to_y:

        Option 2:
        :param to: to_x, to_y are not limits but only direction
        :param check_exlude:

        :param not_checked:
        :return if path is free, if to, return figure id
        """

        delta_x, delta_y = abs_delta(to_x, to_y, self.figure)
        gcd = math.gcd(delta_x, delta_y)
        d_x, d_y = delta_x/gcd, delta_y/gcd
        i = 1
        while True:
            p_x, p_y = i * d_x, i * d_y

            new_x, new_y = int(self.figure['x'] + p_x), int(self.figure['y'] + p_y)

            if to is not None: #limit, place not exists
                if not exists(new_x, new_y, self.map_jso):
                    return False
            elif p_x == delta_x and p_y == delta_y: #limit, end of path
                return True

            #If there is no figure on path
            if not free_place(new_x, new_y, self.map_jso):
                fig_id, to_fig = get_fig_at(new_x, new_y, self.map_jso)
                if fig_id is not None and to_fig['fig_type'] == to:
                    return fig_id
                return False

            #If place is not check by any figure
            if not_checked and checked(new_x, new_y, self.map_jso, color_exclude=check_exlude):
                return False

            i += 1

def kill(map_jso, target_key, realize=True) -> bool: #can be killed?
    if target_key is None:
        return False
    if realize:
        figures = (map_jso['status']['figures'])
        map_jso['status']['figures'] = {key:value
                                        for key, value in figures.items()
                                        if key != target_key}
    return True

def mview(x, y ,view):
    """
    convert player view to absolute view
    """
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
    return mview(x - figure['x'], y - figure['y'], view)

def get_fig_class(fig_type: str):
    try:
        module = importlib.import_module(f'figure_types.{fig_type}')
        return getattr(module, fig_type.capitalize())
    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Unknown figure type: {fig_type} {e}") from e


def exists(x, y, map_jso)->bool: #exist lace on the board?
    if map_jso['start']['load_type'] == 'chess_classic':
        return 0 <= x < map_jso['start']['size'] and 0 <= y < map_jso['start']['size']
    else:
        raise NotImplementedError("Not implemented for this load type")


def signum(n) -> 0|1|-1:
    return 0 if n == 0 else 1 if n > 0 else -1