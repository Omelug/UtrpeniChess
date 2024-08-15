import logging

import figures
from figures import Figure, rel_delta, free_place, kill, exists, abs_delta


class Pawn(Figure):
    def move(self, to_x, to_y, realize=True, **kwargs):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        first_step = (delta_y == 2 and delta_x == 0 and self.figure['moved'] == False)
        hungry = ((abs(delta_x) == 1) and delta_y == 1 and kill(self.map_jso, kwargs.get('target'), realize=realize))
        one_up = ((delta_x == 0) and (delta_y == 1))
        el_passant = (abs(delta_x) == 1 and (delta_y == 1) and self.map_jso['status']['en_passant'] is not None)

        abs_d_x, abs_d_y = abs_delta(to_x, to_y, self.figure)
        if first_step and (not free_place(to_x, to_y - abs_d_y / 2, self.map_jso) or not free_place(to_x, to_y, self.map_jso)):
            logging.error(f"Invalid move: first step ({to_x};{ to_y - abs_d_y / 2}) {first_step} {free_place(to_x, to_y - delta_y / 2, self.map_jso)} {free_place(to_x, to_y, self.map_jso)}")
            return False
        if one_up and not free_place(to_x, to_y, self.map_jso):
            logging.error(f"Invalid move: one up {one_up} {free_place(to_x, to_y, self.map_jso)}")
            return False

        if el_passant:
            fig_id, _ = figures.get_fig_at(to_x, to_y - abs_d_y , self.map_jso)
            if fig_id == self.map_jso['status']['en_passant']:
                #, but in normal game this never be done
                kill(self.map_jso, fig_id, realize=realize)
                if realize:
                    kwargs.get('socketio').emit('fig_action', {'killed': fig_id})
                return True
            return False

        result = one_up or first_step or hungry
        pawn = self.map_jso['status']['figures'][self.id]
        if result and realize and pawn['moved'] != True:
            if first_step:
                # in next move this pawn can be eaten by en passant
                self.map_jso['status']['en_passant'] = self.id
            else:
                pawn['moved'] = True
        return result

    def after_move(self,**kwargs):
        #return {"action_type":"change", "avaible":["queen","horse","bishop","tower"]}
        if not exists(self.figure['x'], self.figure['y']-1, self.map_jso):
            return {"type":"change", "avaible":["queen","horse","bishop","tower"]}
        return None