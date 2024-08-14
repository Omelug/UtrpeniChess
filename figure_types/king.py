import math
import figures
from figures import Figure, rel_delta, abs_delta


class King(Figure):
    def __init__(self, figure_id, figure, map_jso):
        super().__init__(figure_id, figure, map_jso)
        self.castling = None
    def move(self, to_x, to_y, target=None, realize=True):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        one_step = (abs(delta_x) <= 1) and (abs(delta_y) <= 1)
        castling =  self.figure['moved'] == False and abs(delta_x) == 2 and delta_y == 0
        if castling:
            if self.checked(color_exclude=self.figure['color']):
                return False
            tower_id = self.free_gcd_path(to_x=to_x,to_y= to_y, to="tower", not_checked=True, check_exlude=self.figure['color'])


            #invalid tower for castling?
            if not tower_id:
                return False

            tower = self.map_jso['status']['figures'][tower_id]
            if tower['moved'] or figures.checked(tower['x'],tower['y'],color_exclude=self.figure['color'], map_jso=self.map_jso):
                print("invalid tower for castling")
                return False

            if realize:
                king = self.map_jso['status']['figures'][self.id]
                abs_d_x, abs_d_y = abs_delta(to_x, to_y, self.figure)

                tower['x'] = king['x'] + figures.signum(abs_d_x)
                #tower['y'] = king['y'] + math.copysign(1, abs_d_y)
                tower['moved'] = True
                king['moved'] = True
                self.castling = tower_id



        return one_step or castling

    def after_move(self, **kwargs):
        if self.castling is not None:
            tower = self.map_jso['status']['figures'][self.castling]

            game_code = kwargs.get('game_code')
            socketio = kwargs.get('socket')
            if game_code is None and socketio is None:
                raise ValueError("game_code and socketio must be provided")
            socketio.emit('fig_action',{"active_fig": self.castling, "to": {'x': tower['x'],'y': tower['y']}}, room=game_code)
            return None
