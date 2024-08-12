from figures import Figure, rel_delta, free_place, kill, exists

class Pawn(Figure):
    def move(self, to_x, to_y, target=None):
        delta_x, delta_y = rel_delta(to_x, to_y, self.map_jso, self.figure)
        first_step = (delta_y == 2 and self.figure['moved'] == False)
        hungry = ((abs(delta_x) == 1) and delta_y == 1 and kill(self.map_jso, target))
        one_up = ((delta_x == 0) and (delta_y == 1))

        if first_step and not free_place(to_x, to_y+delta_y/2, self.map_jso):
            return False

        if one_up and not free_place(to_x, to_y, self.map_jso):
            return False

        result = one_up or first_step or hungry
        if result and not self.map_jso['status']['figures'][self.id]['moved']:
            self.map_jso['status']['figures'][self.id]['moved'] = True
        return result

    def after_move(self):
        return {"action_type":"change", "avaible":["queen","horse","bishop","tower"]}
        if not exists(self.figure['x'], self.figure['y']-1, self.map_jso):
            return {"type":"change", "avaible":["queen","horse","bishop","tower"]}
        return None